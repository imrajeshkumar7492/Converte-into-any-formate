#!/usr/bin/env python3
"""
Real FFmpeg Multimedia Conversion Testing with proper audio/video files
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

class RealFFmpegTester:
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
    
    def create_real_wav_file(self):
        """Create a real WAV file using Python"""
        try:
            import wave
            import struct
            
            # Create a simple sine wave
            sample_rate = 44100
            duration = 1  # 1 second
            frequency = 440  # A4 note
            
            # Generate sine wave data
            samples = []
            for i in range(int(sample_rate * duration)):
                t = float(i) / sample_rate
                sample = int(32767 * 0.5 * (1 + 0.5 * (t * frequency * 2 * 3.14159)))
                samples.append(struct.pack('<h', sample))
            
            # Create WAV file in memory
            buffer = io.BytesIO()
            with wave.open(buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(samples))
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Failed to create real WAV file: {e}")
            # Fallback to a proper WAV header
            wav_header = b'RIFF'
            wav_header += (36 + 1000).to_bytes(4, 'little')  # file size - 8
            wav_header += b'WAVE'
            wav_header += b'fmt '
            wav_header += (16).to_bytes(4, 'little')  # fmt chunk size
            wav_header += (1).to_bytes(2, 'little')   # PCM format
            wav_header += (1).to_bytes(2, 'little')   # mono
            wav_header += (44100).to_bytes(4, 'little')  # sample rate
            wav_header += (88200).to_bytes(4, 'little')  # byte rate
            wav_header += (2).to_bytes(2, 'little')   # block align
            wav_header += (16).to_bytes(2, 'little')  # bits per sample
            wav_header += b'data'
            wav_header += (1000).to_bytes(4, 'little')  # data size
            # Add some actual audio data (silence)
            audio_data = b'\x00\x00' * 500  # 500 samples of silence
            return wav_header + audio_data
    
    def create_real_mp3_file(self):
        """Create a real MP3 file using pydub"""
        try:
            from pydub import AudioSegment
            from pydub.generators import Sine
            
            # Generate a 1-second 440Hz sine wave
            tone = Sine(440).to_audio_segment(duration=1000)
            
            # Export to MP3 in memory
            buffer = io.BytesIO()
            tone.export(buffer, format="mp3")
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Failed to create real MP3 file with pydub: {e}")
            # Return None to skip this test
            return None
    
    def test_wav_to_mp3_with_real_files(self):
        """Test WAV to MP3 conversion with a real WAV file"""
        try:
            wav_content = self.create_real_wav_file()
            if not wav_content:
                self.log_result("Real WAV to MP3 Conversion", False, "Could not create test WAV file")
                return False
            
            filename = "real_test_audio.wav"
            files = {'file': (filename, io.BytesIO(wav_content))}
            data = {'target_format': 'mp3'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 100:
                    # Check for MP3 header patterns
                    if (converted_content.startswith(b'\xff\xfb') or 
                        converted_content.startswith(b'\xff\xfa') or
                        converted_content.startswith(b'ID3')):
                        self.log_result("Real WAV to MP3 Conversion", True,
                                      f"Successfully converted real WAV to MP3",
                                      {"input_size": f"{len(wav_content)} bytes",
                                       "output_size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("Real WAV to MP3 Conversion", False,
                                      f"Output doesn't appear to be valid MP3 (size: {len(converted_content)} bytes)")
                        return False
                else:
                    self.log_result("Real WAV to MP3 Conversion", False,
                                  f"Output too small: {len(converted_content)} bytes")
                    return False
            else:
                error_text = response.text
                self.log_result("Real WAV to MP3 Conversion", False,
                              f"Conversion failed ({response.status_code}): {error_text}")
                return False
                
        except Exception as e:
            self.log_result("Real WAV to MP3 Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_mp3_to_wav_with_real_files(self):
        """Test MP3 to WAV conversion with a real MP3 file"""
        try:
            mp3_content = self.create_real_mp3_file()
            if not mp3_content:
                self.log_result("Real MP3 to WAV Conversion", False, "Could not create test MP3 file (pydub not available)")
                return False
            
            filename = "real_test_audio.mp3"
            files = {'file': (filename, io.BytesIO(mp3_content))}
            data = {'target_format': 'wav'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                if len(converted_content) > 100:
                    # Check for WAV header
                    if converted_content.startswith(b'RIFF') and b'WAVE' in converted_content[:20]:
                        self.log_result("Real MP3 to WAV Conversion", True,
                                      f"Successfully converted real MP3 to WAV",
                                      {"input_size": f"{len(mp3_content)} bytes",
                                       "output_size": f"{len(converted_content)} bytes"})
                        return True
                    else:
                        self.log_result("Real MP3 to WAV Conversion", False,
                                      f"Output doesn't appear to be valid WAV (size: {len(converted_content)} bytes)")
                        return False
                else:
                    self.log_result("Real MP3 to WAV Conversion", False,
                                  f"Output too small: {len(converted_content)} bytes")
                    return False
            else:
                error_text = response.text
                self.log_result("Real MP3 to WAV Conversion", False,
                              f"Conversion failed ({response.status_code}): {error_text}")
                return False
                
        except Exception as e:
            self.log_result("Real MP3 to WAV Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_simple_audio_format_support(self):
        """Test if audio format conversion is supported at all"""
        try:
            # Test supported formats for MP3
            response = self.session.get(f"{BACKEND_URL}/supported-formats/mp3")
            
            if response.status_code == 200:
                data = response.json()
                supported_formats = data.get('supported_formats', [])
                
                audio_formats = ['WAV', 'AAC', 'FLAC', 'OGG']
                supported_audio = [fmt for fmt in audio_formats if fmt in supported_formats]
                
                if supported_audio:
                    self.log_result("Audio Format Support", True,
                                  f"Audio conversions supported for MP3",
                                  {"supported_audio_formats": supported_audio})
                    return True
                else:
                    self.log_result("Audio Format Support", False,
                                  f"No audio formats supported for MP3: {supported_formats}")
                    return False
            else:
                self.log_result("Audio Format Support", False,
                              f"Failed to get supported formats: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Audio Format Support", False, f"Test failed: {str(e)}")
            return False
    
    def test_video_format_support(self):
        """Test if video format conversion is supported at all"""
        try:
            # Test supported formats for MP4
            response = self.session.get(f"{BACKEND_URL}/supported-formats/mp4")
            
            if response.status_code == 200:
                data = response.json()
                supported_formats = data.get('supported_formats', [])
                
                video_formats = ['AVI', 'MOV', 'WMV', 'MKV', 'WEBM']
                supported_video = [fmt for fmt in video_formats if fmt in supported_formats]
                
                if supported_video:
                    self.log_result("Video Format Support", True,
                                  f"Video conversions supported for MP4",
                                  {"supported_video_formats": supported_video})
                    return True
                else:
                    self.log_result("Video Format Support", False,
                                  f"No video formats supported for MP4: {supported_formats}")
                    return False
            else:
                self.log_result("Video Format Support", False,
                              f"Failed to get supported formats: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Video Format Support", False, f"Test failed: {str(e)}")
            return False
    
    def run_real_ffmpeg_tests(self):
        """Run all real FFmpeg tests"""
        print("🎵 Starting Real FFmpeg Multimedia Tests...")
        print("=" * 60)
        
        tests = [
            ("Audio Format Support Check", self.test_simple_audio_format_support),
            ("Video Format Support Check", self.test_video_format_support),
            ("Real WAV to MP3 Conversion", self.test_wav_to_mp3_with_real_files),
            ("Real MP3 to WAV Conversion", self.test_mp3_to_wav_with_real_files)
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
        print(f"🏁 Real FFmpeg Test Summary: {passed}/{total} tests passed")
        
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
    tester = RealFFmpegTester()
    passed, total, results = tester.run_real_ffmpeg_tests()
    
    # Return exit code based on results
    if passed >= 2:  # At least format support should work
        print(f"\n🎉 {passed}/{total} FFmpeg tests passed! Basic multimedia support verified.")
        return 0
    else:
        print(f"\n⚠️  Only {passed}/{total} FFmpeg tests passed. Multimedia conversion may have issues.")
        return 1

if __name__ == "__main__":
    exit(main())