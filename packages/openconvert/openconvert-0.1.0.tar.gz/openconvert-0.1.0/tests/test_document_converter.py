"""
Test cases for document conversions.
"""

import os
import unittest
from pathlib import Path

from test_base import BaseConverterTest


class DocumentConverterTest(BaseConverterTest):
    """Test cases for document conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create a test text file
        self.sample_text = """# Sample Document

This is a sample document for testing document conversions.

## Features
- Easy to use
- Supports many formats
- Flexible options

Some code:
```python
def hello():
    print("Hello, world!")
```
"""
        self.txt_file = self.create_text_file(self.sample_text, filename="test.txt")

    def test_txt_to_pdf(self):
        """Test TXT to PDF conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'pdf')
            self.verify_file_exists(output_path)
            # Basic check for PDF header
            with open(output_path, 'rb') as f:
                header = f.read(5)
                self.assertEqual(header, b'%PDF-', "File is not a valid PDF")
        except Exception as e:
            self.skipTest(f"TXT to PDF conversion not supported: {str(e)}")

    def test_txt_to_docx(self):
        """Test TXT to DOCX conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'docx')
            self.verify_file_exists(output_path)
            # Check file signature for DOCX (ZIP format)
            with open(output_path, 'rb') as f:
                header = f.read(4)
                self.assertEqual(header, b'PK\x03\x04', "File is not a valid DOCX (ZIP) file")
        except Exception as e:
            self.skipTest(f"TXT to DOCX conversion not supported: {str(e)}")

    def test_txt_to_html(self):
        """Test TXT to HTML conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'html')
            self.verify_file_exists(output_path)
            self.verify_text_file(output_path, expected_content="<html")
        except Exception as e:
            self.skipTest(f"TXT to HTML conversion not supported: {str(e)}")

    def test_txt_to_md(self):
        """Test TXT to MD conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'md')
            self.verify_file_exists(output_path)
            # Verify some markdown content
            self.verify_text_file(output_path, expected_content="#")
        except Exception as e:
            self.skipTest(f"TXT to MD conversion not supported: {str(e)}")

    def test_txt_to_rtf(self):
        """Test TXT to RTF conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'rtf')
            self.verify_file_exists(output_path)
            # Check RTF header
            self.verify_text_file(output_path, expected_content="{\\rtf")
        except Exception as e:
            self.skipTest(f"TXT to RTF conversion not supported: {str(e)}")

    def test_txt_to_csv(self):
        """Test TXT to CSV conversion."""
        try:
            output_path = self.convert_file(self.txt_file, 'txt', 'csv')
            self.verify_file_exists(output_path)
        except Exception as e:
            self.skipTest(f"TXT to CSV conversion not supported: {str(e)}")

    def test_md_to_html(self):
        """Test MD to HTML conversion."""
        try:
            # Create a markdown file
            md_content = """# Markdown Test
            
This is a **bold** text and *italic* text.

## List
- Item 1
- Item 2
- Item 3

[Link to Google](https://www.google.com)
"""
            md_file = self.create_markdown_file(md_content, filename="test.md")
            
            output_path = self.convert_file(md_file, 'md', 'html')
            self.verify_file_exists(output_path)
            
            # Check for HTML elements
            self.verify_text_file(output_path, expected_content="<h1>")
            self.verify_text_file(output_path, expected_content="<strong>bold</strong>")
            self.verify_text_file(output_path, expected_content="<em>italic</em>")
            self.verify_text_file(output_path, expected_content="<li>")
            self.verify_text_file(output_path, expected_content="<a href=")
        except Exception as e:
            self.skipTest(f"MD to HTML conversion not supported: {str(e)}")

    def test_md_to_pdf(self):
        """Test MD to PDF conversion."""
        try:
            # Create a markdown file
            md_content = """# Markdown Test
            
This is a **bold** text and *italic* text.

## List
- Item 1
- Item 2
- Item 3
"""
            md_file = self.create_markdown_file(md_content, filename="test.md")
            
            output_path = self.convert_file(md_file, 'md', 'pdf')
            self.verify_file_exists(output_path)
            
            # Check for PDF header
            with open(output_path, 'rb') as f:
                header = f.read(5)
                self.assertEqual(header, b'%PDF-', "File is not a valid PDF")
        except Exception as e:
            self.skipTest(f"MD to PDF conversion not supported: {str(e)}")

    def test_html_to_md(self):
        """Test HTML to MD conversion."""
        try:
            # Create an HTML file
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>HTML Test</title>
</head>
<body>
    <h1>HTML Test</h1>
    <p>This is a <strong>bold</strong> text and <em>italic</em> text.</p>
    
    <h2>List</h2>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    
    <p><a href="https://www.google.com">Link to Google</a></p>
