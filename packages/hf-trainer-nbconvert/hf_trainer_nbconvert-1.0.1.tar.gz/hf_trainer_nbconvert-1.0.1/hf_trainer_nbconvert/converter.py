"""
Hugging Face Trainer Notebook Converter

A specialized Python module for converting Jupyter notebooks that use the Hugging Face 
Trainer API to various formats while preserving training progress visualization and 
trainer-specific elements.

Author: K N S Sri Harshith
License: MIT
"""

import json
import re
import os
import argparse
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import nbformat
from nbconvert import HTMLExporter, MarkdownExporter, PythonExporter
from nbconvert.preprocessors import Preprocessor
from nbconvert.writers import FilesWriter
import matplotlib.pyplot as plt
from io import StringIO
import base64


class HuggingFaceTrainerPreprocessor(Preprocessor):
    """
    Custom preprocessor to handle Hugging Face Trainer API specific content
    and enhance training progress visualization.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.trainer_cells = []
        self.training_logs = []
        
    def preprocess_cell(self, cell, resources, index):
        """Process each cell to identify and enhance Trainer-related content."""
        
        if cell.cell_type == 'code':
            source = cell.source
            
            # Detect Trainer instantiation
            if self._is_trainer_cell(source):
                cell = self._enhance_trainer_cell(cell, index)
                self.trainer_cells.append(index)
            
            # Detect training execution
            elif self._is_training_cell(source):
                cell = self._enhance_training_cell(cell, index)
            
            # Detect training log visualization
            elif self._is_training_viz_cell(source):
                cell = self._enhance_training_viz_cell(cell, index)
        
        return cell, resources
    
    def _is_trainer_cell(self, source: str) -> bool:
        """Check if cell contains Trainer instantiation."""
        patterns = [
            r'Trainer\s*\(',                             # Trainer(...)
            r'trainer\s*=\s*Trainer',                    # trainer = Trainer
            r'from\s+transformers\s+import.*Trainer',    # from transformers import ... Trainer
            r'AutoModel.*For.*Classification',           # AutoModelForSequenceClassification, etc.
            r'AutoModelFor.*',                           # Any AutoModel variant
            r'TrainingArguments\s*\(',                   # TrainingArguments(...)
            r'training_args\s*=',                        # training_args = ...
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in patterns)
    
    def _is_training_cell(self, source: str) -> bool:
        """Check if cell contains training execution."""
        patterns = [
            r'trainer\.train\(\)',                        # trainer.train()
            r'\.train\(\)',                               # any_object.train()
            r'training_.*=.*\.train\(\)',                 # training_var = obj.train()
            r'train_result\s*=.*\.train\(\)',             # train_result = obj.train()
            r'.*\.fit\(',                                 # model.fit(...)
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in patterns)
    
    def _is_training_viz_cell(self, source: str) -> bool:
        """Check if cell contains training visualization."""
        patterns = [
            r'plt\.plot.*loss',                           # plt.plot(...loss)
            r'matplotlib.*training',                      # matplotlib + training
            r'plot.*training.*loss',                      # plot training loss
            r'visualize.*training',                       # visualize training
            r'trainer\.state\.log_history',               # trainer.state.log_history
            r'plt\.figure',                               # plt.figure
            r'plt\.subplot',                              # plt.subplot
            r'eval.*metrics',                             # evaluation metrics
            r'f1.*score',                                 # F1 score
            r'accuracy.*loss',                            # accuracy and loss
        ]
        return any(re.search(pattern, source, re.IGNORECASE) for pattern in patterns)
    
    def _enhance_trainer_cell(self, cell, index: int):
        """Enhance Trainer instantiation cell with additional documentation."""
        # Detect what type of model is being used
        model_type = "Transformer"
        if re.search(r'AutoModelForSequenceClassification', cell.source, re.IGNORECASE):
            model_type = "Sequence Classification"
        elif re.search(r'AutoModelForTokenClassification', cell.source, re.IGNORECASE):
            model_type = "Token Classification (NER)"
        elif re.search(r'AutoModelForQuestionAnswering', cell.source, re.IGNORECASE):
            model_type = "Question Answering"
        elif re.search(r'AutoModelForMaskedLM', cell.source, re.IGNORECASE):
            model_type = "Masked Language Modeling"
        elif re.search(r'AutoModelForCausalLM', cell.source, re.IGNORECASE):
            model_type = "Causal Language Modeling"
        
        # Add intelligent documentation based on the detected model type
        enhanced_source = cell.source + '\n\n# Enhanced Training Configuration\n'
        enhanced_source += f'# This cell initializes the HuggingFace Trainer for {model_type} with these components:\n'
        enhanced_source += '# - Model: The transformer model architecture\n'
        enhanced_source += '# - Training Arguments: Configuration for training hyperparameters\n'
        enhanced_source += '# - Dataset: Training and evaluation datasets\n'
        
        # Add specific notes based on model type
        if model_type == "Sequence Classification":
            enhanced_source += '# - Classification-specific metrics: Accuracy, F1, etc.\n'
        elif model_type == "Token Classification (NER)":
            enhanced_source += '# - Token-level metrics: Precision, Recall, F1 per entity type\n'
        elif model_type == "Question Answering":
            enhanced_source += '# - QA metrics: Exact Match, F1 overlap\n'
        
        cell.source = enhanced_source
        return cell
    
    def _enhance_training_cell(self, cell, index: int):
        """Enhance training execution cell with progress tracking."""
        enhanced_source = '# Training Progress Tracking\n'
        enhanced_source += 'import time\n'
        enhanced_source += 'from IPython.display import display, clear_output\n'
        enhanced_source += 'import matplotlib.pyplot as plt\n\n'
        
        enhanced_source += cell.source + '\n\n'
        
        enhanced_source += '''
# Enhanced universal training visualization
if 'trainer' in locals() and hasattr(trainer, 'state') and hasattr(trainer.state, 'log_history'):
    logs = trainer.state.log_history
    
    # Extract all metrics
    metrics = {}
    steps = []
    
    for log in logs:
        step = log.get('step', None)
        if step is not None:
            if step not in steps:
                steps.append(step)
            
            # Collect all metrics at this step
            for key, value in log.items():
                if key != 'step' and key != 'epoch':
                    if key not in metrics:
                        metrics[key] = []
                    
                    # Ensure the metrics list is aligned with steps
                    while len(metrics[key]) < len(steps) - 1:
                        metrics[key].append(None)
                    
                    metrics[key].append(value)
    
    # Plot available metrics
    if metrics and steps:
        num_metrics = len(metrics)
        if num_metrics > 0:
            # Determine layout
            cols = min(2, num_metrics)
            rows = (num_metrics + cols - 1) // cols
            
            plt.figure(figsize=(7*cols, 5*rows))
            
            for i, (metric_name, values) in enumerate(metrics.items()):
                if values:  # Skip empty metrics
                    plt.subplot(rows, cols, i+1)
                    
                    # Filter out None values
                    valid_indices = [i for i, v in enumerate(values) if v is not None]
                    valid_steps = [steps[i] for i in valid_indices]
                    valid_values = [values[i] for i in valid_indices]
                    
                    if valid_steps and valid_values:
                        plt.plot(valid_steps, valid_values, 'o-', linewidth=2)
                        plt.xlabel('Steps')
                        plt.ylabel(metric_name.replace('_', ' ').title())
                        plt.title(f'{metric_name.replace("_", " ").title()} vs Steps')
                        plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # Print summary
            print("\\n📊 Training Summary:")
            print("=" * 40)
            
            for metric_name, values in metrics.items():
                valid_values = [v for v in values if v is not None]
                if valid_values:
                    print(f"{metric_name.replace('_', ' ').title()}:")
                    print(f"  Initial: {valid_values[0]:.4f}")
                    print(f"  Final: {valid_values[-1]:.4f}")
                    
                    if metric_name == 'loss' or metric_name == 'train_loss':
                        improvement = valid_values[0] - valid_values[-1]
                        print(f"  Improvement: {improvement:.4f} ({improvement/valid_values[0]*100:.2f}%)")
                    
                    print("-" * 40)
            
            print(f"Total steps: {steps[-1]}")
'''
        
        cell.source = enhanced_source
        return cell
    
    def _enhance_training_viz_cell(self, cell, index: int):
        """Enhance training visualization cell with better formatting."""
        enhanced_source = '# Enhanced Training Visualization\n'
        enhanced_source += cell.source + '\n\n'
        enhanced_source += '''
# Apply professional styling to the visualization
try:
    plt.style.use('seaborn-v0_8')  # Modern, clean style
except:
    try:
        plt.style.use('seaborn')  # Fallback for older matplotlib versions
    except:
        pass  # Default style if seaborn style not available

# Improve plot aesthetics
for fig in [plt.gcf()] if plt.get_fignums() else []:
    for ax in fig.axes:
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Enhance legend if it exists
        if ax.get_legend():
            ax.legend(frameon=True, facecolor='white', framealpha=0.9, 
                     edgecolor='lightgray')
        
        # Improve title and label visibility
        for text in [ax.title, ax.xaxis.label, ax.yaxis.label]:
            if text:
                text.set_fontweight('bold')
    
    # Ensure layout is optimized
    fig.tight_layout()

# Add training summary if metrics are available in the namespace
training_metrics = {}
for var_name in dir():
    if not var_name.startswith('_'):  # Skip private variables
        var = locals()[var_name]
        
        # Look for common metric variable names
        if any(metric_type in var_name.lower() for metric_type in 
              ['loss', 'accuracy', 'f1', 'precision', 'recall', 'score', 'metric']):
            if isinstance(var, (list, tuple, np.ndarray)) and len(var) > 0:
                # Store the metric if it's a sequence type
                training_metrics[var_name] = var

# Print summary of found metrics
if training_metrics:
    print("\\n" + "="*50)
    print("TRAINING VISUALIZATION SUMMARY")
    print("="*50)
    
    for metric_name, values in training_metrics.items():
        if isinstance(values, (list, tuple, np.ndarray)) and len(values) > 0:
            # Only process numeric values
            try:
                values = [float(v) for v in values]
                print(f"{metric_name}:")
                print(f"  Initial: {values[0]:.4f}")
                print(f"  Final: {values[-1]:.4f}")
                
                if 'loss' in metric_name.lower():
                    # For loss, lower is better
                    change = values[0] - values[-1]
                    relative = abs(change/values[0]*100) if values[0] != 0 else 0
                    print(f"  Change: {change:.4f} ({relative:.2f}%)")
                elif any(term in metric_name.lower() for term in ['acc', 'f1', 'precision', 'recall', 'score']):
                    # For these metrics, higher is better
                    change = values[-1] - values[0]
                    relative = (change/values[0]*100) if values[0] != 0 else 0
                    print(f"  Improvement: {change:.4f} ({relative:.2f}%)")
                
                print("-"*40)
            except (ValueError, TypeError):
                # Skip if not numeric
                pass
    
    print("="*50)
'''
        
        cell.source = enhanced_source
        return cell


class HuggingFaceTrainerConverter:
    """
    Main converter class for Hugging Face Trainer notebooks.
    """
    
    def __init__(self, input_path: Union[str, Path]):
        """
        Initialize the converter.
        
        Args:
            input_path: Path to the input .ipynb file
        """
        self.input_path = Path(input_path)
        self.notebook = None
        self.preprocessor = HuggingFaceTrainerPreprocessor()
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Notebook file not found: {self.input_path}")
        
        self._load_notebook()
    
    def _load_notebook(self):
        """Load the Jupyter notebook."""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                self.notebook = nbformat.read(f, as_version=4)
        except Exception as e:
            raise ValueError(f"Error loading notebook: {e}")
    
    def convert_to_python(self, output_path: Optional[Union[str, Path]] = None, 
                         enhance_trainer: bool = True) -> str:
        """
        Convert notebook to Python script with enhanced Trainer handling.
        
        Args:
            output_path: Output file path (optional)
            enhance_trainer: Whether to enhance Trainer-related cells
            
        Returns:
            Python code as string
        """
        exporter = PythonExporter()
        
        if enhance_trainer:
            exporter.register_preprocessor(self.preprocessor, enabled=True)
        
        (body, resources) = exporter.from_notebook_node(self.notebook)
        
        # Add header comment
        header = f'''#!/usr/bin/env python3
"""
Converted from Jupyter Notebook: {self.input_path.name}
Enhanced for Hugging Face Trainer API visualization

