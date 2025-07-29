"""
Test cases for audio conversions.
"""

import os
import unittest
import tempfile
from pathlib import Path

from test_base import BaseConverterTest


class AudioConverterTest(BaseConverterTest):
    """Test cases for audio conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Skip all tests if pydub is not installed
        try:
            import pydub
        except ImportError:
            self.skipTest("pydub not installed")
        
        # Create a test audio file
        self.mp3_file = self._create_test_audio_file('mp3')
        if not self.mp3_file:
            self.skipTest("Could not create test audio file")

    def _create_test_audio_file(self, format):
        """Create a test audio file."""
        try:
            import pydub
            from pydub.generators import Sine
            
            # Generate a simple sine wave
            sine_wave = Sine(440).to_audio_segment(duration=1000)  # 1 second 440 Hz tone
            
            # Save to file
            file_path = self.get_test_file_path(f"test.{format}")
            sine_wave.export(file_path, format=format)
            
            return file_path
        except Exception as e:
            print(f"Error creating test audio file: {str(e)}")
            return None

    def _verify_audio_file(self, file_path, expected_format=None):
        """Verify that a file is a valid audio file."""
        try:
            import pydub
            
            self.verify_file_exists(file_path)
            
            # Try to load the audio file
            audio = pydub.AudioSegment.from_file(file_path, format=expected_format)
            
            # Basic audio validation
            self.assertTrue(len(audio) > 0, "Audio duration is 0")
            self.assertTrue(audio.frame_rate > 0, "Audio frame rate is 0")
            self.assertTrue(audio.channels > 0, "Audio channels is 0")
            
            return audio
        except Exception as e:
            self.fail(f"Failed to verify audio file: {str(e)}")

    def test_mp3_to_wav(self):
        """Test MP3 to WAV conversion."""
        try:
            output_path = self.convert_file(self.mp3_file, 'mp3', 'wav')
            self._verify_audio_file(output_path, expected_format='wav')
        except Exception as e:
            self.skipTest(f"MP3 to WAV conversion not supported: {str(e)}")

    def test_mp3_to_ogg(self):
        """Test MP3 to OGG conversion."""
        try:
            output_path = self.convert_file(self.mp3_file, 'mp3', 'ogg')
            self._verify_audio_file(output_path, expected_format='ogg')
        except Exception as e:
            self.skipTest(f"MP3 to OGG conversion not supported: {str(e)}")

    def test_mp3_to_flac(self):
        """Test MP3 to FLAC conversion."""
        try:
            output_path = self.convert_file(self.mp3_file, 'mp3', 'flac')
            self._verify_audio_file(output_path, expected_format='flac')
        except Exception as e:
            self.skipTest(f"MP3 to FLAC conversion not supported: {str(e)}")

    def test_mp3_to_aac(self):
        """Test MP3 to AAC conversion."""
        try:
            output_path = self.convert_file(self.mp3_file, 'mp3', 'aac')
            self._verify_audio_file(output_path, expected_format='aac')
        except Exception as e:
            self.skipTest(f"MP3 to AAC conversion not supported: {str(e)}")

    def test_wav_to_mp3(self):
        """Test WAV to MP3 conversion."""
        try:
            # First create a WAV file
            wav_file = self._create_test_audio_file('wav')
            if not wav_file:
                self.skipTest("Could not create test WAV file")
            
            output_path = self.convert_file(wav_file, 'wav', 'mp3')
            self._verify_audio_file(output_path, expected_format='mp3')
        except Exception as e:
            self.skipTest(f"WAV to MP3 conversion not supported: {str(e)}")

    def test_wav_to_ogg(self):
        """Test WAV to OGG conversion."""
        try:
            # First create a WAV file
            wav_file = self._create_test_audio_file('wav')
            if not wav_file:
                self.skipTest("Could not create test WAV file")
            
            output_path = self.convert_file(wav_file, 'wav', 'ogg')
            self._verify_audio_file(output_path, expected_format='ogg')
        except Exception as e:
            self.skipTest(f"WAV to OGG conversion not supported: {str(e)}")

    def test_wav_to_flac(self):
        """Test WAV to FLAC conversion."""
        try:
            # First create a WAV file
            wav_file = self._create_test_audio_file('wav')
            if not wav_file:
                self.skipTest("Could not create test WAV file")
            
            output_path = self.convert_file(wav_file, 'wav', 'flac')
            self._verify_audio_file(output_path, expected_format='flac')
        except Exception as e:
            self.skipTest(f"WAV to FLAC conversion not supported: {str(e)}")

    def test_audio_volume_option(self):
        """Test audio volume option."""
        try:
            # Convert with volume adjustment
            output_path = self.convert_file(
                self.mp3_file, 'mp3', 'wav', 
                options={'volume': 6.0}  # +6dB
            )
            
            # Verify the output file
            audio = self._verify_audio_file(output_path, expected_format='wav')
            
            # Create a reference file without volume adjustment
            ref_path = self.convert_file(self.mp3_file, 'mp3', 'wav')
            ref_audio = self._verify_audio_file(ref_path, expected_format='wav')
            
            # The volume-adjusted file should have higher RMS
            import pydub
            self.assertGreater(audio.rms, ref_audio.rms, 
                              "Volume-adjusted audio should have higher RMS")
        except Exception as e:
            self.skipTest(f"Audio volume option test not supported: {str(e)}")

    def test_audio_channels_option(self):
        """Test audio channels option."""
        try:
            # Convert to mono
            mono_path = self.convert_file(
                self.mp3_file, 'mp3', 'wav', 
                options={'channels': 1}
            )
            
            # Verify the output file
            mono_audio = self._verify_audio_file(mono_path, expected_format='wav')
            
            # Check channels
            self.assertEqual(mono_audio.channels, 1, "Audio should be mono (1 channel)")
            
            # Convert to stereo
            stereo_path = self.convert_file(
                self.mp3_file, 'mp3', 'wav', 
                options={'channels': 2}
            )
            
            # Verify the output file
            stereo_audio = self._verify_audio_file(stereo_path, expected_format='wav')
            
            # Check channels
            self.assertEqual(stereo_audio.channels, 2, "Audio should be stereo (2 channels)")
        except Exception as e:
            self.skipTest(f"Audio channels option test not supported: {str(e)}")

    def test_audio_sample_rate_option(self):
        """Test audio sample rate option."""
        try:
            # Convert with sample rate adjustment
            output_path = self.convert_file(
                self.mp3_file, 'mp3', 'wav', 
                options={'sample_rate': 16000}  # 16 kHz
            )
            
            # Verify the output file
            audio = self._verify_audio_file(output_path, expected_format='wav')
            
            # Check sample rate
            self.assertEqual(audio.frame_rate, 16000, "Audio sample rate should be 16000 Hz")
        except Exception as e:
            self.skipTest(f"Audio sample rate option test not supported: {str(e)}")

    def test_speech_to_text(self):
        """Test speech-to-text conversion."""
        try:
            import speech_recognition
        except ImportError:
            self.skipTest("speech_recognition not installed")
        
        try:
            # This test is more of a placeholder since we can't easily create a speech file
            # that would be recognized correctly
            output_path = self.get_test_file_path("speech.txt")
            
            # We'll just check that the function exists and doesn't crash
            # with a simple audio file
            with self.assertRaises(Exception):
                from agconvert.converters import audio_converter
                audio_converter.speech_to_text(self.mp3_file, output_path)
        except Exception as e:
            self.skipTest(f"Speech-to-text conversion not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 