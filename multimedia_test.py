#!/usr/bin/env python3
"""
Focused Multimedia Conversion Testing for Audio and Video
Tests specifically the FFmpeg-dependent conversions that were previously failing
"""

import requests
import json
import io
import os
import tempfile
from PIL import Image
import time
from pathlib import Path

# Get backend URL from environment
BACKEND_URL = "https://clean-embed.preview.emergentagent.com/api"

class MultimediaConversionTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
    
    def create_test_mp3(self):
        """Create a valid test MP3 file using pydub"""
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            import io
            
            # Generate a 1-second sine wave at 440Hz
            sine_wave = Sine(440).to_audio_segment(duration=1000)
            
            # Export to MP3
            buffer = io.BytesIO()
            sine_wave.export(buffer, format="mp3")
            buffer.seek(0)
            return buffer.getvalue()
        except Exception as e:
            print(f"Warning: Could not create real MP3, using minimal data: {e}")
            # Fallback to minimal MP3 data
            mp3_data = b'\xff\xfb\x90\x00' + b'\x00' * 100
            return mp3_data
    
    def create_test_mp4(self):
        """Create a valid test MP4 file using moviepy"""
        try:
            from moviepy import VideoClip
            import numpy as np
            import tempfile
            import os
            
            # Create a simple 1-second video clip
            def make_frame(t):
                # Create a simple red frame
                return np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
            
            clip = VideoClip(make_frame, duration=1)
            
            # Export to MP4
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                clip.write_videofile(temp_path, verbose=False, logger=None)
                
                with open(temp_path, 'rb') as f:
                    mp4_data = f.read()
                
                return mp4_data
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            print(f"Warning: Could not create real MP4, using minimal data: {e}")
            # Fallback to minimal MP4 data
            mp4_data = (
                b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
                b'\x00\x00\x00\x08free'
                + b'\x00' * 200
            )
            return mp4_data
    
    def test_mp3_to_wav_conversion(self):
        """Test MP3 to WAV audio conversion - should now work with FFmpeg"""
        try:
            filename = "test_audio.mp3"
            content = self.create_test_mp3()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'wav'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 20:  # Should be larger than mock content
                    # Check for WAV header
                    if converted_content.startswith(b'RIFF') and b'WAVE' in converted_content[:20]:
                        self.log_result("MP3 to WAV Conversion", True,
                                      f"Successfully converted MP3 to WAV with FFmpeg",
                                      {"size": f"{len(converted_content)} bytes", "format": "Valid WAV header detected"})
                        return True
                    else:
                        self.log_result("MP3 to WAV Conversion", False,
                                      f"Converted content doesn't have valid WAV header")
                        return False
                else:
                    self.log_result("MP3 to WAV Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes) - likely still failing")
                    return False
            else:
                error_text = response.text
                self.log_result("MP3 to WAV Conversion", False,
                              f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP3 to WAV Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_mp4_to_avi_conversion(self):
        """Test MP4 to AVI video conversion - should now work with FFmpeg"""
        try:
            filename = "test_video.mp4"
            content = self.create_test_mp4()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'avi'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 20:  # Should be larger than mock content
                    # Check for AVI header
                    if converted_content.startswith(b'RIFF') and b'AVI ' in converted_content[:20]:
                        self.log_result("MP4 to AVI Conversion", True,
                                      f"Successfully converted MP4 to AVI with FFmpeg",
                                      {"size": f"{len(converted_content)} bytes", "format": "Valid AVI header detected"})
                        return True
                    else:
                        self.log_result("MP4 to AVI Conversion", False,
                                      f"Converted content doesn't have valid AVI header")
                        return False
                else:
                    self.log_result("MP4 to AVI Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes) - likely still failing")
                    return False
            else:
                error_text = response.text
                self.log_result("MP4 to AVI Conversion", False,
                              f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP4 to AVI Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_mp4_to_mp3_extraction(self):
        """Test video to audio extraction (MP4 to MP3) - should now work with FFmpeg"""
        try:
            filename = "test_video.mp4"
            content = self.create_test_mp4()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 20:  # Should be larger than mock content
                    # Check for MP3 header (ID3 tag or MP3 frame header)
                    if (converted_content.startswith(b'ID3') or 
                        converted_content.startswith(b'\xff\xfb') or 
                        converted_content.startswith(b'\xff\xfa')):
                        self.log_result("MP4 to MP3 Extraction", True,
                                      f"Successfully extracted audio from MP4 to MP3 with FFmpeg",
                                      {"size": f"{len(converted_content)} bytes", "format": "Valid MP3 header detected"})
                        return True
                    else:
                        self.log_result("MP4 to MP3 Extraction", False,
                                      f"Converted content doesn't have valid MP3 header")
                        return False
                else:
                    self.log_result("MP4 to MP3 Extraction", False,
                                  f"Converted file too small ({len(converted_content)} bytes) - likely still failing")
                    return False
            else:
                error_text = response.text
                self.log_result("MP4 to MP3 Extraction", False,
                              f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP4 to MP3 Extraction", False, f"Test failed: {str(e)}")
            return False
    
    def test_wav_to_mp3_conversion(self):
        """Test WAV to MP3 audio conversion - additional test to verify FFmpeg audio processing"""
        try:
            # Create a minimal WAV file
            wav_data = (
                b'RIFF' + b'\x24\x00\x00\x00' +  # File size
                b'WAVE' +
                b'fmt ' + b'\x10\x00\x00\x00' +  # Format chunk size
                b'\x01\x00\x01\x00' +  # PCM, mono
                b'\x44\xac\x00\x00' +  # Sample rate 44100
                b'\x88\x58\x01\x00' +  # Byte rate
                b'\x02\x00\x10\x00' +  # Block align, bits per sample
                b'data' + b'\x00\x00\x00\x00'  # Data chunk
            )
            
            filename = "test_audio.wav"
            
            files = {'file': (filename, io.BytesIO(wav_data))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 20:  # Should be larger than mock content
                    # Check for MP3 header
                    if (converted_content.startswith(b'ID3') or 
                        converted_content.startswith(b'\xff\xfb') or 
                        converted_content.startswith(b'\xff\xfa')):
                        self.log_result("WAV to MP3 Conversion", True,
                                      f"Successfully converted WAV to MP3 with FFmpeg",
                                      {"size": f"{len(converted_content)} bytes", "format": "Valid MP3 header detected"})
                        return True
                    else:
                        self.log_result("WAV to MP3 Conversion", False,
                                      f"Converted content doesn't have valid MP3 header")
                        return False
                else:
                    self.log_result("WAV to MP3 Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes) - likely still failing")
                    return False
            else:
                error_text = response.text
                self.log_result("WAV to MP3 Conversion", False,
                              f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("WAV to MP3 Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_ffmpeg_availability(self):
        """Test if FFmpeg is available in the system"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                self.log_result("FFmpeg Availability", True,
                              f"FFmpeg is available and working",
                              {"version": version_info})
                return True
            else:
                self.log_result("FFmpeg Availability", False,
                              f"FFmpeg command failed with return code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("FFmpeg Availability", False, "FFmpeg command timed out")
            return False
        except FileNotFoundError:
            self.log_result("FFmpeg Availability", False, "FFmpeg not found in system PATH")
            return False
        except Exception as e:
            self.log_result("FFmpeg Availability", False, f"FFmpeg test failed: {str(e)}")
            return False
    
    def run_multimedia_tests(self):
        """Run all multimedia conversion tests"""
        print("🎬 Starting Multimedia Conversion Tests (FFmpeg-dependent)...")
        print("=" * 70)
        
        tests = [
            ("FFmpeg System Availability", self.test_ffmpeg_availability),
            ("MP3 to WAV Audio Conversion", self.test_mp3_to_wav_conversion),
            ("MP4 to AVI Video Conversion", self.test_mp4_to_avi_conversion),
            ("MP4 to MP3 Audio Extraction", self.test_mp4_to_mp3_extraction),
            ("WAV to MP3 Audio Conversion", self.test_wav_to_mp3_conversion)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🎵 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"🏁 Multimedia Test Summary: {passed}/{total} tests passed")
        
        # Print detailed results
        print("\n📊 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['test']}: {result['message']}")
            if result.get('details'):
                for key, value in result['details'].items():
                    print(f"   {key}: {value}")
        
        return passed, total, self.test_results

def main():
    """Main test execution"""
    tester = MultimediaConversionTester()
    passed, total, results = tester.run_multimedia_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All multimedia tests passed! FFmpeg-dependent conversions are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} multimedia tests failed. FFmpeg dependency issues may persist.")
        return 1

if __name__ == "__main__":
    exit(main())