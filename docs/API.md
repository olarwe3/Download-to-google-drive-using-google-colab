# API Reference

## Core Classes

### DownloadManager

The main class for handling downloads with support for single, batch, and segmented downloads.

#### Constructor
```python
DownloadManager(config: Dict = None)
```

#### Methods

##### download_file()
```python
download_file(url: str, destination_path: str, filename: str = None,
             progress_widget: widgets.FloatProgress = None,
             status_widget: widgets.HTML = None,
             speed_widget: widgets.HTML = None) -> bool
```

Downloads a single file with progress tracking.

**Parameters:**
- `url`: The URL to download from
- `destination_path`: Local path to save the file
- `filename`: Optional custom filename (auto-detected if None)
- `progress_widget`: Optional progress bar widget
- `status_widget`: Optional status display widget
- `speed_widget`: Optional speed display widget

**Returns:** `bool` - True if successful, False otherwise

##### download_file_segmented()
```python
download_file_segmented(url: str, destination_path: str, filename: str = None,
                       progress_widget: widgets.FloatProgress = None,
                       status_widget: widgets.HTML = None,
                       speed_widget: widgets.HTML = None,
                       segments: int = 4) -> bool
```

Downloads a file using multiple segments for increased speed.

**Parameters:**
- Same as `download_file()` plus:
- `segments`: Number of parallel segments to use (2-16)

**Returns:** `bool` - True if successful, False otherwise

##### download_multiple()
```python
download_multiple(urls: List[str], destination_path: str, 
                 max_workers: int = None) -> List[Tuple[str, bool]]
```

Downloads multiple files concurrently.

**Parameters:**
- `urls`: List of URLs to download
- `destination_path`: Directory to save files
- `max_workers`: Maximum number of concurrent downloads (default: 5)

**Returns:** `List[Tuple[str, bool]]` - List of (url, success) tuples

### FileManager

Class for managing files and folders in Google Drive.

#### Methods

##### browse_folder()
```python
browse_folder(folder_path: str = None) -> Dict
```

Browse a folder and return detailed information about its contents.

##### create_folder()
```python
create_folder(folder_path: str, folder_name: str) -> Tuple[bool, str]
```

Create a new folder.

##### delete_item()
```python
delete_item(item_path: str) -> Tuple[bool, str]
```

Delete a file or folder.

##### search_files()
```python
search_files(search_query: str, search_path: str = None, 
            file_type: str = None) -> List[Dict]
```

Search for files by name, type, or location.

## Archive Functions

### extract_archive()
```python
extract_archive(archive_path: str, extract_to: str = None, 
               password: str = None) -> Tuple[bool, str]
```

Extract an archive file to a specified location.

**Supported formats:** ZIP, RAR, 7Z, TAR, TAR.GZ, TAR.BZ2, TAR.XZ

### create_archive()
```python
create_archive(source_path: str, archive_path: str, archive_type: str = 'zip',
              compression_level: int = 6) -> Tuple[bool, str]
```

Create an archive from files/folders.

**Supported formats:** ZIP, TAR, TAR.GZ, TAR.BZ2, TAR.XZ, 7Z

### get_archive_info()
```python
get_archive_info(file_path: str) -> Dict
```

Get information about an archive file including size, type, and contents.

## Validation Functions

### validate_url()
```python
validate_url(url: str) -> bool
```

Validate if a URL is properly formatted and accessible.

### validate_filename()
```python
validate_filename(filename: str) -> Tuple[bool, str]
```

Validate and sanitize a filename.

### validate_path()
```python
validate_path(path: str) -> Tuple[bool, str]
```

Validate a file path for Google Drive compatibility.

## Utility Functions

### format_size()
```python
format_size(bytes_size: int) -> str
```

Convert bytes to human-readable format (B, KB, MB, GB, TB).

### format_speed()
```python
format_speed(bytes_per_second: int) -> str
```

Format download speed in human-readable format.

### get_file_category()
```python
get_file_category(filename: str) -> str
```

Determine file category based on extension (video, audio, image, etc.).

## Configuration

The download manager accepts a configuration dictionary with the following structure:

```python
CONFIG = {
    "download": {
        "default_destination": "/content/drive/MyDrive/Downloads",
        "chunk_size": 262144,  # 256KB
        "max_workers": 5,
        "max_segments": 8,
        "timeout": 30,
        "retry_attempts": 3,
        "min_file_size_for_segmentation": 10485760  # 10MB
    },
    "ui": {
        "theme": "auto",
        "progress_update_frequency": 1048576,  # 1MB
        "show_speed_tips": True,
        "compact_mode": True
    },
    "archive": {
        "supported_formats": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "default_compression_level": 6,
        "auto_extract_to_drive": True
    }
}
```

## Error Handling

All functions return success/failure indicators and error messages:

- Download functions return `bool` (True/False)
- File operations return `Tuple[bool, str]` (success, message)
- Info functions return `Dict` with error key if failed

## Examples

See the `examples/` directory for complete usage examples:
- `basic_usage.py` - Basic download and archive operations
- `advanced_usage.py` - Advanced features and configurations
- `ui_examples.py` - Creating custom UI components
