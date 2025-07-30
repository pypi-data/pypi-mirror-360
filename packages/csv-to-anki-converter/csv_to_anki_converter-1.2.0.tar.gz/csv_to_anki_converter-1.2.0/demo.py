#!/usr/bin/env python3
"""
Demo script to show both CSV to Anki converters in action
"""

import os
import subprocess
import sys

def main():
    print("=== CSV to Anki Converter Demo ===")
    print()
    
    # Check if required files exist
    if not os.path.exists('examples/test.csv'):
        print("Error: examples/test.csv not found")
        sys.exit(1)
    
    print("1. Testing Command Line Version (csv_to_anki.py)")
    print("   Converting examples/test.csv with custom name...")
    
    # Test command line version
    result = subprocess.run([
        sys.executable, 'csv_to_anki.py', 'examples/test.csv',
        '--deck-name', 'Demo Finance Deck',
        '--output', 'demo_finance.apkg',
        '--verbose'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✓ Success!")
        print(f"   Output: {result.stdout.strip()}")
    else:
        print("   ✗ Failed!")
        print(f"   Error: {result.stderr.strip()}")
    
    print()
    print("2. Testing Automatic Batch Converter (auto_csv_to_anki.py)")
    print("   Converting all CSV files automatically...")
    
    # Test automatic converter (default behavior)
    result = subprocess.run([
        sys.executable, 'auto_csv_to_anki.py'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✓ Success!")
        print("   Output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("   ✗ Failed!")
        print(f"   Error: {result.stderr.strip()}")
    
    print()
    print("3. Testing Automatic Batch Converter with Custom Directories")
    print("   Converting CSV files from examples/ to output/...")
    
    # Test automatic converter with custom directories
    result = subprocess.run([
        sys.executable, 'auto_csv_to_anki.py',
        '--input-dir', 'examples',
        '--output-dir', 'output'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✓ Success!")
        print("   Output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("   ✗ Failed!")
        print(f"   Error: {result.stderr.strip()}")
    
    print()
    print("Demo completed!")
    print("Check the generated .apkg files in the current directory and output/ directory.")

if __name__ == '__main__':
    main()
