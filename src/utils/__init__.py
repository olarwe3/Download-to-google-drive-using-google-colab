"""
Utility modules for the Avance Download Manager
"""

from .constants import CONFIG, DOWNLOAD_HEADERS, FILE_CATEGORIES, UI_THEMES
from .helpers import (
    validate_url, sanitize_filename, get_filename_from_url,
    format_size, format_speed, format_time, get_file_category,
    create_folder_if_not_exists, safe_delete_file, is_archive_file,
    generate_unique_filename, clean_url
)
from .storage import (
    get_storage_info, check_available_space, list_folder_contents,
    delete_file_or_folder, get_available_folders, ensure_downloads_folder,
    cleanup_temp_files, get_drive_mount_status
)

__all__ = [
    'CONFIG', 'DOWNLOAD_HEADERS', 'FILE_CATEGORIES', 'UI_THEMES',
    'validate_url', 'sanitize_filename', 'get_filename_from_url',
    'format_size', 'format_speed', 'format_time', 'get_file_category',
    'create_folder_if_not_exists', 'safe_delete_file', 'is_archive_file',
    'generate_unique_filename', 'clean_url',
    'get_storage_info', 'check_available_space', 'list_folder_contents',
    'delete_file_or_folder', 'get_available_folders', 'ensure_downloads_folder',
    'cleanup_temp_files', 'get_drive_mount_status'
]
