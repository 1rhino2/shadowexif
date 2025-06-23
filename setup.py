#!/usr/bin/env python3
"""
Setup script for ShadowEXIF - EXIF Metadata Removal Tool
Simple, clean setup for PyPI distribution.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Package information
__version__ = "1.0.0"
__author__ = "1rhino2"
__email__ = "xmansussy@yahoo.com"
__license__ = "MIT"
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "ShadowEXIF - Simple and effective EXIF metadata removal tool"

# Core dependencies
requirements = ["Pillow>=8.0.0", "piexif>=1.1.3"]

setup(
    name="shadowexif",
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="Simple and effective EXIF metadata removal tool",
    long_description=long_description,
    long_description_content_type="text/markdown",    url="https://github.com/1rhino2/shadowexif",
    project_urls={
        "Bug Reports": "https://github.com/1rhino2/shadowexif/issues",
        "Source": "https://github.com/1rhino2/shadowexif",
        "Documentation": "https://github.com/1rhino2/shadowexif#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Security",
        "Topic :: Utilities",
    ],
    keywords="exif metadata privacy security image photo",
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "shadowexif=shadowexif.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    license=__license__,
)
