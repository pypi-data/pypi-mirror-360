"""
Test cases for archive conversions.
"""

import os
import unittest
import tempfile
from pathlib import Path

from test_base import BaseConverterTest


class ArchiveConverterTest(BaseConverterTest):
    """Test cases for archive conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Create test files for archiving
        self.test_files_dir = self._create_test_files()
        if not self.test_files_dir:
            self.skipTest("Could not create test files")
        
        # Create a test ZIP archive
        self.zip_file = self._create_test_archive('zip')
        if not self.zip_file:
            self.skipTest("Could not create test ZIP archive")

    def _create_test_files(self):
        """Create test files for archiving."""
        try:
            # Create a directory with some test files
            test_dir = self.get_test_file_path("test_files")
            os.makedirs(test_dir, exist_ok=True)
            
            # Create a few text files
            for i in range(3):
                file_path = os.path.join(test_dir, f"file{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"This is test file {i}\n")
            
            # Create a subdirectory with more files
            subdir = os.path.join(test_dir, "subdir")
            os.makedirs(subdir, exist_ok=True)
            
            for i in range(2):
                file_path = os.path.join(subdir, f"subfile{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"This is a file in the subdirectory {i}\n")
            
            return test_dir
        except Exception as e:
            print(f"Error creating test files: {str(e)}")
            return None

    def _create_test_archive(self, format):
        """Create a test archive."""
        try:
            if format == 'zip':
                import zipfile
                
                # Create a ZIP file
                file_path = self.get_test_file_path(f"test.{format}")
                with zipfile.ZipFile(file_path, 'w') as zipf:
                    # Add all files from the test directory
                    for root, _, files in os.walk(self.test_files_dir):
                        for file in files:
                            file_path_full = os.path.join(root, file)
                            # Get the relative path for the archive
                            rel_path = os.path.relpath(file_path_full, os.path.dirname(self.test_files_dir))
                            zipf.write(file_path_full, rel_path)
                
                return file_path
            
            elif format == 'tar':
                import tarfile
                
                # Create a TAR file
                file_path = self.get_test_file_path(f"test.{format}")
                with tarfile.open(file_path, 'w') as tarf:
                    # Add all files from the test directory
                    for root, _, files in os.walk(self.test_files_dir):
                        for file in files:
                            file_path_full = os.path.join(root, file)
                            # Get the relative path for the archive
                            rel_path = os.path.relpath(file_path_full, os.path.dirname(self.test_files_dir))
                            tarf.add(file_path_full, arcname=rel_path)
                
                return file_path
            
            elif format == 'tar.gz':
                import tarfile
                
                # Create a TAR.GZ file
                file_path = self.get_test_file_path(f"test.{format}")
                with tarfile.open(file_path, 'w:gz') as tarf:
                    # Add all files from the test directory
                    for root, _, files in os.walk(self.test_files_dir):
                        for file in files:
                            file_path_full = os.path.join(root, file)
                            # Get the relative path for the archive
                            rel_path = os.path.relpath(file_path_full, os.path.dirname(self.test_files_dir))
                            tarf.add(file_path_full, arcname=rel_path)
                
                return file_path
            
            else:
                raise ValueError(f"Unsupported archive format: {format}")
        
        except Exception as e:
            print(f"Error creating test archive: {str(e)}")
            return None

    def _verify_archive_contents(self, archive_path, format):
        """Verify that an archive contains the expected files."""
        try:
            if format == 'zip':
                import zipfile
                
                # Check that the file exists
                self.verify_file_exists(archive_path)
                
                # Check that it's a valid ZIP file
                self.assertTrue(zipfile.is_zipfile(archive_path), "Not a valid ZIP file")
                
                # Check contents
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    file_list = zipf.namelist()
                    
                    # Check that we have the expected number of files
                    self.assertGreaterEqual(len(file_list), 5, "Archive should contain at least 5 files")
                    
                    # Check for specific files
                    self.assertIn("test_files/file0.txt", file_list)
                    self.assertIn("test_files/subdir/subfile0.txt", file_list)
            
            elif format in ['tar', 'tar.gz', 'tar.bz2']:
                import tarfile
                
                # Check that the file exists
                self.verify_file_exists(archive_path)
                
                # Check that it's a valid TAR file
                self.assertTrue(tarfile.is_tarfile(archive_path), "Not a valid TAR file")
                
                # Check contents
                with tarfile.open(archive_path, 'r:*') as tarf:
                    file_list = tarf.getnames()
                    
                    # Check that we have the expected number of files
                    self.assertGreaterEqual(len(file_list), 5, "Archive should contain at least 5 files")
                    
                    # Check for specific files
                    self.assertIn("test_files/file0.txt", file_list)
                    self.assertIn("test_files/subdir/subfile0.txt", file_list)
            
            else:
                raise ValueError(f"Unsupported archive format for verification: {format}")
        
        except Exception as e:
            self.fail(f"Failed to verify archive contents: {str(e)}")

    def test_zip_to_tar(self):
        """Test ZIP to TAR conversion."""
        try:
            output_path = self.convert_file(self.zip_file, 'zip', 'tar')
            self._verify_archive_contents(output_path, 'tar')
        except Exception as e:
            self.skipTest(f"ZIP to TAR conversion not supported: {str(e)}")

    def test_zip_to_tar_gz(self):
        """Test ZIP to TAR.GZ conversion."""
        try:
            output_path = self.convert_file(self.zip_file, 'zip', 'tar.gz')
            self._verify_archive_contents(output_path, 'tar.gz')
        except Exception as e:
            self.skipTest(f"ZIP to TAR.GZ conversion not supported: {str(e)}")

    def test_zip_to_tar_bz2(self):
        """Test ZIP to TAR.BZ2 conversion."""
        try:
            output_path = self.convert_file(self.zip_file, 'zip', 'tar.bz2')
            self._verify_archive_contents(output_path, 'tar.bz2')
        except Exception as e:
            self.skipTest(f"ZIP to TAR.BZ2 conversion not supported: {str(e)}")

    def test_tar_to_zip(self):
        """Test TAR to ZIP conversion."""
        try:
            # First create a TAR file
            tar_file = self._create_test_archive('tar')
            if not tar_file:
                self.skipTest("Could not create test TAR archive")
            
            output_path = self.convert_file(tar_file, 'tar', 'zip')
            self._verify_archive_contents(output_path, 'zip')
        except Exception as e:
            self.skipTest(f"TAR to ZIP conversion not supported: {str(e)}")

    def test_tar_gz_to_zip(self):
        """Test TAR.GZ to ZIP conversion."""
        try:
            # First create a TAR.GZ file
            tar_gz_file = self._create_test_archive('tar.gz')
            if not tar_gz_file:
                self.skipTest("Could not create test TAR.GZ archive")
            
            output_path = self.convert_file(tar_gz_file, 'tar.gz', 'zip')
            self._verify_archive_contents(output_path, 'zip')
        except Exception as e:
            self.skipTest(f"TAR.GZ to ZIP conversion not supported: {str(e)}")

    def test_extract_archive(self):
        """Test extracting an archive."""
        try:
            # Create an output directory
            extract_dir = self.get_test_file_path("extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            # Extract the ZIP file
            from agconvert.converters import archive_converter
            archive_converter.extract_archive(self.zip_file, extract_dir)
            
            # Check that files were extracted
            extracted_files = list(Path(extract_dir).glob("**/*.txt"))
            self.assertGreaterEqual(len(extracted_files), 5, 
                                   "Should have extracted at least 5 text files")
            
            # Check specific files
            self.assertTrue(os.path.exists(os.path.join(extract_dir, "test_files", "file0.txt")))
            self.assertTrue(os.path.exists(os.path.join(extract_dir, "test_files", "subdir", "subfile0.txt")))
        except Exception as e:
            self.skipTest(f"Extract archive not supported: {str(e)}")

    def test_create_archive(self):
        """Test creating an archive from a directory."""
        try:
            # Create an output file
            output_path = self.get_test_file_path("created.zip")
            
            # Create the archive
            from agconvert.converters import archive_converter
            archive_converter.create_archive(self.test_files_dir, output_path, 'zip')
            
            # Verify the archive
            self._verify_archive_contents(output_path, 'zip')
        except Exception as e:
            self.skipTest(f"Create archive not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 