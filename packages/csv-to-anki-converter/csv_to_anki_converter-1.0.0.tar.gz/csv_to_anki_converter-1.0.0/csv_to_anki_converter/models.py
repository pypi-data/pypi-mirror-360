"""
Anki model definitions for CSV to Anki converter.
"""

import genanki


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
