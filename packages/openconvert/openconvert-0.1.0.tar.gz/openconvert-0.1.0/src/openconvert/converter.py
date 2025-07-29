"""
Main converter module that provides the open_convert function.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union, List

from .converters import (
    image_converter,
    document_converter,
    audio_converter,
    video_converter,
    archive_converter,
    model_converter,
    code_converter
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define conversion categories
CONVERSION_CATEGORIES = {
    # Image formats
    'png': 'image', 'jpg': 'image', 'jpeg': 'image', 'bmp': 'image', 'tiff': 'image',
    'gif': 'image', 'ico': 'image', 'svg': 'image', 'webp': 'image',
    
    # Document formats
    'txt': 'document', 'pdf': 'document', 'docx': 'document', 'rtf': 'document',
    'md': 'document', 'html': 'document', 'csv': 'document', 'xlsx': 'document',
    'epub': 'document',
    
    # Audio formats
    'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio', 'flac': 'audio', 'aac': 'audio',
    
    # Video formats
    'mp4': 'video', 'avi': 'video', 'mkv': 'video', 'mov': 'video',
    
    # Archive formats
    'zip': 'archive', 'rar': 'archive', '7z': 'archive', 'tar': 'archive', 'gz': 'archive',
    
    # 3D Model formats
    'stl': 'model', 'obj': 'model', 'fbx': 'model', 'ply': 'model',
    
    # Code and markup formats
    'json': 'code', 'yaml': 'code', 'xml': 'code', 'latex': 'code'
}

def open_convert(
    filepath: Union[str, Path],
    source_format: Optional[str] = None,
    target_format: str = None,
    output_path: Optional[Union[str, Path]] = None,
    options: Optional[dict] = None
) -> str:
    """
    Convert a file from one format to another.
    
    Args:
        filepath: Path to the source file
        source_format: Source file format (if None, will be inferred from file extension)
        target_format: Target file format
        output_path: Path to save the converted file (if None, will use the same directory as source)
        options: Additional conversion options
        
    Returns:
        Path to the converted file
    
    Raises:
        ValueError: If the conversion is not supported or parameters are invalid
        FileNotFoundError: If the source file doesn't exist
        RuntimeError: If the conversion fails
    """
    if options is None:
        options = {}
    
    # Convert filepath to Path object
    filepath = Path(filepath)
    
    # Check if file exists
    if not filepath.exists():
        raise FileNotFoundError(f"Source file not found: {filepath}")
    
    # Infer source format from file extension if not provided
    if source_format is None:
        source_format = filepath.suffix.lower().lstrip('.')
        if not source_format:
            raise ValueError("Could not determine source format from file extension. Please specify source_format.")
    else:
        source_format = source_format.lower()
    
    # Ensure target format is provided and lowercase
    if target_format is None:
        raise ValueError("Target format must be specified")
    target_format = target_format.lower()
    
    # Check if formats are supported
    if source_format not in CONVERSION_CATEGORIES:
        raise ValueError(f"Unsupported source format: {source_format}")
    if target_format not in CONVERSION_CATEGORIES:
        raise ValueError(f"Unsupported target format: {target_format}")
    
    # Determine output path if not provided
    if output_path is None:
        output_path = filepath.with_suffix(f".{target_format}")
    else:
        output_path = Path(output_path)
        # If output_path is a directory, use the original filename with new extension
        if output_path.is_dir():
            output_path = output_path / filepath.with_suffix(f".{target_format}").name
    
    logger.info(f"Converting {filepath} from {source_format} to {target_format}")
    
    # Determine conversion category and route to appropriate converter
    source_category = CONVERSION_CATEGORIES[source_format]
    target_category = CONVERSION_CATEGORIES[target_format]
    
    # Handle conversion based on categories
    if source_category == 'image':
        if target_category == 'image' or target_format == 'pdf':
            return image_converter.convert(filepath, source_format, target_format, output_path, options)
    
    elif source_category == 'document':
        return document_converter.convert(filepath, source_format, target_format, output_path, options)
    
    elif source_category == 'audio':
        if target_category == 'audio':
            return audio_converter.convert(filepath, source_format, target_format, output_path, options)
        elif target_format == 'txt':  # Speech-to-text
            return audio_converter.speech_to_text(filepath, output_path, options)
    
    elif source_category == 'video':
        if target_category == 'video' or target_format == 'gif':
            return video_converter.convert(filepath, source_format, target_format, output_path, options)
        elif target_format == 'mp3':  # Audio extraction
            return video_converter.extract_audio(filepath, output_path, options)
        elif target_format in ['png', 'jpg']:  # Frame extraction
            return video_converter.extract_frames(filepath, target_format, output_path, options)
    
    elif source_category == 'archive':
        return archive_converter.convert(filepath, source_format, target_format, output_path, options)
    
    elif source_category == 'model':
        return model_converter.convert(filepath, source_format, target_format, output_path, options)
    
    elif source_category == 'code':
        return code_converter.convert(filepath, source_format, target_format, output_path, options)
    
    # If we get here, the specific conversion is not supported
    raise ValueError(f"Conversion from {source_format} to {target_format} is not supported") 