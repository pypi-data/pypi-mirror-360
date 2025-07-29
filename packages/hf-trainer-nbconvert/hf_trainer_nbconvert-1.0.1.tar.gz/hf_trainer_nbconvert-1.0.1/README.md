# 🤗 HuggingFace Trainer Notebook Converter

[![PyPI version](https://badge.fury.io/py/hf-trainer-nbconvert.svg)](https://badge.fury.io/py/hf-trainer-nbconvert)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A specialized Python package for converting Jupyter notebooks that use the HuggingFace Trainer API to HTML while preserving and enhancing training progress visualization.

## 🧹 Clean Conversion Process

This package provides a **clean, direct conversion** with no intermediate files left behind:

- ✅ **Direct Conversion**: Converts directly from .ipynb to HTML in one step
- ✅ **No Residual Files**: All temporary files are automatically cleaned up
- ✅ **Efficient Processing**: Uses memory for intermediate steps where possible
- ✅ **PyPI Ready**: Designed for simple installation via pip

## � Universal Converter Update

The converter works with a wide variety of HuggingFace Trainer API usage patterns:

- ✅ **Multiple Model Types**: Automatically detects and enhances different model architectures (SequenceClassification, TokenClassification, QuestionAnswering, etc.)
- ✅ **Diverse Metrics**: Identifies and visualizes various evaluation metrics (accuracy, F1, precision, recall, etc.)
- ✅ **Flexible Training Patterns**: Works with different training approaches and visualization styles
- ✅ **Enhanced Analysis**: Generates detailed reports about training configurations and results

## 🚀 Quick Start

### Installation

```bash
pip install hf-trainer-nbconvert
```

### Usage

#### Command Line
```bash
# Convert a notebook to HTML (no residual files)
hf-trainer-nbconvert your_notebook.ipynb

# Specify output file
hf-trainer-nbconvert your_notebook.ipynb -o output.html
```

#### Python API
```python
# Simple, direct API (recommended)
from hf_trainer_nbconvert import convert_notebook_to_html

# One-line conversion with automatic cleanup
html_path = convert_notebook_to_html("your_notebook.ipynb")
print(f"HTML saved to: {html_path}")

# Or with custom output path
html_path = convert_notebook_to_html(
    "your_notebook.ipynb", 
    output_html_path="custom_output.html"
)
```

## 🧪 Test Models

The `test_models` directory contains sample notebooks that demonstrate different usages of the HuggingFace Trainer API:

1. **Text Classification**: Simple sentiment analysis with BERT
2. **Named Entity Recognition**: Token classification with CoNLL-2003 dataset

Use these to test the universality of the converter:

```bash
python test_universal_converter.py -a -v
```

## 🎯 Features

- **Smart Trainer Detection**: Automatically identifies cells containing Hugging Face Trainer API usage
- **Enhanced Training Visualization**: Adds improved progress tracking and loss visualization
- **Multiple Output Formats**: Convert to Python, HTML, Markdown with enhanced formatting
- **Training Analysis**: Comprehensive analysis of Trainer usage patterns
- **Progress Enhancement**: Automatically enhances training cells with better progress tracking
- **Custom Styling**: Adds custom CSS for HTML output to highlight training components

## 🚀 Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 📁 Files

- `hf_trainer_nbconvert.py` - Main converter module
- `example_usage.py` - Usage examples and demonstrations
- `requirements.txt` - Required dependencies
- `README.md` - This documentation

## 🔧 Usage

### Python API

```python
from hf_trainer_nbconvert import HuggingFaceTrainerConverter

# Initialize converter
converter = HuggingFaceTrainerConverter("your_notebook.ipynb")

# Convert to Python with enhancements
python_code = converter.convert_to_python("enhanced_script.py")

# Convert to HTML with custom styling
html_content = converter.convert_to_html("enhanced_notebook.html")

# Convert to Markdown
markdown_content = converter.convert_to_markdown("enhanced_docs.md")

# Analyze Trainer usage
analysis = converter.analyze_trainer_usage()
print(f"Found {len(analysis['trainer_cells'])} Trainer cells")

# Generate training report
report = converter.generate_training_report()
```

### Command Line Interface

```bash
# Basic conversion to Python
python hf_trainer_nbconvert.py notebook.ipynb -f python

# Convert to HTML with custom output path
python hf_trainer_nbconvert.py notebook.ipynb -f html -o output.html

# Convert to all formats
python hf_trainer_nbconvert.py notebook.ipynb -f all

# Generate analysis report
python hf_trainer_nbconvert.py notebook.ipynb --analyze

# Generate training report
python hf_trainer_nbconvert.py notebook.ipynb --report -o report.md

# Convert without enhancements (standard nbconvert)
python hf_trainer_nbconvert.py notebook.ipynb --no-enhance
```

## 🎨 Enhanced Features

### 1. Training Progress Visualization

The converter automatically enhances training cells with:

```python
# Enhanced training visualization
if hasattr(trainer.state, 'log_history'):
    logs = trainer.state.log_history
    if logs:
        steps = [log.get('step', 0) for log in logs if 'loss' in log]
        losses = [log.get('loss', 0) for log in logs if 'loss' in log]
        
        if steps and losses:
            plt.figure(figsize=(10, 6))
            plt.plot(steps, losses, 'b-', linewidth=2, label='Training Loss')
            plt.xlabel('Training Steps')
            plt.ylabel('Loss')
            plt.title('Training Progress - Loss Over Time')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.show()
```

### 2. Training Documentation

Trainer instantiation cells are enhanced with detailed documentation:

```python
# Enhanced Training Configuration
# This cell initializes the Hugging Face Trainer with the following key components:
# - Model: The transformer model to be fine-tuned
# - Training Arguments: Configuration for training hyperparameters
# - Dataset: Training and evaluation datasets
# - Tokenizer: For text preprocessing
```

### 3. Custom HTML Styling

HTML output includes custom CSS for better visualization:

```css
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
```

## 📊 Analysis Features

### Trainer Usage Analysis

The converter can analyze your notebook and provide insights:

```python
analysis = converter.analyze_trainer_usage()
# Returns:
{
    'trainer_cells': [6],           # Cells with Trainer instantiation
    'training_cells': [7],          # Cells with training execution
    'visualization_cells': [8],     # Cells with training visualization
    'imports': [...],               # Detected imports
    'models_used': [...],           # Models found in the notebook
    'datasets_used': [...]          # Datasets detected
}
```

### Training Report Generation

Generate comprehensive reports about your training setup:

```
# Hugging Face Trainer Analysis Report
**Notebook:** example_notebook.ipynb

## Summary
- Total cells: 15
- Code cells: 12
- Trainer-related cells: 3
- Training execution cells: 1
- Visualization cells: 2

## Trainer API Usage
- Trainer instantiation found in cells: [6]
- Training execution found in cells: [7]
- Training visualization found in cells: [8, 10]

## Models Detected
- BertForQuestionAnswering (Cell 6)

## Recommendations
- Consider adding more comprehensive evaluation metrics
- Add early stopping callback for better training control
```

## 🔍 Detected Patterns

The converter automatically detects:

- **Trainer Instantiation**: `Trainer(...)`, `trainer = Trainer(...)`
- **Training Execution**: `trainer.train()`, `training_log = trainer.train()`
- **Visualization**: `plt.plot(...loss...)`, `matplotlib...training`
- **Model Usage**: `BertForQuestionAnswering`, `GPT2LMHeadModel`, etc.
- **Import Statements**: `from transformers import ...`

## 🎯 Use Cases

1. **Converting Training Notebooks**: Transform research notebooks into production-ready scripts
2. **Documentation Generation**: Create comprehensive HTML/Markdown documentation
3. **Training Analysis**: Analyze and optimize your training setup
4. **Progress Visualization**: Enhance training progress tracking
5. **Code Sharing**: Generate clean Python scripts from experimental notebooks

## 🛠️ Customization

You can extend the converter by:

1. **Adding Custom Preprocessors**: Create new pattern detection logic
2. **Custom Templates**: Modify output templates for different formats
3. **Enhanced Analysis**: Add more sophisticated training analysis
4. **Custom Styling**: Modify CSS for HTML output

Example custom preprocessor:

```python
class CustomTrainerPreprocessor(HuggingFaceTrainerPreprocessor):
    def _is_custom_pattern(self, source: str) -> bool:
        # Add your custom detection logic
        return 'your_pattern' in source
    
    def _enhance_custom_cell(self, cell, index: int):
        # Add your custom enhancement
        return cell
```

## 🤝 Contributing

Feel free to contribute by:

- Reporting issues
- Suggesting new features
- Submitting pull requests
- Improving documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**K N S Sri Harshith**  
Email: knssriharshith@gmail.com

1. Adding support for more training frameworks
2. Improving visualization capabilities
3. Adding new output formats
4. Enhancing analysis features
5. Improving documentation

## 📝 License

MIT License - Feel free to use and modify as needed.

## 🔗 Related Tools

- [nbconvert](https://nbconvert.readthedocs.io/) - The underlying conversion library
- [Hugging Face Transformers](https://huggingface.co/transformers/) - The ML library this tool specializes in
- [Jupyter](https://jupyter.org/) - The notebook environment

## 📞 Support

If you encounter issues or have suggestions:

1. Check the analysis output for insights
2. Use the `--analyze` flag to understand your notebook structure
3. Try the `--no-enhance` flag if you encounter compatibility issues
4. Review the generated training report for optimization suggestions

---

**Happy Training! 🚀**
