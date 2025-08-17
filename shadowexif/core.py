#!/usr/bin/env python3
"""
ShadowEXIF Core Module

Simple and effective EXIF metadata processing.
Author: 1rhino2 on discord
"""

import os
import sys
import logging
from typing import List, Tuple, Optional, Union
from pathlib import Path
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass

try:
    from PIL import Image, ExifTags
    import piexif
except ImportError as e:
    print(f"Required libraries not found: {e}")
    print("Please install with: pip install Pillow piexif")
    sys.exit(1)


@dataclass
class ProcessingStats:
    """Simple statistics for processing operations."""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    bytes_saved: int = 0
    
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.processed_files / self.total_files) * 100


class ShadowEXIFProcessor:
    """
    Simple EXIF metadata processor for privacy.
    
    Removes or redacts EXIF data from images.
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'
    }
    
    def __init__(self, verbose: bool = False, max_workers: int = 4):
        """
        Initialize the processor.
        
        Args:
            verbose: Show detailed output
            max_workers: Number of threads for batch processing
        """
        self.verbose = verbose
        self.max_workers = max_workers
        self.stats = ProcessingStats()
        self._lock = threading.Lock()
        
        # Setup simple logging
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup basic logging."""
        logger = logging.getLogger('shadowexif')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """Check if the file format is supported."""
        suffix = Path(file_path).suffix.lower()
        return suffix in self.SUPPORTED_FORMATS
    
    def has_exif_data(self, image_path: Union[str, Path]) -> bool:
        """Check if an image contains EXIF metadata."""
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                return False
                
            with Image.open(image_path) as img:
                # Check for EXIF data
                if hasattr(img, '_getexif') and img._getexif() is not None:
                    return True
                if 'exif' in img.info and img.info['exif']:
                    return True
                return False
                
        except Exception as e:
            self.logger.debug(f"Error checking EXIF for {image_path}: {e}")
            return False
    
    def get_file_size(self, file_path: Union[str, Path]) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def strip_exif(self, input_path: Union[str, Path], 
                   output_path: Optional[Union[str, Path]] = None,
                   backup: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Strip all EXIF metadata from an image.
        
        Args:
            input_path: Path to input image
            output_path: Path for output image (optional)
            backup: Create backup of original file
            
        Returns:
            Tuple of (success, output_path, error_message)
        """
        input_path = Path(input_path)
        
        # Basic validation
        if not input_path.exists():
            return False, "", f"File does not exist: {input_path}"
        
        if not self.is_supported_format(input_path):
            return False, "", f"Unsupported format: {input_path.suffix}"
        
        # Determine output path
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_clean{input_path.suffix}"
        else:
            output_path = Path(output_path)
        
        try:
            # Create backup if requested
            if backup:
                backup_path = input_path.parent / f"{input_path.stem}_backup{input_path.suffix}"
                shutil.copy2(input_path, backup_path)
                self.logger.info(f"Backup created: {backup_path}")
            
            # Process image
            with Image.open(input_path) as img:
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert mode if needed for JPEG
                if output_path.suffix.lower() in {'.jpg', '.jpeg'} and img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparent images
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'RGBA':
                            background.paste(img, mask=img.split()[-1])
                        else:
                            background.paste(img)
                        img = background
                
                # Save without EXIF data
                save_kwargs = {'quality': 95, 'optimize': True}
                if output_path.suffix.lower() == '.png':
                    del save_kwargs['quality']  # PNG doesn't use quality
                    
                img.save(output_path, **save_kwargs)
            
            self.logger.info(f"EXIF stripped: {input_path} -> {output_path}")
            return True, str(output_path), None
            
        except PermissionError:
            return False, "", f"Permission denied: {input_path}"
        except Exception as e:
            error_msg = f"Failed to process {input_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, "", error_msg
    
    def redact_exif(self, input_path: Union[str, Path],
                    output_path: Optional[Union[str, Path]] = None,
                    backup: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Redact EXIF metadata by replacing with "REDACTED".
        
        Args:
            input_path: Path to input image
            output_path: Path for output image (optional)
            backup: Create backup of original file
            
        Returns:
            Tuple of (success, output_path, error_message)
        """
        input_path = Path(input_path)
        
        # Basic validation
        if not input_path.exists():
            return False, "", f"File does not exist: {input_path}"
        
        if not self.is_supported_format(input_path):
            return False, "", f"Unsupported format: {input_path.suffix}"
        
        # Determine output path
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_redacted{input_path.suffix}"
        else:
            output_path = Path(output_path)
        
        try:
            # Create backup if requested
            if backup:
                backup_path = input_path.parent / f"{input_path.stem}_backup{input_path.suffix}"
                shutil.copy2(input_path, backup_path)
                self.logger.info(f"Backup created: {backup_path}")
            
            with Image.open(input_path) as img:
                # Ensure output directory exists
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Try to create redacted EXIF data
                try:
                    if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
                        # Create redacted EXIF dictionary for JPEG
                        exif_dict = {
                            "0th": {
                                piexif.ImageIFD.Make: "REDACTED",
                                piexif.ImageIFD.Model: "REDACTED",
                                piexif.ImageIFD.Software: "REDACTED",
                                piexif.ImageIFD.DateTime: "REDACTED",
                                piexif.ImageIFD.Artist: "REDACTED",
                                piexif.ImageIFD.Copyright: "REDACTED",
                            },
                            "Exif": {
                                piexif.ExifIFD.DateTimeOriginal: "REDACTED",
                                piexif.ExifIFD.DateTimeDigitized: "REDACTED",
                                piexif.ExifIFD.UserComment: b"REDACTED",
                            },
                            "GPS": {},  # Empty GPS data
                            "1st": {},
                            "thumbnail": None
                        }
                        
                        exif_bytes = piexif.dump(exif_dict)
                        img.save(output_path, exif=exif_bytes, quality=95, optimize=True)
                    else:
                        # For non-JPEG formats, just strip the metadata
                        save_kwargs = {'optimize': True}
                        if output_path.suffix.lower() != '.png':
                            save_kwargs['quality'] = 95
                        img.save(output_path, **save_kwargs)
                        
                except Exception as e:
                    # Fallback to stripping if redaction fails
                    self.logger.warning(f"Redaction failed for {input_path}, stripping instead: {e}")
                    save_kwargs = {'quality': 95, 'optimize': True}
                    if output_path.suffix.lower() == '.png':
                        del save_kwargs['quality']
                    img.save(output_path, **save_kwargs)
            
            self.logger.info(f"EXIF redacted: {input_path} -> {output_path}")
            return True, str(output_path), None
            
        except PermissionError:
            return False, "", f"Permission denied: {input_path}"
        except Exception as e:
            error_msg = f"Failed to process {input_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, "", error_msg
    
    def process_file(self, input_path: Union[str, Path],
                     output_path: Optional[Union[str, Path]] = None,
                     mode: str = 'strip',
                     backup: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Process a single file with the specified mode."""
        if mode == 'strip':
            return self.strip_exif(input_path, output_path, backup)
        elif mode == 'redact':
            return self.redact_exif(input_path, output_path, backup)
        else:
            return False, "", f"Invalid mode: {mode}. Use 'strip' or 'redact'"
    
    def find_images(self, directory: Union[str, Path], recursive: bool = False) -> List[Path]:
        """Find all supported image files in a directory."""
        directory = Path(directory)
        images = []
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and self.is_supported_format(file_path):
                images.append(file_path)
        
        return sorted(images)
    
    def _process_single_file(self, args: Tuple) -> Tuple[bool, str, Optional[str], int]:
        """Worker function for batch processing."""
        input_path, output_dir, mode, backup, overwrite = args
        
        # Calculate original file size
        original_size = self.get_file_size(input_path)
        
        # Determine output path
        if output_dir:
            suffix = '_clean' if mode == 'strip' else '_redacted'
            output_path = Path(output_dir) / f"{input_path.stem}{suffix}{input_path.suffix}"
        else:
            output_path = None
        
        # Check if output exists and handle overwrite
        if output_path and output_path.exists() and not overwrite:
            with self._lock:
                self.stats.skipped_files += 1
            return False, str(output_path), "File exists (use --overwrite)", 0
        
        # Process the file
        success, result_path, error = self.process_file(input_path, output_path, mode, backup)
        
        # Calculate size difference
        size_saved = 0
        if success and result_path:
            new_size = self.get_file_size(result_path)
            size_saved = max(0, original_size - new_size)
        
        # Update stats
        with self._lock:
            if success:
                self.stats.processed_files += 1
                self.stats.bytes_saved += size_saved
            else:
                self.stats.failed_files += 1
        
        return success, result_path, error, size_saved
    
    def process_batch(self, input_paths: List[Union[str, Path]],
                      output_dir: Optional[Union[str, Path]] = None,
                      mode: str = 'strip',
                      backup: bool = False,
                      overwrite: bool = False,
                      progress_callback=None) -> ProcessingStats:
        """Process multiple files in batch."""
        # Reset stats
        self.stats = ProcessingStats()
        self.stats.total_files = len(input_paths)
        
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Filter supported files
        worker_args = [
            (Path(path), output_dir, mode, backup, overwrite)
            for path in input_paths
            if self.is_supported_format(path)
        ]
        
        # Process files with thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._process_single_file, args) for args in worker_args]
            
            for i, future in enumerate(as_completed(futures), 1):
                try:
                    success, result_path, error, size_saved = future.result()
                    
                    if progress_callback:
                        progress_callback(i, len(futures), success, result_path, error)
                    
                    if self.verbose:
                        if success:
                            self.logger.info(f"✓ {result_path}")
                        else:
                            self.logger.error(f"✗ {error}")
                            
                except Exception as e:
                    self.logger.error(f"Worker error: {e}")
                    with self._lock:
                        self.stats.failed_files += 1
        
        return self.stats
    
    def process_directory(self, directory: Union[str, Path],
                          output_dir: Optional[Union[str, Path]] = None,
                          mode: str = 'strip',
                          recursive: bool = False,
                          backup: bool = False,
                          overwrite: bool = False,
                          progress_callback=None) -> ProcessingStats:
        """Process all images in a directory."""
        image_files = self.find_images(directory, recursive)
        
        if not image_files:
            self.logger.warning(f"No supported images found in {directory}")
            return ProcessingStats()
        
        self.logger.info(f"Found {len(image_files)} image files")
        
        return self.process_batch(
            image_files, output_dir, mode, backup, overwrite, progress_callback
        )
