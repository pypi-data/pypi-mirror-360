"""
Core converter functions for CSV to Anki conversion.
"""

import os
import random
import pandas as pd
import genanki
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import create_basic_model


def generate_deck_id():
    """Generate a unique deck ID for Anki."""
    return random.randrange(1 << 30, 1 << 31)


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


def csv_to_anki_deck(csv_file: str, deck_name: Optional[str] = None, 
                     output_file: Optional[str] = None) -> str:
    """
    Convert a CSV file to an Anki deck package.
    
    Args:
        csv_file (str): Path to the CSV file
        deck_name (str, optional): Name of the Anki deck
        output_file (str, optional): Output .apkg file path
    
    Returns:
        str: Path to the generated .apkg file
    
    Raises:
        ValueError: If CSV file is invalid or missing required columns
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
        raise ValueError("No valid notes were created from the CSV file")
    
    # Create package and write to file
    package = genanki.Package(deck)
    package.write_to_file(str(output_file))
    
    return str(output_file)


def convert_directory(input_dir: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Convert all CSV files in a directory to Anki deck packages.
    
    Args:
        input_dir (str): Directory containing CSV files
        output_dir (str, optional): Directory to save .apkg files
    
    Returns:
        Dict[str, Any]: Summary of conversion results
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise ValueError(f"Input directory '{input_dir}' does not exist")
    
    if output_dir is None:
        output_dir = input_dir
    
    # Find all CSV files
    csv_files = list(input_path.glob("*.csv"))
    
    if not csv_files:
        return {
            'total_files': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'results': []
        }
    
    # Convert each file
    results = []
    successful_conversions = 0
    
    for csv_file in csv_files:
        try:
            deck_name = csv_file.stem
            output_file = Path(output_dir) / f"{deck_name}.apkg"
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert the file
            result_file = csv_to_anki_deck(
                str(csv_file), 
                deck_name=deck_name, 
                output_file=str(output_file)
            )
            
            # Count notes in the file
            df = pd.read_csv(csv_file)
            notes_count = len(df.dropna(subset=['Front', 'Back']))
            
            results.append({
                'file': str(csv_file),
                'success': True,
                'output_file': result_file,
                'notes_created': notes_count,
                'error': None
            })
            successful_conversions += 1
            
        except Exception as e:
            results.append({
                'file': str(csv_file),
                'success': False,
                'output_file': None,
                'notes_created': 0,
                'error': str(e)
            })
    
    return {
        'total_files': len(csv_files),
        'successful_conversions': successful_conversions,
        'failed_conversions': len(csv_files) - successful_conversions,
        'results': results
    }
