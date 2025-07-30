# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-07-06

### Added

- **Tag sanitization for Anki compatibility**: Added automatic tag sanitization to ensure tags work properly in Anki
- German character conversion in tags (ü→ue, ä→ae, ö→oe, ß→ss)
- Special character handling in tags (spaces and invalid characters converted to underscores)
- Tag validation and cleanup (removes leading/trailing special characters, limits length)
- Enhanced auto CSV converter (`auto_csv_to_anki.py`) with full tag support

### Fixed

- **Tags not appearing in Anki**: Fixed issue where tags with German characters or special characters were not displaying in Anki
- Tag processing now ensures full compatibility with Anki's tag requirements
- Both main converter and auto converter now properly handle tag sanitization

### Enhanced

- Improved tag processing documentation
- Added comprehensive tag sanitization test scripts
- Better error handling for tag processing
- Updated help text to explain tag sanitization features

## [1.1.0] - 2025-07-04

### Added

- **Tag support in CSV files**: Added support for optional 'Tags' column in CSV files
- Cards can now be tagged with comma-separated tags for better organization in Anki
- New example CSV files with tags: `french_with_tags.csv` and `programming_with_tags.csv`

### Enhanced

- Updated CSV format documentation to include tag support
- Enhanced converter to automatically detect and process tags from CSV files
- Tags are automatically cleaned and split by commas

### Examples

- CSV files can now include a 'Tags' column with comma-separated values
- Example: `"What is Python?","A programming language","programming,language,python"`

## [1.0.0] - 2025-07-04

### Initial Release

- Initial release of CSV to Anki Converter
- Command line converter (`csv_to_anki.py`) with customizable options
- Automatic batch converter (`auto_csv_to_anki.py`) with directory support
- **PyPI package distribution** (`pip install csv-to-anki-converter`)
- **Command-line tool** (`csv-to-anki`) for easy access after installation
- Support for HTML formatting in flashcards
- Input and output directory customization
- Comprehensive error handling and validation
- Demo script for testing functionality
- Example CSV files for demonstration
- MIT License
- GitHub Actions workflow for automated testing
- Cross-platform compatibility (Windows, macOS, Linux)
- **Modern Python packaging** with pyproject.toml
- **Comprehensive test suite** with pytest
- **Development documentation** and build scripts

### Features

- Convert CSV files with 'Front' and 'Back' columns to Anki decks
- Custom deck names and output file paths
- Batch processing of multiple CSV files
- Automatic directory creation
- Verbose output mode
- HTML tag support in flashcard content
- Proper .apkg file generation compatible with Anki
- **Package API** for programmatic use in other projects
- **Unified command-line interface** supporting both single file and batch modes

### Installation Methods

- **PyPI installation**: `pip install csv-to-anki-converter`
- **Source installation**: Clone repository and install dependencies
- **Standalone scripts**: Use without installation

### Documentation

- Comprehensive README with usage examples
- Development guide for contributors
- Troubleshooting guide
- Contributing guidelines
- License information
