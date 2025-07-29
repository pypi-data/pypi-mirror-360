"""
Code and markup converter module for handling code and markup format conversions.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'json': ['xml', 'yaml', 'csv', 'txt'],
    'yaml': ['json', 'xml', 'txt'],
    'xml': ['json', 'yaml', 'txt'],
    'html': ['md', 'txt', 'pdf'],
    'md': ['html', 'txt', 'pdf'],
    'latex': ['pdf', 'docx', 'html']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert code or markup from one format to another.
    
    Args:
        filepath: Path to the source file
        source_format: Source format
        target_format: Target format
        output_path: Path to save the converted file
        options: Additional conversion options
        
    Returns:
        Path to the converted file
        
    Raises:
        ValueError: If the conversion is not supported
        RuntimeError: If the conversion fails
    """
    if options is None:
        options = {}
    
    # Check if conversion is supported
    if target_format not in SUPPORTED_CONVERSIONS.get(source_format, []):
        raise ValueError(f"Conversion from {source_format} to {target_format} is not supported")
    
    filepath = Path(filepath)
    output_path = Path(output_path)
    
    try:
        # Route to appropriate conversion method
        if source_format == 'json':
            return _convert_from_json(filepath, target_format, output_path, options)
        elif source_format == 'yaml':
            return _convert_from_yaml(filepath, target_format, output_path, options)
        elif source_format == 'xml':
            return _convert_from_xml(filepath, target_format, output_path, options)
        elif source_format == 'html':
            return _convert_from_html(filepath, target_format, output_path, options)
        elif source_format == 'md':
            return _convert_from_md(filepath, target_format, output_path, options)
        elif source_format == 'latex':
            return _convert_from_latex(filepath, target_format, output_path, options)
        else:
            raise ValueError(f"Unsupported source format: {source_format}")
    
    except Exception as e:
        logger.error(f"Error converting {filepath} to {target_format}: {str(e)}")
        raise RuntimeError(f"Failed to convert {filepath} to {target_format}: {str(e)}")

