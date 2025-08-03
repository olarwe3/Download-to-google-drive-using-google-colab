"""
File management utilities for Google Drive integration
"""
import os
import shutil
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from .validators import validate_path, validate_filename
from ..utils.helpers import format_size, get_file_category, create_folder_if_not_exists
from ..utils.storage import (
    get_storage_info, list_folder_contents, delete_file_or_folder,
    get_folder_size
)

class FileManager:
    """File management class for Google Drive operations"""
    
    def __init__(self):
        self.base_path = '/content/drive/MyDrive'
        self.downloads_path = '/content/drive/MyDrive/Downloads'
    
    def ensure_drive_mounted(self) -> Tuple[bool, str]:
        """Check if Google Drive is properly mounted"""
        if not os.path.exists('/content/drive'):
            return False, "Google Drive not mounted. Please run drive.mount('/content/drive') first."
        
        if not os.path.exists(self.base_path):
            return False, "Google Drive MyDrive not accessible."
        
        # Ensure Downloads folder exists
        if not os.path.exists(self.downloads_path):
            try:
                os.makedirs(self.downloads_path)
            except:
                return False, "Cannot create Downloads folder."
        
        return True, "Google Drive ready"
    
    def get_drive_info(self) -> Dict:
        """Get comprehensive Google Drive information"""
        mounted, message = self.ensure_drive_mounted()
        if not mounted:
            return {'error': message}
        
        storage_info, error = get_storage_info()
        if error:
            storage_info = {'error': error}
        
        return {
            'mounted': mounted,
            'base_path': self.base_path,
            'downloads_path': self.downloads_path,
            'storage': storage_info,
            'status': message
        }
    
    def browse_folder(self, folder_path: str = None) -> Dict:
        """Browse a folder and return detailed information"""
        if folder_path is None:
            folder_path = self.downloads_path
        
        # Validate path
        valid_path, normalized_path = validate_path(folder_path)
        if not valid_path:
            return {'error': f'Invalid path: {normalized_path}'}
        
        folder_path = normalized_path
        
        if not os.path.exists(folder_path):
            return {'error': f'Folder does not exist: {folder_path}'}
        
        # Get folder contents
        contents = list_folder_contents(folder_path)
        if 'error' in contents:
            return contents
        
        # Add additional metadata
        contents['path'] = folder_path
        contents['parent_path'] = os.path.dirname(folder_path) if folder_path != self.base_path else None
        
        # Categorize files
        file_categories = {}
        for file_info in contents['files']:
            category = get_file_category(file_info['name'])
            if category not in file_categories:
                file_categories[category] = []
            file_categories[category].append(file_info)
        
        contents['file_categories'] = file_categories
        
        return contents
    
    def create_folder(self, folder_path: str, folder_name: str) -> Tuple[bool, str]:
        """Create a new folder"""
        # Validate inputs
        valid_path, normalized_path = validate_path(folder_path)
        if not valid_path:
            return False, f'Invalid base path: {normalized_path}'
        
        valid_name, sanitized_name = validate_filename(folder_name)
        if not valid_name:
            return False, f'Invalid folder name: {sanitized_name}'
        
        new_folder_path = os.path.join(normalized_path, sanitized_name)
        
        # Check if folder already exists
        if os.path.exists(new_folder_path):
            return False, f'Folder already exists: {sanitized_name}'
        
        # Create folder
        try:
            os.makedirs(new_folder_path)
            return True, f'Created folder: {sanitized_name}'
        except Exception as e:
            return False, f'Error creating folder: {str(e)}'
    
    def delete_item(self, item_path: str) -> Tuple[bool, str]:
        """Delete a file or folder"""
        # Validate path
        valid_path, normalized_path = validate_path(item_path)
        if not valid_path:
            return False, f'Invalid path: {normalized_path}'
        
        return delete_file_or_folder(normalized_path)
    
    def move_item(self, source_path: str, destination_path: str) -> Tuple[bool, str]:
        """Move a file or folder to a new location"""
        # Validate paths
        valid_source, normalized_source = validate_path(source_path)
        if not valid_source:
            return False, f'Invalid source path: {normalized_source}'
        
        valid_dest, normalized_dest = validate_path(destination_path)
        if not valid_dest:
            return False, f'Invalid destination path: {normalized_dest}'
        
        if not os.path.exists(normalized_source):
            return False, 'Source does not exist'
        
        if os.path.exists(normalized_dest):
            return False, 'Destination already exists'
        
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(normalized_dest)
            if not create_folder_if_not_exists(dest_dir):
                return False, 'Cannot create destination directory'
            
            shutil.move(normalized_source, normalized_dest)
            return True, f'Moved {os.path.basename(normalized_source)} to {normalized_dest}'
        except Exception as e:
            return False, f'Error moving item: {str(e)}'
    
    def copy_item(self, source_path: str, destination_path: str) -> Tuple[bool, str]:
        """Copy a file or folder to a new location"""
        # Validate paths
        valid_source, normalized_source = validate_path(source_path)
        if not valid_source:
            return False, f'Invalid source path: {normalized_source}'
        
        valid_dest, normalized_dest = validate_path(destination_path)
        if not valid_dest:
            return False, f'Invalid destination path: {normalized_dest}'
        
        if not os.path.exists(normalized_source):
            return False, 'Source does not exist'
        
        if os.path.exists(normalized_dest):
            return False, 'Destination already exists'
        
        try:
            # Ensure destination directory exists
            dest_dir = os.path.dirname(normalized_dest)
            if not create_folder_if_not_exists(dest_dir):
                return False, 'Cannot create destination directory'
            
            if os.path.isfile(normalized_source):
                shutil.copy2(normalized_source, normalized_dest)
            else:
                shutil.copytree(normalized_source, normalized_dest)
            
            return True, f'Copied {os.path.basename(normalized_source)} to {normalized_dest}'
        except Exception as e:
            return False, f'Error copying item: {str(e)}'
    
    def rename_item(self, item_path: str, new_name: str) -> Tuple[bool, str]:
        """Rename a file or folder"""
        # Validate path
        valid_path, normalized_path = validate_path(item_path)
        if not valid_path:
            return False, f'Invalid path: {normalized_path}'
        
        # Validate new name
        valid_name, sanitized_name = validate_filename(new_name)
        if not valid_name:
            return False, f'Invalid name: {sanitized_name}'
        
        if not os.path.exists(normalized_path):
            return False, 'Item does not exist'
        
        parent_dir = os.path.dirname(normalized_path)
        new_path = os.path.join(parent_dir, sanitized_name)
        
        if os.path.exists(new_path):
            return False, f'Item with name "{sanitized_name}" already exists'
        
        try:
            os.rename(normalized_path, new_path)
            return True, f'Renamed to: {sanitized_name}'
        except Exception as e:
            return False, f'Error renaming item: {str(e)}'
    
    def get_item_info(self, item_path: str) -> Dict:
        """Get detailed information about a file or folder"""
        # Validate path
        valid_path, normalized_path = validate_path(item_path)
        if not valid_path:
            return {'error': f'Invalid path: {normalized_path}'}
        
        if not os.path.exists(normalized_path):
            return {'error': 'Item does not exist'}
        
        try:
            stat = os.stat(normalized_path)
            is_file = os.path.isfile(normalized_path)
            
            info = {
                'path': normalized_path,
                'name': os.path.basename(normalized_path),
                'type': 'file' if is_file else 'folder',
                'size': stat.st_size if is_file else get_folder_size(normalized_path),
                'size_formatted': format_size(stat.st_size if is_file else get_folder_size(normalized_path)),
                'modified': stat.st_mtime,
                'permissions': oct(stat.st_mode)[-3:]
            }
            
            if is_file:
                info['extension'] = os.path.splitext(normalized_path)[1].lower()
                info['category'] = get_file_category(normalized_path)
            else:
                # For folders, get contents count
                try:
                    contents = os.listdir(normalized_path)
                    info['items_count'] = len(contents)
                    info['files_count'] = len([item for item in contents 
                                             if os.path.isfile(os.path.join(normalized_path, item))])
                    info['folders_count'] = len([item for item in contents 
                                               if os.path.isdir(os.path.join(normalized_path, item))])
                except:
                    info['items_count'] = 'Unknown'
                    info['files_count'] = 'Unknown'
                    info['folders_count'] = 'Unknown'
            
            return info
            
        except Exception as e:
            return {'error': f'Error getting item info: {str(e)}'}
    
    def search_files(self, search_query: str, search_path: str = None, 
                    file_type: str = None) -> List[Dict]:
        """Search for files by name, type, or content"""
        if search_path is None:
            search_path = self.base_path
        
        # Validate search path
        valid_path, normalized_path = validate_path(search_path)
        if not valid_path:
            return [{'error': f'Invalid search path: {normalized_path}'}]
        
        if not os.path.exists(normalized_path):
            return [{'error': 'Search path does not exist'}]
        
        results = []
        search_query_lower = search_query.lower()
        
        try:
            for root, dirs, files in os.walk(normalized_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    # Check if file matches search criteria
                    matches = False
                    
                    # Name search
                    if search_query_lower in file_lower:
                        matches = True
                    
                    # File type filter
                    if file_type and matches:
                        file_category = get_file_category(file)
                        if file_category != file_type.lower():
                            matches = False
                    
                    if matches:
                        try:
                            stat = os.stat(file_path)
                            results.append({
                                'path': file_path,
                                'name': file,
                                'size': stat.st_size,
                                'size_formatted': format_size(stat.st_size),
                                'category': get_file_category(file),
                                'modified': stat.st_mtime,
                                'folder': root
                            })
                        except:
                            continue  # Skip files that can't be accessed
                
                # Limit results to prevent overwhelming output
                if len(results) >= 100:
                    break
            
            return results
            
        except Exception as e:
            return [{'error': f'Search error: {str(e)}'}]
    
    def get_storage_usage_by_category(self, folder_path: str = None) -> Dict:
        """Get storage usage breakdown by file category"""
        if folder_path is None:
            folder_path = self.base_path
        
        # Validate path
        valid_path, normalized_path = validate_path(folder_path)
        if not valid_path:
            return {'error': f'Invalid path: {normalized_path}'}
        
        if not os.path.exists(normalized_path):
            return {'error': 'Folder does not exist'}
        
        category_usage = {}
        total_size = 0
        
        try:
            for root, dirs, files in os.walk(normalized_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        category = get_file_category(file)
                        
                        if category not in category_usage:
                            category_usage[category] = {'size': 0, 'count': 0}
                        
                        category_usage[category]['size'] += file_size
                        category_usage[category]['count'] += 1
                        total_size += file_size
                    except:
                        continue  # Skip files that can't be accessed
            
            # Format sizes and calculate percentages
            for category in category_usage:
                category_usage[category]['size_formatted'] = format_size(category_usage[category]['size'])
                category_usage[category]['percentage'] = (category_usage[category]['size'] / total_size * 100) if total_size > 0 else 0
            
            return {
                'categories': category_usage,
                'total_size': total_size,
                'total_size_formatted': format_size(total_size),
                'path': normalized_path
            }
            
        except Exception as e:
            return {'error': f'Error analyzing storage: {str(e)}'}
    
    def cleanup_empty_folders(self, folder_path: str = None) -> Tuple[bool, str]:
        """Remove empty folders recursively"""
        if folder_path is None:
            folder_path = self.downloads_path
        
        # Validate path
        valid_path, normalized_path = validate_path(folder_path)
        if not valid_path:
            return False, f'Invalid path: {normalized_path}'
        
        if not os.path.exists(normalized_path):
            return False, 'Folder does not exist'
        
        removed_count = 0
        
        try:
            # Walk bottom-up to remove empty folders
            for root, dirs, files in os.walk(normalized_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Check if empty
                            os.rmdir(dir_path)
                            removed_count += 1
                    except:
                        continue  # Skip folders that can't be removed
            
            return True, f'Removed {removed_count} empty folders'
            
        except Exception as e:
            return False, f'Error cleaning up folders: {str(e)}'
