"""
Example usage of the Avance Download Manager
"""

# Basic single file download
from src.core import DownloadManager

# Initialize download manager
dm = DownloadManager()

# Single file download
url = "https://example.com/file.zip"
destination = "/content/drive/MyDrive/Downloads"
filename = "myfile.zip"

success = dm.download_file(url, destination, filename)
if success:
    print("✅ Download completed successfully!")
else:
    print("❌ Download failed!")

# Batch downloads
urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.pdf", 
    "https://example.com/file3.mp4"
]

results = dm.download_multiple(urls, destination, max_workers=3)
for url, success in results:
    status = "✅" if success else "❌"
    print(f"{status} {url}")

# Segmented download for large files
success = dm.download_file_segmented(
    "https://example.com/large_file.zip",
    destination,
    "large_file.zip",
    segments=4
)

# Archive operations
from src.core.archive_manager import extract_archive, create_archive

# Extract archive
success, message = extract_archive(
    "/content/drive/MyDrive/Downloads/archive.zip",
    "/content/drive/MyDrive/Extracted"
)
print(message)

# Create archive
success, message = create_archive(
    "/content/drive/MyDrive/Documents",
    "/content/drive/MyDrive/backup.zip",
    "zip",
    compression_level=6
)
print(message)

# File management
from src.core import FileManager

fm = FileManager()

# Browse folder
contents = fm.browse_folder("/content/drive/MyDrive/Downloads")
print(f"Found {contents['total_files']} files and {contents['total_folders']} folders")

# Get storage info
drive_info = fm.get_drive_info()
if 'storage' in drive_info:
    storage = drive_info['storage']
    print(f"Storage: {storage['free']} bytes free of {storage['total']} bytes total")

# Search files
results = fm.search_files("*.pdf", "/content/drive/MyDrive")
print(f"Found {len(results)} PDF files")

# Clean up resources
dm.cleanup()
