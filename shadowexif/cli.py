#!/usr/bin/env python3
"""
ShadowEXIF Command Line Interface

Professional CLI for EXIF metadata removal and redaction with comprehensive
options for batch processing, directory scanning, and progress tracking.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List
import time

from .core import ShadowEXIFProcessor, ProcessingStats


def format_bytes(bytes_value: int) -> str:
    """Format bytes in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"


def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                      suffix: str = '', length: int = 50, fill: str = '█'):
    """Print a progress bar to the console."""
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='', flush=True)
    if iteration == total:
        print()  # New line on completion


def print_banner():
    """Print a simple, clean banner."""
    print("""
ShadowEXIF - EXIF Metadata Removal Tool
========================================
Strip or redact EXIF data from your images
Author: 1rhino2 on discord
    """)


def print_completion_message():
    """Print a simple completion message."""
    print("""
✅ Processing Complete!
Your images have been cleaned of EXIF metadata.
    """)


class CLIProgressTracker:
    """Progress tracker for CLI operations."""
    
    def __init__(self, total_files: int, verbose: bool = False):
        self.total_files = total_files
        self.verbose = verbose
        self.current = 0
        self.start_time = time.time()
        
    def update(self, current: int, total: int, success: bool, 
               result_path: str, error: Optional[str]):
        """Update progress and print status."""
        self.current = current
        
        # Calculate ETA
        elapsed = time.time() - self.start_time
        if current > 0:
            eta = (elapsed / current) * (total - current)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        
        # Update progress bar
        print_progress_bar(
            current, total,
            prefix=f'Processing ({current}/{total})',
            suffix=eta_str
        )
        
        # Print individual file status if verbose
        if self.verbose:
            status = "✓" if success else "✗"
            if success:
                print(f"\n{status} {Path(result_path).name}")
            else:
                print(f"\n{status} Error: {error}")


def validate_input_path(path_str: str) -> Path:
    """Validate and return a Path object for input."""
    path = Path(path_str)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"Path does not exist: {path_str}")
    return path


def validate_output_path(path_str: str) -> Path:
    """Validate and return a Path object for output."""
    path = Path(path_str)
    if path.exists() and not path.is_dir():
        raise argparse.ArgumentTypeError(f"Output path exists and is not a directory: {path_str}")
    return path


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='shadowexif',
        description='Professional EXIF metadata removal and redaction tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shadowexif image.jpg                    # Strip EXIF from single image
  shadowexif *.jpg --mode redact          # Redact EXIF from multiple images
  shadowexif /photos --directory          # Process entire directory
  shadowexif /photos -d -r -o /clean      # Recursive processing with output dir
  shadowexif image.jpg --backup           # Create backup before processing
  shadowexif /photos -d --stats           # Show detailed statistics

Modes:
  strip    Remove all EXIF metadata completely (default)
  redact   Replace sensitive EXIF fields with "REDACTED"

Supported formats: JPEG, PNG, BMP, GIF, TIFF, WebP
        """
    )
    
    # Input specification
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        'files',
        nargs='*',
        type=validate_input_path,
        help='Image files to process'
    )
    input_group.add_argument(
        '-d', '--directory',
        type=validate_input_path,
        help='Directory containing images to process'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        type=validate_output_path,
        help='Output directory for processed images'
    )
    
    # Processing options
    parser.add_argument(
        '-m', '--mode',
        choices=['strip', 'redact'],
        default='strip',
        help='Processing mode (default: strip)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Process directories recursively'
    )
    
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create backup files before processing'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing output files'
    )
    
    # Performance options
    parser.add_argument(
        '-j', '--jobs',
        type=int,
        default=4,
        metavar='N',
        help='Number of parallel processing jobs (default: 4)'
    )
    
    # Output control
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show detailed processing statistics'
    )
    
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Suppress the banner display'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='ShadowEXIF 1.0.0'
    )
    
    return parser


def print_statistics(stats: ProcessingStats, elapsed_time: float):
    """Print detailed processing statistics."""
    print("\n" + "="*60)
    print("PROCESSING STATISTICS")
    print("="*60)
    print(f"Total files:        {stats.total_files:>8}")
    print(f"Successfully processed: {stats.processed_files:>4} ({stats.success_rate():.1f}%)")
    print(f"Failed:             {stats.failed_files:>8}")
    print(f"Skipped:            {stats.skipped_files:>8}")
    print(f"Bytes saved:        {format_bytes(stats.bytes_saved):>8}")
    print(f"Processing time:    {elapsed_time:.2f}s")
    if stats.processed_files > 0:
        print(f"Average per file:   {elapsed_time/stats.processed_files:.2f}s")
    print("="*60)


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle quiet mode
    if args.quiet:
        args.verbose = False
        args.no_banner = True
    
    # Print banner unless suppressed
    if not args.no_banner and not args.quiet:
        print_banner()
    
    # Validate arguments
    if args.files and not args.files:
        parser.error("No input files specified")
    
    if args.recursive and not args.directory:
        parser.error("--recursive can only be used with --directory")
    
    # Initialize processor
    processor = ShadowEXIFProcessor(
        verbose=args.verbose and not args.quiet,
        max_workers=args.jobs
    )
    
    start_time = time.time()
    
    try:
        # Determine input files
        if args.directory:
            if not args.quiet:
                print(f"Scanning directory: {args.directory}")
                if args.recursive:
                    print("Recursive mode enabled")
            
            input_files = processor.find_images(args.directory, args.recursive)
            
            if not input_files:
                print(f"No supported image files found in {args.directory}")
                return 1
            
            if not args.quiet:
                print(f"Found {len(input_files)} image files")
            
            # Setup progress tracking
            progress_tracker = None
            if not args.quiet:
                progress_tracker = CLIProgressTracker(len(input_files), args.verbose)
            
            # Process directory
            stats = processor.process_directory(
                args.directory,
                output_dir=args.output,
                mode=args.mode,
                recursive=args.recursive,
                backup=args.backup,
                overwrite=args.overwrite,
                progress_callback=progress_tracker.update if progress_tracker else None
            )
            
        else:
            # Process individual files
            input_files = args.files
            
            if not args.quiet:
                print(f"Processing {len(input_files)} file(s)")
            
            # Setup progress tracking
            progress_tracker = None
            if not args.quiet:
                progress_tracker = CLIProgressTracker(len(input_files), args.verbose)
            
            # Process files
            stats = processor.process_batch(
                input_files,
                output_dir=args.output,
                mode=args.mode,
                backup=args.backup,
                overwrite=args.overwrite,
                progress_callback=progress_tracker.update if progress_tracker else None
            )
        
        elapsed_time = time.time() - start_time
          # Print completion message
        if not args.quiet:
            if args.mode == 'redact':
                print("\n🔒 EXIF data has been redacted from your images.")
            else:
                print("\n🧹 EXIF data has been stripped from your images.")
            print_completion_message()# Print statistics if requested or if there were any failures
        if args.stats or (stats.failed_files > 0 and not args.quiet):
            print_statistics(stats, elapsed_time)
        
        # Return appropriate exit code
        if stats.failed_files > 0:
            if not args.quiet:
                print(f"\nWarning: {stats.failed_files} files failed to process")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    
    except Exception as e:
        print(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
