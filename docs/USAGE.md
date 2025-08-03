# Usage Guide

## Quick Start

### 1. Upload to Google Colab

1. Upload the entire `avance-download-manager` folder to your Google Drive
2. Open `main_notebook.ipynb` in Google Colab
3. Run the cells in order: Cell 1 → Cell 2 → Cell 3

### 2. Using Individual Components

You can also use the components programmatically:

```python
# Add the project to Python path
import sys
sys.path.append('/content/drive/MyDrive/avance-download-manager')

# Import components
from src.core import DownloadManager, FileManager
from src.core.archive_manager import extract_archive
```

## Features Overview

### 🚀 High-Speed Downloads

The download manager supports three download modes:

1. **Standard**: Traditional single-connection download
2. **Optimized**: Enhanced single-connection with better headers and chunking
3. **Segmented**: Multi-connection download for maximum speed

#### When to Use Segmented Downloads
- Files larger than 10MB
- Server supports range requests
- Good internet connection with low latency
- Downloading from fast servers

#### Configuration
```python
# For segmented downloads
success = dm.download_file_segmented(
    url="https://example.com/large_file.zip",
    destination_path="/content/drive/MyDrive/Downloads",
    filename="large_file.zip",
    segments=8  # Use 2-16 segments
)
```

### ⚡ Batch Downloads

Download multiple files simultaneously:

```python
urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.pdf",
    "https://example.com/file3.mp4"
]

results = dm.download_multiple(
    urls, 
    "/content/drive/MyDrive/Downloads",
    max_workers=5  # Adjust based on your connection
)
```

### 📦 Archive Management

#### Extracting Archives

Supports ZIP, RAR, 7Z, TAR, and compressed TAR formats:

```python
# Extract to default location
success, message = extract_archive("/path/to/archive.zip")

# Extract to specific location
success, message = extract_archive(
    "/path/to/archive.zip",
    "/content/drive/MyDrive/Extracted"
)

# Extract password-protected archive
success, message = extract_archive(
    "/path/to/encrypted.zip",
    "/content/drive/MyDrive/Extracted",
    password="secret123"
)
```

#### Creating Archives

```python
# Create ZIP archive
success, message = create_archive(
    "/content/drive/MyDrive/Documents",  # Source
    "/content/drive/MyDrive/backup.zip", # Destination
    "zip",                               # Format
    6                                    # Compression level (0-9)
)

# Create TAR.GZ archive
success, message = create_archive(
    "/path/to/folder",
    "/content/drive/MyDrive/archive.tar.gz",
    "tar.gz"
)
```

### 📁 File Management

#### Browsing Files

```python
fm = FileManager()

# Browse Downloads folder
contents = fm.browse_folder("/content/drive/MyDrive/Downloads")

print(f"Files: {contents['total_files']}")
print(f"Folders: {contents['total_folders']}")
print(f"Total size: {contents['total_size']} bytes")

# List files by category
for category, files in contents['file_categories'].items():
    print(f"{category}: {len(files)} files")
```

#### File Operations

```python
# Create folder
success, message = fm.create_folder(
    "/content/drive/MyDrive", 
    "NewFolder"
)

# Delete file or folder
success, message = fm.delete_item(
    "/content/drive/MyDrive/old_file.txt"
)

# Move file
success, message = fm.move_item(
    "/content/drive/MyDrive/file.txt",
    "/content/drive/MyDrive/Documents/file.txt"
)

# Copy file
success, message = fm.copy_item(
    "/content/drive/MyDrive/important.txt",
    "/content/drive/MyDrive/Backup/important.txt"
)
```

#### Searching Files

```python
# Search by name
results = fm.search_files("*.pdf")

# Search in specific location
results = fm.search_files("report", "/content/drive/MyDrive/Documents")

# Search by file type
results = fm.search_files("", file_type="video")

for file_info in results:
    print(f"{file_info['name']} - {file_info['size_formatted']}")
```

### 💾 Storage Management

```python
# Get storage information
storage_info, error = get_storage_info()
if not error:
    print(f"Total: {format_size(storage_info['total'])}")
    print(f"Used: {format_size(storage_info['used'])}")
    print(f"Free: {format_size(storage_info['free'])}")
    print(f"Usage: {storage_info['usage_percent']:.1f}%")

# Check if enough space for download
file_size = 100 * 1024 * 1024  # 100MB
has_space, message = check_available_space(file_size)
print(message)

# Get storage usage by category
usage = fm.get_storage_usage_by_category()
for category, info in usage['categories'].items():
    print(f"{category}: {info['size_formatted']} ({info['count']} files)")
```

