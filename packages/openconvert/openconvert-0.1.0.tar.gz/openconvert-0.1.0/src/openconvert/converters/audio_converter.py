"""
Audio converter module for handling audio format conversions.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'mp3': ['wav', 'ogg', 'flac', 'aac'],
    'wav': ['mp3', 'ogg', 'flac', 'aac'],
    'ogg': ['mp3', 'wav', 'flac', 'aac'],
    'flac': ['mp3', 'wav', 'ogg', 'aac'],
    'aac': ['mp3', 'wav', 'ogg', 'flac']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert an audio file from one format to another.
    
    Args:
        filepath: Path to the source audio file
        source_format: Source audio format
        target_format: Target audio format
        output_path: Path to save the converted audio
        options: Additional conversion options
        
    Returns:
        Path to the converted audio
        
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
        # Try using pydub for audio conversion
        return _convert_with_pydub(filepath, source_format, target_format, output_path, options)
    except ImportError:
        logger.warning("pydub not installed. Trying alternative method...")
        
        # Try using ffmpeg directly
        return _convert_with_ffmpeg(filepath, source_format, target_format, output_path, options)

def speech_to_text(
    filepath: Union[str, Path],
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert speech audio to text.
    
    Args:
        filepath: Path to the source audio file
        output_path: Path to save the text file
        options: Additional conversion options
        
    Returns:
        Path to the text file
        
    Raises:
        RuntimeError: If the conversion fails
    """
    if options is None:
        options = {}
    
    filepath = Path(filepath)
    output_path = Path(output_path)
    
    try:
        # Try using SpeechRecognition library
        import speech_recognition as sr
        
        # Initialize recognizer
        recognizer = sr.Recognizer()
        
        # Load the audio file
        with sr.AudioFile(str(filepath)) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            
            # Record the audio
            audio_data = recognizer.record(source)
            
            # Recognize speech using Google Speech Recognition
            language = options.get('language', 'en-US')
            text = recognizer.recognize_google(audio_data, language=language)
            
            # Write the text to the output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return str(output_path)
    
    except ImportError:
        logger.error("SpeechRecognition library is required for speech-to-text conversion")
        raise RuntimeError("SpeechRecognition library is required for speech-to-text conversion. Please install it.")
    
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        raise RuntimeError(f"Failed to convert speech to text: {str(e)}")

def _convert_with_pydub(
    filepath: Path,
    source_format: str,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert audio using pydub library."""
    from pydub import AudioSegment
    
    # Load the audio file
    audio = AudioSegment.from_file(str(filepath), format=source_format)
    
    # Apply audio processing options
    if 'volume' in options:
        # Adjust volume (in dB)
        audio = audio + options['volume']
    
    if 'speed' in options:
        # Change speed (requires ffmpeg with rubberband)
        speed = options['speed']
        audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        })
    
    if 'sample_rate' in options:
        # Change sample rate
        audio = audio.set_frame_rate(options['sample_rate'])
    
    if 'channels' in options:
        # Change number of channels
        if options['channels'] == 1:
            audio = audio.set_channels(1)
        elif options['channels'] == 2:
            audio = audio.set_channels(2)
    
    if 'trim' in options:
        # Trim audio (start_ms, end_ms)
        start_ms, end_ms = options['trim']
        audio = audio[start_ms:end_ms]
    
    # Set export parameters
    export_params = {}
    
    if 'bitrate' in options:
        export_params['bitrate'] = options['bitrate']
    
    # Export to target format
    audio.export(str(output_path), format=target_format, **export_params)
    
    return str(output_path)

def _convert_with_ffmpeg(
    filepath: Path,
    source_format: str,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert audio using ffmpeg directly."""
    import subprocess
    
    # Basic ffmpeg command
    cmd = ['ffmpeg', '-i', str(filepath)]
    
    # Add options
    if 'volume' in options:
        # Volume adjustment in dB
        cmd.extend(['-filter:a', f'volume={options["volume"]}dB'])
    
    if 'speed' in options:
        # Speed adjustment
        cmd.extend(['-filter:a', f'atempo={options["speed"]}'])
    
    if 'sample_rate' in options:
        # Sample rate
        cmd.extend(['-ar', str(options['sample_rate'])])
    
    if 'channels' in options:
        # Number of channels
        cmd.extend(['-ac', str(options['channels'])])
    
    if 'bitrate' in options:
        # Bitrate
        cmd.extend(['-b:a', options['bitrate']])
    
    if 'trim' in options:
        # Trim (start_seconds, duration_seconds)
        start_sec, duration_sec = options['trim']
        cmd.extend(['-ss', str(start_sec), '-t', str(duration_sec)])
    
    # Add output file
    cmd.append(str(output_path))
    
    # Run ffmpeg
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    except subprocess.SubprocessError as e:
        logger.error(f"Error running ffmpeg: {str(e)}")
        raise RuntimeError(f"Failed to convert audio with ffmpeg: {str(e)}") 