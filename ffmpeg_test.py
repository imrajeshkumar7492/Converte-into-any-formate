#!/usr/bin/env python3
"""
FFmpeg Multimedia Conversion Testing
Tests audio and video conversions to verify FFmpeg is working properly
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

class FFmpegTester:
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
        """Create a minimal MP3 file for testing"""
        # This is a minimal MP3 header + some data
        mp3_data = b'\xff\xfb\x90\x00' + b'\x00' * 1000  # MP3 header + padding
        return mp3_data
    
    def create_test_wav(self):
        """Create a minimal WAV file for testing"""
        # WAV file header for a simple audio file
        wav_header = b'RIFF' + (1044).to_bytes(4, 'little') + b'WAVE'
        wav_header += b'fmt ' + (16).to_bytes(4, 'little')
        wav_header += (1).to_bytes(2, 'little')  # PCM format
        wav_header += (1).to_bytes(2, 'little')  # mono
        wav_header += (44100).to_bytes(4, 'little')  # sample rate
        wav_header += (88200).to_bytes(4, 'little')  # byte rate
        wav_header += (2).to_bytes(2, 'little')  # block align
        wav_header += (16).to_bytes(2, 'little')  # bits per sample
        wav_header += b'data' + (1000).to_bytes(4, 'little')
        wav_data = wav_header + b'\x00' * 1000
        return wav_data
    
    def create_test_mp4(self):
        """Create a minimal MP4 file for testing"""
        # Minimal MP4 file structure
        mp4_data = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
        mp4_data += b'\x00' * 1000  # Add some padding
        return mp4_data
    
    def test_audio_conversion_mp3_to_wav(self):
        """Test MP3 to WAV conversion using FFmpeg"""
        try:
            filename = "test_audio.mp3"
            content = self.create_test_mp3()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'wav'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 100:  # Should be larger than minimal content
                    # Check if it's a valid WAV file (starts with RIFF)
                    if converted_content.startswith(b'RIFF'):
                        self.log_result("MP3 to WAV Audio Conversion", True,
                                      f"Successfully converted MP3 to WAV using FFmpeg",
                                      {"size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("MP3 to WAV Audio Conversion", False,
                                      "Converted file doesn't have valid WAV header")
                        return False
                else:
                    self.log_result("MP3 to WAV Audio Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes)")
                    return False
            else:
                error_text = response.text
                if "ffmpeg" in error_text.lower() or "not found" in error_text.lower():
                    self.log_result("MP3 to WAV Audio Conversion", False,
                                  f"FFmpeg not available: {error_text}")
                else:
                    self.log_result("MP3 to WAV Audio Conversion", False,
                                  f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP3 to WAV Audio Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_video_conversion_mp4_to_avi(self):
        """Test MP4 to AVI conversion using FFmpeg"""
        try:
            filename = "test_video.mp4"
            content = self.create_test_mp4()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'avi'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 100:  # Should be larger than minimal content
                    # Check if it's a valid AVI file (starts with RIFF...AVI)
                    if converted_content.startswith(b'RIFF') and b'AVI' in converted_content[:20]:
                        self.log_result("MP4 to AVI Video Conversion", True,
                                      f"Successfully converted MP4 to AVI using FFmpeg",
                                      {"size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("MP4 to AVI Video Conversion", False,
                                      "Converted file doesn't have valid AVI header")
                        return False
                else:
                    self.log_result("MP4 to AVI Video Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes)")
                    return False
            else:
                error_text = response.text
                if "ffmpeg" in error_text.lower() or "not found" in error_text.lower():
                    self.log_result("MP4 to AVI Video Conversion", False,
                                  f"FFmpeg not available: {error_text}")
                else:
                    self.log_result("MP4 to AVI Video Conversion", False,
                                  f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP4 to AVI Video Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_audio_extraction_mp4_to_mp3(self):
        """Test MP4 to MP3 audio extraction using FFmpeg"""
        try:
            filename = "test_video.mp4"
            content = self.create_test_mp4()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 50:  # Should be larger than minimal content
                    # Check if it's a valid MP3 file (starts with MP3 header)
                    if converted_content.startswith(b'\xff\xfb') or converted_content.startswith(b'\xff\xfa'):
                        self.log_result("MP4 to MP3 Audio Extraction", True,
                                      f"Successfully extracted audio from MP4 to MP3 using FFmpeg",
                                      {"size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("MP4 to MP3 Audio Extraction", False,
                                      "Converted file doesn't have valid MP3 header")
                        return False
                else:
                    self.log_result("MP4 to MP3 Audio Extraction", False,
                                  f"Converted file too small ({len(converted_content)} bytes)")
                    return False
            else:
                error_text = response.text
                if "ffmpeg" in error_text.lower() or "not found" in error_text.lower():
                    self.log_result("MP4 to MP3 Audio Extraction", False,
                                  f"FFmpeg not available: {error_text}")
                else:
                    self.log_result("MP4 to MP3 Audio Extraction", False,
                                  f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("MP4 to MP3 Audio Extraction", False, f"Test failed: {str(e)}")
            return False
    
    def test_wav_to_mp3_conversion(self):
        """Test WAV to MP3 conversion using FFmpeg"""
        try:
            filename = "test_audio.wav"
            content = self.create_test_wav()
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 50:  # Should be larger than minimal content
                    # Check if it's a valid MP3 file
                    if converted_content.startswith(b'\xff\xfb') or converted_content.startswith(b'\xff\xfa'):
                        self.log_result("WAV to MP3 Audio Conversion", True,
                                      f"Successfully converted WAV to MP3 using FFmpeg",
                                      {"size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("WAV to MP3 Audio Conversion", False,
                                      "Converted file doesn't have valid MP3 header")
                        return False
                else:
                    self.log_result("WAV to MP3 Audio Conversion", False,
                                  f"Converted file too small ({len(converted_content)} bytes)")
                    return False
            else:
                error_text = response.text
                if "ffmpeg" in error_text.lower() or "not found" in error_text.lower():
                    self.log_result("WAV to MP3 Audio Conversion", False,
                                  f"FFmpeg not available: {error_text}")
                else:
                    self.log_result("WAV to MP3 Audio Conversion", False,
                                  f"Conversion failed with status {response.status_code}: {error_text}")
                return False
                
        except Exception as e:
            self.log_result("WAV to MP3 Audio Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def run_ffmpeg_tests(self):
        """Run all FFmpeg-related tests"""
        print("🎵 Starting FFmpeg Multimedia Conversion Tests...")
        print("=" * 60)
        
        tests = [
            ("MP3 to WAV Audio", self.test_audio_conversion_mp3_to_wav),
            ("MP4 to AVI Video", self.test_video_conversion_mp4_to_avi),
            ("MP4 to MP3 Audio Extraction", self.test_audio_extraction_mp4_to_mp3),
            ("WAV to MP3 Audio", self.test_wav_to_mp3_conversion)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🎬 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"🏁 FFmpeg Test Summary: {passed}/{total} tests passed")
        
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
    tester = FFmpegTester()
    passed, total, results = tester.run_ffmpeg_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All FFmpeg tests passed! Multimedia conversion is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} FFmpeg tests failed. FFmpeg may not be properly installed or configured.")
        return 1

if __name__ == "__main__":
    exit(main())