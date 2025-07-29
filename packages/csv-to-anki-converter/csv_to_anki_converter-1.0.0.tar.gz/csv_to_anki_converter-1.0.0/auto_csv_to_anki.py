#!/usr/bin/env python3
"""
Automatic CSV to Anki Deck Converter

This script automatically converts all CSV files in a specified input directory to Anki deck packages.
The deck names and output file names are automatically derived from the CSV file names.
Supports custom input and output directories.

This is a standalone script that can be used without installing the package.
For the installed package version, use: csv-to-anki --batch

Usage:
    python auto_csv_to_anki.py [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]

Features:
- Automatically finds all .csv files in the input directory
- Creates .apkg files with the same base name as the CSV files
- Deck names are set to the CSV file name (without extension)
- Skips files that don't have the required 'Front' and 'Back' columns
- Provides summary of conversion results
- Supports custom input and output directories
"""

import os
import sys
import argparse
import random
import pandas as pd
import genanki
from pathlib import Path
import glob

# Try to import from package if available, otherwise use local functions
try:
    from csv_to_anki_converter import convert_directory
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


def convert_single_csv(csv_file, output_dir):
    """
    Convert a single CSV file to an Anki deck package.
    
    Args:
        csv_file (str): Path to the CSV file
        output_dir (str): Directory to save the .apkg file
    
    Returns:
        dict: Result dictionary with success status and details
    """
    result = {
        'file': csv_file,
        'success': False,
        'output_file': None,
        'notes_created': 0,
        'error': None
    }
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        if 'Front' not in df.columns or 'Back' not in df.columns:
            result['error'] = "Missing 'Front' or 'Back' columns"
            return result
        
        # Create deck name and output file path
        deck_name = Path(csv_file).stem
        output_file = Path(output_dir) / f"{deck_name}.apkg"
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
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
                    continue
                
                # Create note
                note = genanki.Note(
                    model=model,
                    fields=[front_content, back_content]
                )
                
                deck.add_note(note)
                notes_created += 1
                
            except Exception as e:
                continue
        
        if notes_created == 0:
            result['error'] = "No valid notes could be created"
            return result
        
        # Create package and write to file
        package = genanki.Package(deck)
        package.write_to_file(str(output_file))
        
        result['success'] = True
        result['output_file'] = str(output_file)
        result['notes_created'] = notes_created
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def find_csv_files(input_dir):
    """Find all CSV files in the specified directory."""
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input directory '{input_dir}' does not exist")
    
    csv_files = list(input_path.glob("*.csv"))
    return sorted([str(f) for f in csv_files])


def main():
    """Main function for automatic CSV to Anki conversion."""
    parser = argparse.ArgumentParser(
        description='Automatically convert CSV files to Anki deck packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_csv_to_anki.py
  python auto_csv_to_anki.py --input-dir ./csv_files
  python auto_csv_to_anki.py --output-dir ./anki_decks
  python auto_csv_to_anki.py --input-dir ./csv_files --output-dir ./anki_decks

CSV Format:
  Each CSV file should have columns named 'Front' and 'Back'.
  HTML formatting is supported in both columns.
        """
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        default='.',
        help='Directory to search for CSV files (default: current directory)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='.',
        help='Directory to save .apkg files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    print("=== Automatic CSV to Anki Converter ===")
    print(f"Input directory: {os.path.abspath(args.input_dir)}")
    print(f"Output directory: {os.path.abspath(args.output_dir)}")
    print()
    
    # Find all CSV files
    try:
        csv_files = find_csv_files(args.input_dir)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    if not csv_files:
        print(f"No CSV files found in '{args.input_dir}'.")
        print("Please ensure you have CSV files with 'Front' and 'Back' columns.")
        sys.exit(0)
    
    print(f"Found {len(csv_files)} CSV file(s):")
    for file in csv_files:
        print(f"  - {Path(file).name}")
    print()
    
    # Convert each CSV file
    results = []
    successful_conversions = 0
    
    for csv_file in csv_files:
        print(f"Converting {Path(csv_file).name}...")
        result = convert_single_csv(csv_file, args.output_dir)
        results.append(result)
        
        if result['success']:
            successful_conversions += 1
            output_name = Path(result['output_file']).name
            print(f"  ✓ Success: Created {output_name} with {result['notes_created']} notes")
        else:
            print(f"  ✗ Failed: {result['error']}")
    
    print()
    print("=== Conversion Summary ===")
    print(f"Input directory: {args.input_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Successful conversions: {successful_conversions}")
    print(f"Failed conversions: {len(csv_files) - successful_conversions}")
    
    if successful_conversions > 0:
        print()
        print("Generated Anki decks:")
        for result in results:
            if result['success']:
                output_name = Path(result['output_file']).name
                print(f"  - {output_name} ({result['notes_created']} notes)")
    
    if len(csv_files) - successful_conversions > 0:
        print()
        print("Failed files:")
        for result in results:
            if not result['success']:
                input_name = Path(result['file']).name
                print(f"  - {input_name}: {result['error']}")
    
    print()
    print("Done! You can now import the .apkg files into Anki.")


if __name__ == '__main__':
    main()
