#!/usr/bin/env python3
"""
Comprehensive test script for Converte Pro backend functionality.
This script tests all conversion tools and verifies they work correctly.
"""

import asyncio
import aiohttp
import json
import os
import tempfile
from pathlib import Path
import time
from PIL import Image
import PyPDF2

# Test configuration
BACKEND_URL = "http://localhost:8000"
API_URL = f"{BACKEND_URL}/api"

class ConverteTester:
    def __init__(self):
        self.session = None
        self.test_files = {}
        self.results = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_test_files(self):
        """Create test files for conversion testing"""
        print("Creating test files...")
        
        # Create test image
        img = Image.new('RGB', (800, 600), color='red')
        img_path = Path(tempfile.gettempdir()) / 'test_image.jpg'
        img.save(img_path, 'JPEG', quality=90)
        self.test_files['image'] = img_path
        
        # Create test PDF
        pdf_path = Path(tempfile.gettempdir()) / 'test_document.pdf'
        with open(pdf_path, 'wb') as f:
            writer = PyPDF2.PdfWriter()
            # Add a simple page
            page = PyPDF2.PageObject.create_blank_page(width=612, height=792)
            writer.add_page(page)
            writer.write(f)
        self.test_files['pdf'] = pdf_path
        
        print(f"Created test files: {list(self.test_files.keys())}")
    
    async def test_api_health(self):
        """Test API health endpoint"""
        print("\n🔍 Testing API health...")
        try:
            async with self.session.get(f"{API_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API is healthy: {data.get('message', 'OK')}")
                    return True
                else:
                    print(f"❌ API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ API health check error: {e}")
            return False
    
    async def test_stats(self):
        """Test stats endpoint"""
        print("\n📊 Testing stats endpoint...")
        try:
            async with self.session.get(f"{API_URL}/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Stats retrieved: {data}")
                    return True
                else:
                    print(f"❌ Stats endpoint failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Stats endpoint error: {e}")
            return False
    
    async def test_image_conversion(self):
        """Test image conversion functionality"""
        print("\n🖼️ Testing image conversion...")
        
        if 'image' not in self.test_files:
            print("❌ No test image available")
            return False
        
        try:
            # Create job
            job_data = {
                "conversion_type": "jpg_to_png",
                "priority": "normal",
                "options": {"quality": 90}
            }
            
            async with self.session.post(f"{API_URL}/jobs", json=job_data) as response:
                if response.status != 200:
                    print(f"❌ Failed to create job: {response.status}")
                    return False
                
                job = await response.json()
                job_id = job['id']
                print(f"✅ Created job: {job_id}")
            
            # Upload file
            with open(self.test_files['image'], 'rb') as f:
                files = {'files': f}
                async with self.session.post(f"{API_URL}/jobs/{job_id}/upload", data=files) as response:
                    if response.status != 200:
                        print(f"❌ Failed to upload file: {response.status}")
                        return False
                    print("✅ File uploaded successfully")
            
            # Start job
            async with self.session.post(f"{API_URL}/jobs/{job_id}/start") as response:
                if response.status != 200:
                    print(f"❌ Failed to start job: {response.status}")
                    return False
                print("✅ Job started")
            
            # Monitor job progress
            max_wait = 60  # 60 seconds timeout
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                async with self.session.get(f"{API_URL}/jobs/{job_id}") as response:
                    if response.status == 200:
                        job_status = await response.json()
                        status = job_status['status']
                        progress = job_status.get('progress', 0)
                        
                        print(f"📈 Job progress: {progress}% - Status: {status}")
                        
                        if status == 'completed':
                            print("✅ Image conversion completed successfully!")
                            if job_status.get('download_urls'):
                                print(f"📥 Download URLs: {job_status['download_urls']}")
                            return True
                        elif status == 'failed':
                            error = job_status.get('error_message', 'Unknown error')
                            print(f"❌ Image conversion failed: {error}")
                            return False
                        
                        await asyncio.sleep(2)
                    else:
                        print(f"❌ Failed to get job status: {response.status}")
                        return False
            
            print("⏰ Job timed out")
            return False
            
        except Exception as e:
            print(f"❌ Image conversion test error: {e}")
            return False
    
    async def test_pdf_operations(self):
        """Test PDF operations"""
        print("\n📄 Testing PDF operations...")
        
        if 'pdf' not in self.test_files:
            print("❌ No test PDF available")
            return False
        
        try:
            # Test PDF compression
            job_data = {
                "conversion_type": "compress_pdf",
                "priority": "normal",
                "options": {"compression_level": "medium"}
            }
            
            async with self.session.post(f"{API_URL}/jobs", json=job_data) as response:
                if response.status != 200:
                    print(f"❌ Failed to create PDF job: {response.status}")
                    return False
                
                job = await response.json()
                job_id = job['id']
                print(f"✅ Created PDF job: {job_id}")
            
            # Upload PDF
            with open(self.test_files['pdf'], 'rb') as f:
                files = {'files': f}
                async with self.session.post(f"{API_URL}/jobs/{job_id}/upload", data=files) as response:
                    if response.status != 200:
                        print(f"❌ Failed to upload PDF: {response.status}")
                        return False
                    print("✅ PDF uploaded successfully")
            
            # Start job
            async with self.session.post(f"{API_URL}/jobs/{job_id}/start") as response:
                if response.status != 200:
                    print(f"❌ Failed to start PDF job: {response.status}")
                    return False
                print("✅ PDF job started")
            
            # Monitor job
            max_wait = 30
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                async with self.session.get(f"{API_URL}/jobs/{job_id}") as response:
                    if response.status == 200:
                        job_status = await response.json()
                        status = job_status['status']
                        
                        if status == 'completed':
                            print("✅ PDF compression completed successfully!")
                            return True
                        elif status == 'failed':
                            error = job_status.get('error_message', 'Unknown error')
                            print(f"❌ PDF compression failed: {error}")
                            return False
                        
                        await asyncio.sleep(1)
                    else:
                        print(f"❌ Failed to get PDF job status: {response.status}")
                        return False
            
            print("⏰ PDF job timed out")
            return False
            
        except Exception as e:
            print(f"❌ PDF operations test error: {e}")
            return False
    
    async def test_batch_operations(self):
        """Test batch operations"""
        print("\n📦 Testing batch operations...")
        
        if 'image' not in self.test_files:
            print("❌ No test files available for batch operations")
            return False
        
        try:
            # Create batch job
            job_data = {
                "conversion_type": "batch_image_convert",
                "priority": "normal",
                "options": {
                    "target_format": "png",
                    "quality": 90
                }
            }
            
            async with self.session.post(f"{API_URL}/jobs", json=job_data) as response:
                if response.status != 200:
                    print(f"❌ Failed to create batch job: {response.status}")
                    return False
                
                job = await response.json()
                job_id = job['id']
                print(f"✅ Created batch job: {job_id}")
            
            # Upload multiple files (same file twice for testing)
            with open(self.test_files['image'], 'rb') as f1, open(self.test_files['image'], 'rb') as f2:
                files = [
                    ('files', f1),
                    ('files', f2)
                ]
                async with self.session.post(f"{API_URL}/jobs/{job_id}/upload", data=files) as response:
                    if response.status != 200:
                        print(f"❌ Failed to upload batch files: {response.status}")
                        return False
                    print("✅ Batch files uploaded successfully")
            
            # Start batch job
            async with self.session.post(f"{API_URL}/jobs/{job_id}/start") as response:
                if response.status != 200:
                    print(f"❌ Failed to start batch job: {response.status}")
                    return False
                print("✅ Batch job started")
            
            # Monitor batch job
            max_wait = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                async with self.session.get(f"{API_URL}/jobs/{job_id}") as response:
                    if response.status == 200:
                        job_status = await response.json()
                        status = job_status['status']
                        progress = job_status.get('progress', 0)
                        
                        print(f"📈 Batch job progress: {progress}% - Status: {status}")
                        
                        if status == 'completed':
                            print("✅ Batch operation completed successfully!")
                            return True
                        elif status == 'failed':
                            error = job_status.get('error_message', 'Unknown error')
                            print(f"❌ Batch operation failed: {error}")
                            return False
                        
                        await asyncio.sleep(2)
                    else:
                        print(f"❌ Failed to get batch job status: {response.status}")
                        return False
            
            print("⏰ Batch job timed out")
            return False
            
        except Exception as e:
            print(f"❌ Batch operations test error: {e}")
            return False
    
    async def test_websocket_connection(self):
        """Test WebSocket connection for real-time updates"""
        print("\n🔌 Testing WebSocket connection...")
        
        try:
            # Create a test job first
            job_data = {
                "conversion_type": "jpg_to_png",
                "priority": "normal",
                "options": {}
            }
            
            async with self.session.post(f"{API_URL}/jobs", json=job_data) as response:
                if response.status != 200:
                    print("❌ Failed to create test job for WebSocket")
                    return False
                
                job = await response.json()
                job_id = job['id']
            
            # Test WebSocket connection
            ws_url = f"ws://localhost:8000/api/ws/{job_id}"
            
            try:
                async with self.session.ws_connect(ws_url) as ws:
                    print("✅ WebSocket connection established")
                    
                    # Wait for a message
                    try:
                        msg = await asyncio.wait_for(ws.receive(), timeout=5.0)
                        print(f"✅ Received WebSocket message: {msg.data}")
                        return True
                    except asyncio.TimeoutError:
                        print("⚠️ No WebSocket message received within timeout")
                        return True  # Connection works, just no message
                        
            except Exception as e:
                print(f"❌ WebSocket connection failed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ WebSocket test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests and report results"""
        print("🚀 Starting Converte Pro Backend Tests")
        print("=" * 50)
        
        self.create_test_files()
        
        tests = [
            ("API Health", self.test_api_health),
            ("Stats Endpoint", self.test_stats),
            ("Image Conversion", self.test_image_conversion),
            ("PDF Operations", self.test_pdf_operations),
            ("Batch Operations", self.test_batch_operations),
            ("WebSocket Connection", self.test_websocket_connection),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results[test_name] = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
        
        print("-" * 50)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Backend is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the logs above for details.")
        
        return passed == total

async def main():
    """Main test runner"""
    async with ConverteTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)