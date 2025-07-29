"""
CSV to Anki Converter Package

A Python package to convert CSV files to Anki deck packages (.apkg files).
"""

__version__ = "1.0.0"
__author__ = "CSV to Anki Converter Team"
__email__ = "support@example.com"
__description__ = "Convert CSV files to Anki deck packages with ease"

from .converter import csv_to_anki_deck, convert_directory
from .models import create_basic_model

__all__ = [
    'csv_to_anki_deck',
    'convert_directory', 
    'create_basic_model',
    '__version__'
]
