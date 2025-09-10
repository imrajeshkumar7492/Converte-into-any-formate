#!/usr/bin/env python3
"""
Debug Video Conversion Test
"""

import requests
import json
import io
import os
import tempfile
import subprocess

# Get backend URL from environment
BACKEND_URL = "https://broken-converter.preview.emergentagent.com/api"

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
            print(f"Created MP4 file: {len(data)} bytes")
            os.unlink(temp_path)
            return data
        else:
            print(f"FFmpeg MP4 generation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error creating MP4: {e}")
        return None

def test_video_conversion():
    """Test MP4 to AVI conversion with detailed debugging"""
    print("🎬 Testing MP4 to AVI conversion...")
    
    # Create test MP4
    mp4_data = create_real_mp4()
    if mp4_data is None:
        print("❌ Could not create test MP4 file")
        return False
    
    # Test conversion
    files = {'file': ('test_video.mp4', io.BytesIO(mp4_data))}
    data = {'target_format': 'avi'}
    
    try:
        response = requests.post(f"{BACKEND_URL}/convert", files=files, data=data)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            converted_content = response.content
            print(f"Converted content size: {len(converted_content)} bytes")
            
            if len(converted_content) > 0:
                # Check first few bytes
                print(f"First 20 bytes: {converted_content[:20]}")
                
                # Check if it's an AVI file
                if converted_content.startswith(b'RIFF') and b'AVI ' in converted_content[:20]:
                    print("✅ Valid AVI file detected")
                    return True
                else:
                    print("❌ Not a valid AVI file")
                    return False
            else:
                print("❌ Empty response content")
                return False
        else:
            print(f"❌ Conversion failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during conversion: {e}")
        return False

if __name__ == "__main__":
    test_video_conversion()