"""
Tests for hf-trainer-nbconvert package
"""

import unittest
import tempfile
import json
from pathlib import Path

from hf_trainer_nbconvert.enhanced_converter import (
    enhanced_clean_notebook,
    extract_widget_training_data,
    format_training_data
)


class TestHFTrainerConverter(unittest.TestCase):
    """Test cases for HF Trainer Converter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": "print('Hello World')",
                    "outputs": [
                        {
                            "output_type": "stream",
                            "name": "stdout",
                            "text": ["Hello World\n"]
                        }
                    ]
                },
                {
                    "cell_type": "code", 
                    "source": "trainer.train()",
                    "outputs": [
                        {
                            "output_type": "display_data",
                            "data": {
                                "application/vnd.jupyter.widget-view+json": {},
                                "text/plain": ["Training: 100%|██████████| 100/100 [00:30<00:00,  3.33it/s]"]
                            }
                        }
                    ]
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }
    
    def test_extract_widget_training_data(self):
        """Test extraction of training data from widgets."""
        outputs = self.test_notebook_content["cells"][1]["outputs"]
        training_data = extract_widget_training_data(outputs)
        
        self.assertIsInstance(training_data, list)
        self.assertTrue(any("Training:" in line for line in training_data))
    
    def test_format_training_data(self):
        """Test formatting of training data."""
        training_lines = ["Training: 100%|██████████| 100/100 [00:30<00:00,  3.33it/s]"]
        formatted = format_training_data(training_lines)
        
        self.assertIsInstance(formatted, str)
        self.assertIn("HUGGING FACE TRAINER PROGRESS", formatted)
    
    def test_enhanced_clean_notebook(self):
        """Test notebook cleaning functionality."""
        # Create temporary notebook file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ipynb', delete=False) as f:
            json.dump(self.test_notebook_content, f)
            temp_path = f.name
        
        try:
            # Test cleaning
            cleaned_path = enhanced_clean_notebook(temp_path)
            self.assertTrue(Path(cleaned_path).exists())
            
            # Verify cleaned notebook
            with open(cleaned_path, 'r') as f:
                cleaned_data = json.load(f)
            
            self.assertEqual(len(cleaned_data['cells']), 2)
            
            # Clean up
            Path(cleaned_path).unlink()
            
        finally:
            # Clean up temp file
            Path(temp_path).unlink()


if __name__ == '__main__':
    unittest.main()
