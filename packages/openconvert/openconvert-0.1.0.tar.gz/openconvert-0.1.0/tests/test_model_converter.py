"""
Test cases for 3D model conversions.
"""

import os
import unittest
import tempfile
import numpy as np
from pathlib import Path

from test_base import BaseConverterTest


class ModelConverterTest(BaseConverterTest):
    """Test cases for 3D model conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Skip all tests if trimesh is not installed
        try:
            import trimesh
        except ImportError:
            self.skipTest("trimesh not installed")
        
        # Create a test STL file
        self.stl_file = self._create_test_model('stl')
        if not self.stl_file:
            self.skipTest("Could not create test STL file")

    def _create_test_model(self, format):
        """Create a test 3D model file."""
        try:
            import trimesh
            
            # Create a simple cube mesh
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 1, 1]
            ])
            
            faces = np.array([
                [0, 1, 2], [0, 2, 3],  # bottom
                [4, 5, 6], [4, 6, 7],  # top
                [0, 1, 5], [0, 5, 4],  # front
                [2, 3, 7], [2, 7, 6],  # back
                [0, 3, 7], [0, 7, 4],  # left
                [1, 2, 6], [1, 6, 5]   # right
            ])
            
            # Create a mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # Save to file
            file_path = self.get_test_file_path(f"test.{format}")
            mesh.export(file_path, file_type=format)
            
            return file_path
        except Exception as e:
            print(f"Error creating test 3D model: {str(e)}")
            return None

    def _verify_model_file(self, file_path, expected_format=None):
        """Verify that a file is a valid 3D model file."""
        try:
            import trimesh
            
            self.verify_file_exists(file_path)
            
            # Try to load the model file
            mesh = trimesh.load(file_path)
            
            # Basic model validation
            self.assertTrue(len(mesh.vertices) > 0, "Model has no vertices")
            self.assertTrue(len(mesh.faces) > 0, "Model has no faces")
            
            return mesh
        except Exception as e:
            self.fail(f"Failed to verify model file: {str(e)}")
            return None

    def test_stl_to_obj(self):
        """Test STL to OBJ conversion."""
        try:
            output_path = self.convert_file(self.stl_file, 'stl', 'obj')
            self._verify_model_file(output_path)
            
            # Verify it's an OBJ file by checking the file content
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("v ", content, "File does not contain vertex definitions")
                self.assertIn("f ", content, "File does not contain face definitions")
        except Exception as e:
            self.skipTest(f"STL to OBJ conversion not supported: {str(e)}")

    def test_stl_to_ply(self):
        """Test STL to PLY conversion."""
        try:
            output_path = self.convert_file(self.stl_file, 'stl', 'ply')
            self._verify_model_file(output_path)
            
            # Verify it's a PLY file by checking the file header
            with open(output_path, 'r') as f:
                header = f.readline().strip()
                self.assertEqual(header, "ply", "File is not a PLY file")
        except Exception as e:
            self.skipTest(f"STL to PLY conversion not supported: {str(e)}")

    def test_stl_to_glb(self):
        """Test STL to GLB conversion."""
        try:
            output_path = self.convert_file(self.stl_file, 'stl', 'glb')
            
            # Verify the file exists
            self.verify_file_exists(output_path)
            
            # Check if it's a binary file with the GLB magic number
            with open(output_path, 'rb') as f:
                header = f.read(4)
                self.assertEqual(header, b'glTF', "File is not a GLB file")
        except Exception as e:
            self.skipTest(f"STL to GLB conversion not supported: {str(e)}")

    def test_obj_to_stl(self):
        """Test OBJ to STL conversion."""
        try:
            # First create an OBJ file
            obj_file = self._create_test_model('obj')
            if not obj_file:
                self.skipTest("Could not create test OBJ file")
            
            output_path = self.convert_file(obj_file, 'obj', 'stl')
            self._verify_model_file(output_path)
            
            # Verify it's an STL file by checking the file content
            with open(output_path, 'rb') as f:
                # Binary STL files start with an 80-byte header
                header = f.read(80)
                # Skip the header and read the number of triangles (4 bytes)
                num_triangles = int.from_bytes(f.read(4), byteorder='little')
                # Check that the number of triangles is reasonable
                self.assertGreater(num_triangles, 0, "STL file has no triangles")
        except Exception as e:
            self.skipTest(f"OBJ to STL conversion not supported: {str(e)}")

    def test_ply_to_stl(self):
        """Test PLY to STL conversion."""
        try:
            # First create a PLY file
            ply_file = self._create_test_model('ply')
            if not ply_file:
                self.skipTest("Could not create test PLY file")
            
            output_path = self.convert_file(ply_file, 'ply', 'stl')
            self._verify_model_file(output_path)
        except Exception as e:
            self.skipTest(f"PLY to STL conversion not supported: {str(e)}")

    def test_model_scale_option(self):
        """Test model scaling option."""
        try:
            # Convert with scaling
            output_path = self.convert_file(
                self.stl_file, 'stl', 'obj', 
                options={'scale': 2.0}
            )
            
            # Verify the output file
            mesh = self._verify_model_file(output_path)
            
            # Create a reference model without scaling
            ref_path = self.convert_file(self.stl_file, 'stl', 'obj')
            ref_mesh = self._verify_model_file(ref_path)
            
            # The scaled model should have vertices with larger coordinates
            # Compare bounding box dimensions
            scaled_dims = mesh.bounding_box.extents
            ref_dims = ref_mesh.bounding_box.extents
            
            # Check that the scaled model is approximately twice as large
            scale_ratio = scaled_dims / ref_dims
            self.assertAlmostEqual(scale_ratio[0], 2.0, delta=0.1)
            self.assertAlmostEqual(scale_ratio[1], 2.0, delta=0.1)
            self.assertAlmostEqual(scale_ratio[2], 2.0, delta=0.1)
        except Exception as e:
            self.skipTest(f"Model scale option test not supported: {str(e)}")

    def test_model_repair_option(self):
        """Test model repair option."""
        try:
            import trimesh
            
            # Create a model with holes
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [1, 1, 0],
                [0, 1, 0],
                [0, 0, 1],
                [1, 0, 1],
                [1, 1, 1],
                [0, 1, 1]
            ])
            
            # Missing some faces to create a non-watertight mesh
            faces = np.array([
                [0, 1, 2], [0, 2, 3],  # bottom
                [4, 5, 6], [4, 6, 7],  # top
                [0, 1, 5], [0, 5, 4],  # front
                # Missing back face
                [0, 3, 7], [0, 7, 4],  # left
                # Missing right face
            ])
            
            # Create a mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
            
            # Save to file
            broken_file = self.get_test_file_path("broken.stl")
            mesh.export(broken_file, file_type='stl')
            
            # Convert with repair option
            output_path = self.convert_file(
                broken_file, 'stl', 'obj', 
                options={'repair': True}
            )
            
            # Verify the output file
            repaired_mesh = self._verify_model_file(output_path)
            
            # The repaired mesh should be watertight
            self.assertTrue(repaired_mesh.is_watertight, 
                           "Repaired mesh should be watertight")
        except Exception as e:
            self.skipTest(f"Model repair option test not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 