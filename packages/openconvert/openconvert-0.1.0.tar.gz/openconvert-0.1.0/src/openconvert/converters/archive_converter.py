"""
Archive converter module for handling archive format conversions.
"""

import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'zip': ['rar', '7z', 'tar', 'gz'],
    'rar': ['zip', '7z', 'tar', 'gz'],
    '7z': ['zip', 'rar', 'tar', 'gz'],
    'tar': ['zip', 'rar', '7z', 'gz'],
    'gz': ['zip', 'rar', '7z', 'tar']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert an archive from one format to another.
    
    Args:
        filepath: Path to the source archive file
        source_format: Source archive format
        target_format: Target archive format
        output_path: Path to save the converted archive
        options: Additional conversion options
        
    Returns:
        Path to the converted archive
        
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
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Extract the source archive
            extract_dir = _extract_archive(filepath, source_format, temp_dir_path)
            
            # Create the target archive
            return _create_archive(extract_dir, target_format, output_path, options)
    
    except Exception as e:
        logger.error(f"Error converting {filepath} to {target_format}: {str(e)}")
        raise RuntimeError(f"Failed to convert {filepath} to {target_format}: {str(e)}")

def _extract_archive(
    filepath: Path,
    format: str,
    output_dir: Path
) -> Path:
    """Extract an archive to a directory."""
    if format == 'zip':
        return _extract_zip(filepath, output_dir)
    elif format == 'rar':
        return _extract_rar(filepath, output_dir)
    elif format == '7z':
        return _extract_7z(filepath, output_dir)
    elif format == 'tar':
        return _extract_tar(filepath, output_dir)
    elif format == 'gz':
        return _extract_gz(filepath, output_dir)
    else:
        raise ValueError(f"Unsupported archive format for extraction: {format}")

def _create_archive(
    source_dir: Path,
    format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Create an archive from a directory."""
    if format == 'zip':
        return _create_zip(source_dir, output_path, options)
    elif format == 'rar':
        return _create_rar(source_dir, output_path, options)
    elif format == '7z':
        return _create_7z(source_dir, output_path, options)
    elif format == 'tar':
        return _create_tar(source_dir, output_path, options)
    elif format == 'gz':
        return _create_gz(source_dir, output_path, options)
    else:
        raise ValueError(f"Unsupported archive format for creation: {format}")

def _extract_zip(filepath: Path, output_dir: Path) -> Path:
    """Extract a ZIP archive."""
    import zipfile
    
    with zipfile.ZipFile(filepath, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
    
    return output_dir

def _extract_rar(filepath: Path, output_dir: Path) -> Path:
    """Extract a RAR archive."""
    try:
        import rarfile
        
        with rarfile.RarFile(filepath) as rf:
            rf.extractall(output_dir)
        
        return output_dir
    
    except ImportError:
        # Try using unrar command-line tool
        import subprocess
        
        try:
            cmd = ['unrar', 'x', str(filepath), str(output_dir)]
            subprocess.run(cmd, check=True, capture_output=True)
            return output_dir
        
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to extract RAR archive: {str(e)}. Please install rarfile or unrar.")

def _extract_7z(filepath: Path, output_dir: Path) -> Path:
    """Extract a 7Z archive."""
    try:
        import py7zr
        
        with py7zr.SevenZipFile(filepath, mode='r') as z:
            z.extractall(output_dir)
        
        return output_dir
    
    except ImportError:
        # Try using 7z command-line tool
        import subprocess
        
        try:
            cmd = ['7z', 'x', str(filepath), f'-o{output_dir}']
            subprocess.run(cmd, check=True, capture_output=True)
            return output_dir
        
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to extract 7Z archive: {str(e)}. Please install py7zr or 7z.")

def _extract_tar(filepath: Path, output_dir: Path) -> Path:
    """Extract a TAR archive."""
    import tarfile
    
    with tarfile.open(filepath, 'r') as tar:
        tar.extractall(output_dir)
    
    return output_dir

def _extract_gz(filepath: Path, output_dir: Path) -> Path:
    """Extract a GZ archive."""
    import gzip
    import tarfile
    
    # Check if it's a tar.gz file
    if filepath.name.endswith('.tar.gz') or filepath.name.endswith('.tgz'):
        with tarfile.open(filepath, 'r:gz') as tar:
            tar.extractall(output_dir)
        return output_dir
    
    # Otherwise, it's a single gzipped file
    with gzip.open(filepath, 'rb') as f_in:
        output_file = output_dir / filepath.with_suffix('').name
        with open(output_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    
    return output_dir

def _create_zip(source_dir: Path, output_path: Path, options: Dict[str, Any]) -> str:
    """Create a ZIP archive."""
    import zipfile
    
    compression = options.get('compression', zipfile.ZIP_DEFLATED)
    compression_level = options.get('compression_level', 9)  # 0-9, 9 is highest
    
    with zipfile.ZipFile(output_path, 'w', compression=compression, compresslevel=compression_level) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(source_dir)
                zipf.write(file_path, arcname)
    
    return str(output_path)

def _create_rar(source_dir: Path, output_path: Path, options: Dict[str, Any]) -> str:
    """Create a RAR archive."""
    # RAR creation requires command-line tool
    import subprocess
    
    try:
        # Determine compression level
        compression_level = options.get('compression_level', 5)  # 0-5, 5 is highest
        
        cmd = ['rar', f'a{compression_level}', str(output_path), str(source_dir)]
        subprocess.run(cmd, check=True, capture_output=True)
        return str(output_path)
    
    except subprocess.SubprocessError as e:
        raise RuntimeError(f"Failed to create RAR archive: {str(e)}. Please install rar command-line tool.")

def _create_7z(source_dir: Path, output_path: Path, options: Dict[str, Any]) -> str:
    """Create a 7Z archive."""
    try:
        import py7zr
        
        compression_level = options.get('compression_level', 9)  # 0-9, 9 is highest
        
        with py7zr.SevenZipFile(output_path, 'w', compression_level=compression_level) as z:
            z.writeall(source_dir)
        
        return str(output_path)
    
    except ImportError:
        # Try using 7z command-line tool
        import subprocess
        
        try:
            compression_level = options.get('compression_level', 9)  # 0-9, 9 is highest
            
            cmd = ['7z', 'a', f'-mx={compression_level}', str(output_path), f'{source_dir}/*']
            subprocess.run(cmd, check=True, capture_output=True, shell=True)
            return str(output_path)
        
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Failed to create 7Z archive: {str(e)}. Please install py7zr or 7z.")

def _create_tar(source_dir: Path, output_path: Path, options: Dict[str, Any]) -> str:
    """Create a TAR archive."""
    import tarfile
    
    with tarfile.open(output_path, 'w') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))
    
    return str(output_path)

def _create_gz(source_dir: Path, output_path: Path, options: Dict[str, Any]) -> str:
    """Create a GZ archive."""
    import tarfile
    
    # If there are multiple files, create a tar.gz
    files = list(source_dir.glob('*'))
    if len(files) > 1 or any(f.is_dir() for f in files):
        with tarfile.open(output_path, 'w:gz') as tar:
            tar.add(source_dir, arcname='')
    else:
        # If there's only one file, create a simple .gz
        import gzip
        
        input_file = files[0]
        with open(input_file, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    return str(output_path) 