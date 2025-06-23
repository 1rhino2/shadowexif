# ShadowEXIF

**Simple EXIF Metadata Removal Tool**

ShadowEXIF is a straightforward command-line tool that removes or redacts EXIF metadata from your images. Perfect for protecting your privacy when sharing photos online.

## Why Use ShadowEXIF?

Digital photos contain hidden metadata (EXIF) that can reveal:

- Your exact location (GPS coordinates)
- Camera make and model
- When the photo was taken
- Software used to edit the image
- Sometimes even your name

ShadowEXIF cleans this data so you can share photos safely.

## Installation

```bash
pip install shadowexif
```

## Quick Start

```bash
# Clean a single image
shadowexif photo.jpg

# Clean multiple images
shadowexif *.jpg *.png

# Clean all images in a folder
shadowexif --directory /path/to/photos

# Replace metadata with "REDACTED" instead of removing it
shadowexif photo.jpg --mode redact
```

## How It Works

**Strip Mode (default)**: Completely removes all EXIF metadata

```bash
shadowexif photo.jpg
```

**Redact Mode**: Replaces sensitive data with "REDACTED"

```bash
shadowexif photo.jpg --mode redact
```

## More Examples

```bash
# Process entire directory
shadowexif --directory ./photos

# Process with subdirectories too
shadowexif --directory ./photos --recursive

# Save cleaned images to a different folder
shadowexif --directory ./photos --output ./clean_photos

# Create backup copies before cleaning
shadowexif photo.jpg --backup

# Process multiple files with verbose output
shadowexif *.jpg --verbose

# Get detailed statistics
shadowexif --directory ./photos --stats
```

## Command Line Options

```
Options:
  -d, --directory PATH     Directory containing images to process
  -o, --output PATH        Output directory for cleaned images
  -m, --mode {strip,redact} Processing mode (default: strip)
  -r, --recursive          Process subdirectories too
  --backup                 Create backup before processing
  --overwrite              Overwrite existing output files
  -j, --jobs N            Number of parallel jobs (default: 4)
  -v, --verbose           Show detailed output
  -q, --quiet             Show minimal output
  --stats                 Show processing statistics
  --version               Show version
  -h, --help              Show help
```

## Supported Image Formats

- JPEG/JPG
- PNG
- TIFF/TIF
- BMP
- GIF
- WebP

## Python API

You can also use ShadowEXIF in your Python code:

```python
from shadowexif import ShadowEXIFProcessor

# Create processor
processor = ShadowEXIFProcessor()

# Clean a single file
success, output_path, error = processor.strip_exif('input.jpg')
if success:
    print(f"Cleaned image saved to: {output_path}")
else:
    print(f"Error: {error}")

# Process entire directory
stats = processor.process_directory('./photos', mode='strip')
print(f"Processed {stats.processed_files} files")
```

## Privacy Benefits

- 🛡️ **Remove Location Data**: Strip GPS coordinates from photos
- 🔒 **Hide Camera Info**: Remove camera make, model, and settings
- 📅 **Remove Timestamps**: Clean creation and modification dates
- 👤 **Remove Personal Info**: Strip artist, copyright, and comments
- 🔍 **Prevent Tracking**: Remove identifying digital fingerprints

## Requirements

- Python 3.7 or higher
- Pillow (PIL) for image processing
- piexif for EXIF handling

## License

MIT License - see LICENSE file for details.

## Author

Created by 1rhino2 (xmansussy@yahoo.com)

## Issues & Support

If you encounter any problems or have questions, please open an issue on GitHub:
https://github.com/1rhino2/shadowexif/issues

## Changelog

**v1.0.0** - Initial release

- EXIF stripping and redaction
- Multi-threaded batch processing
- Command-line interface
- Python API
- Support for multiple image formats
