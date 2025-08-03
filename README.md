# 🚀 Avance Download Manager

A professional, feature-rich download manager for Google Colab with advanced multi-threading, archive management, and beautiful UI.

## 🚀 Try it Now!

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/sk-labs/Download-to-google-drive-using-google-colab/blob/master/main_notebook.ipynb)

**Click the button above to open and run the main notebook directly in Google Colab!**

## ✨ Features

- **🚀 High-Speed Downloads**: Segmented downloads with up to 8 parallel connections
- **⚡ Multi-Threading**: Concurrent batch downloads for maximum efficiency
- **📦 Archive Management**: Extract and create ZIP, RAR, 7Z, TAR archives
- **📁 File Management**: Browse, organize, and manage Google Drive files
- **🎨 Modern UI**: Responsive interface with light/dark theme support
- **🔧 Error Handling**: Robust error recovery and validation
- **💾 Google Drive Integration**: Seamless integration with Google Drive storage

## 🚀 Quick Start

### Method 1: Direct Notebook Usage
1. Open the `main_notebook.ipynb` in Google Colab
2. Run all cells in sequence (Cell 1 → Cell 2 → Cell 3)
3. Start downloading!

### Method 2: Modular Installation
1. Upload the entire project to Google Colab
2. Install requirements: `!pip install -r requirements.txt`
3. Import and use individual modules as needed

## 📁 Project Structure

```
avance-download-manager/
├── 📓 main_notebook.ipynb          # Main interactive notebook
├── 📱 notebooks/                   # Additional specialized notebooks
│   ├── quick_download.ipynb        # Simplified download interface
│   ├── batch_processor.ipynb       # Batch download specialist
│   └── archive_tools.ipynb         # Archive management tools
├── 🐍 src/                        # Core Python modules
│   ├── core/                      # Core functionality
│   │   ├── download_manager.py    # Main download engine
│   │   ├── archive_manager.py     # Archive operations
│   │   ├── file_manager.py        # File management utilities
│   │   └── validators.py          # URL and input validation
│   ├── ui/                        # User interface components
│   │   ├── interfaces.py          # Main UI creation functions
│   │   ├── widgets.py             # Custom widget implementations
│   │   └── themes.py              # Theme and styling
│   └── utils/                     # Utility functions
│       ├── helpers.py             # General helper functions
│       ├── storage.py             # Storage management
│       └── constants.py           # Configuration constants
├── 🎨 assets/                     # Static assets
│   ├── css/                       # CSS styling files
│   └── images/                    # Icons and images
├── 📋 examples/                   # Usage examples
├── 🧪 tests/                      # Test suites
├── 📄 requirements.txt            # Python dependencies
├── ⚙️ setup.py                    # Package setup
├── 🔧 config.json                # Configuration file
└── 📖 docs/                       # Documentation
    ├── API.md                     # API documentation
    ├── USAGE.md                   # Usage guide
    └── TROUBLESHOOTING.md         # Common issues
```

## 🎯 Usage Examples

### Quick Download
```python
from src.core.download_manager import DownloadManager

dm = DownloadManager()
success = dm.download_file(
    "https://example.com/file.zip",
    "/content/drive/MyDrive/Downloads",
    "myfile.zip"
)
```

### Batch Downloads
```python
urls = [
    "https://example.com/file1.zip",
    "https://example.com/file2.pdf",
    "https://example.com/file3.mp4"
]

results = dm.download_multiple(
    urls, 
    "/content/drive/MyDrive/Downloads",
    max_workers=5
)
```

### Archive Operations
```python
from src.core.archive_manager import extract_archive, create_archive

# Extract archive
success, message = extract_archive(
    "/path/to/archive.zip",
    "/content/drive/MyDrive/Extracted"
)

# Create archive
success, message = create_archive(
    "/path/to/source",
    "/content/drive/MyDrive/new_archive.zip",
    "zip"
)
```

## 🔧 Configuration

Edit `config.json` to customize:
- Default download locations
- Maximum concurrent downloads
- Chunk sizes for optimal performance
- Theme preferences
- Archive extraction settings

## 🚀 Performance Features

- **Segmented Downloads**: Automatically splits large files (>10MB) into multiple segments
- **Optimized Chunking**: 256KB chunks for better I/O performance
- **Connection Pooling**: Reuses HTTP connections for efficiency
- **Smart Threading**: Adaptive worker allocation based on file sizes
- **Progress Tracking**: Real-time download progress with ETA calculations

## 🎨 UI Features

- **Theme Adaptation**: Automatically adapts to Colab's light/dark themes
- **Responsive Design**: Works seamlessly across different screen sizes
- **Real-time Updates**: Live progress bars and status updates
- **Error Display**: Clear error messages with suggested solutions
- **Quick Actions**: One-click download, refresh, and storage check

## 📦 Archive Support

| Format | Extract | Create | Password |
|--------|---------|--------|----------|
| ZIP    | ✅      | ✅     | ✅       |
| RAR    | ✅      | ❌     | ✅       |
| 7Z     | ✅      | ✅     | ✅       |
| TAR    | ✅      | ✅     | ❌       |
| TAR.GZ | ✅      | ✅     | ❌       |

## 🔧 Requirements

- Python 3.7+
- Google Colab environment
- Required packages listed in `requirements.txt`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📖 Check the [documentation](docs/) for detailed guides
- 🐛 Report issues on GitHub
- 💡 Suggest features through issues
- 📧 Contact: [Your Email]

## 🙏 Acknowledgments

- Built for Google Colab environment
- Inspired by professional download managers
- Thanks to the open-source community

---

**⭐ Star this repository if you find it helpful!**
