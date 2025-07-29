"""
Command-line interface for CSV to Anki converter.
"""

import argparse
import sys
from pathlib import Path

from .converter import csv_to_anki_deck, convert_directory


def main():
    """Main entry point for the csv-to-anki command."""
    parser = argparse.ArgumentParser(
        description='Convert CSV files to Anki deck packages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  csv-to-anki test.csv
  csv-to-anki test.csv --deck-name "My Study Deck"
  csv-to-anki test.csv --output my_deck.apkg
  csv-to-anki --batch --input-dir ./csv_files --output-dir ./anki_decks

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
        nargs='?',
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
        '--batch', '-b',
        action='store_true',
        help='Batch mode: convert all CSV files in input directory'
    )
    
    parser.add_argument(
        '--input-dir', '-i',
        help='Input directory for batch mode (default: current directory)'
    )
    
    parser.add_argument(
        '--output-dir', '-d',
        help='Output directory for batch mode (default: current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch mode
            input_dir = args.input_dir or '.'
            output_dir = args.output_dir or '.'
            
            if args.verbose:
                print(f"Converting all CSV files from '{input_dir}' to '{output_dir}'")
            
            result = convert_directory(input_dir, output_dir)
            
            print(f"Conversion complete!")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful_conversions']}")
            print(f"Failed: {result['failed_conversions']}")
            
            if args.verbose:
                for res in result['results']:
                    status = "✓" if res['success'] else "✗"
                    print(f"  {status} {Path(res['file']).name}")
                    
        else:
            # Single file mode
            if not args.csv_file:
                print("Error: CSV file is required for single file mode")
                parser.print_help()
                sys.exit(1)
            
            if not Path(args.csv_file).exists():
                print(f"Error: CSV file '{args.csv_file}' not found")
                sys.exit(1)
            
            output_file = csv_to_anki_deck(
                csv_file=args.csv_file,
                deck_name=args.deck_name,
                output_file=args.output
            )
            
            print(f"Successfully created Anki deck: {output_file}")
            
            if args.verbose:
                print(f"Input file: {args.csv_file}")
                print(f"Output file: {output_file}")
                print(f"Deck name: {args.deck_name or Path(args.csv_file).stem}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
