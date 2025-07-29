"""
3D model converter module for handling 3D model format conversions.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Union, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Define supported conversions
SUPPORTED_CONVERSIONS = {
    'stl': ['obj', 'fbx', 'ply'],
    'obj': ['stl', 'fbx', 'ply'],
    'fbx': ['stl', 'obj', 'ply'],
    'ply': ['stl', 'obj', 'fbx']
}

def convert(
    filepath: Union[str, Path],
    source_format: str,
    target_format: str,
    output_path: Union[str, Path],
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convert a 3D model from one format to another.
    
    Args:
        filepath: Path to the source model file
        source_format: Source model format
        target_format: Target model format
        output_path: Path to save the converted model
        options: Additional conversion options
        
    Returns:
        Path to the converted model
        
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
        # Try using trimesh for model conversion
        return _convert_with_trimesh(filepath, source_format, target_format, output_path, options)
    
    except ImportError:
        logger.warning("trimesh not installed. Trying alternative method...")
        
        # Try using Blender for conversion
        return _convert_with_blender(filepath, source_format, target_format, output_path, options)

def _convert_with_trimesh(
    filepath: Path,
    source_format: str,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert 3D model using trimesh library."""
    import trimesh
    
    # Load the model
    mesh = trimesh.load(str(filepath))
    
    # Apply transformations if specified
    if 'scale' in options:
        scale = options['scale']
        if isinstance(scale, (int, float)):
            # Uniform scaling
            mesh.apply_scale(scale)
        elif isinstance(scale, (list, tuple)) and len(scale) == 3:
            # Non-uniform scaling
            mesh.apply_scale(scale)
    
    if 'rotation' in options:
        # Rotation in degrees around x, y, z axes
        import numpy as np
        from scipy.spatial.transform import Rotation as R
        
        rotation = options['rotation']
        if isinstance(rotation, (list, tuple)) and len(rotation) == 3:
            # Convert degrees to radians
            rotation_rad = [np.radians(r) for r in rotation]
            r = R.from_euler('xyz', rotation_rad)
            mesh.apply_transform(np.eye(4))
            mesh.apply_transform(np.vstack((np.hstack((r.as_matrix(), np.zeros((3, 1)))), [0, 0, 0, 1])))
    
    if 'translation' in options:
        # Translation along x, y, z axes
        translation = options['translation']
        if isinstance(translation, (list, tuple)) and len(translation) == 3:
            mesh.apply_translation(translation)
    
    # Export to target format
    export_options = {}
    
    if target_format == 'stl' and 'ascii' in options:
        export_options['file_type'] = 'ascii' if options['ascii'] else 'binary'
    
    mesh.export(str(output_path), file_type=target_format, **export_options)
    
    return str(output_path)

def _convert_with_blender(
    filepath: Path,
    source_format: str,
    target_format: str,
    output_path: Path,
    options: Dict[str, Any]
) -> str:
    """Convert 3D model using Blender."""
    import subprocess
    import tempfile
    
    # Create a temporary Python script for Blender
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as script_file:
        script_path = script_file.name
        
        # Write Blender Python script
        script_file.write(f"""
import bpy
import os
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the model
if '{source_format}' == 'stl':
    bpy.ops.import_mesh.stl(filepath='{filepath}')
elif '{source_format}' == 'obj':
    bpy.ops.import_scene.obj(filepath='{filepath}')
elif '{source_format}' == 'fbx':
    bpy.ops.import_scene.fbx(filepath='{filepath}')
elif '{source_format}' == 'ply':
    bpy.ops.import_mesh.ply(filepath='{filepath}')

# Select all objects
bpy.ops.object.select_all(action='SELECT')

# Apply transformations
""")
        
        # Add transformation code if options are provided
        if 'scale' in options:
            scale = options['scale']
            if isinstance(scale, (int, float)):
                script_file.write(f"bpy.ops.transform.resize(value=({scale}, {scale}, {scale}))\n")
            elif isinstance(scale, (list, tuple)) and len(scale) == 3:
                script_file.write(f"bpy.ops.transform.resize(value=({scale[0]}, {scale[1]}, {scale[2]}))\n")
        
        if 'rotation' in options:
            rotation = options['rotation']
            if isinstance(rotation, (list, tuple)) and len(rotation) == 3:
                script_file.write(f"""
bpy.ops.transform.rotate(value={math.radians(rotation[0])}, orient_axis='X')
bpy.ops.transform.rotate(value={math.radians(rotation[1])}, orient_axis='Y')
bpy.ops.transform.rotate(value={math.radians(rotation[2])}, orient_axis='Z')
""")
        
        if 'translation' in options:
            translation = options['translation']
            if isinstance(translation, (list, tuple)) and len(translation) == 3:
                script_file.write(f"bpy.ops.transform.translate(value=({translation[0]}, {translation[1]}, {translation[2]}))\n")
        
        # Add export code
        script_file.write(f"""
# Export the model
if '{target_format}' == 'stl':
    bpy.ops.export_mesh.stl(filepath='{output_path}', {'ascii=True' if options.get('ascii', False) else ''})
elif '{target_format}' == 'obj':
    bpy.ops.export_scene.obj(filepath='{output_path}')
elif '{target_format}' == 'fbx':
    bpy.ops.export_scene.fbx(filepath='{output_path}')
elif '{target_format}' == 'ply':
    bpy.ops.export_mesh.ply(filepath='{output_path}')
""")
    
    try:
        # Run Blender with the script
        cmd = ['blender', '--background', '--python', script_path]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Clean up the temporary script
        os.unlink(script_path)
        
        return str(output_path)
    
    except subprocess.SubprocessError as e:
        # Clean up the temporary script
        os.unlink(script_path)
        
        logger.error(f"Error running Blender: {str(e)}")
        raise RuntimeError(f"Failed to convert model with Blender: {str(e)}. Please install Blender.") 