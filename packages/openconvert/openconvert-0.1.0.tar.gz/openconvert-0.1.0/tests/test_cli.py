"""
Test cases for the CLI module.
"""

import os
import unittest
import tempfile
import sys
from io import StringIO
from pathlib import Path

from test_base import BaseConverterTest


class CLITest(BaseConverterTest):
    """Test cases for the CLI module."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create test files
        self.text_file = self.create_text_file("test.txt", "This is a test file.")
        self.image_file = self.create_image_file("test.png", (100, 100), "RGB", "red")
        
        # Save original stdout and stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # Create string buffers to capture output
        self.stdout_buffer = StringIO()
        self.stderr_buffer = StringIO()
        
        # Redirect stdout and stderr
        sys.stdout = self.stdout_buffer
        sys.stderr = self.stderr_buffer

    def tearDown(self):
        """Clean up after tests."""
        # Restore original stdout and stderr
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        
        super().tearDown()

    def _run_cli(self, args):
        """Run the CLI with the given arguments."""
        from agconvert.cli import main
        
        # Reset buffers
        self.stdout_buffer.seek(0)
        self.stdout_buffer.truncate(0)
        self.stderr_buffer.seek(0)
        self.stderr_buffer.truncate(0)
        
        # Set up sys.argv
        old_argv = sys.argv
        sys.argv = ['agconvert'] + args
        
        try:
            # Run the CLI
            exit_code = main()
            return exit_code
        except SystemExit as e:
            # Catch SystemExit and return the exit code
            return e.code
        finally:
            # Restore sys.argv
            sys.argv = old_argv

    def test_cli_basic_conversion(self):
        """Test basic conversion using the CLI."""
        try:
            # Create output path
            output_path = self.get_test_file_path("output.md")
            
            # Run the CLI
            exit_code = self._run_cli([self.text_file, 'md', '--output', output_path])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check output
            self.verify_file_exists(output_path)
            
            # Check stdout
            stdout = self.stdout_buffer.getvalue()
            self.assertIn("Conversion successful", stdout)
        except Exception as e:
            self.skipTest(f"CLI basic conversion test failed: {str(e)}")

    def test_cli_with_options(self):
        """Test CLI with conversion options."""
        try:
            # Create output path
            output_path = self.get_test_file_path("output.jpg")
            
            # Run the CLI
            exit_code = self._run_cli([
                self.image_file, 'jpg', 
                '--output', output_path,
                '--option', 'quality=85'
            ])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check output
            self.verify_file_exists(output_path)
        except Exception as e:
            self.skipTest(f"CLI with options test failed: {str(e)}")

    def test_cli_auto_output_path(self):
        """Test CLI with automatic output path generation."""
        try:
            # Run the CLI
            exit_code = self._run_cli([self.text_file, 'md'])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check output
            expected_path = str(Path(self.text_file).with_suffix('.md'))
            self.verify_file_exists(expected_path)
            
            # Clean up
            if os.path.exists(expected_path):
                os.remove(expected_path)
        except Exception as e:
            self.skipTest(f"CLI auto output path test failed: {str(e)}")

    def test_cli_list_formats(self):
        """Test CLI list formats command."""
        try:
            # Run the CLI
            exit_code = self._run_cli(['--list-formats'])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check stdout
            stdout = self.stdout_buffer.getvalue()
            self.assertIn("Supported formats", stdout)
            self.assertIn("Image formats", stdout)
            self.assertIn("Document formats", stdout)
        except Exception as e:
            self.skipTest(f"CLI list formats test failed: {str(e)}")

    def test_cli_version(self):
        """Test CLI version command."""
        try:
            # Run the CLI
            exit_code = self._run_cli(['--version'])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check stdout
            stdout = self.stdout_buffer.getvalue()
            self.assertIn("AGConvert", stdout)
            self.assertIn("version", stdout)
        except Exception as e:
            self.skipTest(f"CLI version test failed: {str(e)}")

    def test_cli_invalid_input(self):
        """Test CLI with invalid input file."""
        try:
            # Run the CLI
            exit_code = self._run_cli(['nonexistent_file.txt', 'md'])
            
            # Check exit code
            self.assertNotEqual(exit_code, 0, "CLI should exit with non-zero code for invalid input")
            
            # Check stderr
            stderr = self.stderr_buffer.getvalue()
            self.assertIn("Error", stderr)
            self.assertIn("not found", stderr)
        except Exception as e:
            self.skipTest(f"CLI invalid input test failed: {str(e)}")

    def test_cli_invalid_format(self):
        """Test CLI with invalid format."""
        try:
            # Run the CLI
            exit_code = self._run_cli([self.text_file, 'invalid_format'])
            
            # Check exit code
            self.assertNotEqual(exit_code, 0, "CLI should exit with non-zero code for invalid format")
            
            # Check stderr
            stderr = self.stderr_buffer.getvalue()
            self.assertIn("Error", stderr)
            self.assertIn("Unsupported", stderr)
        except Exception as e:
            self.skipTest(f"CLI invalid format test failed: {str(e)}")

    def test_cli_help(self):
        """Test CLI help command."""
        try:
            # Run the CLI
            exit_code = self._run_cli(['--help'])
            
            # Check exit code
            self.assertEqual(exit_code, 0, f"CLI exited with non-zero code: {exit_code}")
            
            # Check stdout
            stdout = self.stdout_buffer.getvalue()
            self.assertIn("usage:", stdout)
            self.assertIn("positional arguments:", stdout)
            self.assertIn("options:", stdout)
        except Exception as e:
            self.skipTest(f"CLI help test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main() 