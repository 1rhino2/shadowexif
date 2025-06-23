# Changelog

All notable changes to ShadowEXIF will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added

- Initial release of ShadowEXIF
- Professional EXIF metadata removal and redaction capabilities
- Multi-threaded batch processing for high performance
- Support for JPEG, PNG, BMP, GIF, TIFF, and WebP formats
- Comprehensive command-line interface with argparse
- Directory processing with recursive scanning
- Backup and overwrite protection features
- Detailed processing statistics and progress tracking
- Beautiful CLI with progress bars and professional output
- Python API for programmatic usage
- Strip mode for complete EXIF removal
- Redact mode for replacing sensitive fields with "REDACTED"
- Automatic output file naming with customizable suffixes
- Verbose and quiet operation modes
- Cross-platform compatibility (Windows, macOS, Linux)
- Professional packaging for PyPI distribution
- Comprehensive test suite with unit and integration tests
- Documentation with usage examples and API reference

### Features

- **High Performance**: Multi-threaded processing with configurable worker count
- **Safety First**: Backup creation and overwrite protection
- **Privacy Focused**: Complete metadata removal or redaction
- **User Friendly**: Intuitive CLI with helpful error messages
- **Flexible**: Both command-line tool and Python library
- **Robust**: Comprehensive error handling and recovery
- **Professional**: Enterprise-grade code quality and documentation

### Technical Details

- Built with Python 3.7+ compatibility
- Uses Pillow (PIL) for image processing
- Uses piexif for EXIF metadata handling
- Optional C++ acceleration support with pybind11
- Type hints for better IDE support
- Extensive logging and debugging capabilities
- Memory efficient for large batch operations
- Progress tracking with ETA calculations

### Command Line Usage

```bash
# Basic usage
shadowexif image.jpg                    # Strip EXIF from single image
shadowexif *.jpg --mode redact          # Redact EXIF from multiple images
shadowexif --directory /photos         # Process entire directory
shadowexif /photos -d -r -o /clean     # Recursive with output directory

# Advanced options
shadowexif /photos --jobs 8 --stats    # High performance with statistics
shadowexif image.jpg --backup          # Create backup before processing
shadowexif /photos --quiet --overwrite # Script-friendly operation
```

### Python API Usage

```python
from shadowexif import ShadowEXIFProcessor

processor = ShadowEXIFProcessor(verbose=True)
success, output_path, error = processor.strip_exif('input.jpg')
stats = processor.process_directory('./photos', mode='redact')
```

### Dependencies

- Pillow >= 8.0.0
- piexif >= 1.1.3
- Python >= 3.7

### Optional Dependencies

- pybind11 >= 2.6.0 (for C++ acceleration)

---

## Future Releases

### Planned Features for 1.1.0

- Web interface for drag-and-drop processing
- Additional image format support (RAW, HEIC)
- Metadata analysis and reporting tools
- Custom redaction templates
- Batch rename capabilities
- Integration with cloud storage services

### Planned Features for 1.2.0

- GUI application with visual preview
- Automated workflow scheduling
- Advanced privacy analysis
- Watermarking capabilities
- Multi-language support
- Plugin system for extensibility

---

## Development

### Building from Source

```bash
git clone https://github.com/shadowexif/shadowexif.git
cd shadowexif
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/ -v --cov=shadowexif
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### License

MIT License - see [LICENSE](LICENSE) for details.
