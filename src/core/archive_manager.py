"""
Archive management functionality for creating and extracting various archive formats
"""
import os
import shutil
import zipfile
import tarfile
import subprocess
from typing import Tuple, Dict, Optional, List

from .validators import validate_path, validate_filename, validate_archive_format
from ..utils.helpers import create_folder_if_not_exists, format_size

def get_archive_info(file_path: str) -> Dict:
    """Get information about an archive file"""
    try:
        if not os.path.exists(file_path):
            return {'error': 'File does not exist'}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        # Handle compound extensions like .tar.gz
        if file_path.lower().endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
            if file_path.lower().endswith('.tar.gz'):
                file_ext = '.tar.gz'
            elif file_path.lower().endswith('.tar.bz2'):
                file_ext = '.tar.bz2'
            elif file_path.lower().endswith('.tar.xz'):
                file_ext = '.tar.xz'
        
        info = {
            'type': file_ext,
            'size': file_size,
            'size_formatted': format_size(file_size),
            'supported': file_ext in ['.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz', '.gz', '.bz2', '.xz'],
            'can_extract': True,
            'can_create': file_ext not in ['.rar']  # Can't create RAR files
        }
        
        # Try to get contents for different archive types
        try:
            if file_ext == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    info['files'] = len(zip_ref.namelist())
                    info['content'] = zip_ref.namelist()[:10]  # First 10 files
                    info['is_encrypted'] = any(f.flag_bits & 0x1 for f in zip_ref.filelist)
            
            elif file_ext in ['.tar', '.tar.gz', '.tar.bz2', '.tar.xz']:
                mode = 'r'
                if file_ext == '.tar.gz':
                    mode = 'r:gz'
                elif file_ext == '.tar.bz2':
                    mode = 'r:bz2'
                elif file_ext == '.tar.xz':
                    mode = 'r:xz'
                
                with tarfile.open(file_path, mode) as tar_ref:
                    info['files'] = len(tar_ref.getnames())
                    info['content'] = tar_ref.getnames()[:10]  # First 10 files
                    info['is_encrypted'] = False
            
            elif file_ext == '.7z':
                try:
                    import py7zr
                    with py7zr.SevenZipFile(file_path, mode='r') as z:
                        info['files'] = len(z.getnames())
                        info['content'] = z.getnames()[:10]
                        info['is_encrypted'] = z.needs_password()
                except ImportError:
                    info['files'] = 'Unknown (py7zr not available)'
                    info['content'] = []
                    info['is_encrypted'] = False
            
            elif file_ext == '.rar':
                # For RAR files, we can try to use command line tools
                try:
                    result = subprocess.run(['unrar', 'l', file_path], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')
                        # Parse unrar output to count files
                        file_count = 0
                        content = []
                        in_list = False
                        for line in lines:
                            if '---------------' in line:
                                in_list = not in_list
                                continue
                            if in_list and line.strip():
                                file_count += 1
                                if len(content) < 10:
                                    # Extract filename from unrar output
                                    parts = line.split()
                                    if len(parts) >= 5:
                                        content.append(parts[-1])
                        info['files'] = file_count
                        info['content'] = content
                    else:
                        info['files'] = 'Unknown'
                        info['content'] = []
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    info['files'] = 'Unknown (unrar not available)'
                    info['content'] = []
                info['is_encrypted'] = False  # Can't easily detect without trying
            
            else:
                info['files'] = 'Unknown'
                info['content'] = []
                info['is_encrypted'] = False
        
        except Exception as e:
            info['files'] = f'Error reading: {str(e)}'
            info['content'] = []
            info['is_encrypted'] = False
        
        return info
        
    except Exception as e:
        return {'error': str(e)}

def extract_archive(archive_path: str, extract_to: str = None, 
                   password: str = None) -> Tuple[bool, str]:
    """Extract archive file to specified location"""
    try:
        if not os.path.exists(archive_path):
            return False, "Archive file does not exist"
        
        # Validate archive format
        valid_format, format_msg = validate_archive_format(archive_path)
        if not valid_format:
            return False, format_msg
        
        # Set default extraction path
        if extract_to is None:
            extract_to = '/content/drive/MyDrive/Downloads'
        
        # Validate and ensure destination is on Google Drive
        if not extract_to.startswith('/content/drive/MyDrive'):
            extract_to = f'/content/drive/MyDrive/Downloads/{os.path.basename(extract_to)}'
        
        valid_path, normalized_path = validate_path(extract_to)
        if not valid_path:
            return False, f"Invalid extraction path: {normalized_path}"
        extract_to = normalized_path
        
        # Create destination folder
        if not create_folder_if_not_exists(extract_to):
            return False, "Cannot create extraction folder"
        
        file_ext = os.path.splitext(archive_path)[1].lower()
        
        # Handle compound extensions
        if archive_path.lower().endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
            if archive_path.lower().endswith('.tar.gz'):
                file_ext = '.tar.gz'
            elif archive_path.lower().endswith('.tar.bz2'):
                file_ext = '.tar.bz2'
            elif archive_path.lower().endswith('.tar.xz'):
                file_ext = '.tar.xz'
        
        extracted_files = 0
        
        if file_ext == '.zip':
            try:
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    if password:
                        zip_ref.setpassword(password.encode())
                    zip_ref.extractall(extract_to)
                    extracted_files = len(zip_ref.namelist())
                return True, f"Extracted {extracted_files} files from ZIP archive"
            except zipfile.BadZipFile:
                return False, "Invalid or corrupted ZIP file"
            except RuntimeError as e:
                if "Bad password" in str(e):
                    return False, "Incorrect password for encrypted ZIP"
                return False, f"ZIP extraction error: {str(e)}"
        
        elif file_ext in ['.tar', '.tar.gz', '.tar.bz2', '.tar.xz']:
            try:
                mode = 'r'
                if file_ext == '.tar.gz':
                    mode = 'r:gz'
                elif file_ext == '.tar.bz2':
                    mode = 'r:bz2'
                elif file_ext == '.tar.xz':
                    mode = 'r:xz'
                
                with tarfile.open(archive_path, mode) as tar_ref:
                    # Security check: prevent path traversal
                    def safe_extract(tarinfo, path):
                        if os.path.isabs(tarinfo.name) or ".." in tarinfo.name:
                            return None
                        return tarinfo
                    
                    tar_ref.extractall(extract_to, members=[
                        member for member in tar_ref.getmembers() 
                        if safe_extract(member, extract_to)
                    ])
                    extracted_files = len(tar_ref.getnames())
                
                return True, f"Extracted {extracted_files} files from TAR archive"
            except tarfile.TarError as e:
                return False, f"TAR extraction error: {str(e)}"
        
        elif file_ext == '.7z':
            try:
                import py7zr
                with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                    z.extractall(extract_to)
                    extracted_files = len(z.getnames())
                return True, f"Extracted {extracted_files} files from 7Z archive"
            except ImportError:
                return False, "7Z extraction requires py7zr library (pip install py7zr)"
            except py7zr.exceptions.Bad7zFile:
                return False, "Invalid or corrupted 7Z file"
            except py7zr.exceptions.PasswordRequired:
                return False, "Password required for encrypted 7Z file"
            except py7zr.exceptions.WrongPassword:
                return False, "Incorrect password for encrypted 7Z file"
            except Exception as e:
                return False, f"7Z extraction error: {str(e)}"
        
        elif file_ext == '.rar':
            try:
                cmd = ['unrar', 'x', archive_path, extract_to]
                if password:
                    cmd.extend(['-p' + password])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode == 0:
                    # Count extracted files from output
                    output_lines = result.stdout.split('\n')
                    for line in output_lines:
                        if 'files' in line and 'extracted' in line.lower():
                            try:
                                extracted_files = int(line.split()[0])
                            except:
                                extracted_files = "Unknown"
                            break
                    return True, f"Extracted RAR archive ({extracted_files} files)"
                else:
                    error_msg = result.stderr or result.stdout
                    if "password" in error_msg.lower():
                        return False, "Incorrect password for encrypted RAR"
                    return False, f"RAR extraction failed: {error_msg}"
            except subprocess.TimeoutExpired:
                return False, "RAR extraction timed out"
            except FileNotFoundError:
                return False, "RAR extraction requires unrar tool (not available)"
            except Exception as e:
                return False, f"RAR extraction error: {str(e)}"
        
        else:
            return False, f"Unsupported archive format: {file_ext}"
    
    except Exception as e:
        return False, f"Extraction error: {str(e)}"

def create_archive(source_path: str, archive_path: str, archive_type: str = 'zip',
                  compression_level: int = 6) -> Tuple[bool, str]:
    """Create archive from files/folders"""
    try:
        if not os.path.exists(source_path):
            return False, "Source path does not exist"
        
        # Validate archive type
        supported_types = ['zip', 'tar', 'tar.gz', 'tar.bz2', 'tar.xz', '7z']
        if archive_type.lower() not in supported_types:
            return False, f"Unsupported archive type: {archive_type}"
        
        # Ensure archive is saved to Google Drive
        if not archive_path.startswith('/content/drive/MyDrive'):
            if '/' not in archive_path:
                archive_path = f'/content/drive/MyDrive/Downloads/{archive_path}'
            else:
                filename = os.path.basename(archive_path)
                archive_path = f'/content/drive/MyDrive/Downloads/{filename}'
        
        # Validate destination path
        dest_dir = os.path.dirname(archive_path)
        valid_path, normalized_path = validate_path(dest_dir)
        if not valid_path:
            return False, f"Invalid destination path: {normalized_path}"
        
        # Create destination folder
        if not create_folder_if_not_exists(dest_dir):
            return False, "Cannot create destination folder"
        
        archive_type = archive_type.lower()
        file_count = 0
        
        if archive_type == 'zip':
            try:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, 
                                   compresslevel=compression_level) as zip_ref:
                    if os.path.isfile(source_path):
                        zip_ref.write(source_path, os.path.basename(source_path))
                        file_count = 1
                    else:
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, os.path.dirname(source_path))
                                zip_ref.write(file_path, arc_name)
                                file_count += 1
                return True, f"Created ZIP archive with {file_count} files: {archive_path}"
            except Exception as e:
                return False, f"ZIP creation error: {str(e)}"
        
        elif archive_type in ['tar', 'tar.gz', 'tar.bz2', 'tar.xz']:
            try:
                mode = 'w'
                if archive_type == 'tar.gz':
                    mode = 'w:gz'
                elif archive_type == 'tar.bz2':
                    mode = 'w:bz2'
                elif archive_type == 'tar.xz':
                    mode = 'w:xz'
                
                with tarfile.open(archive_path, mode) as tar_ref:
                    if os.path.isfile(source_path):
                        tar_ref.add(source_path, arcname=os.path.basename(source_path))
                        file_count = 1
                    else:
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, os.path.dirname(source_path))
                                tar_ref.add(file_path, arcname=arc_name)
                                file_count += 1
                
                return True, f"Created {archive_type.upper()} archive with {file_count} files: {archive_path}"
            except Exception as e:
                return False, f"TAR creation error: {str(e)}"
        
        elif archive_type == '7z':
            try:
                import py7zr
                with py7zr.SevenZipFile(archive_path, 'w') as z:
                    if os.path.isfile(source_path):
                        z.write(source_path, os.path.basename(source_path))
                        file_count = 1
                    else:
                        for root, dirs, files in os.walk(source_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arc_name = os.path.relpath(file_path, os.path.dirname(source_path))
                                z.write(file_path, arc_name)
                                file_count += 1
                
                return True, f"Created 7Z archive with {file_count} files: {archive_path}"
            except ImportError:
                return False, "7Z creation requires py7zr library (pip install py7zr)"
            except Exception as e:
                return False, f"7Z creation error: {str(e)}"
        
        else:
            return False, f"Unsupported archive type: {archive_type}"
    
    except Exception as e:
        return False, f"Archive creation error: {str(e)}"

def list_archive_contents(archive_path: str, password: str = None) -> Tuple[bool, List[str]]:
    """List contents of an archive without extracting"""
    try:
        if not os.path.exists(archive_path):
            return False, ["Archive file does not exist"]
        
        file_ext = os.path.splitext(archive_path)[1].lower()
        
        # Handle compound extensions
        if archive_path.lower().endswith(('.tar.gz', '.tar.bz2', '.tar.xz')):
            if archive_path.lower().endswith('.tar.gz'):
                file_ext = '.tar.gz'
            elif archive_path.lower().endswith('.tar.bz2'):
                file_ext = '.tar.bz2'
            elif archive_path.lower().endswith('.tar.xz'):
                file_ext = '.tar.xz'
        
        contents = []
        
        if file_ext == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                if password:
                    zip_ref.setpassword(password.encode())
                contents = zip_ref.namelist()
        
        elif file_ext in ['.tar', '.tar.gz', '.tar.bz2', '.tar.xz']:
            mode = 'r'
            if file_ext == '.tar.gz':
                mode = 'r:gz'
            elif file_ext == '.tar.bz2':
                mode = 'r:bz2'
            elif file_ext == '.tar.xz':
                mode = 'r:xz'
            
            with tarfile.open(archive_path, mode) as tar_ref:
                contents = tar_ref.getnames()
        
        elif file_ext == '.7z':
            import py7zr
            with py7zr.SevenZipFile(archive_path, mode='r', password=password) as z:
                contents = z.getnames()
        
        elif file_ext == '.rar':
            result = subprocess.run(['unrar', 'lb', archive_path], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                contents = [line.strip() for line in result.stdout.split('\n') 
                           if line.strip() and not line.startswith('UNRAR')]
            else:
                return False, ["Could not list RAR contents"]
        
        else:
            return False, [f"Unsupported archive format: {file_ext}"]
        
        return True, contents
        
    except Exception as e:
        return False, [f"Error listing contents: {str(e)}"]
