"""
Video converter module for handling video format conversions.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'mp4': ['avi', 'mkv', 'mov', 'gif'],
    'avi': ['mp4', 'mkv', 'mov', 'gif'],
    'mkv': ['mp4', 'avi', 'mov'],
    'mov': ['mp4', 'avi', 'mkv'],
    'gif': ['mp4', 'avi']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert a video file from one format to another.
    
    Args:
        filepath: Path to the source video file
        source_format: Source video format
        target_format: Target video format
        output_path: Path to save the converted video
        options: Additional conversion options
        
    Returns:
        Path to the converted video
        
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
        # Use ffmpeg for video conversion
        return _convert_with_ffmpeg(filepath, source_format, target_format, output_path, options)
    
    except Exception as e:
        logger.error(f"Error converting {filepath} to {target_format}: {str(e)}")
        raise RuntimeError(f"Failed to convert {filepath} to {target_format}: {str(e)}")

def extract_audio(
    filepath: Union[str, Path],
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Extract audio from a video file.
    
    Args:
        filepath: Path to the source video file
        output_path: Path to save the extracted audio
        options: Additional extraction options
        
    Returns:
        Path to the extracted audio
        
    Raises:
        RuntimeError: If the extraction fails
    """
    if options is None:
        options = {}
    
    filepath = Path(filepath)
    output_path = Path(output_path)
    
    try:
        import subprocess
        
        # Basic ffmpeg command for audio extraction
        cmd = ['ffmpeg', '-i', str(filepath), '-vn']  # -vn means no video
        
        # Add audio options
        if 'audio_codec' in options:
            cmd.extend(['-acodec', options['audio_codec']])
        else:
            cmd.extend(['-acodec', 'libmp3lame'])  # Default to MP3
        
        if 'bitrate' in options:
            cmd.extend(['-b:a', options['bitrate']])
        else:
            cmd.extend(['-b:a', '192k'])  # Default bitrate
        
        if 'sample_rate' in options:
            cmd.extend(['-ar', str(options['sample_rate'])])
        
        if 'channels' in options:
            cmd.extend(['-ac', str(options['channels'])])
        
        # Add output file
        cmd.append(str(output_path))
        
        # Run ffmpeg
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error extracting audio: {str(e)}")
        raise RuntimeError(f"Failed to extract audio: {str(e)}")

def extract_frames(
    filepath: Union[str, Path],
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Extract frames from a video file.
    
    Args:
        filepath: Path to the source video file
        target_format: Target image format (png or jpg)
        output_path: Path to save the extracted frames
        options: Additional extraction options
        
    Returns:
        Path to the directory containing extracted frames
        
    Raises:
        ValueError: If the target format is not supported
        RuntimeError: If the extraction fails
    """
    if options is None:
        options = {}
    
    if target_format not in ['png', 'jpg', 'jpeg']:
        raise ValueError(f"Unsupported frame format: {target_format}")
    
    filepath = Path(filepath)
    output_path = Path(output_path)
    
    # If output_path is a file, use its parent directory and name as prefix
    if output_path.suffix:
        output_dir = output_path.parent
        output_prefix = output_path.stem
    else:
        # If output_path is a directory, use it as is
        output_dir = output_path
        output_prefix = 'frame'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        import subprocess
        
        # Get frame rate for extraction
        fps = options.get('fps', 1)  # Default: 1 frame per second
        
        # Determine output pattern
        output_pattern = str(output_dir / f"{output_prefix}_%04d.{target_format}")
        
        # Basic ffmpeg command for frame extraction
        cmd = ['ffmpeg', '-i', str(filepath)]
        
        if 'start_time' in options:
            cmd.extend(['-ss', str(options['start_time'])])
        
        if 'duration' in options:
            cmd.extend(['-t', str(options['duration'])])
        
        # Set frame rate
        cmd.extend(['-vf', f'fps={fps}'])
        
        # Set quality
        if target_format in ['jpg', 'jpeg']:
            quality = options.get('quality', 95)
            cmd.extend(['-q:v', str(int(quality / 10))])  # ffmpeg uses 1-10 scale
        
        # Add output pattern
        cmd.append(output_pattern)
        
        # Run ffmpeg
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_dir)
    
    except Exception as e:
        logger.error(f"Error extracting frames: {str(e)}")
        raise RuntimeError(f"Failed to extract frames: {str(e)}")

def _convert_with_ffmpeg(
    filepath: Path,
    source_format: str,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert video using ffmpeg."""
    import subprocess
    
    # Basic ffmpeg command
    cmd = ['ffmpeg', '-i', str(filepath)]
    
    # Special handling for GIF output
    if target_format == 'gif':
        # Optimize for GIF output
        scale = options.get('scale', 320)
        fps = options.get('fps', 10)
        cmd.extend([
            '-vf', f'fps={fps},scale={scale}:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse'
        ])
    else:
        # Add video options
        if 'video_codec' in options:
            cmd.extend(['-c:v', options['video_codec']])
        
        if 'audio_codec' in options:
            cmd.extend(['-c:a', options['audio_codec']])
        
        if 'bitrate' in options:
            cmd.extend(['-b:v', options['bitrate']])
        
        if 'resolution' in options:
            width, height = options['resolution']
            cmd.extend(['-s', f'{width}x{height}'])
        
        if 'framerate' in options:
            cmd.extend(['-r', str(options['framerate'])])
        
        if 'crf' in options:
            # Constant Rate Factor (quality)
            cmd.extend(['-crf', str(options['crf'])])
        
        if 'preset' in options:
            # Encoding preset (slower = better compression)
            cmd.extend(['-preset', options['preset']])
    
    # Add output file
    cmd.append(str(output_path))
    
    # Run ffmpeg
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    except subprocess.SubprocessError as e:
        logger.error(f"Error running ffmpeg: {str(e)}")
        raise RuntimeError(f"Failed to convert video with ffmpeg: {str(e)}") 