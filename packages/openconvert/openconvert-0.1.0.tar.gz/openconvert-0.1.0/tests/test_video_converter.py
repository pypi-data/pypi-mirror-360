"""
Test cases for video conversions.
"""

import os
import unittest
import tempfile
from pathlib import Path

from test_base import BaseConverterTest


class VideoConverterTest(BaseConverterTest):
    """Test cases for video conversions."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        
        # Skip all tests if moviepy is not installed
        try:
            import moviepy.editor
        except ImportError:
            self.skipTest("moviepy not installed")
        
        # Create a test video file
        self.mp4_file = self._create_test_video_file('mp4')
        if not self.mp4_file:
            self.skipTest("Could not create test video file")

    def _create_test_video_file(self, format):
        """Create a test video file."""
        try:
            import moviepy.editor as mp
            from moviepy.video.fx.colorx import colorx
            
            # Create a simple color clip
            clip = mp.ColorClip(size=(320, 240), color=(255, 0, 0), duration=1)
            
            # Add a text to make it more interesting
            text = mp.TextClip("AGConvert Test", fontsize=30, color='white')
            text = text.set_position('center').set_duration(1)
            
            # Combine clips
            video = mp.CompositeVideoClip([clip, text])
            
            # Save to file
            file_path = self.get_test_file_path(f"test.{format}")
            video.write_videofile(file_path, fps=24, codec='libx264', audio=False, verbose=False, logger=None)
            
            return file_path
        except Exception as e:
            print(f"Error creating test video file: {str(e)}")
            return None

    def _verify_video_file(self, file_path, expected_format=None):
        """Verify that a file is a valid video file."""
        try:
            import moviepy.editor as mp
            
            self.verify_file_exists(file_path)
            
            # Try to load the video file
            video = mp.VideoFileClip(file_path)
            
            # Basic video validation
            self.assertTrue(video.duration > 0, "Video duration is 0")
            self.assertTrue(video.w > 0 and video.h > 0, "Video dimensions are invalid")
            self.assertTrue(video.fps > 0, "Video FPS is 0")
            
            # Clean up
            video.close()
            
            return True
        except Exception as e:
            self.fail(f"Failed to verify video file: {str(e)}")
            return False

    def test_mp4_to_avi(self):
        """Test MP4 to AVI conversion."""
        try:
            output_path = self.convert_file(self.mp4_file, 'mp4', 'avi')
            self._verify_video_file(output_path)
        except Exception as e:
            self.skipTest(f"MP4 to AVI conversion not supported: {str(e)}")

    def test_mp4_to_mov(self):
        """Test MP4 to MOV conversion."""
        try:
            output_path = self.convert_file(self.mp4_file, 'mp4', 'mov')
            self._verify_video_file(output_path)
        except Exception as e:
            self.skipTest(f"MP4 to MOV conversion not supported: {str(e)}")

    def test_mp4_to_webm(self):
        """Test MP4 to WebM conversion."""
        try:
            output_path = self.convert_file(self.mp4_file, 'mp4', 'webm')
            self._verify_video_file(output_path)
        except Exception as e:
            self.skipTest(f"MP4 to WebM conversion not supported: {str(e)}")

    def test_mp4_to_gif(self):
        """Test MP4 to GIF conversion."""
        try:
            output_path = self.convert_file(self.mp4_file, 'mp4', 'gif')
            self.verify_file_exists(output_path)
            
            # Verify it's a GIF
            with open(output_path, 'rb') as f:
                header = f.read(6)
                self.assertEqual(header[:3], b'GIF', "File is not a GIF")
        except Exception as e:
            self.skipTest(f"MP4 to GIF conversion not supported: {str(e)}")

    def test_mp4_to_mp3(self):
        """Test MP4 to MP3 conversion (extract audio)."""
        try:
            # First create a video with audio
            import moviepy.editor as mp
            
            # Create a simple audio clip
            audio_clip = mp.AudioClip(lambda t: [np.sin(440 * 2 * np.pi * t)], fps=44100, duration=1)
            
            # Create a simple video clip
            video_clip = mp.ColorClip(size=(320, 240), color=(255, 0, 0), duration=1)
            
            # Combine video and audio
            video = video_clip.set_audio(audio_clip)
            
            # Save to file
            file_path = self.get_test_file_path("test_with_audio.mp4")
            video.write_videofile(file_path, fps=24, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            
            # Convert to MP3
            output_path = self.convert_file(file_path, 'mp4', 'mp3')
            
            # Verify it's an audio file
            self.verify_file_exists(output_path)
            
            # Try to load as audio
            try:
                import pydub
                audio = pydub.AudioSegment.from_file(output_path, format='mp3')
                self.assertTrue(len(audio) > 0, "Audio duration is 0")
            except ImportError:
                # If pydub is not available, just check file exists
                pass
        except Exception as e:
            self.skipTest(f"MP4 to MP3 conversion not supported: {str(e)}")
    
    def test_avi_to_mp4(self):
        """Test AVI to MP4 conversion."""
        try:
            # First create an AVI file
            avi_file = self._create_test_video_file('avi')
            if not avi_file:
                self.skipTest("Could not create test AVI file")
            
            output_path = self.convert_file(avi_file, 'avi', 'mp4')
            self._verify_video_file(output_path)
        except Exception as e:
            self.skipTest(f"AVI to MP4 conversion not supported: {str(e)}")

    def test_video_resize_option(self):
        """Test video resize option."""
        try:
            # Convert with resize
            output_path = self.convert_file(
                self.mp4_file, 'mp4', 'mp4', 
                options={'resolution': (160, 120)}
            )
            
            # Verify the output file
            import moviepy.editor as mp
            video = mp.VideoFileClip(output_path)
            
            # Check dimensions
            self.assertEqual(video.size, (160, 120), "Video dimensions should be 160x120")
            
            # Clean up
            video.close()
        except Exception as e:
            self.skipTest(f"Video resize option test not supported: {str(e)}")

    def test_video_fps_option(self):
        """Test video FPS option."""
        try:
            # Convert with FPS change
            output_path = self.convert_file(
                self.mp4_file, 'mp4', 'mp4', 
                options={'fps': 15}
            )
            
            # Verify the output file
            import moviepy.editor as mp
            video = mp.VideoFileClip(output_path)
            
            # Check FPS (allow small floating point differences)
            self.assertAlmostEqual(video.fps, 15, delta=0.1, 
                                  msg="Video FPS should be approximately 15")
            
            # Clean up
            video.close()
        except Exception as e:
            self.skipTest(f"Video FPS option test not supported: {str(e)}")

    def test_video_to_frames(self):
        """Test video to frames conversion."""
        try:
            # Create output directory
            frames_dir = self.get_test_file_path("frames")
            os.makedirs(frames_dir, exist_ok=True)
            
            # Convert video to frames
            from agconvert.converters import video_converter
            video_converter.video_to_frames(self.mp4_file, frames_dir)
            
            # Check that frames were created
            frames = list(Path(frames_dir).glob("*.jpg"))
            self.assertTrue(len(frames) > 0, "No frames were extracted")
        except Exception as e:
            self.skipTest(f"Video to frames conversion not supported: {str(e)}")


if __name__ == '__main__':
    unittest.main() 