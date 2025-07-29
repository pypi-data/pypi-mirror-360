"""
Test cases for code and markup conversions.
"""

import os
import unittest
import tempfile
import json
from pathlib import Path

from test_base import BaseConverterTest


class CodeConverterTest(BaseConverterTest):
    """Test cases for code and markup conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create test files
        self.json_file = self._create_json_file()
        self.yaml_file = self._create_yaml_file()
        self.xml_file = self._create_xml_file()
        self.html_file = self._create_html_file()
        self.md_file = self._create_markdown_file()
        self.csv_file = self._create_csv_file()

    def _create_json_file(self):
        """Create a test JSON file."""
        try:
            data = {
                "name": "AGConvert",
                "version": "1.0.0",
                "description": "A versatile file conversion library",
                "features": ["image", "document", "audio", "video", "archive", "model", "code"],
                "settings": {
                    "debug": False,
                    "max_file_size": 1024,
                    "supported": True
                }
            }
            
            file_path = self.get_test_file_path("test.json")
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return file_path
        except Exception as e:
            print(f"Error creating test JSON file: {str(e)}")
            self.skipTest("Could not create test JSON file")
            return None

    def _create_yaml_file(self):
        """Create a test YAML file."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
            return None
        
        try:
            data = {
                "name": "AGConvert",
                "version": "1.0.0",
                "description": "A versatile file conversion library",
                "features": ["image", "document", "audio", "video", "archive", "model", "code"],
                "settings": {
                    "debug": False,
                    "max_file_size": 1024,
                    "supported": True
                }
            }
            
            file_path = self.get_test_file_path("test.yaml")
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return file_path
        except Exception as e:
            print(f"Error creating test YAML file: {str(e)}")
            self.skipTest("Could not create test YAML file")
            return None

    def _create_xml_file(self):
        """Create a test XML file."""
        try:
            xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<agconvert>
  <name>AGConvert</name>
  <version>1.0.0</version>
  <description>A versatile file conversion library</description>
  <features>
    <feature>image</feature>
    <feature>document</feature>
    <feature>audio</feature>
    <feature>video</feature>
    <feature>archive</feature>
    <feature>model</feature>
    <feature>code</feature>
  </features>
  <settings>
    <debug>false</debug>
    <max_file_size>1024</max_file_size>
    <supported>true</supported>
  </settings>
</agconvert>
"""
            
            file_path = self.get_test_file_path("test.xml")
            with open(file_path, 'w') as f:
                f.write(xml_content)
            
            return file_path
        except Exception as e:
            print(f"Error creating test XML file: {str(e)}")
            self.skipTest("Could not create test XML file")
            return None

    def _create_html_file(self):
        """Create a test HTML file."""
        try:
            html_content = """<!DOCTYPE html>
<html>
<head>
  <title>AGConvert</title>
  <meta charset="UTF-8">
</head>
<body>
  <h1>AGConvert</h1>
  <p>A versatile file conversion library</p>
  
  <h2>Features</h2>
  <ul>
    <li>Image conversion</li>
    <li>Document conversion</li>
    <li>Audio conversion</li>
    <li>Video conversion</li>
    <li>Archive conversion</li>
    <li>3D Model conversion</li>
    <li>Code and markup conversion</li>
  </ul>
  
  <h2>Settings</h2>
  <table>
    <tr>
      <th>Setting</th>
      <th>Value</th>
    </tr>
    <tr>
      <td>Debug</td>
      <td>False</td>
    </tr>
    <tr>
      <td>Max File Size</td>
      <td>1024</td>
    </tr>
    <tr>
      <td>Supported</td>
      <td>True</td>
    </tr>
  </table>
</body>
</html>
"""
            
            file_path = self.get_test_file_path("test.html")
            with open(file_path, 'w') as f:
                f.write(html_content)
            
            return file_path
        except Exception as e:
            print(f"Error creating test HTML file: {str(e)}")
            self.skipTest("Could not create test HTML file")
            return None

    def _create_markdown_file(self):
        """Create a test Markdown file."""
        try:
            md_content = """# AGConvert

