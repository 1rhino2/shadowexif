"""
ShadowEXIF - Professional EXIF Metadata Removal Tool

A powerful, fast, and user-friendly tool for removing or redacting EXIF metadata
from images while preserving image quality. Designed for privacy-conscious users,
photographers, and security professionals.

Features:
- Strip or redact EXIF metadata from images
- Support for multiple image formats (JPEG, PNG, BMP, GIF, TIFF, WebP)
- Batch processing with multi-threading
- Recursive directory processing
- Professional CLI with progress tracking
- Backup and overwrite protection
- Detailed processing statistics

Usage:
    from shadowexif import ShadowEXIFProcessor
    
    processor = ShadowEXIFProcessor()
    success, output_path, error = processor.strip_exif('input.jpg')
"""

__version__ = "1.0.0"
__author__ = ""
__email__ = ""
__license__ = "MIT"

from .core import ShadowEXIFProcessor, ProcessingStats
from .cli import main as cli_main

__all__ = [
    'ShadowEXIFProcessor',
    'ProcessingStats',
    'cli_main',
]
