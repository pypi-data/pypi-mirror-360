#!/bin/bash
# Build script for PyPI distribution

set -e

echo "🔧 Building CSV to Anki Converter for PyPI..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade build twine

# Build the package
echo "🏗️ Building package..."
python -m build

# Check the distribution
echo "🔍 Checking distribution..."
python -m twine check dist/*

echo "✅ Build complete!"
echo ""
echo "📁 Distribution files:"
ls -la dist/

echo ""
echo "🚀 To upload to PyPI:"
echo "   Test PyPI: python -m twine upload --repository testpypi dist/*"
echo "   Real PyPI: python -m twine upload dist/*"