## Performance Optimization

### Download Speed Tips

1. **Use Segmented Downloads** for files > 10MB
2. **Increase concurrent workers** for batch downloads (up to 10)
3. **Optimize chunk size** based on your connection:
   - Slow connection: 64KB chunks
   - Fast connection: 512KB chunks
4. **Choose appropriate segments**:
   - 2-4 segments for moderate files (10-100MB)
   - 4-8 segments for large files (100MB+)

### Configuration Optimization

```python
CONFIG = {
    "download": {
        "chunk_size": 524288,     # 512KB for fast connections
        "max_workers": 8,         # More concurrent downloads
        "max_segments": 8,        # Maximum segments for large files
        "timeout": 60,            # Longer timeout for slow servers
    }
}

dm = DownloadManager(CONFIG)
```

## Error Handling

### Common Issues and Solutions

1. **"Invalid URL" Error**
   - Check URL format (must include http:// or https://)
   - Verify the URL is accessible
   - Try the URL in a browser first

2. **"Cannot create destination folder" Error**
   - Ensure Google Drive is mounted
   - Check folder permissions
   - Verify the path is within Google Drive

3. **"Segmented download failed" Error**
   - Server may not support range requests
   - Try standard download mode instead
   - Reduce number of segments

4. **"Archive extraction failed" Error**
   - Check if archive is corrupted
   - Verify password for encrypted archives
   - Ensure enough space for extraction

### Error Handling in Code

```python
try:
    success = dm.download_file(url, destination, filename)
    if not success:
        print("Download failed - check the logs above")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## UI Components

### Creating Custom Progress Widgets

```python
import ipywidgets as widgets
from IPython.display import display

# Create custom progress display
progress = widgets.FloatProgress(
    value=0, min=0, max=100,
    description='Downloading:',
    bar_style='info',
    style={'bar_color': '#1f77b4'},
    layout=widgets.Layout(width='80%')
)

status = widgets.HTML(value="Ready to download")
speed = widgets.HTML(value="")

# Display widgets
display(widgets.VBox([progress, status, speed]))

# Use in download
dm.download_file(url, destination, filename, progress, status, speed)
```

### Theme Customization

The interface automatically adapts to Colab's theme, but you can customize it:

```python
from src.ui.themes import get_adaptive_css
from IPython.display import HTML

# Apply custom styling
custom_css = """
<style>
.dm-container {
    border-radius: 15px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}
/* Add your custom styles */
</style>
"""

display(HTML(custom_css))
```

## Advanced Usage

### Custom Download Headers

```python
# Modify headers for specific sites
custom_headers = {
    'User-Agent': 'Custom-Bot/1.0',
    'Referer': 'https://example.com',
    'Authorization': 'Bearer token123'
}

# Apply to session
dm.session.headers.update(custom_headers)
```

### Monitoring Downloads

```python
# Track download progress manually
class DownloadMonitor:
    def __init__(self):
        self.downloads = {}
    
    def track_download(self, url, progress_widget):
        self.downloads[url] = {
            'start_time': time.time(),
            'progress': progress_widget
        }
    
    def get_active_downloads(self):
        return len([d for d in self.downloads.values() 
                   if d['progress'].value < 100])

monitor = DownloadMonitor()
```

### Batch Processing with Custom Logic

```python
def smart_batch_download(urls, destination, max_size_mb=100):
    """Download files with size limits and smart retry"""
    results = []
    
    for url in urls:
        # Check file size first
        info_success, file_info = dm.get_file_info(url)
        if info_success and file_info.get('size'):
            size_mb = file_info['size'] / (1024 * 1024)
            if size_mb > max_size_mb:
                print(f"Skipping {url} - too large ({size_mb:.1f}MB)")
                continue
        
        # Download with retry logic
        success = False
        for attempt in range(3):
            try:
                if file_info.get('size', 0) > 10 * 1024 * 1024:  # >10MB
                    success = dm.download_file_segmented(url, destination)
                else:
                    success = dm.download_file(url, destination)
                
                if success:
                    break
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(2)  # Wait before retry
        
        results.append((url, success))
    
    return results
```

## Best Practices

1. **Always check return values** for success/failure
2. **Use appropriate download mode** based on file size
3. **Monitor storage space** before large downloads
4. **Clean up temporary files** after operations
5. **Handle errors gracefully** with try-catch blocks
6. **Use progress widgets** for better user experience
7. **Test URLs** before batch downloads
8. **Organize files** in appropriate folders

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for detailed troubleshooting guide.
