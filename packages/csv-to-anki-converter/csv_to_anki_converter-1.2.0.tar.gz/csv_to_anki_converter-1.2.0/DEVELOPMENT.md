# Development Guide

## Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/csv-to-anki-converter.git
   cd csv-to-anki-converter
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=csv_to_anki_converter

# Run specific test file
pytest tests/test_converter.py
```

## Code Quality

```bash
# Format code
black csv_to_anki_converter/

# Lint code
flake8 csv_to_anki_converter/

# Type checking
mypy csv_to_anki_converter/
```

## Building and Testing the Package

1. **Build the package:**
   ```bash
   ./build_package.sh
   ```

2. **Test installation locally:**
   ```bash
   pip install dist/csv_to_anki_converter-1.0.0-py3-none-any.whl
   csv-to-anki --help
   ```

3. **Test with example files:**
   ```bash
   csv-to-anki examples/simple_programming.csv
   csv-to-anki --batch --input-dir examples --output-dir test_output
   ```

## Publishing to PyPI

### Test PyPI (Recommended first)

1. **Upload to Test PyPI:**
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

2. **Test installation from Test PyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ csv-to-anki-converter
   ```

### Production PyPI

1. **Upload to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

2. **Verify installation:**
   ```bash
   pip install csv-to-anki-converter
   csv-to-anki --help
   ```

## Release Process

1. Update version in `pyproject.toml` and `csv_to_anki_converter/__init__.py`
2. Update `CHANGELOG.md`
3. Create and push git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
4. Build and upload to PyPI
5. Create GitHub release

## Project Structure

```
csv-to-anki-converter/
├── csv_to_anki_converter/      # Main package
│   ├── __init__.py            # Package initialization
│   ├── cli.py                 # Command-line interface
│   ├── converter.py           # Core conversion logic
│   └── models.py              # Anki model definitions
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_converter.py
├── examples/                  # Sample CSV files
├── csv_to_anki.py            # Standalone script (backwards compatibility)
├── auto_csv_to_anki.py       # Standalone batch script
├── pyproject.toml            # Modern Python packaging
├── setup.py                  # Legacy setup (for compatibility)
├── MANIFEST.in               # Package data inclusion
├── build_package.sh          # Build script
└── README.md                 # Documentation
```

## API Usage

```python
# Import the package
from csv_to_anki_converter import csv_to_anki_deck, convert_directory

# Convert a single file
output_file = csv_to_anki_deck("my_vocab.csv", deck_name="Vocabulary")

# Batch convert a directory
results = convert_directory("csv_files/", "anki_output/")
print(f"Converted {results['successful_conversions']} files")
```
