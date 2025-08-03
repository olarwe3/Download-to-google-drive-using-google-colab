"""
Validation functions for URLs, files, and user inputs
"""
import os
import re
from urllib.parse import urlparse
from typing import Tuple, List
from ..utils.helpers import sanitize_filename

def validate_url(url: str) -> bool:
    """Validate if the URL is properly formatted and accessible"""
    try:
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if not url:
            return False
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = urlparse(url)
        return all([
            result.scheme in ['http', 'https'],
            result.netloc,
            '.' in result.netloc  # Basic domain validation
        ])
    except:
        return False

def validate_filename(filename: str) -> Tuple[bool, str]:
    """Validate filename and return sanitized version"""
    if not filename or not isinstance(filename, str):
        return False, "Filename cannot be empty"
    
    # Remove dangerous characters
    sanitized = sanitize_filename(filename)
    
    # Check length
    if len(sanitized) > 255:
        return False, "Filename too long (max 255 characters)"
    
    # Check for reserved names on Windows
    reserved_names = ['CON', 'PRN', 'AUX', 'NUL'] + [f'COM{i}' for i in range(1, 10)] + [f'LPT{i}' for i in range(1, 10)]
    name_without_ext = os.path.splitext(sanitized)[0].upper()
    if name_without_ext in reserved_names:
        return False, f"Filename '{filename}' is reserved"
    
    # Check for valid characters
    if not sanitized or sanitized in ['.', '..']:
        return False, "Invalid filename"
    
    return True, sanitized

def validate_path(path: str) -> Tuple[bool, str]:
    """Validate file path for Google Drive"""
    if not path or not isinstance(path, str):
        return False, "Path cannot be empty"
    
    # Normalize path
    normalized_path = os.path.normpath(path)
    
    # Check if path is within Google Drive
    if not normalized_path.startswith('/content/drive/MyDrive'):
        return False, "Path must be within Google Drive (/content/drive/MyDrive)"
    
    # Check path length
    if len(normalized_path) > 4096:
        return False, "Path too long"
    
    # Check for valid characters in path components
    path_components = normalized_path.split('/')
    for component in path_components:
        if component and not re.match(r'^[^<>:"|?*]+$', component):
            return False, f"Invalid characters in path component: {component}"
    
    return True, normalized_path

def validate_url_list(urls: List[str]) -> Tuple[List[str], List[str]]:
    """Validate a list of URLs and return valid and invalid ones"""
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if validate_url(url):
            valid_urls.append(url.strip())
        else:
            invalid_urls.append(url.strip() if url else "Empty URL")
    
    return valid_urls, invalid_urls

def validate_archive_password(password: str) -> Tuple[bool, str]:
    """Validate archive password"""
    if not password:
        return True, ""  # Empty password is valid (no password)
    
    if not isinstance(password, str):
        return False, "Password must be a string"
    
    if len(password) > 128:
        return False, "Password too long (max 128 characters)"
    
    return True, password

def validate_chunk_size(chunk_size: int) -> Tuple[bool, int]:
    """Validate chunk size for downloads"""
    if not isinstance(chunk_size, int):
        return False, 262144  # Default 256KB
    
    # Minimum 1KB, maximum 10MB
    min_size = 1024
    max_size = 10 * 1024 * 1024
    
    if chunk_size < min_size:
        return False, min_size
    elif chunk_size > max_size:
        return False, max_size
    
    return True, chunk_size

def validate_max_workers(max_workers: int) -> Tuple[bool, int]:
    """Validate maximum number of worker threads"""
    if not isinstance(max_workers, int):
        return False, 5  # Default
    
    # Minimum 1, maximum 20
    if max_workers < 1:
        return False, 1
    elif max_workers > 20:
        return False, 20
    
    return True, max_workers

def validate_timeout(timeout: int) -> Tuple[bool, int]:
    """Validate timeout value"""
    if not isinstance(timeout, int):
        return False, 30  # Default
    
    # Minimum 5 seconds, maximum 300 seconds (5 minutes)
    if timeout < 5:
        return False, 5
    elif timeout > 300:
        return False, 300
    
    return True, timeout

def validate_compression_level(level: int) -> Tuple[bool, int]:
    """Validate compression level for archives"""
    if not isinstance(level, int):
        return False, 6  # Default
    
    # Standard compression levels 0-9
    if level < 0:
        return False, 0
    elif level > 9:
        return False, 9
    
    return True, level

def validate_segments(segments: int) -> Tuple[bool, int]:
    """Validate number of segments for segmented downloads"""
    if not isinstance(segments, int):
        return False, 4  # Default
    
    # Minimum 2, maximum 16
    if segments < 2:
        return False, 2
    elif segments > 16:
        return False, 16
    
    return True, segments

def is_safe_url(url: str) -> bool:
    """Check if URL is from a safe domain (basic security check)"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Block localhost and local IPs
        if domain in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
        
        # Block private IP ranges (basic check)
        if domain.startswith(('192.168.', '10.', '172.')):
            return False
        
        # Allow common file hosting domains
        safe_domains = [
            'drive.google.com', 'dropbox.com', 'mega.nz', 'mediafire.com',
            'github.com', 'sourceforge.net', 'archive.org', 'www.archive.org'
        ]
        
        if any(safe_domain in domain for safe_domain in safe_domains):
            return True
        
        # For other domains, just check basic validity
        return '.' in domain and len(domain) > 3
        
    except:
        return False

def sanitize_url_input(url: str) -> str:
    """Sanitize URL input from user"""
    if not url:
        return ""
    
    # Remove extra whitespace
    url = url.strip()
    
    # Remove common prefixes that users might add
    prefixes_to_remove = ['www.', 'http://', 'https://']
    for prefix in prefixes_to_remove:
        if url.lower().startswith(prefix):
            url = url[len(prefix):]
    
    # Add https:// prefix
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return url

def validate_archive_format(filename: str) -> Tuple[bool, str]:
    """Validate if file is a supported archive format"""
    if not filename:
        return False, "No filename provided"
    
    supported_formats = ['.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.gz', '.bz2', '.xz']
    file_ext = os.path.splitext(filename.lower())[1]
    
    # Handle .tar.gz, .tar.bz2, etc.
    if filename.lower().endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
        return True, "Supported archive format"
    
    if file_ext in supported_formats:
        return True, "Supported archive format"
    
    return False, f"Unsupported archive format: {file_ext}"
