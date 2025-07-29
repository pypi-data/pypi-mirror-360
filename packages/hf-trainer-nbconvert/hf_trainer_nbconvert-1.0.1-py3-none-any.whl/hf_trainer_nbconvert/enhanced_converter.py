"""
Enhanced converter that extracts actual training values from HuggingFace widgets
and displays them in the HTML with standard Jupyter styling.

Author: K N S Sri Harshith
License: MIT
"""

import json
import re
from pathlib import Path
import os
import tempfile
import atexit


def extract_widget_training_data(outputs):
    """Extract actual training data from widget outputs."""
    training_data = []
    
    for output in outputs:
        if output.get('output_type') == 'display_data':
            data = output.get('data', {})
            
            # Check for widget with text/plain data
            if ('application/vnd.jupyter.widget-view+json' in data and 
                'text/plain' in data):
                
                plain_text = data['text/plain']
                if isinstance(plain_text, list):
                    text_content = ''.join(plain_text)
                else:
                    text_content = str(plain_text)
                
                # Look for training progress indicators
                lines = text_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and any(keyword in line.lower() for keyword in [
                        'epoch', 'step', 'loss', '%', 'it/s', 's/it', 'train_loss'
                    ]):
                        # Clean up the line
                        clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)  # Remove ANSI
                        clean_line = re.sub(r'<[^>]+>', '', clean_line)  # Remove HTML tags
                        if clean_line.strip():
                            training_data.append(clean_line.strip())
    
    return training_data


def enhanced_clean_notebook(notebook_path, output_path=None):
    """Clean notebook and extract detailed training information."""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook_data = json.load(f)
    
    print("🔍 Extracting training data from widgets...")
    
    for i, cell in enumerate(notebook_data.get('cells', [])):
        if cell.get('cell_type') == 'code' and 'outputs' in cell:
            original_count = len(cell['outputs'])
            
            # Extract training data from widgets first
            widget_training_data = extract_widget_training_data(cell['outputs'])
            
            # Clean outputs
            cleaned_outputs = []
            widget_data_added = False
            
            for output in cell['outputs']:
                output_type = output.get('output_type')
                
                if output_type == 'display_data':
                    data = output.get('data', {})
                    
                    # Handle widget outputs
                    if 'application/vnd.jupyter.widget-view+json' in data:
                        # Add widget training data once per cell
                        if widget_training_data and not widget_data_added:
                            training_text = format_training_data(widget_training_data)
                            training_output = {
                                'output_type': 'stream',
                                'name': 'stdout',
                                'text': [training_text]
                            }
                            cleaned_outputs.append(training_output)
                            widget_data_added = True
                        continue
                    
                    # Keep safe display data
                    safe_data = {}
                    for mime_type, content in data.items():
                        if mime_type in ['text/plain', 'text/html', 'image/png', 'image/jpeg']:
                            safe_data[mime_type] = content
                    
                    if safe_data:
                        cleaned_outputs.append({
                            'output_type': 'display_data',
                            'data': safe_data,
                            'metadata': {}
                        })
                
                elif output_type == 'stream':
                    # Keep stream outputs
                    cleaned_outputs.append(output)
                
                elif output_type == 'execute_result':
                    # Keep execute results with safe data only
                    data = output.get('data', {})
                    safe_data = {k: v for k, v in data.items() 
                               if k in ['text/plain', 'text/html']}
                    
                    if safe_data:
                        cleaned_outputs.append({
                            'output_type': 'execute_result',
                            'execution_count': output.get('execution_count'),
                            'data': safe_data,
                            'metadata': {}
                        })
            
            cell['outputs'] = cleaned_outputs
            
            if original_count != len(cleaned_outputs) or widget_training_data:
                data_status = f"(+{len(widget_training_data)} training lines)" if widget_training_data else ""
                print(f"   Cell {i+1}: {original_count} → {len(cleaned_outputs)} outputs {data_status}")
    
    # Clean metadata
    if 'metadata' in notebook_data:
        metadata = notebook_data['metadata']
        if 'widgets' in metadata:
            del metadata['widgets']
    
    # Use memory file by default if no output path is specified
    use_memory = output_path is None
    
    if use_memory:
        # Create a temporary file in the system temp directory
        temp_dir = tempfile.gettempdir()
        temp_filename = f"temp_{Path(notebook_path).stem}_{os.getpid()}.ipynb"
        output_path = Path(temp_dir) / temp_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook_data, f, indent=1)
    
    # Ensure the file is removed when the program exits
    if use_memory:
        def cleanup_temp_file():
            try:
                if output_path.exists():
                    output_path.unlink()
            except Exception:
                pass
                
        atexit.register(cleanup_temp_file)
    
    print(f"✅ Enhanced cleaned notebook saved: {output_path}")
    return output_path


