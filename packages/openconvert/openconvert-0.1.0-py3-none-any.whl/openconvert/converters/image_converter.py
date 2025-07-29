"""
Image converter module for handling image format conversions.
"""

import logging
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'png': ['jpg', 'jpeg', 'bmp', 'tiff', 'gif', 'pdf', 'ico', 'svg', 'webp'],
    'jpg': ['png', 'bmp', 'tiff', 'gif', 'pdf', 'ico', 'svg', 'webp'],
    'jpeg': ['png', 'bmp', 'tiff', 'gif', 'pdf', 'ico', 'svg', 'webp'],
    'bmp': ['png', 'jpg', 'tiff', 'gif', 'pdf', 'ico', 'webp'],
    'gif': ['png', 'jpg', 'bmp', 'tiff', 'pdf', 'ico', 'webp'],
    'tiff': ['png', 'jpg', 'bmp', 'gif', 'pdf', 'webp'],
    'ico': ['png', 'jpg', 'bmp', 'tiff', 'gif', 'webp'],
    'svg': ['png', 'jpg', 'bmp', 'tiff', 'pdf', 'webp'],
    'webp': ['png', 'jpg', 'bmp', 'tiff', 'gif', 'pdf']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert an image from one format to another.
    
    Args:
        filepath: Path to the source image file
        source_format: Source image format
        target_format: Target image format
        output_path: Path to save the converted image
        options: Additional conversion options
        
    Returns:
        Path to the converted image
        
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
        # Use Pillow for most image conversions
        from PIL import Image
        
        # Special handling for SVG conversions
        if source_format == 'svg':
            if target_format in ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp']:
                return _convert_svg_to_raster(filepath, target_format, output_path, options)
            elif target_format == 'pdf':
                return _convert_svg_to_pdf(filepath, output_path, options)
        
        # Special handling for PDF output
        if target_format == 'pdf':
            return _convert_to_pdf(filepath, source_format, output_path, options)
        
        # Standard image conversion using Pillow
        with Image.open(filepath) as img:
            # Apply any image processing options
            if 'resize' in options:
                width, height = options['resize']
                img = img.resize((width, height), Image.LANCZOS)
            
            if 'rotate' in options:
                img = img.rotate(options['rotate'])
            
            # Convert palette mode (P) to RGB for formats that don't support it
            if img.mode == 'P' and target_format in ['jpg', 'jpeg']:
                img = img.convert('RGB')
            
            if 'quality' in options and target_format in ['jpg', 'jpeg', 'webp']:
                img.save(output_path, quality=options['quality'])
            else:
                img.save(output_path)
        
        logger.info(f"Successfully converted {filepath} to {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error converting {filepath} to {target_format}: {str(e)}")
        raise RuntimeError(f"Failed to convert {filepath} to {target_format}: {str(e)}")

def _convert_svg_to_raster(
    filepath: Path,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert SVG to raster formats like PNG, JPG, etc."""
    try:
        # Try using cairosvg for SVG conversion
        import cairosvg
        
        width = options.get('width', 800)
        height = options.get('height', 600)
        
        if target_format == 'png':
            cairosvg.svg2png(url=str(filepath), write_to=str(output_path), 
                             width=width, height=height)
        elif target_format in ['jpg', 'jpeg']:
            # Convert to PNG first, then to JPG
            temp_png = output_path.with_suffix('.png')
            cairosvg.svg2png(url=str(filepath), write_to=str(temp_png), 
                             width=width, height=height)
            
            from PIL import Image
            with Image.open(temp_png) as img:
                img.convert('RGB').save(output_path, quality=options.get('quality', 90))
            
            # Remove temporary PNG
            temp_png.unlink()
        else:
            # For other formats, convert to PNG first, then use Pillow
            temp_png = output_path.with_suffix('.png')
            cairosvg.svg2png(url=str(filepath), write_to=str(temp_png), 
                             width=width, height=height)
            
            from PIL import Image
            with Image.open(temp_png) as img:
                img.save(output_path)
            
            # Remove temporary PNG
            temp_png.unlink()
        
        return str(output_path)
    
    except ImportError:
        logger.warning("cairosvg not installed. Trying alternative method...")
        
        # Try using Inkscape as a fallback
        try:
            import subprocess
            
            cmd = [
                'inkscape',
                '--export-filename', str(output_path),
                str(filepath)
            ]
            
            subprocess.run(cmd, check=True)
            return str(output_path)
        
        except (ImportError, subprocess.SubprocessError) as e:
            raise RuntimeError(f"Failed to convert SVG: {str(e)}. Please install cairosvg or Inkscape.")

def _convert_svg_to_pdf(
    filepath: Path,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert SVG to PDF."""
    try:
        # Try using cairosvg
        import cairosvg
        cairosvg.svg2pdf(url=str(filepath), write_to=str(output_path))
        return str(output_path)
    
    except ImportError:
        logger.warning("cairosvg not installed. Trying alternative method...")
        
        # Try using Inkscape as a fallback
        try:
            import subprocess
            
            cmd = [
                'inkscape',
                '--export-filename', str(output_path),
                str(filepath)
            ]
            
            subprocess.run(cmd, check=True)
            return str(output_path)
        
        except (ImportError, subprocess.SubprocessError) as e:
            raise RuntimeError(f"Failed to convert SVG to PDF: {str(e)}. Please install cairosvg or Inkscape.")

def _convert_to_pdf(
    filepath: Path,
    source_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert image to PDF."""
    from PIL import Image
    
    try:
        with Image.open(filepath) as img:
            # Convert to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            img.save(output_path, 'PDF', resolution=options.get('dpi', 100))
        
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error converting to PDF: {str(e)}")
        raise RuntimeError(f"Failed to convert to PDF: {str(e)}") 