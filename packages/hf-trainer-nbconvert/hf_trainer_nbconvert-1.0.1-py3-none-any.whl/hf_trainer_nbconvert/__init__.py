"""
HuggingFace Trainer Notebook Converter

A Python package for converting Jupyter notebooks that use HuggingFace Trainer API
to various formats while preserving training progress visualization.

This package ensures that actual training progress (epochs, loss, learning rate, etc.)
is visible in the HTML output, not just static or broken widgets.

Quick usage:
    hf-trainer-nbconvert notebook.ipynb
"""

__version__ = "1.0.0"
__author__ = "K N S Sri Harshith"
__email__ = "knssriharshith@gmail.com"
__description__ = "Convert HuggingFace Trainer notebooks to HTML with preserved training data"

# Import the main conversion functions for API usage
from .enhanced_converter import (
    enhanced_clean_notebook,
    convert_to_html_with_standard_styling,
)

# Simplified API function for direct conversion
def convert_notebook_to_html(notebook_path, output_html_path=None, keep_cleaned=False):
    """
    Convert a HuggingFace Trainer notebook to HTML with preserved training data.
    
    Args:
        notebook_path: Path to the input notebook
        output_html_path: Path for the HTML output (optional)
        keep_cleaned: Whether to keep the intermediate cleaned notebook
    
    Returns:
        Path to the generated HTML file
    """
    from pathlib import Path
    import os
    import tempfile
    
    notebook_path = Path(notebook_path)
    
    # Process the notebook and extract training data
    # If keep_cleaned is True, don't use a temporary file
    if keep_cleaned:
        # Create a permanent cleaned file if the user wants to keep it
        cleaned_notebook_path = notebook_path.parent / f"{notebook_path.stem}_enhanced_clean.ipynb"
        cleaned_notebook = enhanced_clean_notebook(notebook_path, cleaned_notebook_path)
    else:
        # Use a temporary file that will be automatically cleaned up
        cleaned_notebook = enhanced_clean_notebook(notebook_path)
    
    # Convert to HTML
    html_output = convert_to_html_with_standard_styling(
        cleaned_notebook, 
        output_html_path
    )
    
    # Additional cleanup check, in case the automatic cleanup failed
    if not keep_cleaned and cleaned_notebook.exists():
        try:
            cleaned_notebook.unlink()
        except Exception:
            pass
    
    return html_output

# Export the main functions for API usage
__all__ = [
    "convert_notebook_to_html", 
    "enhanced_clean_notebook",
    "convert_to_html_with_standard_styling"
]
