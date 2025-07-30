# CSV to Anki Converter

Convert CSV files to Anki deck packages (.apkg) with support for tags and HTML formatting.

## Features

- Convert CSV files to Anki flashcard decks
- Support for tags (comma-separated)
- HTML formatting support
- German character sanitization for tags
- Batch processing
- Command-line interface

## Installation

```bash
pip install csv-to-anki-converter
```

## Quick Start

### Basic Usage
```bash
csv-to-anki input.csv
```

### CSV Format
```csv
Front,Back,Tags
"What is Python?","A programming language","programming,python"
"Bonjour","Hello in French","french,greeting"
```

### Batch Processing
```bash
csv-to-anki --batch input_folder/ output_folder/
```

## Requirements

- Python 3.8+
- pandas >= 1.3.0
- genanki >= 0.13.0

## Tag Sanitization

German characters in tags are automatically converted for Anki compatibility:
- ü → ue, ä → ae, ö → oe, ß → ss

## Documentation

Full documentation and examples: [GitHub Repository](https://github.com/NurNichtWilly/ankipak)

## License

MIT License
