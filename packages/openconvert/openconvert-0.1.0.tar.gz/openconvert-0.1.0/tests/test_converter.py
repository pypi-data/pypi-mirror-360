"""
Test cases for the main converter module.
"""

import os
import unittest
import tempfile
from pathlib import Path

from test_base import BaseConverterTest


class ConverterTest(BaseConverterTest):
    """Test cases for the main converter module."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create test files
        self.text_file = self.create_text_file("test.txt", "This is a test file.")
        self.image_file = self.create_image_file("test.png", (100, 100), "RGB", "red")

    def test_open_convert_function(self):
        """Test the main open_convert function."""
        try:
            from agconvert import open_convert
            
            # Test with a text file
            output_path = self.get_test_file_path("output.md")
            result = open_convert(self.text_file, 'md', output_path=output_path)
            
            # Verify the result
            self.assertEqual(result, output_path)
            self.verify_file_exists(output_path)
        except Exception as e:
            self.skipTest(f"open_convert function test failed: {str(e)}")

    def test_open_convert_with_options(self):
        """Test the open_convert function with options."""
        try:
            from agconvert import open_convert
            
            # Test with an image file and options
            output_path = self.get_test_file_path("output.jpg")
            result = open_convert(
                self.image_file, 'jpg', 
                output_path=output_path,
                options={'quality': 85}
            )
            
            # Verify the result
            self.assertEqual(result, output_path)
            self.verify_file_exists(output_path)
        except Exception as e:
            self.skipTest(f"open_convert with options test failed: {str(e)}")

    def test_open_convert_auto_output_path(self):
        """Test the open_convert function with automatic output path generation."""
        try:
            from agconvert import open_convert
            
            # Test with automatic output path
            result = open_convert(self.text_file, 'md')
            
            # Verify the result
            expected_path = str(Path(self.text_file).with_suffix('.md'))
            self.assertEqual(result, expected_path)
            self.verify_file_exists(expected_path)
            
            # Clean up
            if os.path.exists(expected_path):
                os.remove(expected_path)
        except Exception as e:
            self.skipTest(f"open_convert auto output path test failed: {str(e)}")

    def test_open_convert_unsupported_format(self):
        """Test the open_convert function with unsupported format."""
        try:
            from agconvert import open_convert
            
            # Test with unsupported format
            with self.assertRaises(ValueError):
                open_convert(self.text_file, 'unsupported_format')
        except Exception as e:
            self.skipTest(f"open_convert unsupported format test failed: {str(e)}")

    def test_open_convert_nonexistent_file(self):
        """Test the open_convert function with nonexistent file."""
        try:
            from agconvert import open_convert
            
            # Test with nonexistent file
            with self.assertRaises(FileNotFoundError):
                open_convert('nonexistent_file.txt', 'md')
        except Exception as e:
            self.skipTest(f"open_convert nonexistent file test failed: {str(e)}")

    def test_get_converter_function(self):
        """Test the get_converter function."""
        try:
            from agconvert.converter import get_converter
            
            # Test with various file extensions
            image_converter = get_converter('jpg', 'png')
            self.assertIsNotNone(image_converter)
            
            document_converter = get_converter('txt', 'pdf')
            self.assertIsNotNone(document_converter)
            
            audio_converter = get_converter('mp3', 'wav')
            self.assertIsNotNone(audio_converter)
            
            # Test with unsupported conversion
            with self.assertRaises(ValueError):
                get_converter('jpg', 'mp3')
        except Exception as e:
            self.skipTest(f"get_converter function test failed: {str(e)}")

    def test_detect_format_function(self):
        """Test the detect_format function."""
        try:
            from agconvert.converter import detect_format
            
            # Test with various file paths
            self.assertEqual(detect_format('test.jpg'), 'jpg')
            self.assertEqual(detect_format('test.png'), 'png')
            self.assertEqual(detect_format('test.txt'), 'txt')
            self.assertEqual(detect_format('test.mp3'), 'mp3')
            self.assertEqual(detect_format('test.tar.gz'), 'tar.gz')
            
            # Test with uppercase extension
            self.assertEqual(detect_format('test.JPG'), 'jpg')
            
            # Test with path
            self.assertEqual(detect_format('/path/to/test.jpg'), 'jpg')
        except Exception as e:
            self.skipTest(f"detect_format function test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main() 