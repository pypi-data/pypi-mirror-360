# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-04

### Added
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
