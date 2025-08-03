"""
Storage management utilities for Google Drive integration
"""
import os
import shutil
import math
from typing import Dict, Optional, Tuple, List

def get_storage_info() -> Tuple[Optional[Dict], Optional[str]]:
    """Get detailed storage information for Google Drive"""
    try:
        if not os.path.exists('/content/drive/MyDrive'):
            return None, "Google Drive not mounted"

        statvfs = os.statvfs('/content/drive/MyDrive')
        total_space = statvfs.f_frsize * statvfs.f_blocks
        free_space = statvfs.f_frsize * statvfs.f_bavail
        used_space = total_space - free_space

        return {
            'total': total_space,
            'used': used_space,
            'free': free_space,
            'usage_percent': (used_space/total_space)*100 if total_space > 0 else 0
        }, None
    except Exception as e:
        return None, str(e)

def check_available_space(required_size: int, path: str = '/content/drive/MyDrive') -> Tuple[bool, str]:
    """Check if there's enough space for a download"""
    try:
        statvfs = os.statvfs(path)
        free_space = statvfs.f_frsize * statvfs.f_bavail
        
        if free_space >= required_size:
            return True, f"Sufficient space available"
        else:
            return False, f"Insufficient space. Need {format_size(required_size)}, have {format_size(free_space)}"
    except Exception as e:
        return False, f"Cannot check space: {str(e)}"

def format_size(bytes_size: int) -> str:
    """Convert bytes to human readable format"""
    if bytes_size == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes_size, 1024)))
    p = math.pow(1024, i)
    s = round(bytes_size / p, 2)
    return f"{s} {size_names[i]}"

def get_folder_size(folder_path: str) -> int:
    """Calculate total size of a folder"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except:
                    continue
    except:
        pass
    return total_size

def list_folder_contents(folder_path: str) -> Dict:
    """List folder contents with detailed information"""
    try:
        if not os.path.exists(folder_path):
            return {'error': 'Folder does not exist'}
        
        items = os.listdir(folder_path)
        items.sort()
        
        folders = []
        files = []
        
        for item in items:
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isdir(item_path):
                    size = get_folder_size(item_path)
                    folders.append({
                        'name': item,
                        'type': 'folder',
                        'size': size,
                        'size_formatted': format_size(size),
                        'path': item_path
                    })
                else:
                    size = os.path.getsize(item_path)
                    files.append({
                        'name': item,
                        'type': 'file',
                        'size': size,
                        'size_formatted': format_size(size),
                        'path': item_path
                    })
            except:
                # Skip items that can't be accessed
                continue
        
        return {
            'folders': folders,
            'files': files,
            'total_folders': len(folders),
            'total_files': len(files),
            'total_size': sum(item['size'] for item in folders + files)
        }
    except Exception as e:
        return {'error': str(e)}

def delete_file_or_folder(path: str) -> Tuple[bool, str]:
    """Safely delete a file or folder"""
    try:
        if not os.path.exists(path):
            return False, "Path does not exist"
        
        if os.path.isfile(path):
            os.remove(path)
            return True, f"File deleted: {os.path.basename(path)}"
        elif os.path.isdir(path):
            shutil.rmtree(path)
            return True, f"Folder deleted: {os.path.basename(path)}"
        else:
            return False, "Unknown path type"
    except Exception as e:
        return False, f"Error deleting: {str(e)}"

def create_directory_structure(base_path: str, structure: Dict) -> bool:
    """Create a directory structure from a dictionary"""
    try:
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(content, dict):
                # It's a directory
                os.makedirs(path, exist_ok=True)
                create_directory_structure(path, content)
            else:
                # It's a file (content is the file content)
                with open(path, 'w') as f:
                    f.write(content)
        return True
    except Exception:
        return False

def get_available_folders() -> List[Tuple[str, str]]:
    """Get list of available folders in Google Drive"""
    available_folders = []
    potential_folders = [
        ('/content/drive/MyDrive', '📁 Root Drive'),
        ('/content/drive/MyDrive/Downloads', '📁 Downloads'),
        ('/content/drive/MyDrive/Documents', '📁 Documents'),
        ('/content/drive/MyDrive/Videos', '📁 Videos'),
        ('/content/drive/MyDrive/Images', '📁 Images'),
        ('/content/drive/MyDrive/Music', '📁 Music'),
        ('/content/drive/MyDrive/Archives', '📁 Archives'),
        ('/content/drive/MyDrive/Projects', '📁 Projects'),
    ]

    for folder_path, folder_label in potential_folders:
        if os.path.exists(folder_path):
            available_folders.append((folder_label, folder_path))

    if not available_folders:
        available_folders = [('Drive not mounted', '')]

    return available_folders

def ensure_downloads_folder() -> str:
    """Ensure the Downloads folder exists and return its path"""
    downloads_path = '/content/drive/MyDrive/Downloads'
    try:
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path)
        return downloads_path
    except:
        # Fallback to root drive
        return '/content/drive/MyDrive'

def cleanup_temp_files(temp_dir: str = '/tmp') -> int:
    """Clean up temporary files and return count of files deleted"""
    deleted_count = 0
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith('download_temp_') or filename.endswith('.part'):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except:
                    continue
    except:
        pass
    return deleted_count

def get_drive_mount_status() -> Dict[str, bool]:
    """Check the status of Google Drive mount"""
    return {
        'mounted': os.path.exists('/content/drive'),
        'mydrive_accessible': os.path.exists('/content/drive/MyDrive'),
        'downloads_folder': os.path.exists('/content/drive/MyDrive/Downloads')
    }

def create_backup_structure() -> bool:
    """Create a backup folder structure for important files"""
    try:
        backup_structure = {
            'Backups': {
                'Downloads': {},
                'Archives': {},
                'Configs': {}
            }
        }
        return create_directory_structure('/content/drive/MyDrive', backup_structure)
    except:
        return False
