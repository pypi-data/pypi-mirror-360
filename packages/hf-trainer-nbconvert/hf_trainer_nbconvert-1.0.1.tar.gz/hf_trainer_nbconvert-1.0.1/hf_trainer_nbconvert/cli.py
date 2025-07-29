#!/usr/bin/env python3
"""
Command-line interface for HuggingFace Trainer Notebook Converter
"""

import argparse
import sys
from pathlib import Path

from .enhanced_converter import (
    enhanced_clean_notebook,
    convert_to_html_with_standard_styling
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert HuggingFace Trainer notebooks to HTML with preserved training data",
        prog="hf-trainer-nbconvert"
    )
    
    parser.add_argument(
        "notebook",
        help="Input Jupyter notebook file (.ipynb)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output HTML file path (default: notebook_name_converted.html)"
    )
    
    parser.add_argument(
        "--keep-cleaned",
        action="store_true",
        help="Keep the cleaned intermediate notebook file (not recommended)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"❌ Error: Notebook file not found: {notebook_path}")
        sys.exit(1)
    
    if not notebook_path.suffix.lower() == '.ipynb':
        print(f"❌ Error: Input file must be a Jupyter notebook (.ipynb)")
        sys.exit(1)
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = notebook_path.parent / f"{notebook_path.stem}_converted.html"
    
    try:
        print(f"🎯 Converting: {notebook_path.name}")
        
        # Step 1: Clean notebook and extract training data (using temporary file)
        cleaned_notebook = enhanced_clean_notebook(notebook_path)
        
        # Step 2: Convert to HTML
        html_output = convert_to_html_with_standard_styling(
            cleaned_notebook, 
            output_path
        )
        
        # Step 3: Always cleanup intermediate files
        if not args.keep_cleaned and cleaned_notebook.exists():
            try:
                cleaned_notebook.unlink()
                print(f"🗑️  Cleaned up temporary file")
            except Exception as e:
                print(f"⚠️  Note: Could not clean up temporary file: {e}")
        
        if html_output:
            print(f"\n🎉 Conversion successful!")
            print(f"📄 Input: {notebook_path.name}")
            print(f"🌐 Output: {Path(html_output).name}")
            print(f"🎨 Styling: Standard Jupyter appearance")
            print(f"📊 Training data: Extracted and preserved")
        else:
            print(f"❌ Conversion failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
