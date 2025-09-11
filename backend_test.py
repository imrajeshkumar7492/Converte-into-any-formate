#!/usr/bin/env python3
"""
Backend API Testing for FreeConvert Clone
Tests the core backend functionality including health check, file upload, 
supported formats, and basic conversion functionality.
"""

import requests
import json
import io
import os
import tempfile
from PIL import Image
import time

# Backend URL configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASSED" if success else "❌ FAILED"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        print(f"{status} - {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"  {key}: {value}")
        print()

    def test_health_check(self):
        """Test 1: Basic API health check (/api/health)"""
        try:
            response = self.session.get(f"{API_BASE}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                services = data.get('services', {})
                
                # Check all services are healthy
                all_healthy = all('healthy' in str(status) for status in services.values())
                
                if all_healthy:
                    self.log_result(
                        "Health Check API",
                        True,
                        "Health check endpoint working perfectly",
                        {
                            "status_code": response.status_code,
                            "api_status": data.get('status'),
                            "database": services.get('database'),
                            "conversion_engine": services.get('conversion_engine'),
                            "version": data.get('version')
                        }
                    )
                else:
                    self.log_result(
                        "Health Check API",
                        False,
                        "Some services are unhealthy",
                        {"services": services}
                    )
            else:
                self.log_result(
                    "Health Check API",
                    False,
                    f"Health check returned status {response.status_code}",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Health Check API",
                False,
                f"Health check failed with exception: {str(e)}"
            )

    def create_test_files(self):
        """Create test files for upload testing"""
        test_files = {}
        
        # Create a simple text file
        text_content = "This is a test text file for FreeConvert clone testing.\nIt contains multiple lines of text."
        test_files['test.txt'] = ('test.txt', text_content.encode(), 'text/plain')
        
        # Create a simple JPG image using PIL
        try:
            img = Image.new('RGB', (100, 100), color='red')
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            test_files['test.jpg'] = ('test.jpg', img_buffer.getvalue(), 'image/jpeg')
        except Exception as e:
            print(f"Warning: Could not create test JPG image: {e}")
            
        return test_files

    def test_file_upload(self):
        """Test 2: File upload endpoint (/api/upload) - test with a simple text file"""
        try:
            test_files = self.create_test_files()
            
            # Test with text file
            if 'test.txt' in test_files:
                files = {'files': test_files['test.txt']}
                response = self.session.post(f"{API_BASE}/upload", files=files, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    uploaded_files = data.get('files', [])
                    
                    if uploaded_files and len(uploaded_files) > 0:
                        file_info = uploaded_files[0]
                        file_size = file_info.get('file_size', 0)
                        
                        # Verify file metadata
                        has_id = 'id' in file_info
                        has_filename = file_info.get('filename') == 'test.txt'
                        has_format = file_info.get('source_format') == 'TXT'
                        has_supported_formats = len(file_info.get('supported_formats', [])) > 0
                        
                        if all([has_id, has_filename, has_format, has_supported_formats, file_size > 0]):
                            self.log_result(
                                "File Upload API (Text File)",
                                True,
                                "Text file upload working perfectly",
                                {
                                    "filename": file_info.get('filename'),
                                    "source_format": file_info.get('source_format'),
                                    "file_size": f"{file_size} bytes",
                                    "supported_formats_count": len(file_info.get('supported_formats', [])),
                                    "supported_formats": file_info.get('supported_formats', [])[:5]  # Show first 5
                                }
                            )
                        else:
                            self.log_result(
                                "File Upload API (Text File)",
                                False,
                                "File upload missing required metadata",
                                {"file_info": file_info}
                            )
                    else:
                        self.log_result(
                            "File Upload API (Text File)",
                            False,
                            "No files returned in upload response",
                            {"response_data": data}
                        )
                else:
                    self.log_result(
                        "File Upload API (Text File)",
                        False,
                        f"Upload failed with status {response.status_code}",
                        {"response": response.text[:200]}
                    )
            else:
                self.log_result(
                    "File Upload API (Text File)",
                    False,
                    "Could not create test text file"
                )
                
        except Exception as e:
            self.log_result(
                "File Upload API (Text File)",
                False,
                f"Upload test failed with exception: {str(e)}"
            )

    def test_supported_formats(self):
        """Test 3: Supported formats endpoint (/api/supported-formats/JPG)"""
        try:
            response = self.session.get(f"{API_BASE}/supported-formats/JPG", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                source_format = data.get('source_format')
                supported_formats = data.get('supported_formats', [])
                count = data.get('count', 0)
                
                if source_format == 'JPG' and count > 0 and len(supported_formats) > 0:
                    self.log_result(
                        "Supported Formats API (JPG)",
                        True,
                        f"JPG format support working perfectly with {count} supported formats",
                        {
                            "source_format": source_format,
                            "supported_formats_count": count,
                            "supported_formats": supported_formats
                        }
                    )
                else:
                    self.log_result(
                        "Supported Formats API (JPG)",
                        False,
                        "Invalid supported formats response",
                        {"response_data": data}
                    )
            else:
                self.log_result(
                    "Supported Formats API (JPG)",
                    False,
                    f"Supported formats request failed with status {response.status_code}",
                    {"response": response.text[:200]}
                )
                
        except Exception as e:
            self.log_result(
                "Supported Formats API (JPG)",
                False,
                f"Supported formats test failed with exception: {str(e)}"
            )

    def test_quick_conversion(self):
        """Test 4: Quick conversion test (JPG to PNG if possible)"""
        try:
            test_files = self.create_test_files()
            
            if 'test.jpg' in test_files:
                # Prepare the conversion request
                files = {'file': test_files['test.jpg']}
                data = {'target_format': 'png'}
                
                response = self.session.post(
                    f"{API_BASE}/convert", 
                    files=files, 
                    data=data, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Check if we got a file back
                    content_type = response.headers.get('content-type', '')
                    content_length = len(response.content)
                    
                    # Check for PNG file signature
                    is_png = response.content.startswith(b'\x89PNG')
                    
                    if content_length > 0 and is_png:
                        self.log_result(
                            "Quick Conversion (JPG to PNG)",
                            True,
                            "JPG to PNG conversion working perfectly",
                            {
                                "content_type": content_type,
                                "output_size": f"{content_length} bytes",
                                "valid_png_header": is_png,
                                "content_disposition": response.headers.get('content-disposition', 'N/A')
                            }
                        )
                    else:
                        self.log_result(
                            "Quick Conversion (JPG to PNG)",
                            False,
                            "Conversion returned invalid or empty file",
                            {
                                "content_length": content_length,
                                "is_png": is_png,
                                "first_bytes": response.content[:20].hex() if response.content else "empty"
                            }
                        )
                else:
                    self.log_result(
                        "Quick Conversion (JPG to PNG)",
                        False,
                        f"Conversion failed with status {response.status_code}",
                        {"response": response.text[:200]}
                    )
            else:
                self.log_result(
                    "Quick Conversion (JPG to PNG)",
                    False,
                    "Could not create test JPG file for conversion"
                )
                
        except Exception as e:
            self.log_result(
                "Quick Conversion (JPG to PNG)",
                False,
                f"Conversion test failed with exception: {str(e)}"
            )

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting FreeConvert Clone Backend API Testing")
        print("=" * 60)
        print()
        
        # Run the requested tests
        self.test_health_check()
        self.test_file_upload()
        self.test_supported_formats()
        self.test_quick_conversion()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅ PASSED" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAILED" in result['status'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "0%")
        print()
        
        if failed > 0:
            print("❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAILED" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
            print()
        
        print("✅ BACKEND API TESTING COMPLETED!")
        return passed, failed, total

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    exit(0 if failed == 0 else 1)