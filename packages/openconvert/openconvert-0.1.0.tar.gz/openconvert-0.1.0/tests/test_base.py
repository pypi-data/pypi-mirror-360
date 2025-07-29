"""
Base test class for AGConvert tests.
"""

import os
import shutil
import tempfile
import unittest
import sys
from pathlib import Path

# Add the src directory to the path so we can import agconvert
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agconvert import open_convert


class BaseConverterTest(unittest.TestCase):
    """Base class for converter tests."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)

    def tearDown(self):
        """Clean up after tests."""
        pass

    def get_test_file_path(self, filename):
        """Get the path to a test file."""
        return os.path.join(self.test_dir, filename)

    def convert_file(self, source_path, source_format, target_format, options=None):
        """Convert a file and return the output path."""
        output_path = self.get_test_file_path(f"output.{target_format}")
        
        try:
            result = open_convert(
                filepath=source_path,
                source_format=source_format,
                target_format=target_format,
                output_path=output_path,
                options=options
            )
            
            # Verify the output file exists
            self.assertTrue(os.path.exists(result), f"Output file {result} does not exist")
            
            return result
        except Exception as e:
            self.fail(f"Conversion failed: {str(e)}")

    def create_text_file(self, content, filename="test.txt"):
        """Create a text file with the given content."""
        file_path = self.get_test_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def create_image_file(self, filename="test.png", size=(300, 200), mode="RGB", color="white"):
        """Create a test image file."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a simple image
            width, height = size if isinstance(size, tuple) else (size, size)
            img = Image.new(mode, (width, height), color=color)
            draw = ImageDraw.Draw(img)
            
            # Draw a rectangle
            draw.rectangle(
                [(20, 20), (width - 20, height - 20)],
                outline='blue',
                width=2
            )
            
            # Add text
            draw.text(
                (width // 2 - 40, height // 2 - 10),
                'AGConvert',
                fill='black'
            )
            
            # Save the image
            file_path = self.get_test_file_path(filename)
            img.save(file_path)
            
            return file_path
        except ImportError:
            self.skipTest("PIL not installed")
        except Exception as e:
            self.skipTest(f"Could not create test image file: {str(e)}")

    def create_json_file(self, data, filename="test.json"):
        """Create a JSON file with the given data."""
        import json
        
        file_path = self.get_test_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        
        return file_path

    def create_yaml_file(self, data, filename="test.yaml"):
        """Create a YAML file with the given data."""
        try:
            import yaml
            
            file_path = self.get_test_file_path(filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return file_path
        except ImportError:
            self.skipTest("PyYAML not installed")

    def create_xml_file(self, content, filename="test.xml"):
        """Create an XML file with the given content."""
        file_path = self.get_test_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    def create_html_file(self, content, filename="test.html"):
        """Create an HTML file with the given content."""
        file_path = self.get_test_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    def create_markdown_file(self, content, filename="test.md"):
        """Create a Markdown file with the given content."""
        file_path = self.get_test_file_path(filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path

    def create_complex_image_file(self, filename="complex.png", size=(800, 600)):
        """Create a complex test image with gradients and patterns."""
        try:
            from PIL import Image, ImageDraw
            import math
            
            width, height = size
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Create a gradient background
            for y in range(height):
                for x in range(width):
                    r = int(255 * x / width)
                    g = int(255 * y / height)
                    b = int(255 * (x + y) / (width + height))
                    draw.point((x, y), fill=(r, g, b))
            
            # Draw some patterns
            for i in range(0, width, 10):
                draw.line([(i, 0), (i, height)], fill=(255, 255, 255), width=1)
            
            for i in range(0, height, 10):
                draw.line([(0, i), (width, i)], fill=(255, 255, 255), width=1)
            
            # Draw some circles
            for i in range(10):
                x = int(width * (0.1 + 0.08 * i))
                y = int(height * 0.5)
                radius = int(min(width, height) * 0.05)
                draw.ellipse(
                    [(x - radius, y - radius), (x + radius, y + radius)],
                    outline='blue',
                    width=2
                )
            
            # Save the image
            file_path = self.get_test_file_path(filename)
            img.save(file_path)
            
            return file_path
        except ImportError:
            self.skipTest("PIL not installed")
        except Exception as e:
            self.skipTest(f"Could not create complex test image file: {str(e)}")

    def verify_file_exists(self, file_path):
        """Verify that a file exists."""
        self.assertTrue(os.path.exists(file_path), f"File {file_path} does not exist")
        self.assertTrue(os.path.getsize(file_path) > 0, f"File {file_path} is empty")
        
    def verify_image_file(self, file_path, expected_format=None):
        """Verify that a file is a valid image file."""
        try:
            from PIL import Image
            
            self.verify_file_exists(file_path)
            
            # Try to open the image
            with Image.open(file_path) as img:
                # Check format if specified
                if expected_format:
                    self.assertEqual(img.format.lower(), expected_format.lower(),
                                    f"Image format is {img.format}, expected {expected_format.upper()}")
                
                # Basic image validation
                self.assertTrue(img.width > 0, "Image width is 0")
                self.assertTrue(img.height > 0, "Image height is 0")
        except ImportError:
            self.skipTest("PIL not installed")
        except Exception as e:
            self.fail(f"Failed to verify image file: {str(e)}")

    def verify_text_file(self, file_path, expected_content=None):
        """Verify that a file is a valid text file."""
        self.verify_file_exists(file_path)
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Check content if specified
        if expected_content:
            self.assertIn(expected_content, content,
                         f"Expected content not found in file") 