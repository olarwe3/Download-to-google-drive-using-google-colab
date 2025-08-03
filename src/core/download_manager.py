"""
Main download manager class with optimized performance and error handling
"""
import os
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple, Optional, Dict, Any
import ipywidgets as widgets

from .validators import validate_url, validate_path, validate_filename
from ..utils.helpers import (
    get_filename_from_url, format_size, format_speed, format_time,
    create_folder_if_not_exists, parse_content_disposition, 
    detect_file_type_from_content
)
from ..utils.constants import DOWNLOAD_HEADERS, CONFIG

class DownloadManager:
    """Enhanced download manager with support for single and segmented downloads"""
    
    def __init__(self, config: Dict = None):
        self.config = config or CONFIG
        self.downloads = {}
        self.active_downloads = 0
        self.session = requests.Session()
        self.session.headers.update(DOWNLOAD_HEADERS)
    
    def get_file_info(self, url: str) -> Tuple[bool, Dict]:
        """Get file information from URL headers"""
        try:
            response = self.session.head(url, allow_redirects=True, timeout=15)
            response.raise_for_status()
            
            info = {
                'size': None,
                'filename': None,
                'content_type': None,
                'supports_ranges': False,
                'url': response.url  # Final URL after redirects
            }
            
            # Get file size
            if 'content-length' in response.headers:
                info['size'] = int(response.headers['content-length'])
            
            # Get filename from Content-Disposition
            if 'content-disposition' in response.headers:
                filename = parse_content_disposition(response.headers['content-disposition'])
                if filename:
                    info['filename'] = filename
            
            # Get content type
            if 'content-type' in response.headers:
                info['content_type'] = response.headers['content-type']
            
            # Check if server supports range requests
            if 'accept-ranges' in response.headers:
                info['supports_ranges'] = response.headers['accept-ranges'].lower() == 'bytes'
            
            return True, info
            
        except Exception as e:
            return False, {'error': str(e)}
    
    def download_file(self, url: str, destination_path: str, filename: str = None,
                     progress_widget: widgets.FloatProgress = None,
                     status_widget: widgets.HTML = None,
                     speed_widget: widgets.HTML = None) -> bool:
        """Download a single file with progress tracking"""
        try:
            # Validate inputs
            if not validate_url(url):
                if status_widget:
                    status_widget.value = "❌ Invalid URL"
                return False
            
            # Get file info
            info_success, file_info = self.get_file_info(url)
            if not info_success:
                if status_widget:
                    status_widget.value = f"❌ Cannot access file: {file_info.get('error', 'Unknown error')}"
                return False
            
            # Determine filename
            if not filename:
                filename = file_info.get('filename') or get_filename_from_url(url)
            
            # Validate and sanitize filename
            valid_filename, sanitized_filename = validate_filename(filename)
            if not valid_filename:
                if status_widget:
                    status_widget.value = f"❌ Invalid filename: {sanitized_filename}"
                return False
            filename = sanitized_filename
            
            # Validate destination path
            valid_path, normalized_path = validate_path(destination_path)
            if not valid_path:
                if status_widget:
                    status_widget.value = f"❌ Invalid path: {normalized_path}"
                return False
            destination_path = normalized_path
            
            # Create destination folder
            if not create_folder_if_not_exists(destination_path):
                if status_widget:
                    status_widget.value = "❌ Cannot create destination folder"
                return False
            
            full_path = os.path.join(destination_path, filename)
            
            # Check if file already exists
            if os.path.exists(full_path):
                if status_widget:
                    status_widget.value = f"⚠️ File exists: {filename}"
                return False
            
            # Update status
            if status_widget:
                status_widget.value = "⬇️ Downloading..."
            
            # Start download
            return self._download_with_progress(
                file_info['url'], full_path, file_info.get('size'),
                progress_widget, status_widget, speed_widget
            )
            
        except Exception as e:
            if status_widget:
                status_widget.value = f"❌ Error: {str(e)[:50]}..."
            return False
    
    def _download_with_progress(self, url: str, full_path: str, file_size: Optional[int],
                               progress_widget: widgets.FloatProgress = None,
                               status_widget: widgets.HTML = None,
                               speed_widget: widgets.HTML = None) -> bool:
        """Internal method to download with progress tracking"""
        try:
            # Start streaming download
            response = self.session.get(url, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Get file size if not already known
            if not file_size and 'content-length' in response.headers:
                file_size = int(response.headers['content-length'])
            
            downloaded = 0
            start_time = time.time()
            chunk_size = self.config['download']['chunk_size']
            
            # Write file with buffered I/O
            with open(full_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        self._update_progress(
                            downloaded, file_size, start_time,
                            progress_widget, speed_widget
                        )
            
            # Final update
            if status_widget:
                status_widget.value = f"✅ Downloaded: {os.path.basename(full_path)}"
            if progress_widget:
                progress_widget.value = 100
            
            return True
            
        except requests.exceptions.RequestException as e:
            if status_widget:
                status_widget.value = f"❌ Network error: {str(e)[:50]}..."
            return False
        except Exception as e:
            if status_widget:
                status_widget.value = f"❌ Error: {str(e)[:50]}..."
            return False
    
    def download_file_segmented(self, url: str, destination_path: str, filename: str = None,
                               progress_widget: widgets.FloatProgress = None,
                               status_widget: widgets.HTML = None,
                               speed_widget: widgets.HTML = None,
                               segments: int = 4) -> bool:
        """Download file using multiple segments for increased speed"""
        try:
            # Get file info first
            info_success, file_info = self.get_file_info(url)
            if not info_success:
                if status_widget:
                    status_widget.value = f"❌ Cannot access file: {file_info.get('error', 'Unknown error')}"
                return False
            
            file_size = file_info.get('size')
            supports_ranges = file_info.get('supports_ranges', False)
            
            # Check if segmented download is beneficial
            min_size = self.config['download']['min_file_size_for_segmentation']
            if not file_size or file_size < min_size or not supports_ranges:
                if status_widget:
                    status_widget.value = "📥 Using standard download (file too small or no range support)"
                return self.download_file(url, destination_path, filename, 
                                        progress_widget, status_widget, speed_widget)
            
            # Determine filename
            if not filename:
                filename = file_info.get('filename') or get_filename_from_url(url)
            
            # Validate inputs
            valid_filename, sanitized_filename = validate_filename(filename)
            if not valid_filename:
                if status_widget:
                    status_widget.value = f"❌ Invalid filename: {sanitized_filename}"
                return False
            filename = sanitized_filename
            
            valid_path, normalized_path = validate_path(destination_path)
            if not valid_path:
                if status_widget:
                    status_widget.value = f"❌ Invalid path: {normalized_path}"
                return False
            destination_path = normalized_path
            
            if not create_folder_if_not_exists(destination_path):
                if status_widget:
                    status_widget.value = "❌ Cannot create destination folder"
                return False
            
            full_path = os.path.join(destination_path, filename)
            
            if os.path.exists(full_path):
                if status_widget:
                    status_widget.value = f"⚠️ File exists: {filename}"
                return False
            
            if status_widget:
                status_widget.value = f"⚡ Starting {segments}-segment download..."
            
            # Download segments
            return self._download_segmented(
                file_info['url'], full_path, file_size, segments,
                progress_widget, status_widget, speed_widget
            )
            
        except Exception as e:
            if status_widget:
                status_widget.value = f"❌ Segmented download failed: {str(e)[:50]}..."
            return False
    
    def _download_segmented(self, url: str, full_path: str, file_size: int, segments: int,
                           progress_widget: widgets.FloatProgress = None,
                           status_widget: widgets.HTML = None,
                           speed_widget: widgets.HTML = None) -> bool:
        """Internal method for segmented download"""
        try:
            # Calculate segment ranges
            segment_size = file_size // segments
            ranges = []
            for i in range(segments):
                start = i * segment_size
                end = start + segment_size - 1 if i < segments - 1 else file_size - 1
                ranges.append((start, end))
            
            # Download segments concurrently
            segment_files = []
            downloaded_total = 0
            start_time = time.time()
            download_lock = threading.Lock()
            
            def download_segment(segment_id: int, start_byte: int, end_byte: int) -> bool:
                nonlocal downloaded_total
                
                segment_headers = DOWNLOAD_HEADERS.copy()
                segment_headers['Range'] = f'bytes={start_byte}-{end_byte}'
                
                segment_file = f"{full_path}.part{segment_id}"
                segment_files.append(segment_file)
                
                try:
                    response = self.session.get(url, headers=segment_headers, 
                                              stream=True, timeout=30)
                    response.raise_for_status()
                    
                    with open(segment_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=self.config['download']['chunk_size']):
                            if chunk:
                                f.write(chunk)
                                with download_lock:
                                    downloaded_total += len(chunk)
                                    self._update_progress(
                                        downloaded_total, file_size, start_time,
                                        progress_widget, speed_widget, segmented=True
                                    )
                    return True
                except Exception as e:
                    print(f"Segment {segment_id} failed: {e}")
                    return False
            
            # Execute downloads in parallel
            with ThreadPoolExecutor(max_workers=segments) as executor:
                futures = []
                for i, (start, end) in enumerate(ranges):
                    future = executor.submit(download_segment, i, start, end)
                    futures.append(future)
                
                # Wait for completion
                all_success = all(future.result() for future in futures)
            
            if not all_success:
                # Clean up and fallback
                for segment_file in segment_files:
                    if os.path.exists(segment_file):
                        os.remove(segment_file)
                if status_widget:
                    status_widget.value = "❌ Some segments failed, falling back to regular download"
                return self.download_file(url, os.path.dirname(full_path), 
                                        os.path.basename(full_path),
                                        progress_widget, status_widget, speed_widget)
            
            # Combine segments
            if status_widget:
                status_widget.value = "🔧 Combining segments..."
                
            with open(full_path, 'wb') as output_file:
                for i in range(segments):
                    segment_file = f"{full_path}.part{i}"
                    if os.path.exists(segment_file):
                        with open(segment_file, 'rb') as segment:
                            output_file.write(segment.read())
                        os.remove(segment_file)
            
            if progress_widget:
                progress_widget.value = 100
            if status_widget:
                status_widget.value = f"✅ Downloaded: {os.path.basename(full_path)} (Segmented)"
            
            return True
            
        except Exception as e:
            # Clean up partial files
            for segment_file in segment_files:
                if os.path.exists(segment_file):
                    os.remove(segment_file)
            raise e
    
    def download_multiple(self, urls: List[str], destination_path: str, 
                         max_workers: int = None) -> List[Tuple[str, bool]]:
        """Download multiple files concurrently"""
        if max_workers is None:
            max_workers = self.config['download']['max_workers']
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {}
            
            for i, url in enumerate(urls):
                if validate_url(url):
                    filename = get_filename_from_url(url)
                    
                    # Create progress widgets
                    progress_widget = widgets.FloatProgress(
                        value=0, min=0, max=100, 
                        description=f'File {i+1}:',
                        layout=widgets.Layout(width='100%')
                    )
                    status_widget = widgets.HTML(value="⏳ Queued...")
                    speed_widget = widgets.HTML(value="")
                    
                    # Display widgets
                    from IPython.display import display
                    display(widgets.VBox([
                        widgets.HTML(value=f"<b>📁 {filename}</b>"),
                        progress_widget,
                        status_widget,
                        speed_widget
                    ]))
                    
                    # Submit download task
                    future = executor.submit(
                        self.download_file,
                        url, destination_path, filename,
                        progress_widget, status_widget, speed_widget
                    )
                    future_to_url[future] = url
            
            # Collect results
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append((url, result))
                except Exception as e:
                    results.append((url, False))
        
        return results
    
    def _update_progress(self, downloaded: int, file_size: Optional[int], start_time: float,
                        progress_widget: widgets.FloatProgress = None,
                        speed_widget: widgets.HTML = None,
                        segmented: bool = False):
        """Update progress widgets with current download status"""
        try:
            # Update progress bar
            if progress_widget and file_size and file_size > 0:
                progress = min(100, (downloaded / file_size) * 100)
                progress_widget.value = progress
            
            # Update speed display
            if speed_widget:
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    speed = downloaded / elapsed_time
                    speed_text = f"Speed: {format_speed(speed)}"
                    
                    if segmented:
                        speed_text += " (Segmented)"
                    
                    # Add ETA if we know the file size
                    if file_size and file_size > 0 and speed > 0:
                        remaining = file_size - downloaded
                        eta = remaining / speed
                        if eta < 60:
                            eta_str = f" | ETA: {int(eta)}s"
                        elif eta < 3600:
                            eta_str = f" | ETA: {int(eta/60)}m {int(eta%60)}s"
                        else:
                            eta_str = f" | ETA: {int(eta/3600)}h {int((eta%3600)/60)}m"
                        speed_text += eta_str
                    
                    speed_widget.value = speed_text
        except:
            pass  # Ignore errors in progress updates
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.session.close()
        except:
            pass
