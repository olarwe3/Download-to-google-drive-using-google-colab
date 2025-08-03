"""
Setup script for Avance Download Manager
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="avance-download-manager",
    version="4.1.0",
    author="Avance Team",
    author_email="contact@avance.dev",
    description="Professional Google Drive download manager with advanced features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/avance-team/avance-download-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving",
        "Topic :: Utilities",
        "Environment :: Console",
        "Framework :: Jupyter",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "7z": [
            "py7zr>=0.20.0",
        ],
        "all": [
            "py7zr>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "avance-dl=src.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/avance-team/avance-download-manager/issues",
        "Source": "https://github.com/avance-team/avance-download-manager",
        "Documentation": "https://github.com/avance-team/avance-download-manager/docs",
    },
    keywords="download manager google-drive colab jupyter segmented multi-threaded archive",
    include_package_data=True,
    zip_safe=False,
)