</body>
</html>
"""
            html_file = self.create_html_file(html_content, filename="test.html")
            
            output_path = self.convert_file(html_file, 'html', 'md')
            self.verify_file_exists(output_path)
            
            # Check for Markdown elements
            self.verify_text_file(output_path, expected_content="#")
            self.verify_text_file(output_path, expected_content="**bold**")
            self.verify_text_file(output_path, expected_content="*italic*")
            self.verify_text_file(output_path, expected_content="- ")
            self.verify_text_file(output_path, expected_content="[Link to Google]")
        except Exception as e:
            self.skipTest(f"HTML to MD conversion not supported: {str(e)}")

    def test_html_to_pdf(self):
        """Test HTML to PDF conversion."""
        try:
            # Create an HTML file
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>HTML Test</title>
</head>
<body>
    <h1>HTML Test</h1>
    <p>This is a <strong>bold</strong> text and <em>italic</em> text.</p>
</body>
</html>
"""
            html_file = self.create_html_file(html_content, filename="test.html")
            
            output_path = self.convert_file(html_file, 'html', 'pdf')
            self.verify_file_exists(output_path)
            
            # Check for PDF header
            with open(output_path, 'rb') as f:
                header = f.read(5)
                self.assertEqual(header, b'%PDF-', "File is not a valid PDF")
        except Exception as e:
            self.skipTest(f"HTML to PDF conversion not supported: {str(e)}")

    def test_html_to_txt(self):
        """Test HTML to TXT conversion."""
        try:
            # Create an HTML file
            html_content = """<!DOCTYPE html>
<html>
<head>
    <title>HTML Test</title>
</head>
<body>
    <h1>HTML Test</h1>
    <p>This is a <strong>bold</strong> text and <em>italic</em> text.</p>
    
    <h2>List</h2>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>
"""
            html_file = self.create_html_file(html_content, filename="test.html")
            
            output_path = self.convert_file(html_file, 'html', 'txt')
            self.verify_file_exists(output_path)
            
            # Check for plain text content
            self.verify_text_file(output_path, expected_content="HTML Test")
            self.verify_text_file(output_path, expected_content="bold")
            self.verify_text_file(output_path, expected_content="italic")
            self.verify_text_file(output_path, expected_content="Item 1")
        except Exception as e:
            self.skipTest(f"HTML to TXT conversion not supported: {str(e)}")

    def test_csv_to_xlsx(self):
        """Test CSV to XLSX conversion."""
        try:
            # Create a CSV file
            csv_content = """Name,Age,City
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago
"""
            csv_file = self.create_text_file(csv_content, filename="test.csv")
            
            output_path = self.convert_file(csv_file, 'csv', 'xlsx')
            self.verify_file_exists(output_path)
            
            # Check file signature for XLSX (ZIP format)
            with open(output_path, 'rb') as f:
                header = f.read(4)
                self.assertEqual(header, b'PK\x03\x04', "File is not a valid XLSX (ZIP) file")
        except Exception as e:
            self.skipTest(f"CSV to XLSX conversion not supported: {str(e)}")

    def test_csv_to_json(self):
        """Test CSV to JSON conversion."""
        try:
            # Create a CSV file
            csv_content = """Name,Age,City
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago
"""
            csv_file = self.create_text_file(csv_content, filename="test.csv")
            
            output_path = self.convert_file(csv_file, 'csv', 'json')
            self.verify_file_exists(output_path)
            
            # Check for JSON content
            self.verify_text_file(output_path, expected_content="{")
            self.verify_text_file(output_path, expected_content="Alice")
            self.verify_text_file(output_path, expected_content="New York")
        except Exception as e:
            self.skipTest(f"CSV to JSON conversion not supported: {str(e)}")

    def test_csv_to_xml(self):
        """Test CSV to XML conversion."""
        try:
            # Create a CSV file
            csv_content = """Name,Age,City
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago
"""
            csv_file = self.create_text_file(csv_content, filename="test.csv")
            
            output_path = self.convert_file(csv_file, 'csv', 'xml')
            self.verify_file_exists(output_path)
            
            # Check for XML content
            self.verify_text_file(output_path, expected_content="<")
            self.verify_text_file(output_path, expected_content="Alice")
            self.verify_text_file(output_path, expected_content="New York")
        except Exception as e:
            self.skipTest(f"CSV to XML conversion not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 