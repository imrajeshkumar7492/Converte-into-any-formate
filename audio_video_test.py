#!/usr/bin/env python3
"""
Audio and Video Conversion Testing - Tests multimedia conversions
"""

import requests
import json
import io
import os
import tempfile
import time

# Get backend URL from environment
BACKEND_URL = "https://clean-embed.preview.emergentagent.com/api"

class AudioVideoTester:
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
    
    def create_simple_mp3(self):
        """Create a minimal MP3-like file (header only for testing)"""
        # MP3 header for a simple file
        mp3_header = b'\xff\xfb\x90\x00'  # MP3 sync word and basic header
        # Add some dummy data to make it look like a real MP3
        dummy_data = b'\x00' * 1000  # 1KB of dummy audio data
        return mp3_header + dummy_data
    
    def create_simple_mp4(self):
        """Create a minimal MP4-like file (header only for testing)"""
        # MP4 ftyp box header
        mp4_header = b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom'
        # Add some dummy data
        dummy_data = b'\x00' * 2000  # 2KB of dummy video data
        return mp4_header + dummy_data
    
    def test_audio_conversion_support(self):
        """Test if audio conversions are supported"""
        try:
            # Test MP3 to WAV conversion
            mp3_content = self.create_simple_mp3()
            
            files = {'file': ('test_audio.mp3', io.BytesIO(mp3_content))}
            data = {'target_format': 'wav'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Check if we got some content back
                if len(converted_content) > 100:
                    self.log_result("Audio Conversion Support", True,
                                  f"Audio conversion appears to work",
                                  {"converted_size": f"{len(converted_content)} bytes"})
                    return True
                else:
                    self.log_result("Audio Conversion Support", False,
                                  f"Converted audio file too small: {len(converted_content)} bytes")
                    return False
            elif response.status_code == 400:
                self.log_result("Audio Conversion Support", False,
                              f"Audio conversion not supported: {response.text}")
                return False
            elif response.status_code == 500:
                error_text = response.text
                if "FFmpeg" in error_text or "ffmpeg" in error_text:
                    self.log_result("Audio Conversion Support", False,
                                  f"Audio conversion failed - FFmpeg required: {error_text}")
                else:
                    self.log_result("Audio Conversion Support", False,
                                  f"Audio conversion failed: {error_text}")
                return False
            else:
                self.log_result("Audio Conversion Support", False,
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Audio Conversion Support", False, f"Test failed: {str(e)}")
            return False
    
    def test_video_conversion_support(self):
        """Test if video conversions are supported"""
        try:
            # Test MP4 to AVI conversion
            mp4_content = self.create_simple_mp4()
            
            files = {'file': ('test_video.mp4', io.BytesIO(mp4_content))}
            data = {'target_format': 'avi'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Check if we got some content back
                if len(converted_content) > 100:
                    self.log_result("Video Conversion Support", True,
                                  f"Video conversion appears to work",
                                  {"converted_size": f"{len(converted_content)} bytes"})
                    return True
                else:
                    self.log_result("Video Conversion Support", False,
                                  f"Converted video file too small: {len(converted_content)} bytes")
                    return False
            elif response.status_code == 400:
                self.log_result("Video Conversion Support", False,
                              f"Video conversion not supported: {response.text}")
                return False
            elif response.status_code == 500:
                error_text = response.text
                if "FFmpeg" in error_text or "ffmpeg" in error_text:
                    self.log_result("Video Conversion Support", False,
                                  f"Video conversion failed - FFmpeg required: {error_text}")
                else:
                    self.log_result("Video Conversion Support", False,
                                  f"Video conversion failed: {error_text}")
                return False
            else:
                self.log_result("Video Conversion Support", False,
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Video Conversion Support", False, f"Test failed: {str(e)}")
            return False
    
    def test_video_to_audio_extraction(self):
        """Test video to audio extraction"""
        try:
            # Test MP4 to MP3 conversion (audio extraction)
            mp4_content = self.create_simple_mp4()
            
            files = {'file': ('test_extract.mp4', io.BytesIO(mp4_content))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Check if we got some content back
                if len(converted_content) > 50:
                    self.log_result("Video to Audio Extraction", True,
                                  f"Audio extraction appears to work",
                                  {"extracted_size": f"{len(converted_content)} bytes"})
                    return True
                else:
                    self.log_result("Video to Audio Extraction", False,
                                  f"Extracted audio file too small: {len(converted_content)} bytes")
                    return False
            elif response.status_code == 400:
                self.log_result("Video to Audio Extraction", False,
                              f"Audio extraction not supported: {response.text}")
                return False
            elif response.status_code == 500:
                error_text = response.text
                if "FFmpeg" in error_text or "ffmpeg" in error_text:
                    self.log_result("Video to Audio Extraction", False,
                                  f"Audio extraction failed - FFmpeg required: {error_text}")
                else:
                    self.log_result("Video to Audio Extraction", False,
                                  f"Audio extraction failed: {error_text}")
                return False
            else:
                self.log_result("Video to Audio Extraction", False,
                              f"Unexpected response: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Video to Audio Extraction", False, f"Test failed: {str(e)}")
            return False
    
    def check_ffmpeg_availability(self):
        """Check if FFmpeg is available on the system"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0] if result.stdout else "Unknown version"
                self.log_result("FFmpeg Availability", True,
                              f"FFmpeg is available",
                              {"version": version_info})
                return True
            else:
                self.log_result("FFmpeg Availability", False,
                              f"FFmpeg command failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result("FFmpeg Availability", False, "FFmpeg command timed out")
            return False
        except FileNotFoundError:
            self.log_result("FFmpeg Availability", False, "FFmpeg not found in system PATH")
            return False
        except Exception as e:
            self.log_result("FFmpeg Availability", False, f"FFmpeg check failed: {str(e)}")
            return False
    
    def run_multimedia_tests(self):
        """Run all multimedia tests"""
        print("🎵 Starting Audio/Video Conversion Tests...")
        print("=" * 60)
        
        tests = [
            ("FFmpeg Availability", self.check_ffmpeg_availability),
            ("Audio Conversion Support", self.test_audio_conversion_support),
            ("Video Conversion Support", self.test_video_conversion_support),
            ("Video to Audio Extraction", self.test_video_to_audio_extraction)
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
    tester = AudioVideoTester()
    passed, total, results = tester.run_multimedia_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All multimedia tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} multimedia tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())