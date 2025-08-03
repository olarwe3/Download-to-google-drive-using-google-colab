"""
Core modules for the Avance Download Manager
"""

from .download_manager import DownloadManager
from .archive_manager import get_archive_info, extract_archive, create_archive, list_archive_contents
from .file_manager import FileManager
from .validators import (
    validate_url, validate_filename, validate_path, validate_url_list,
    validate_archive_password, validate_chunk_size, validate_max_workers,
    validate_timeout, validate_compression_level, validate_segments,
    is_safe_url, sanitize_url_input, validate_archive_format
)

__all__ = [
    'DownloadManager',
    'get_archive_info', 'extract_archive', 'create_archive', 'list_archive_contents',
    'FileManager',
    'validate_url', 'validate_filename', 'validate_path', 'validate_url_list',
    'validate_archive_password', 'validate_chunk_size', 'validate_max_workers',
    'validate_timeout', 'validate_compression_level', 'validate_segments',
    'is_safe_url', 'sanitize_url_input', 'validate_archive_format'
]
