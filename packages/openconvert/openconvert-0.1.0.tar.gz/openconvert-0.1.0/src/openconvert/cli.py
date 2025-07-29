"""
Command-line interface for AGConvert.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from . import __version__
from .converter import open_convert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="AGConvert - A versatile file and data conversion tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  agconvert image.png image.jpg                # Convert PNG to JPG
  agconvert document.docx document.pdf         # Convert DOCX to PDF
  agconvert audio.mp3 audio.wav                # Convert MP3 to WAV
  agconvert video.mp4 video.gif                # Convert MP4 to GIF
  agconvert data.json data.yaml                # Convert JSON to YAML
  agconvert --options '{"quality": 90}' image.png image.jpg  # With options
"""
    )
    
    parser.add_argument(
        "input_file",
        help="Path to the input file"
    )
    
    parser.add_argument(
        "output_file",
        help="Path to the output file"
    )
    
    parser.add_argument(
        "--source-format",
        help="Source file format (if not specified, will be inferred from input file extension)"
    )
    
    parser.add_argument(
        "--target-format",
        help="Target file format (if not specified, will be inferred from output file extension)"
    )
    
    parser.add_argument(
        "--options",
        help="Additional conversion options as JSON string",
        default="{}"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"AGConvert {__version__}"
    )
    
    return parser.parse_args()

def parse_options(options_str: str) -> Dict[str, Any]:
    """Parse options from JSON string."""
    try:
        return json.loads(options_str)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing options: {str(e)}")
        logger.error("Options must be a valid JSON string")
        sys.exit(1)

def infer_format(filepath: str) -> str:
    """Infer file format from file extension."""
    ext = os.path.splitext(filepath)[1].lower().lstrip('.')
    
    # Handle special cases
    if ext == 'jpeg':
        return 'jpg'
    elif ext == 'tif':
        return 'tiff'
    elif ext == 'yml':
        return 'yaml'
    elif ext == 'htm':
        return 'html'
    elif ext == 'markdown':
        return 'md'
    elif ext == 'tex':
        return 'latex'
    
    return ext

def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse options
    options = parse_options(args.options)
    
    # Infer formats if not specified
    source_format = args.source_format or infer_format(args.input_file)
    target_format = args.target_format or infer_format(args.output_file)
    
    if not source_format:
        logger.error("Could not determine source format. Please specify --source-format")
        sys.exit(1)
    
    if not target_format:
        logger.error("Could not determine target format. Please specify --target-format")
        sys.exit(1)
    
    try:
        # Perform the conversion
        output_path = open_convert(
            filepath=args.input_file,
            source_format=source_format,
            target_format=target_format,
            output_path=args.output_file,
            options=options
        )
        
        logger.info(f"Conversion successful: {args.input_file} → {output_path}")
    
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 