def _convert_from_json(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from JSON to other formats."""
    import json
    
    # Read the JSON file
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if target_format == 'xml':
        try:
            import dicttoxml
            
            # Convert to XML
            xml = dicttoxml.dicttoxml(data, custom_root=options.get('root_name', 'root'), attr_type=False)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(xml)
        
        except ImportError:
            raise RuntimeError("dicttoxml library is required for JSON to XML conversion. Please install it.")
    
    elif target_format == 'yaml':
        try:
            import yaml
            
            # Convert to YAML
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        except ImportError:
            raise RuntimeError("PyYAML library is required for JSON to YAML conversion. Please install it.")
    
    elif target_format == 'csv':
        try:
            import csv
            
            # Check if the JSON is a list of dictionaries (suitable for CSV)
            if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
                raise ValueError("JSON must be a list of dictionaries to convert to CSV")
            
            # Get all unique keys as CSV headers
            headers = set()
            for item in data:
                headers.update(item.keys())
            headers = sorted(headers)
            
            # Write to CSV
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
        
        except ValueError as e:
            raise ValueError(f"Error converting JSON to CSV: {str(e)}")
    
    elif target_format == 'txt':
        # Simple pretty-printed JSON to text
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    
    return str(output_path)

def _convert_from_yaml(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from YAML to other formats."""
    try:
        import yaml
        
        # Read the YAML file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if target_format == 'json':
            import json
            
            # Convert to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        
        elif target_format == 'xml':
            import dicttoxml
            
            # Convert to XML
            xml = dicttoxml.dicttoxml(data, custom_root=options.get('root_name', 'root'), attr_type=False)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(xml)
        
        elif target_format == 'txt':
            # Simple YAML to text (just copy the content)
            with open(filepath, 'r', encoding='utf-8') as f_in:
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
    
    except ImportError:
        raise RuntimeError("PyYAML library is required for YAML conversions. Please install it.")
    
    return str(output_path)

def _convert_from_xml(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from XML to other formats."""
    try:
        import xmltodict
        
        # Read the XML file
        with open(filepath, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        # Convert XML to dict
        data = xmltodict.parse(xml_content)
        
        if target_format == 'json':
            import json
            
            # Convert to JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        
        elif target_format == 'yaml':
            import yaml
            
            # Convert to YAML
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        elif target_format == 'txt':
            # Simple XML to text (just copy the content)
            with open(filepath, 'r', encoding='utf-8') as f_in:
                with open(output_path, 'w', encoding='utf-8') as f_out:
                    f_out.write(f_in.read())
    
    except ImportError:
        raise RuntimeError("xmltodict library is required for XML conversions. Please install it.")
    
    return str(output_path)

def _convert_from_html(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from HTML to other formats."""
    if target_format == 'md':
        try:
            import html2text
            
            # Read the HTML file
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Convert to Markdown
            h = html2text.HTML2Text()
            h.ignore_links = options.get('ignore_links', False)
            h.ignore_images = options.get('ignore_images', False)
            h.body_width = options.get('body_width', 0)  # 0 means no wrapping
            
            markdown = h.handle(html_content)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
        
        except ImportError:
            # Alternative method using pandoc
            _convert_using_pandoc(filepath, target_format, output_path)
    
    elif target_format == 'txt':
        try:
            from bs4 import BeautifulSoup
            
            # Read the HTML file
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator='\n\n')
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
        
        except ImportError:
            # Alternative method using pandoc
            _convert_using_pandoc(filepath, target_format, output_path)
    
    elif target_format == 'pdf':
        # Use pandoc for HTML to PDF conversion
        _convert_using_pandoc(filepath, target_format, output_path)
    
    return str(output_path)

def _convert_from_md(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from Markdown to other formats."""
    if target_format == 'html':
        try:
            import markdown
            
            # Read the Markdown file
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Convert to HTML
            html = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
            
            # Add HTML boilerplate
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{filepath.stem}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: monospace; }}
        img {{ max-width: 100%; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
        
        except ImportError:
            # Alternative method using pandoc
            _convert_using_pandoc(filepath, target_format, output_path)
    
    elif target_format == 'txt':
        # Simple conversion - just strip markdown syntax
        with open(filepath, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Very basic markdown stripping
        import re
        
        # Remove headers
        text = re.sub(r'^#+\s+', '', md_content, flags=re.MULTILINE)
        
        # Remove bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    elif target_format == 'pdf':
        # Use pandoc for Markdown to PDF conversion
        _convert_using_pandoc(filepath, target_format, output_path)
    
    return str(output_path)

def _convert_from_latex(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert from LaTeX to other formats."""
    # Use pandoc for all LaTeX conversions
    _convert_using_pandoc(filepath, target_format, output_path)
    return str(output_path)

def _convert_using_pandoc(
    filepath: Path,
    target_format: str,
    output_path: Path
) -> None:
    """Use pandoc for document conversion."""
    try:
        import subprocess
        
        # Map our format names to pandoc format names
        format_map = {
            'md': 'markdown',
            'html': 'html',
            'pdf': 'pdf',
            'docx': 'docx',
            'latex': 'latex',
            'txt': 'plain'
        }
        
        source_ext = filepath.suffix.lower().lstrip('.')
        if source_ext == 'tex':
            source_ext = 'latex'
        
        pandoc_source = format_map.get(source_ext, source_ext)
        pandoc_target = format_map.get(target_format, target_format)
        
        cmd = [
            'pandoc',
            '-f', pandoc_source,
            '-t', pandoc_target,
            '-o', str(output_path),
            str(filepath)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
    
    except (ImportError, subprocess.SubprocessError) as e:
        raise RuntimeError(f"Failed to convert using pandoc: {str(e)}. Please install pandoc.") 