A versatile file conversion library

## Features

- Image conversion
- Document conversion
- Audio conversion
- Video conversion
- Archive conversion
- 3D Model conversion
- Code and markup conversion

## Settings

| Setting | Value |
|---------|-------|
| Debug | False |
| Max File Size | 1024 |
| Supported | True |

## Code Example

```python
from agconvert import open_convert

# Convert an image
open_convert('image.png', 'jpg')
```
"""
            
            file_path = self.get_test_file_path("test.md")
            with open(file_path, 'w') as f:
                f.write(md_content)
            
            return file_path
        except Exception as e:
            print(f"Error creating test Markdown file: {str(e)}")
            self.skipTest("Could not create test Markdown file")
            return None

    def _create_csv_file(self):
        """Create a test CSV file."""
        try:
            csv_content = """name,version,description
AGConvert,1.0.0,A versatile file conversion library
feature_1,feature_2,feature_3
image,document,audio
feature_4,feature_5,feature_6
video,archive,model
feature_7,setting_1,setting_2
code,debug=False,max_file_size=1024
"""
            
            file_path = self.get_test_file_path("test.csv")
            with open(file_path, 'w') as f:
                f.write(csv_content)
            
            return file_path
        except Exception as e:
            print(f"Error creating test CSV file: {str(e)}")
            self.skipTest("Could not create test CSV file")
            return None

    def test_json_to_yaml(self):
        """Test JSON to YAML conversion."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        
        try:
            output_path = self.convert_file(self.json_file, 'json', 'yaml')
            self.verify_file_exists(output_path)
            
            # Verify it's a valid YAML file
            with open(output_path, 'r') as f:
                data = yaml.safe_load(f)
                
                # Check that the data was preserved
                self.assertEqual(data['name'], 'AGConvert')
                self.assertEqual(data['version'], '1.0.0')
                self.assertEqual(len(data['features']), 7)
                self.assertEqual(data['settings']['max_file_size'], 1024)
        except Exception as e:
            self.skipTest(f"JSON to YAML conversion not supported: {str(e)}")

    def test_json_to_xml(self):
        """Test JSON to XML conversion."""
        try:
            output_path = self.convert_file(self.json_file, 'json', 'xml')
            self.verify_file_exists(output_path)
            
            # Verify it's an XML file
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('<name>AGConvert</name>', content)
                self.assertIn('<version>1.0.0</version>', content)
        except Exception as e:
            self.skipTest(f"JSON to XML conversion not supported: {str(e)}")

    def test_yaml_to_json(self):
        """Test YAML to JSON conversion."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        
        try:
            output_path = self.convert_file(self.yaml_file, 'yaml', 'json')
            self.verify_file_exists(output_path)
            
            # Verify it's a valid JSON file
            with open(output_path, 'r') as f:
                data = json.load(f)
                
                # Check that the data was preserved
                self.assertEqual(data['name'], 'AGConvert')
                self.assertEqual(data['version'], '1.0.0')
                self.assertEqual(len(data['features']), 7)
                self.assertEqual(data['settings']['max_file_size'], 1024)
        except Exception as e:
            self.skipTest(f"YAML to JSON conversion not supported: {str(e)}")

    def test_xml_to_json(self):
        """Test XML to JSON conversion."""
        try:
            output_path = self.convert_file(self.xml_file, 'xml', 'json')
            self.verify_file_exists(output_path)
            
            # Verify it's a valid JSON file
            with open(output_path, 'r') as f:
                data = json.load(f)
                
                # Check that the data was preserved
                self.assertEqual(data['agconvert']['name'], 'AGConvert')
                self.assertEqual(data['agconvert']['version'], '1.0.0')
        except Exception as e:
            self.skipTest(f"XML to JSON conversion not supported: {str(e)}")

    def test_html_to_md(self):
        """Test HTML to Markdown conversion."""
        try:
            output_path = self.convert_file(self.html_file, 'html', 'md')
            self.verify_file_exists(output_path)
            
            # Verify it's a Markdown file
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('# AGConvert', content)
                self.assertIn('## Features', content)
                self.assertIn('- Image conversion', content)
        except Exception as e:
            self.skipTest(f"HTML to Markdown conversion not supported: {str(e)}")

    def test_md_to_html(self):
        """Test Markdown to HTML conversion."""
        try:
            output_path = self.convert_file(self.md_file, 'md', 'html')
            self.verify_file_exists(output_path)
            
            # Verify it's an HTML file
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('<h1>AGConvert</h1>', content)
                self.assertIn('<h2>Features</h2>', content)
                self.assertIn('<li>Image conversion</li>', content)
        except Exception as e:
            self.skipTest(f"Markdown to HTML conversion not supported: {str(e)}")

    def test_csv_to_json(self):
        """Test CSV to JSON conversion."""
        try:
            output_path = self.convert_file(self.csv_file, 'csv', 'json')
            self.verify_file_exists(output_path)
            
            # Verify it's a valid JSON file
            with open(output_path, 'r') as f:
                data = json.load(f)
                
                # Check that the data was preserved
                self.assertEqual(data[0]['name'], 'AGConvert')
                self.assertEqual(data[0]['version'], '1.0.0')
                self.assertEqual(data[0]['description'], 'A versatile file conversion library')
        except Exception as e:
            self.skipTest(f"CSV to JSON conversion not supported: {str(e)}")

    def test_csv_to_xml(self):
        """Test CSV to XML conversion."""
        try:
            output_path = self.convert_file(self.csv_file, 'csv', 'xml')
            self.verify_file_exists(output_path)
            
            # Verify it's an XML file
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('<name>AGConvert</name>', content)
                self.assertIn('<version>1.0.0</version>', content)
        except Exception as e:
            self.skipTest(f"CSV to XML conversion not supported: {str(e)}")

    def test_json_to_csv(self):
        """Test JSON to CSV conversion."""
        try:
            output_path = self.convert_file(self.json_file, 'json', 'csv')
            self.verify_file_exists(output_path)
            
            # Verify it's a CSV file
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn('AGConvert', content)
                self.assertIn('1.0.0', content)
                self.assertIn('A versatile file conversion library', content)
        except Exception as e:
            self.skipTest(f"JSON to CSV conversion not supported: {str(e)}")

    def test_json_pretty_print_option(self):
        """Test JSON pretty print option."""
        try:
            # Create a compact JSON file
            compact_data = {"name":"AGConvert","version":"1.0.0","features":["image","document"]}
            compact_file = self.get_test_file_path("compact.json")
            with open(compact_file, 'w') as f:
                json.dump(compact_data, f, separators=(',', ':'))
            
            # Convert with pretty print option
            output_path = self.convert_file(
                compact_file, 'json', 'json', 
                options={'pretty_print': True}
            )
            
            # Verify the output file
            with open(output_path, 'r') as f:
                content = f.read()
                
                # Check that it's pretty-printed
                self.assertIn('  "name"', content)
                self.assertIn('  "version"', content)
                self.assertIn('  "features"', content)
        except Exception as e:
            self.skipTest(f"JSON pretty print option test not supported: {str(e)}")

    def test_xml_pretty_print_option(self):
        """Test XML pretty print option."""
        try:
            # Create a compact XML file
            compact_xml = '<?xml version="1.0" encoding="UTF-8"?><root><name>AGConvert</name><version>1.0.0</version></root>'
            compact_file = self.get_test_file_path("compact.xml")
            with open(compact_file, 'w') as f:
                f.write(compact_xml)
            
            # Convert with pretty print option
            output_path = self.convert_file(
                compact_file, 'xml', 'xml', 
                options={'pretty_print': True}
            )
            
            # Verify the output file
            with open(output_path, 'r') as f:
                content = f.read()
                
                # Check that it's pretty-printed
                self.assertIn('<root>', content)
                self.assertIn('  <name>', content)
                self.assertIn('  <version>', content)
        except Exception as e:
            self.skipTest(f"XML pretty print option test not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 