This script includes enhanced training progress tracking and visualization
for better monitoring of the fine-tuning process.
"""

'''
        
        body = header + body
        
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(body)
            print(f"Python script saved to: {output_path}")
        
        return body
    
    def convert_to_html(self, output_path: Optional[Union[str, Path]] = None, 
                       enhance_trainer: bool = True) -> str:
        """
        Convert notebook to HTML with enhanced Trainer visualization.
        
        Args:
            output_path: Output file path (optional)
            enhance_trainer: Whether to enhance Trainer-related cells
            
        Returns:
            HTML content as string
        """
        exporter = HTMLExporter()
        exporter.template_name = 'lab'  # Use modern template
        
        if enhance_trainer:
            exporter.register_preprocessor(self.preprocessor, enabled=True)
        
        (body, resources) = exporter.from_notebook_node(self.notebook)
        
        # Enhance HTML with custom CSS for trainer visualization
        custom_css = '''
        <style>
        .trainer-cell {
            border-left: 4px solid #ff6b6b;
            padding-left: 10px;
            background-color: #fff5f5;
        }
        .training-progress {
            border-left: 4px solid #4ecdc4;
            padding-left: 10px;
            background-color: #f0fffe;
        }
        .training-summary {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
            margin: 10px 0;
        }
        </style>
        '''
        
        # Insert custom CSS
        body = body.replace('<head>', f'<head>{custom_css}')
        
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(body)
            print(f"HTML file saved to: {output_path}")
        
        return body
    
    def convert_to_markdown(self, output_path: Optional[Union[str, Path]] = None,
                          enhance_trainer: bool = True) -> str:
        """
        Convert notebook to Markdown with enhanced documentation.
        
        Args:
            output_path: Output file path (optional)
            enhance_trainer: Whether to enhance Trainer-related cells
            
        Returns:
            Markdown content as string
        """
        exporter = MarkdownExporter()
        
        if enhance_trainer:
            exporter.register_preprocessor(self.preprocessor, enabled=True)
        
        (body, resources) = exporter.from_notebook_node(self.notebook)
        
        # Add front matter
        front_matter = f'''# {self.input_path.stem}

**Converted from Jupyter Notebook with Hugging Face Trainer Enhancement**

This document includes enhanced visualization and documentation for the Hugging Face Trainer API usage.

---

'''
        
        body = front_matter + body
        
        if output_path:
            output_path = Path(output_path)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(body)
            print(f"Markdown file saved to: {output_path}")
        
        return body
    
    def analyze_trainer_usage(self):
        """
        Analyze the notebook for Trainer API usage and return detailed information.
        
        Returns:
            dict: Dictionary containing analysis results with keys:
                - trainer_cells: List of cell indices with Trainer instantiation
                - training_cells: List of cell indices with training execution
                - visualization_cells: List of cell indices with training visualization
                - model_types: List of detected model types
                - metrics: List of detected evaluation metrics
        """
        if not self.notebook:
            self._load_notebook()
        
        # Process the notebook to gather analysis
        trainer_cells = []
        training_cells = []
        visualization_cells = []
        model_types = set()
        metrics = set()
        
        for i, cell in enumerate(self.notebook.cells):
            if cell.cell_type == 'code':
                source = cell.source
                
                # Check for Trainer cells
                if self.preprocessor._is_trainer_cell(source):
                    trainer_cells.append(i)
                    
                    # Detect model types
                    if re.search(r'AutoModelForSequenceClassification', source, re.IGNORECASE):
                        model_types.add('SequenceClassification')
                    elif re.search(r'AutoModelForTokenClassification', source, re.IGNORECASE):
                        model_types.add('TokenClassification')
                    elif re.search(r'AutoModelForQuestionAnswering', source, re.IGNORECASE):
                        model_types.add('QuestionAnswering')
                    elif re.search(r'AutoModelForMaskedLM', source, re.IGNORECASE):
                        model_types.add('MaskedLM')
                    elif re.search(r'AutoModelForCausalLM', source, re.IGNORECASE):
                        model_types.add('CausalLM')
                    elif re.search(r'AutoModelFor', source, re.IGNORECASE):
                        model_types.add('OtherAutoModel')
                    elif re.search(r'Trainer', source, re.IGNORECASE):
                        model_types.add('GenericTrainer')
                
                # Check for training cells
                if self.preprocessor._is_training_cell(source):
                    training_cells.append(i)
                
                # Check for visualization cells
                if self.preprocessor._is_training_viz_cell(source):
                    visualization_cells.append(i)
                
                # Detect evaluation metrics
                if re.search(r'accuracy|precision|recall|f1|roc|auc', source, re.IGNORECASE):
                    for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc', 'auc']:
                        if re.search(metric, source, re.IGNORECASE):
                            metrics.add(metric)
        
        return {
            'trainer_cells': trainer_cells,
            'training_cells': training_cells,
            'visualization_cells': visualization_cells,
            'model_types': list(model_types),
            'metrics': list(metrics)
        }
    
    def generate_training_report(self):
        """
        Generate a comprehensive markdown report about the training in the notebook.
        
        Returns:
            str: Markdown formatted report
        """
        analysis = self.analyze_trainer_usage()
        
        report = [
            "# HuggingFace Trainer Analysis Report\n",
            f"## Notebook: {self.input_path.name}\n",
            "## Overview\n",
            f"- **Model Types**: {', '.join(analysis['model_types']) if analysis['model_types'] else 'None detected'}\n",
            f"- **Metrics Used**: {', '.join(analysis['metrics']) if analysis['metrics'] else 'None detected'}\n",
            f"- **Trainer Cells**: {len(analysis['trainer_cells'])}\n",
            f"- **Training Cells**: {len(analysis['training_cells'])}\n",
            f"- **Visualization Cells**: {len(analysis['visualization_cells'])}\n\n"
        ]
        
        # Add detailed cell information
        if analysis['trainer_cells']:
            report.append("## Trainer Setup\n")
            for idx in analysis['trainer_cells']:
                cell = self.notebook.cells[idx]
                # Extract key info from the cell
                summary = self._summarize_code_cell(cell.source)
                report.append(f"### Cell {idx+1}\n")
                report.append(f"```python\n{summary}\n```\n\n")
        
        if analysis['training_cells']:
            report.append("## Training Execution\n")
            for idx in analysis['training_cells']:
                cell = self.notebook.cells[idx]
                # Extract key info from the cell
                summary = self._summarize_code_cell(cell.source)
                report.append(f"### Cell {idx+1}\n")
                report.append(f"```python\n{summary}\n```\n\n")
        
        if analysis['visualization_cells']:
            report.append("## Training Visualization\n")
            for idx in analysis['visualization_cells']:
                cell = self.notebook.cells[idx]
                # Extract key info from the cell
                summary = self._summarize_code_cell(cell.source)
                report.append(f"### Cell {idx+1}\n")
                report.append(f"```python\n{summary}\n```\n\n")
        
        return ''.join(report)
    
    def _summarize_code_cell(self, code, max_lines=10):
        """
        Create a concise summary of a code cell, focusing on key elements.
        
        Args:
            code: The source code to summarize
            max_lines: Maximum number of lines to include
            
        Returns:
            str: Summarized code
        """
        lines = code.split('\n')
        
        # If code is already short, return it as is
        if len(lines) <= max_lines:
            return code
        
        # Focus on key parts - imports, function/class definitions, and trainer related lines
        key_lines = []
        for line in lines:
            stripped = line.strip()
            # Keep imports, function/class definitions, and trainer-related code
            if (stripped.startswith('import ') or 
                stripped.startswith('from ') or
                stripped.startswith('def ') or
                stripped.startswith('class ') or
                'trainer' in stripped.lower() or
                'model' in stripped.lower() or
                '.train(' in stripped or
                'plt.' in stripped):
                key_lines.append(line)
        
        # If we found some key lines, return them
        if len(key_lines) > 0:
            # But don't exceed max lines
            if len(key_lines) > max_lines:
                return '\n'.join(key_lines[:max_lines-1] + ['# ... more code ...'])
            return '\n'.join(key_lines)
        
        # Otherwise return first few and last few lines
        half = max_lines // 2
        return '\n'.join(lines[:half] + ['# ... more code ...'] + lines[-half:])
