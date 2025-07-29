"""
Basic tests for CSV to Anki converter package.
"""

import tempfile
import pytest
from pathlib import Path
import csv

from csv_to_anki_converter import csv_to_anki_deck, convert_directory


def create_test_csv(content, filepath):
    """Helper function to create a test CSV file."""
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in content:
            writer.writerow(row)


def test_csv_to_anki_deck_basic():
    """Test basic CSV to Anki deck conversion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test CSV
        csv_file = Path(temp_dir) / "test.csv"
        test_data = [
            ["Front", "Back"],
            ["What is Python?", "A programming language"],
            ["What is 2+2?", "4"]
        ]
        create_test_csv(test_data, csv_file)
        
        # Convert to Anki deck
        output_file = csv_to_anki_deck(str(csv_file))
        
        # Check that output file exists
        assert Path(output_file).exists()
        assert Path(output_file).suffix == ".apkg"


def test_csv_to_anki_deck_custom_names():
    """Test CSV to Anki deck conversion with custom names."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test CSV
        csv_file = Path(temp_dir) / "test.csv"
        test_data = [
            ["Front", "Back"],
            ["Hello", "Hola"],
            ["Goodbye", "Adiós"]
        ]
        create_test_csv(test_data, csv_file)
        
        # Convert with custom names
        output_file = Path(temp_dir) / "custom_deck.apkg"
        result = csv_to_anki_deck(
            str(csv_file), 
            deck_name="Custom Deck",
            output_file=str(output_file)
        )
        
        assert Path(result).exists()
        assert Path(result).name == "custom_deck.apkg"


def test_csv_to_anki_deck_invalid_csv():
    """Test CSV to Anki deck conversion with invalid CSV."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create invalid CSV (missing required columns)
        csv_file = Path(temp_dir) / "invalid.csv"
        test_data = [
            ["Question", "Answer"],
            ["What is Python?", "A programming language"]
        ]
        create_test_csv(test_data, csv_file)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="must contain 'Front' and 'Back' columns"):
            csv_to_anki_deck(str(csv_file))


def test_convert_directory():
    """Test directory batch conversion."""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = Path(temp_dir) / "input"
        output_dir = Path(temp_dir) / "output"
        input_dir.mkdir()
        output_dir.mkdir()
        
        # Create multiple test CSV files
        for i, name in enumerate(["vocab", "math"]):
            csv_file = input_dir / f"{name}.csv"
            test_data = [
                ["Front", "Back"],
                [f"Question {i+1}", f"Answer {i+1}"],
                [f"Question {i+2}", f"Answer {i+2}"]
            ]
            create_test_csv(test_data, csv_file)
        
        # Convert directory
        result = convert_directory(str(input_dir), str(output_dir))
        
        assert result['total_files'] == 2
        assert result['successful_conversions'] == 2
        assert result['failed_conversions'] == 0
        
        # Check output files exist
        assert (output_dir / "vocab.apkg").exists()
        assert (output_dir / "math.apkg").exists()


def test_package_import():
    """Test that the package can be imported correctly."""
    import csv_to_anki_converter
    
    assert hasattr(csv_to_anki_converter, 'csv_to_anki_deck')
    assert hasattr(csv_to_anki_converter, 'convert_directory')
    assert hasattr(csv_to_anki_converter, '__version__')
    assert csv_to_anki_converter.__version__ == "1.0.0"
