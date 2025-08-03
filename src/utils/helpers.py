"""
Helper utility functions for the Avance Download Manager
"""
import os
import time
import re
import math
from urllib.parse import urlparse, unquote
from .constants import FILE_CATEGORIES

def validate_url(url):
    """Validate if the URL is properly formatted"""
    try:
        result = urlparse(url.strip())
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()

def get_filename_from_url(url, custom_name=None):
    """Extract filename from URL or use custom name"""
    if custom_name:
        return sanitize_filename(custom_name)
    try:
        parsed_url = urlparse(url)
        filename = os.path.basename(unquote(parsed_url.path))
        if not filename or '.' not in filename:
            filename = f"download_{int(time.time())}.file"
        return sanitize_filename(filename)
    except:
        return f"download_{int(time.time())}.file"

def format_size(bytes_size):
    """Convert bytes to human readable format"""
    if bytes_size == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_size, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_size / p, 2)
    return f"{s} {size_names[i]}"

def format_speed(bytes_per_second):
    """Format download speed"""
    return f"{format_size(bytes_per_second)}/s"

def format_time(seconds):
    """Format time duration"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds/60)}m {int(seconds%60)}s"
    else:
        return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"

def get_file_category(filename):
    """Determine file category based on extension"""
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return category
    return 'other'

def create_folder_if_not_exists(folder_path):
    """Create folder if it doesn't exist"""
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        return True
    except:
        return False

def safe_delete_file(file_path):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except:
        return False

def get_file_extension(filename):
    """Get file extension in lowercase"""
    return os.path.splitext(filename)[1].lower()

def is_archive_file(filename):
    """Check if file is an archive based on extension"""
    ext = get_file_extension(filename)
    return ext in FILE_CATEGORIES['archive']

def generate_unique_filename(directory, filename):
    """Generate a unique filename if file already exists"""
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1

def estimate_download_time(file_size, speed_bps):
    """Estimate download time based on current speed"""
    if speed_bps <= 0:
        return None
    return file_size / speed_bps

def calculate_progress_percentage(downloaded, total):
    """Calculate progress percentage safely"""
    if total <= 0:
        return 0
    return min(100, (downloaded / total) * 100)

def validate_file_path(path):
    """Validate if a file path is safe and accessible"""
    try:
        # Check if path is within allowed directories (Google Drive)
        normalized_path = os.path.normpath(path)
        if not normalized_path.startswith('/content/drive/MyDrive'):
            return False, "Path must be within Google Drive"
        
        # Check if parent directory exists or can be created
        parent_dir = os.path.dirname(normalized_path)
        if not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir)
            except:
                return False, "Cannot create destination directory"
        
        return True, "Valid path"
    except Exception as e:
        return False, f"Invalid path: {str(e)}"

def clean_url(url):
    """Clean and normalize URL"""
    if not url:
        return url
    
    # Remove extra whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def parse_content_disposition(header_value):
    """Parse Content-Disposition header to extract filename"""
    if not header_value:
        return None
    
    # Look for filename parameter
    filename_match = re.search(r'filename\*?=["\']?([^"\';\s]+)', header_value)
    if filename_match:
        filename = filename_match.group(1)
        # Handle RFC 5987 encoding
        if filename.startswith("UTF-8''"):
            filename = filename[7:]
            try:
                filename = unquote(filename)
            except:
                pass
        return sanitize_filename(filename)
    
    return None

def detect_file_type_from_content(content_type):
    """Detect file extension from Content-Type header"""
    content_type_map = {
        'application/zip': '.zip',
        'application/x-rar-compressed': '.rar',
        'application/x-7z-compressed': '.7z',
        'video/mp4': '.mp4',
        'video/avi': '.avi',
        'audio/mpeg': '.mp3',
        'audio/wav': '.wav',
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'application/pdf': '.pdf',
        'text/plain': '.txt',
        'application/json': '.json',
        'text/html': '.html',
        'text/css': '.css',
        'application/javascript': '.js'
    }
    
    if content_type in content_type_map:
        return content_type_map[content_type]
    
    # Handle Content-Type with charset
    main_type = content_type.split(';')[0].strip()
    return content_type_map.get(main_type, '.bin')
