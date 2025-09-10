#!/usr/bin/env python3
"""
Simple Multimedia Conversion Testing
Tests FFmpeg-dependent conversions with real generated files
"""

import requests
import json
import io
import os
import tempfile
import subprocess

# Get backend URL from environment
BACKEND_URL = "https://clean-embed.preview.emergentagent.com/api"

def create_real_mp3():
    """Create a real MP3 file using FFmpeg"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate a 1-second sine wave MP3 using FFmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
            '-acodec', 'mp3', '-y', temp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(temp_path):
            with open(temp_path, 'rb') as f:
                data = f.read()
            os.unlink(temp_path)
            return data
        else:
            print(f"FFmpeg MP3 generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error creating MP3: {e}")
        return None

def create_real_mp4():
    """Create a real MP4 file using FFmpeg"""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Generate a 1-second test video using FFmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
            '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest', '-y', temp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(temp_path):
            with open(temp_path, 'rb') as f:
                data = f.read()
            os.unlink(temp_path)
            return data
        else:
            print(f"FFmpeg MP4 generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error creating MP4: {e}")
        return None

def test_conversion(filename, content, target_format, description):
    """Test a single conversion"""
    try:
        if content is None:
            print(f"❌ SKIP: {description} - Could not create test file")
            return False
            
        files = {'file': (filename, io.BytesIO(content))}
        data = {'target_format': target_format}
        
        response = requests.post(f"{BACKEND_URL}/convert", files=files, data=data)
        
        if response.status_code == 200:
            converted_content = response.content
            
            if len(converted_content) > 100:  # Should be reasonably sized
                print(f"✅ PASS: {description} - Successfully converted ({len(converted_content)} bytes)")
                return True
            else:
                print(f"❌ FAIL: {description} - Converted file too small ({len(converted_content)} bytes)")
                return False
        else:
            error_text = response.text
            print(f"❌ FAIL: {description} - Status {response.status_code}: {error_text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {description} - Exception: {str(e)}")
        return False

def main():
    """Run simple multimedia tests"""
    print("🎬 Simple Multimedia Conversion Tests")
    print("=" * 50)
    
    # Test FFmpeg availability
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available")
        else:
            print("❌ FFmpeg not working properly")
            return 1
    except Exception as e:
        print(f"❌ FFmpeg not available: {e}")
        return 1
    
    # Create test files
    print("\n📁 Creating test files...")
    mp3_data = create_real_mp3()
    mp4_data = create_real_mp4()
    
    # Run tests
    print("\n🧪 Running conversion tests...")
    tests = [
        ("test_audio.mp3", mp3_data, "wav", "MP3 to WAV Audio Conversion"),
        ("test_video.mp4", mp4_data, "avi", "MP4 to AVI Video Conversion"),
        ("test_video.mp4", mp4_data, "mp3", "MP4 to MP3 Audio Extraction"),
    ]
    
    passed = 0
    total = len(tests)
    
    for filename, content, target_format, description in tests:
        if test_conversion(filename, content, target_format, description):
            passed += 1
    
    print(f"\n🏁 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All multimedia conversions are working with FFmpeg!")
        return 0
    else:
        print("⚠️ Some multimedia conversions are still failing")
        return 1

if __name__ == "__main__":
    exit(main())