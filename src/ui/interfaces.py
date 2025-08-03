"""
User interface components for the Avance Download Manager
"""
import os
import time
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
from typing import Optional

from ..core import DownloadManager, FileManager
from ..core.archive_manager import get_archive_info, extract_archive, create_archive
from ..core.validators import validate_url, validate_filename
from ..utils import (
    get_filename_from_url, format_size, format_speed, create_folder_if_not_exists,
    get_available_folders, ensure_downloads_folder, get_storage_info
)
from .themes import (
    get_adaptive_css, get_speed_tips_html, get_error_display_html,
    get_success_display_html, get_theme_adaptation_script
)

def create_single_download_interface() -> widgets.VBox:
    """Create single file download interface with speed optimization options"""
    
    url_input = widgets.Text(
        placeholder="🔗 Enter download URL here...",
        description="URL:",
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%', height='35px')
    )

    filename_input = widgets.Text(
        placeholder="Optional: Custom filename (leave empty for auto-detect)",
        description="Filename:",
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    # Speed optimization options
    speed_mode = widgets.Dropdown(
        options=[
            ('🚀 High Speed (Segmented)', 'segmented'),
            ('⚡ Optimized (Single)', 'optimized'),
            ('🔄 Standard', 'standard')
        ],
        value='segmented',
        description='Download Mode:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    segments_slider = widgets.IntSlider(
        value=4,
        min=2,
        max=8,
        step=1,
        description='Segments:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='45%')
    )

    folder_options = get_available_folders()
    default_folder_value = ensure_downloads_folder()

    folder_dropdown = widgets.Dropdown(
        options=folder_options,
        value=default_folder_value if any(val == default_folder_value for label, val in folder_options) else folder_options[0][1],
        description='Destination:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    custom_folder_input = widgets.Text(
        placeholder="Or enter custom folder path...",
        description="Custom Path:",
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    download_btn = widgets.Button(
        description="🚀 Start Download",
        button_style='primary',
        layout=widgets.Layout(width='200px', height='40px')
    )

    progress_bar = widgets.FloatProgress(
        value=0,
        min=0,
        max=100,
        description='Progress:',
        bar_style='info',
        style={'bar_color': '#3498db'},
        layout=widgets.Layout(width='95%')
    )

    status_display = widgets.HTML(value="🔧 Ready to download")
    speed_display = widgets.HTML(value="")
    output_area = widgets.Output()

    def update_segments_visibility(change):
        """Show/hide segments slider based on download mode"""
        if change['new'] == 'segmented':
            segments_slider.layout.visibility = 'visible'
        else:
            segments_slider.layout.visibility = 'hidden'

    speed_mode.observe(update_segments_visibility, names='value')

    def on_download_click(b):
        with output_area:
            clear_output(wait=True)

            url = url_input.value.strip()
            custom_filename = filename_input.value.strip()
            destination = custom_folder_input.value.strip() or folder_dropdown.value
            download_mode = speed_mode.value
            num_segments = segments_slider.value

            if not url:
                status_display.value = "❌ Please enter a URL"
                return

            if not validate_url(url):
                status_display.value = "❌ Invalid URL format"
                return

            if not create_folder_if_not_exists(destination):
                status_display.value = "❌ Cannot create destination folder"
                return

            filename = get_filename_from_url(url, custom_filename)
            progress_bar.value = 0
            download_btn.disabled = True

            # Initialize download manager
            dm = DownloadManager()

            # Choose download method based on selected mode
            try:
                if download_mode == 'segmented':
                    download_btn.description = "⏳ Segmented Download..."
                    print(f"🚀 Starting high-speed segmented download with {num_segments} segments")
                    success = dm.download_file_segmented(
                        url, destination, filename, progress_bar, status_display, speed_display, num_segments
                    )
                elif download_mode == 'optimized':
                    download_btn.description = "⏳ Optimized Download..."
                    print("⚡ Starting optimized single-connection download")
                    success = dm.download_file(
                        url, destination, filename, progress_bar, status_display, speed_display
                    )
                else:  # standard
                    download_btn.description = "⏳ Standard Download..."
                    print("🔄 Starting standard download")
                    success = dm.download_file(
                        url, destination, filename, progress_bar, status_display, speed_display
                    )

                if success:
                    print(f"✅ Successfully downloaded: {filename}")
                    print(f"📁 Location: {destination}")
                    print(f"🚀 Mode used: {download_mode}")
                else:
                    print(f"❌ Download failed for: {url}")

            except Exception as e:
                print(f"❌ Error during download: {str(e)}")
                status_display.value = f"❌ Error: {str(e)[:50]}..."
            
            finally:
                download_btn.disabled = False
                download_btn.description = "🚀 Start Download"
                dm.cleanup()

    download_btn.on_click(on_download_click)

    interface = widgets.VBox([
        widgets.HTML("<h3>🎯 Single File Download</h3>"),
        url_input,
        filename_input,
        widgets.HTML("<h4>⚡ Speed Optimization</h4>"),
        widgets.HBox([speed_mode, segments_slider]),
        widgets.HTML("<i>💡 Segmented mode splits large files into multiple parts for faster downloads</i>"),
        widgets.HTML("<br>"),
        widgets.HBox([folder_dropdown]),
        custom_folder_input,
        widgets.HTML("<br>"),
        download_btn,
        widgets.HTML("<br>"),
        progress_bar,
        status_display,
        speed_display,
        output_area
    ])

    return interface

def create_multiple_downloads_interface() -> widgets.VBox:
    """Create multiple downloads interface"""

    urls_textarea = widgets.Textarea(
        placeholder="Enter download URLs here (one per line):\\nhttps://example.com/file1.zip\\nhttps://example.com/file2.pdf\\nhttps://example.com/file3.mp4",
        description="URLs:",
        rows=8,
        layout=widgets.Layout(width='95%', height='200px')
    )

    max_workers_slider = widgets.IntSlider(
        value=5,
        min=1,
        max=10,
        step=1,
        description='Concurrent Downloads:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    batch_folder_options = get_available_folders()
    default_batch_folder_value = ensure_downloads_folder()

    batch_folder_dropdown = widgets.Dropdown(
        options=batch_folder_options,
        value=default_batch_folder_value if any(val == default_batch_folder_value for label, val in batch_folder_options) else batch_folder_options[0][1] if batch_folder_options else '',
        description='Destination:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    batch_custom_folder = widgets.Text(
        placeholder="Or enter custom folder path...",
        description="Custom Path:",
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    start_batch_btn = widgets.Button(
        description="🚀 Start Batch Download",
        button_style='success',
        layout=widgets.Layout(width='200px', height='40px')
    )

    validate_urls_btn = widgets.Button(
        description="🔍 Validate URLs",
        button_style='info',
        layout=widgets.Layout(width='150px', height='40px')
    )

    clear_urls_btn = widgets.Button(
        description="🗑️ Clear",
        button_style='warning',
        layout=widgets.Layout(width='100px', height='40px')
    )

    batch_status = widgets.HTML(value="📋 Ready for batch download")
    batch_output = widgets.Output()

    def validate_urls_click(b):
        with batch_output:
            clear_output(wait=True)
            urls = [url.strip() for url in urls_textarea.value.split('\\n') if url.strip()]

            if not urls:
                batch_status.value = "❌ No URLs entered"
                return

            valid_urls = []
            invalid_urls = []

            for url in urls:
                if validate_url(url):
                    valid_urls.append(url)
                else:
                    invalid_urls.append(url)

            print(f"✅ Valid URLs: {len(valid_urls)}")
            print(f"❌ Invalid URLs: {len(invalid_urls)}")

            if invalid_urls:
                print("\\n🚫 Invalid URLs found:")
                for invalid_url in invalid_urls[:5]:
                    print(f"  • {invalid_url}")
                if len(invalid_urls) > 5:
                    print(f"  ... and {len(invalid_urls) - 5} more")

            batch_status.value = f"✅ {len(valid_urls)} valid, ❌ {len(invalid_urls)} invalid URLs"

    def clear_urls_click(b):
        urls_textarea.value = ""
        batch_status.value = "📋 URLs cleared"
        with batch_output:
            clear_output()

    def start_batch_download_click(b):
        with batch_output:
            clear_output(wait=True)

            urls = [url.strip() for url in urls_textarea.value.split('\\n') if url.strip()]
            destination = batch_custom_folder.value.strip() or batch_folder_dropdown.value
            max_workers = max_workers_slider.value

            if not urls:
                batch_status.value = "❌ No URLs entered"
                return

            valid_urls = [url for url in urls if validate_url(url)]

            if not valid_urls:
                batch_status.value = "❌ No valid URLs found"
                return

            if not create_folder_if_not_exists(destination):
                batch_status.value = "❌ Cannot create destination folder"
                return

            start_batch_btn.disabled = True
            start_batch_btn.description = "⏳ Downloading..."

            batch_status.value = f"🚀 Starting download of {len(valid_urls)} files with {max_workers} concurrent downloads..."

            print(f"📥 Starting batch download...")
            print(f"📁 Destination: {destination}")
            print(f"🔗 URLs to download: {len(valid_urls)}")
            print(f"⚡ Concurrent downloads: {max_workers}")
            print("=" * 50)

            # Initialize download manager
            dm = DownloadManager()
            
            try:
                start_time = time.time()
                results = dm.download_multiple(valid_urls, destination, max_workers)
                end_time = time.time()

                successful = sum(1 for _, success in results if success)
                failed = len(results) - successful
                total_time = end_time - start_time

                print("=" * 50)
                print(f"📊 Batch Download Complete!")
                print(f"✅ Successful: {successful}")
                print(f"❌ Failed: {failed}")
                print(f"⏱️ Total time: {total_time:.1f} seconds")

                batch_status.value = f"📊 Complete: ✅ {successful} successful, ❌ {failed} failed"
            
            except Exception as e:
                print(f"❌ Batch download error: {str(e)}")
                batch_status.value = f"❌ Batch download failed: {str(e)[:50]}..."
            
            finally:
                start_batch_btn.disabled = False
                start_batch_btn.description = "🚀 Start Batch Download"
                dm.cleanup()

    validate_urls_btn.on_click(validate_urls_click)
    clear_urls_btn.on_click(clear_urls_click)
    start_batch_btn.on_click(start_batch_download_click)

    interface = widgets.VBox([
        widgets.HTML("<h3>⚡ Multiple Concurrent Downloads</h3>"),
        urls_textarea,
        widgets.HTML("<br>"),
        widgets.HBox([max_workers_slider, batch_folder_dropdown]),
        batch_custom_folder,
        widgets.HTML("<br>"),
        widgets.HBox([start_batch_btn, validate_urls_btn, clear_urls_btn]),
        widgets.HTML("<br>"),
        batch_status,
        batch_output
    ])

    return interface

def create_file_management_interface() -> widgets.VBox:
    """Create file management interface"""

    storage_info_widget = widgets.HTML()
    default_path = ensure_downloads_folder()

    folder_path_input = widgets.Text(
        value=default_path,
        description='Browse Folder:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='70%')
    )

    browse_btn = widgets.Button(
        description="🗂️ Browse",
        button_style='info',
        layout=widgets.Layout(width='100px')
    )

    refresh_btn = widgets.Button(
        description="🔄 Refresh",
        button_style='primary',
        layout=widgets.Layout(width='100px')
    )

    delete_btn = widgets.Button(
        description="🗑️ Delete",
        button_style='danger',
        layout=widgets.Layout(width='100px')
    )

    create_folder_btn = widgets.Button(
        description="📁 New Folder",
        button_style='success',
        layout=widgets.Layout(width='120px')
    )

    new_folder_input = widgets.Text(
        placeholder="Enter new folder name...",
        description='Folder Name:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    delete_path_input = widgets.Text(
        placeholder="Enter file/folder path to delete...",
        description='Delete Path:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='70%')
    )

    file_browser_output = widgets.Output(layout=widgets.Layout(background='transparent'))

    def get_storage_info_display():
        try:
            if not os.path.exists('/content/drive/MyDrive'):
                storage_info_widget.value = "<p>⚠️ Google Drive is not mounted. Please run the Drive mounting cell first.</p>"
                return

            storage_data, error = get_storage_info()
            if error:
                storage_info_widget.value = f"<p>❌ Cannot retrieve storage information: {error}</p>"
                return

            storage_info_widget.value = f"""
            <div style='background-color: var(--colab-secondary-surface-color, #f0f0f0); padding: 10px; border-radius: 5px; margin: 10px 0;'>
                <h4>💾 Google Drive Storage</h4>
                <p>📊 Total: {format_size(storage_data['total'])} |
                   📁 Used: {format_size(storage_data['used'])} |
                   💽 Free: {format_size(storage_data['free'])}</p>
                <p>Usage: {storage_data['usage_percent']:.1f}%</p>
            </div>
            """
        except Exception as e:
            storage_info_widget.value = f"<p>❌ Cannot retrieve storage information: {str(e)}</p>"

    def browse_folder(folder_path):
        with file_browser_output:
            clear_output(wait=True)

            if not os.path.exists(folder_path):
                print(f"❌ Folder does not exist: {folder_path}")
                return

            try:
                fm = FileManager()
                contents = fm.browse_folder(folder_path)
                
                if 'error' in contents:
                    print(f"❌ Error: {contents['error']}")
                    return

                print(f"📁 Contents of: {folder_path}")
                print("=" * 60)

                if contents['folders']:
                    print("📂 Folders:")
                    for folder in contents['folders']:
                        print(f"  📁 {folder['name']}/ ({folder['size_formatted']})")
                    print()

                if contents['files']:
                    print("📄 Files:")
                    for file in contents['files']:
                        print(f"  📄 {file['name']} ({file['size_formatted']})")

                if not contents['folders'] and not contents['files']:
                    print("📭 Folder is empty")

                print(f"\\n📊 Total: {contents['total_folders']} folders, {contents['total_files']} files")
                print(f"💾 Total size: {format_size(contents['total_size'])}")

            except Exception as e:
                print(f"❌ Error browsing folder: {str(e)}")

    def on_browse_click(b):
        folder_path = folder_path_input.value.strip()
        browse_folder(folder_path)

    def on_refresh_click(b):
        get_storage_info_display()
        folder_path = folder_path_input.value.strip()
        browse_folder(folder_path)

    def on_delete_click(b):
        delete_path = delete_path_input.value.strip()

        if not delete_path:
            with file_browser_output:
                print("❌ Please enter a path to delete")
            return

        if not os.path.exists(delete_path):
            with file_browser_output:
                print(f"❌ Path does not exist: {delete_path}")
            return

        # Confirmation prompt
        item_type = "folder" if os.path.isdir(delete_path) else "file"
        item_name = os.path.basename(delete_path)

        with file_browser_output:
            print(f"⚠️ Are you sure you want to delete this {item_type}: {item_name}?")
            print("Type 'YES' to confirm or anything else to cancel:")

        # Simple confirmation system
        confirm_input = widgets.Text(
            placeholder="Type YES to confirm deletion",
            description='Confirm:',
            layout=widgets.Layout(width='300px')
        )

        confirm_btn = widgets.Button(
            description="Confirm Delete",
            button_style='danger',
            layout=widgets.Layout(width='120px')
        )

        def confirm_delete(b):
            if confirm_input.value.strip().upper() == 'YES':
                fm = FileManager()
                success, message = fm.delete_item(delete_path)
                with file_browser_output:
                    if success:
                        print(f"✅ {message}")
                        delete_path_input.value = ""
                        on_refresh_click(None)
                    else:
                        print(f"❌ {message}")
            else:
                with file_browser_output:
                    print("❌ Deletion cancelled")

            # Remove confirmation widgets
            confirm_input.close()
            confirm_btn.close()

        confirm_btn.on_click(confirm_delete)
        display(widgets.HBox([confirm_input, confirm_btn]))

    def on_create_folder_click(b):
        folder_name = new_folder_input.value.strip()
        base_path = folder_path_input.value.strip()

        if not folder_name:
            with file_browser_output:
                print("❌ Please enter a folder name")
            return

        try:
            fm = FileManager()
            success, message = fm.create_folder(base_path, folder_name)
            
            with file_browser_output:
                if success:
                    print(f"✅ {message}")
                    new_folder_input.value = ""
                    browse_folder(base_path)
                else:
                    print(f"❌ {message}")
        except Exception as e:
            with file_browser_output:
                print(f"❌ Error creating folder: {str(e)}")

    browse_btn.on_click(on_browse_click)
    refresh_btn.on_click(on_refresh_click)
    delete_btn.on_click(on_delete_click)
    create_folder_btn.on_click(on_create_folder_click)

    get_storage_info_display()
    if os.path.exists(folder_path_input.value):
        browse_folder(folder_path_input.value)
    else:
        with file_browser_output:
            print("⚠️ Please mount Google Drive first, then refresh this section.")

    interface = widgets.VBox([
        widgets.HTML("<h3>📂 File Management & Utilities</h3>"),
        storage_info_widget,
        widgets.HBox([folder_path_input, browse_btn]),
        widgets.HBox([refresh_btn, delete_btn, create_folder_btn]),
        widgets.HBox([new_folder_input]),
        widgets.HBox([delete_path_input]),
        file_browser_output
    ])

    return interface

def create_archive_management_interface() -> widgets.VBox:
    """Create archive management interface"""

    # Operation selection dropdown
    operation_dropdown = widgets.Dropdown(
        options=[
            ('🔍 Analyze Archive', 'analyze'),
            ('📦 Extract Archive', 'extract'),
            ('🗜️ Create Archive', 'create')
        ],
        value='analyze',
        description='Operation:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='60%')
    )

    # Archive file path
    archive_path_input = widgets.Text(
        placeholder="Enter path to archive file (zip, rar, 7z, tar, etc.)",
        description='Archive File:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    # Destination folder dropdown
    destination_dropdown = widgets.Dropdown(
        options=get_available_folders(),
        value=ensure_downloads_folder(),
        description='Destination:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    # Custom destination path
    custom_destination_input = widgets.Text(
        placeholder="Or enter custom Google Drive path...",
        description='Custom Path:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    # Password input for encrypted archives
    password_input = widgets.Password(
        placeholder="Password (if required)",
        description='Password:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    # Archive creation specific inputs
    source_path_input = widgets.Text(
        placeholder="Enter path to file/folder to compress",
        description='Source:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='95%')
    )

    output_filename_input = widgets.Text(
        placeholder="Output filename (e.g., my_archive.zip)",
        description='Filename:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='70%')
    )

    archive_type_dropdown = widgets.Dropdown(
        options=[('ZIP', 'zip'), ('TAR', 'tar'), ('TAR.GZ', 'tar.gz'), ('7Z', '7z')],
        value='zip',
        description='Archive Type:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='30%')
    )

    compression_slider = widgets.IntSlider(
        value=6,
        min=0,
        max=9,
        step=1,
        description='Compression:',
        style={'description_width': 'initial'},
        layout=widgets.Layout(width='50%')
    )

    # Execute button
    execute_btn = widgets.Button(
        description="🚀 Execute",
        button_style='primary',
        layout=widgets.Layout(width='150px', height='35px')
    )

    # Dynamic UI containers
    extract_ui = widgets.VBox([
        widgets.HTML("<h4>📦 Extract Archive Settings</h4>"),
        widgets.HBox([destination_dropdown, password_input]),
        custom_destination_input
    ], layout=widgets.Layout(display='none'))

    create_ui = widgets.VBox([
        widgets.HTML("<h4>🗜️ Create Archive Settings</h4>"),
        source_path_input,
        widgets.HBox([output_filename_input, archive_type_dropdown]),
        widgets.HBox([destination_dropdown]),
        custom_destination_input,
        widgets.HBox([compression_slider])
    ], layout=widgets.Layout(display='none'))

    # Output area
    archive_output = widgets.Output()

    def update_ui_visibility(change):
        """Update UI based on selected operation"""
        operation = change['new']

        # Hide all specific UIs first
        extract_ui.layout.display = 'none'
        create_ui.layout.display = 'none'

        # Update button text and show relevant UI
        if operation == 'analyze':
            execute_btn.description = "🔍 Analyze"
            execute_btn.button_style = 'info'
        elif operation == 'extract':
            execute_btn.description = "📦 Extract"
            execute_btn.button_style = 'primary'
            extract_ui.layout.display = 'block'
        elif operation == 'create':
            execute_btn.description = "🗜️ Create"
            execute_btn.button_style = 'success'
            create_ui.layout.display = 'block'

    def on_execute_click(b):
        """Handle execute button click based on selected operation"""
        operation = operation_dropdown.value

        with archive_output:
            clear_output(wait=True)

            if operation == 'analyze':
                # Analyze Archive
                archive_path = archive_path_input.value.strip()

                if not archive_path:
                    print("❌ Please enter archive file path")
                    return

                if not os.path.exists(archive_path):
                    print(f"❌ Archive file not found: {archive_path}")
                    return

                print("🔍 Analyzing archive...")
                info = get_archive_info(archive_path)

                if 'error' in info:
                    print(f"❌ Error analyzing archive: {info['error']}")
                    return

                print(f"📦 Archive Analysis: {os.path.basename(archive_path)}")
                print("=" * 50)
                print(f"📄 Type: {info['type']}")
                print(f"📊 Size: {info['size_formatted']}")
                print(f"✅ Supported: {'Yes' if info['supported'] else 'No'}")

                if 'files' in info:
                    print(f"📁 Files: {info['files']}")

                if 'content' in info and info['content']:
                    print("\\n📋 Contents (first 10 files):")
                    for item in info['content']:
                        print(f"  • {item}")

            elif operation == 'extract':
                # Extract Archive
                archive_path = archive_path_input.value.strip()
                destination = custom_destination_input.value.strip() or destination_dropdown.value
                password = password_input.value.strip() if password_input.value else None

                if not archive_path:
                    print("❌ Please enter archive file path")
                    return

                if not os.path.exists(archive_path):
                    print(f"❌ Archive file not found: {archive_path}")
                    return

                execute_btn.disabled = True
                execute_btn.description = "⏳ Extracting..."

                print(f"📦 Extracting: {os.path.basename(archive_path)}")
                print(f"📁 Destination: {destination}")
                if password:
                    print("🔐 Using password protection")
                print("=" * 50)

                try:
                    success, message = extract_archive(archive_path, destination, password)

                    if success:
                        print(f"✅ {message}")
                        print(f"📁 Files extracted to Google Drive: {destination}")
                    else:
                        print(f"❌ {message}")
                except Exception as e:
                    print(f"❌ Extraction error: {str(e)}")

                execute_btn.disabled = False
                execute_btn.description = "📦 Extract"

            elif operation == 'create':
                # Create Archive
                source_path = source_path_input.value.strip()
                output_filename = output_filename_input.value.strip()
                destination = custom_destination_input.value.strip() or destination_dropdown.value
                archive_type = archive_type_dropdown.value
                compression_level = compression_slider.value

                if not source_path:
                    print("❌ Please enter source path")
                    return

                if not output_filename:
                    print("❌ Please enter output filename")
                    return

                if not os.path.exists(source_path):
                    print(f"❌ Source path not found: {source_path}")
                    return

                # Create full output path
                output_path = os.path.join(destination, output_filename)

                execute_btn.disabled = True
                execute_btn.description = "⏳ Creating..."

                print(f"🗜️ Creating {archive_type.upper()} archive")
                print(f"📁 Source: {source_path}")
                print(f"📄 Output: {output_path}")
                print(f"⚙️ Compression Level: {compression_level}")
                print("=" * 50)

                try:
                    success, message = create_archive(source_path, output_path, archive_type, compression_level)

                    if success:
                        print(f"✅ {message}")
                        try:
                            size = os.path.getsize(output_path)
                            print(f"📊 Archive size: {format_size(size)}")
                            print(f"💾 Saved to Google Drive: {output_path}")
                        except:
                            pass
                    else:
                        print(f"❌ {message}")
                except Exception as e:
                    print(f"❌ Archive creation error: {str(e)}")

                execute_btn.disabled = False
                execute_btn.description = "🗜️ Create"

    # Connect event handlers
    operation_dropdown.observe(update_ui_visibility, names='value')
    execute_btn.on_click(on_execute_click)

    # Initialize UI visibility
    update_ui_visibility({'new': operation_dropdown.value})

    interface = widgets.VBox([
        widgets.HTML("<h3>📦 Archive Management (ZIP/RAR/7Z)</h3>"),
        widgets.HTML("<p><i>All archives and extracted files are automatically saved to your Google Drive</i></p>"),
        operation_dropdown,
        widgets.HTML("<br>"),
        archive_path_input,
        extract_ui,
        create_ui,
        widgets.HTML("<br>"),
        execute_btn,
        widgets.HTML("<br>"),
        archive_output
    ])

    return interface

def create_main_interface() -> tuple:
    """Create the main interface with system status"""
    
    # System status check
    def get_system_status():
        drive_mounted = os.path.exists('/content/drive/MyDrive')
        downloads_folder = os.path.exists('/content/drive/MyDrive/Downloads')
        # We can't check for download_manager here as it might not be in global scope
        
        if drive_mounted and downloads_folder:
            return "good", "Ready"
        elif not drive_mounted:
            return "error", "Run Cell 1"
        else:
            return "warning", "Setup Issue"

    status_type, status_message = get_system_status()
    
    # Get adaptive CSS
    interface_css = get_adaptive_css()
    
    # Main interface HTML
    main_interface_html = f"""
    <div class="dm-container">
        <div class="dm-header">
            <div class="dm-status">
                <span class="status-dot status-{status_type}"></span>
                <span>{status_message}</span>
            </div>
            <h1 class="dm-title">🚀 Download Manager</h1>
            <p class="dm-subtitle">Professional Google Drive Downloader</p>
        </div>
        <div class="dm-content">
            <div class="quick-section">
                <div class="quick-title">⚡ Quick Download</div>
            </div>
        </div>
    </div>
    """
    
    return interface_css, main_interface_html, status_type
