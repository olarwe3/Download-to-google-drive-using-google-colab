"""
Constants and configuration values for the Avance Download Manager
"""
import json
import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
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
    },
    "storage": {
        "check_available_space": True,
        "warn_threshold_percent": 90,
        "cleanup_temp_files": True
    }
}

# HTTP Headers for optimal download performance
DOWNLOAD_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# File type categories
FILE_CATEGORIES = {
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'],
    'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
    'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
    'executable': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg', '.apk'],
    'data': ['.csv', '.json', '.xml', '.sql', '.db', '.sqlite'],
    'code': ['.py', '.js', '.html', '.css', '.cpp', '.java', '.php']
}

# UI Theme Constants
UI_THEMES = {
    'light': {
        'primary_color': '#4f46e5',
        'secondary_color': '#7c3aed',
        'background_color': '#ffffff',
        'text_color': '#000000',
        'border_color': '#e1e5e9',
        'success_color': '#10b981',
        'warning_color': '#f59e0b',
        'error_color': '#ef4444'
    },
    'dark': {
        'primary_color': '#6366f1',
        'secondary_color': '#8b5cf6',
        'background_color': '#1f2937',
        'text_color': '#f9fafb',
        'border_color': '#374151',
        'success_color': '#10b981',
        'warning_color': '#f59e0b',
        'error_color': '#ef4444'
    }
}

def load_config(config_path=None):
    """Load configuration from file or return defaults"""
    if config_path is None:
        # Try to find config.json in the project root
        current_dir = Path(__file__).parent.parent.parent
        config_path = current_dir / 'config.json'
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            for section in config:
                if section in merged_config:
                    merged_config[section].update(config[section])
                else:
                    merged_config[section] = config[section]
            return merged_config
        else:
            return DEFAULT_CONFIG
    except Exception:
        return DEFAULT_CONFIG

# Load the configuration
CONFIG = load_config()
