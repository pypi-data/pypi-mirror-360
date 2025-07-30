#!/usr/bin/env python3
"""
CSV to Anki Deck Converter (Command Line Version)

This script converts CSV files to Anki deck packages (.apkg files) using command line arguments.
The CSV should have columns 'Front' and 'Back' for flashcard content.

This is a standalone script that can be used without installing the package.
For the installed package version, use: csv-to-anki

Usage:
    python csv_to_anki.py input.csv
    python csv_to_anki.py input.csv --deck-name "My Deck" --output my_deck.apkg
"""

import os
import sys
import argparse
import random
import pandas as pd
import genanki
from pathlib import Path
import html

# Try to import from package if available, otherwise use local functions
try:
    from csv_to_anki_converter import csv_to_anki_deck
    PACKAGE_AVAILABLE = True
except ImportError:
    PACKAGE_AVAILABLE = False


def generate_model_id():
    """Generate a unique model ID for Anki."""
    return random.randrange(1 << 30, 1 << 31)


def generate_deck_id():
    """Generate a unique deck ID for Anki."""
    return random.randrange(1 << 30, 1 << 31)


def create_basic_model():
    """Create a basic Anki model for Front/Back flashcards."""
    return genanki.Model(
        1607392319,  # Fixed model ID for consistency
        'Basic CSV Import Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ],
        css='''
        .card {
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
            line-height: 1.4;
        }
        
        .card hr {
            border: 1px solid #ddd;
            margin: 20px 0;
        }
        
        .card b {
            color: #2c5aa0;
        }
        
        .card i {
            color: #666;
        }
        '''
    )


def clean_html_content(content):
    """Clean and validate HTML content for Anki."""
    if pd.isna(content):
        return ""
    
    # Convert to string and strip whitespace
    content = str(content).strip()
    
    # Basic HTML validation - ensure proper encoding
    # The content is already HTML, so we don't need to escape it
    # But we should handle any encoding issues
    return content


def csv_to_anki_deck(csv_file, deck_name=None, output_file=None):
    """
    Convert a CSV file to an Anki deck package.
    
    Args:
        csv_file (str): Path to the CSV file
        deck_name (str): Name of the Anki deck (optional)
        output_file (str): Output .apkg file path (optional)
    
    Returns:
        str: Path to the generated .apkg file
    """
    # Read CSV file
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")
    
    # Validate required columns
    if 'Front' not in df.columns or 'Back' not in df.columns:
        raise ValueError("CSV file must contain 'Front' and 'Back' columns")
    
    # Create deck name if not provided
    if deck_name is None:
        deck_name = Path(csv_file).stem
    
    # Create output file path if not provided
    if output_file is None:
        output_file = Path(csv_file).with_suffix('.apkg')
    
    # Create model and deck
    model = create_basic_model()
    deck = genanki.Deck(
        deck_id=generate_deck_id(),
        name=deck_name
    )
    
    # Process each row and create notes
    notes_created = 0
    for index, row in df.iterrows():
        try:
            # Clean the content
            front_content = clean_html_content(row['Front'])
            back_content = clean_html_content(row['Back'])
            
            # Skip empty rows
            if not front_content or not back_content:
                print(f"Warning: Skipping row {index + 1} due to empty content")
                continue
            
            # Create note
            note = genanki.Note(
                model=model,
                fields=[front_content, back_content]
            )
            
            deck.add_note(note)
            notes_created += 1
            
        except Exception as e:
            print(f"Warning: Error processing row {index + 1}: {e}")
            continue
    
    if notes_created == 0:
        raise ValueError("No valid notes were created from the CSV file")
    
    # Create package and write to file
    package = genanki.Package(deck)
    package.write_to_file(str(output_file))
    
    print(f"Successfully created Anki deck: {output_file}")
    print(f"Notes created: {notes_created}")
    
    return str(output_file)


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description='Convert CSV files to Anki deck packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python csv_to_anki.py test.csv
  python csv_to_anki.py test.csv --deck-name "My Study Deck"
  python csv_to_anki.py test.csv --output my_deck.apkg
  python csv_to_anki.py test.csv --deck-name "German Vocabulary" --output german.apkg

CSV Format:
  The CSV file should have columns named 'Front' and 'Back'.
  HTML formatting is supported in both columns.
  
  Example CSV:
    Front,Back
    "What is the capital of France?","Paris"
    "What is 2+2?","4"
        """
    )
    
    parser.add_argument(
        'csv_file',
        help='Path to the CSV file to convert'
    )
    
    parser.add_argument(
        '--deck-name', '-n',
        help='Name of the Anki deck (default: CSV filename)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output .apkg file path (default: CSV filename with .apkg extension)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file '{args.csv_file}' not found")
        sys.exit(1)
    
    try:
        output_file = csv_to_anki_deck(
            csv_file=args.csv_file,
            deck_name=args.deck_name,
            output_file=args.output
        )
        
        if args.verbose:
            print(f"Input file: {args.csv_file}")
            print(f"Output file: {output_file}")
            print(f"Deck name: {args.deck_name or Path(args.csv_file).stem}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