def format_training_data(training_lines):
    """Format training data for display."""
    if not training_lines:
        return "Training Progress: Completed\n"
    
    # Remove duplicates while preserving order
    unique_lines = []
    seen = set()
    for line in training_lines:
        if line not in seen:
            unique_lines.append(line)
            seen.add(line)
    
    # Format the output
    result = "🚀 HUGGING FACE TRAINER PROGRESS\n"
    result += "=" * 50 + "\n"
    
    # Group and format lines
    epoch_lines = [l for l in unique_lines if 'epoch' in l.lower()]
    step_lines = [l for l in unique_lines if 'step' in l.lower() and 'epoch' not in l.lower()]
    loss_lines = [l for l in unique_lines if 'loss' in l.lower()]
    progress_lines = [l for l in unique_lines if any(x in l for x in ['%', 'it/s', 's/it'])]
    
    if epoch_lines:
        result += "\n📊 EPOCHS:\n"
        for line in epoch_lines[:5]:
            result += f"  • {line}\n"
    
    if step_lines:
        result += "\n⚡ STEPS:\n"
        for line in step_lines[:5]:
            result += f"  • {line}\n"
    
    if loss_lines:
        result += "\n📉 LOSS VALUES:\n"
        for line in loss_lines[:5]:
            result += f"  • {line}\n"
    
    if progress_lines:
        result += "\n🔄 PROGRESS:\n"
        for line in progress_lines[:5]:
            result += f"  • {line}\n"
    
    # Add any remaining important lines
    other_lines = [l for l in unique_lines 
                  if l not in epoch_lines + step_lines + loss_lines + progress_lines]
    if other_lines:
        result += "\n📝 OTHER INFO:\n"
        for line in other_lines[:3]:
            result += f"  • {line}\n"
    
    result += "\n" + "=" * 50 + "\n"
    result += "✅ Training completed successfully!\n"
    
    return result


def convert_to_html_with_standard_styling(cleaned_notebook_path, output_html_path=None):
    """Convert to HTML with standard Jupyter styling."""
    try:
        from nbconvert import HTMLExporter
        
        exporter = HTMLExporter()
        exporter.template_name = 'classic'  # Standard Jupyter template
        
        (body, resources) = exporter.from_filename(str(cleaned_notebook_path))
        
        if output_html_path is None:
            # Use original notebook name for output
            notebook_path = str(cleaned_notebook_path)
            if 'temp_' in notebook_path:
                # Extract original name from temp filename
                stem = Path(notebook_path).stem
                parts = stem.split('_')
                if len(parts) > 1:
                    # Skip 'temp_' prefix and PID suffix
                    original_name = '_'.join(parts[1:-1])
                    output_html_path = Path(cleaned_notebook_path).parent / f"{original_name}_converted.html"
                else:
                    output_html_path = Path(cleaned_notebook_path).parent / f"{stem}_converted.html"
            else:
                output_html_path = Path(cleaned_notebook_path).parent / f"{Path(cleaned_notebook_path).stem}_converted.html"
        
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        # Immediately try to clean up the temporary input file
        if 'temp_' in str(cleaned_notebook_path):
            try:
                Path(cleaned_notebook_path).unlink(missing_ok=True)
                print(f"🗑️  Cleaned up temporary file")
            except Exception:
                pass
        
        print(f"✅ HTML with training data saved: {output_html_path}")
        return output_html_path
        
    except Exception as e:
        print(f"❌ HTML conversion failed: {e}")
        return None


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract HF Trainer values and convert to HTML")
    parser.add_argument("notebook", help="Input notebook file")
    parser.add_argument("-o", "--output", help="Output HTML file")
    parser.add_argument("--keep-cleaned", action="store_true", help="Keep cleaned notebook")
    
    args = parser.parse_args()
    
    notebook_path = Path(args.notebook)
    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        return
    
    print(f"🎯 Extracting training values from: {notebook_path.name}")
    
    # Clean and extract training data
    cleaned_notebook = enhanced_clean_notebook(notebook_path)
    
    # Convert to HTML
    html_output = convert_to_html_with_standard_styling(cleaned_notebook, args.output)
    
    # Always clean up temporary files
    if not args.keep_cleaned:
        if cleaned_notebook.exists():
            try:
                cleaned_notebook.unlink()
                print(f"🗑️  Cleaned up temporary file: {cleaned_notebook.name}")
            except Exception as e:
                print(f"⚠️  Note: Could not clean up temporary file: {e}")
    
    if html_output:
        print(f"\n🎉 Conversion successful!")
        print(f"📄 Input: {notebook_path.name}")
        print(f"🌐 Output: {Path(html_output).name}")
    else:
        print(f"❌ Conversion failed!")
    
    return html_output


class EnhancedTrainerConverter:
    """
    Enhanced converter class for easy API usage.
    """
    
    def __init__(self, notebook_path):
        """Initialize with notebook path."""
        self.notebook_path = Path(notebook_path)
        
        if not self.notebook_path.exists():
            raise FileNotFoundError(f"Notebook not found: {self.notebook_path}")
    
    def convert_to_html(self, output_path=None, keep_cleaned=False):
        """
        Convert notebook to HTML with training data extraction.
        
        Args:
            output_path: Output HTML file path
            keep_cleaned: Whether to keep the cleaned notebook file
            
        Returns:
            Path to the generated HTML file
        """
        # Clean notebook
        cleaned_notebook = enhanced_clean_notebook(self.notebook_path)
        
        try:
            # Convert to HTML
            html_output = convert_to_html_with_standard_styling(
                cleaned_notebook, 
                output_path
            )
            
            return html_output
            
        finally:
            # Cleanup if requested
            if not keep_cleaned and cleaned_notebook.exists():
                cleaned_notebook.unlink()
        
    def analyze_training_data(self):
        """Analyze training data in the notebook."""
        with open(self.notebook_path, 'r', encoding='utf-8') as f:
            notebook_data = json.load(f)
        
        training_cells = []
        for i, cell in enumerate(notebook_data.get('cells', [])):
            if cell.get('cell_type') == 'code' and 'outputs' in cell:
                widget_data = extract_widget_training_data(cell['outputs'])
                if widget_data:
                    training_cells.append({
                        'cell_index': i,
                        'training_lines': widget_data
                    })