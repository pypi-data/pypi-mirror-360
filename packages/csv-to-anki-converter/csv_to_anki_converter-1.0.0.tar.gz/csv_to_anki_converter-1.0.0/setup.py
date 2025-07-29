"""
Setup script for CSV to Anki Converter package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read the requirements
requirements = (this_directory / "requirements.txt").read_text().strip().split('\n')

setup(
    name="csv-to-anki-converter",
    version="1.0.0",
    author="CSV to Anki Converter Team",
    author_email="support@example.com",
    description="Convert CSV files to Anki deck packages with ease",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/csv-to-anki-converter",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/csv-to-anki-converter/issues",
        "Source": "https://github.com/yourusername/csv-to-anki-converter",
        "Documentation": "https://github.com/yourusername/csv-to-anki-converter#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Education",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ]
    },
    entry_points={
        "console_scripts": [
            "csv-to-anki=csv_to_anki_converter.cli:main",
        ],
    },
    keywords="anki flashcards csv converter education study",
    include_package_data=True,
    zip_safe=False,
)
