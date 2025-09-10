#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for File Conversion Endpoints
Tests all new file conversion functionality with real files and conversions
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
BACKEND_URL = "https://system-status-2.preview.emergentagent.com/api"

class FileConversionTester:
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
    
    def create_test_image(self, format_name="PNG", size=(100, 100)):
        """Create a test image file"""
        img = Image.new('RGB', size, color='red')
        buffer = io.BytesIO()
        img.save(buffer, format=format_name)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_test_text_file(self, content="This is a test document for conversion testing."):
        """Create a test text file"""
        return content.encode('utf-8')
    
    def create_test_pdf(self):
        """Create a simple test PDF using reportlab"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Test PDF Document")
            c.drawString(100, 730, "This is a test PDF for conversion testing.")
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            # Fallback: create a minimal PDF-like content
            pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
            return pdf_content
    
    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                self.log_result("Basic Connectivity", True, f"API accessible: {data.get('message', 'OK')}")
                return True
            else:
                self.log_result("Basic Connectivity", False, f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Basic Connectivity", False, f"Connection failed: {str(e)}")
            return False
    
    def test_file_upload(self):
        """Test POST /api/upload endpoint"""
        try:
            # Test with multiple file types
            test_files = [
                ("test_image.jpg", self.create_test_image("JPEG"), "image/jpeg"),
                ("test_image.png", self.create_test_image("PNG"), "image/png"),
                ("test_document.txt", self.create_test_text_file(), "text/plain"),
                ("test_document.pdf", self.create_test_pdf(), "application/pdf")
            ]
            
            files = []
            for filename, content, mime_type in test_files:
                files.append(('files', (filename, io.BytesIO(content), mime_type)))
            
            response = self.session.post(f"{BACKEND_URL}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                uploaded_files = data.get('files', [])
                
                if len(uploaded_files) == len(test_files):
                    # Check each uploaded file has required fields
                    all_valid = True
                    for file_info in uploaded_files:
                        required_fields = ['id', 'filename', 'source_format', 'file_size', 'supported_formats']
                        for field in required_fields:
                            if field not in file_info:
                                all_valid = False
                                break
                        
                        # Check file size is reasonable (not just mock 20 bytes)
                        file_size = file_info.get('file_size', 0)
                        if file_size <= 20:  # Only fail if it's the old mock size
                            print(f"DEBUG: File {file_info.get('filename')} has suspiciously small size {file_size} bytes")
                            all_valid = False
                            break
                    
                    if all_valid:
                        self.log_result("File Upload", True, 
                                      f"Successfully uploaded {len(uploaded_files)} files with proper metadata",
                                      {"files": [f"{f['filename']} ({f['file_size']} bytes)" for f in uploaded_files]})
                        return True
                    else:
                        self.log_result("File Upload", False, "Uploaded files missing required fields or too small")
                        return False
                else:
                    self.log_result("File Upload", False, f"Expected {len(test_files)} files, got {len(uploaded_files)}")
                    return False
            else:
                self.log_result("File Upload", False, f"Upload failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("File Upload", False, f"Upload test failed: {str(e)}")
            return False
    
    def test_supported_formats(self):
        """Test GET /api/supported-formats/{source_format} endpoint"""
        try:
            test_formats = ['jpg', 'png', 'pdf', 'mp4', 'mp3', 'docx']
            all_passed = True
            
            for source_format in test_formats:
                response = self.session.get(f"{BACKEND_URL}/supported-formats/{source_format}")
                
                if response.status_code == 200:
                    data = response.json()
                    supported_formats = data.get('supported_formats', [])
                    
                    if len(supported_formats) > 0:
                        self.log_result(f"Supported Formats - {source_format.upper()}", True,
                                      f"Found {len(supported_formats)} supported formats",
                                      {"formats": supported_formats})
                    else:
                        self.log_result(f"Supported Formats - {source_format.upper()}", False,
                                      "No supported formats returned")
                        all_passed = False
                else:
                    self.log_result(f"Supported Formats - {source_format.upper()}", False,
                                  f"Request failed with status {response.status_code}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_result("Supported Formats", False, f"Test failed: {str(e)}")
            return False
    
    def test_single_file_conversion(self):
        """Test POST /api/convert endpoint with real conversions"""
        try:
            # Test different conversion scenarios
            test_conversions = [
                ("test_image.jpg", self.create_test_image("JPEG"), "png", "Image JPG to PNG"),
                ("test_image.png", self.create_test_image("PNG"), "pdf", "Image PNG to PDF"),
                ("test_document.txt", self.create_test_text_file(), "pdf", "Text to PDF"),
                ("test_document.pdf", self.create_test_pdf(), "txt", "PDF to Text")
            ]
            
            all_passed = True
            
            for filename, content, target_format, description in test_conversions:
                try:
                    files = {'file': (filename, io.BytesIO(content))}
                    data = {'target_format': target_format}
                    
                    response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
                    
                    if response.status_code == 200:
                        # Check if we got actual file content (not just mock)
                        converted_content = response.content
                        
                        if len(converted_content) > 20:  # Should be larger than mock content
                            # Verify content type based on target format
                            content_valid = True
                            if target_format.lower() == 'pdf':
                                content_valid = converted_content.startswith(b'%PDF')
                            elif target_format.lower() == 'png':
                                content_valid = converted_content.startswith(b'\x89PNG')
                            elif target_format.lower() == 'txt':
                                try:
                                    converted_content.decode('utf-8')
                                    content_valid = True
                                except:
                                    content_valid = False
                            
                            if content_valid:
                                self.log_result(f"Single Conversion - {description}", True,
                                              f"Successfully converted to {target_format.upper()}",
                                              {"size": f"{len(converted_content)} bytes"})
                            else:
                                self.log_result(f"Single Conversion - {description}", False,
                                              f"Converted content appears invalid for {target_format}")
                                all_passed = False
                        else:
                            self.log_result(f"Single Conversion - {description}", False,
                                          f"Converted file too small ({len(converted_content)} bytes) - likely mock content")
                            all_passed = False
                    else:
                        self.log_result(f"Single Conversion - {description}", False,
                                      f"Conversion failed with status {response.status_code}: {response.text}")
                        all_passed = False
                        
                except Exception as e:
                    self.log_result(f"Single Conversion - {description}", False, f"Test failed: {str(e)}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_result("Single File Conversion", False, f"Test suite failed: {str(e)}")
            return False
    
    def test_batch_conversion(self):
        """Test POST /api/convert-batch endpoint"""
        try:
            # Create test files for batch conversion
            test_files = [
                ("image1.jpg", self.create_test_image("JPEG")),
                ("image2.png", self.create_test_image("PNG")),
                ("document.txt", self.create_test_text_file())
            ]
            
            # Define target formats for each file
            format_mapping = {
                "image1.jpg": "png",
                "image2.png": "pdf", 
                "document.txt": "pdf"
            }
            
            files = []
            for filename, content in test_files:
                files.append(('files', (filename, io.BytesIO(content))))
            
            data = {'target_formats': json.dumps(format_mapping)}
            
            response = self.session.post(f"{BACKEND_URL}/convert-batch", files=files, data=data)
            
            if response.status_code == 200:
                result_data = response.json()
                results = result_data.get('results', [])
                
                if len(results) == len(test_files):
                    successful_conversions = [r for r in results if r.get('status') == 'success']
                    
                    if len(successful_conversions) > 0:
                        # Check if converted files have reasonable sizes
                        valid_sizes = all(r.get('size', 0) > 50 for r in successful_conversions)
                        
                        if valid_sizes:
                            self.log_result("Batch Conversion", True,
                                          f"Successfully converted {len(successful_conversions)}/{len(results)} files",
                                          {"results": [f"{r['original_filename']} -> {r.get('converted_filename', 'N/A')} ({r.get('size', 0)} bytes)" 
                                                     for r in successful_conversions]})
                            return True
                        else:
                            self.log_result("Batch Conversion", False,
                                          "Some converted files have suspiciously small sizes")
                            return False
                    else:
                        self.log_result("Batch Conversion", False, "No successful conversions in batch")
                        return False
                else:
                    self.log_result("Batch Conversion", False,
                                  f"Expected {len(test_files)} results, got {len(results)}")
                    return False
            else:
                self.log_result("Batch Conversion", False,
                              f"Batch conversion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Batch Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def test_conversion_jobs(self):
        """Test conversion job tracking endpoints"""
        try:
            # First, perform a conversion to create a job
            filename = "test_job.jpg"
            content = self.create_test_image("JPEG")
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'png'}
            
            # Perform conversion
            conversion_response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if conversion_response.status_code != 200:
                self.log_result("Conversion Jobs Setup", False, "Failed to create test conversion job")
                return False
            
            # Test GET /api/conversion-jobs
            jobs_response = self.session.get(f"{BACKEND_URL}/conversion-jobs")
            
            if jobs_response.status_code == 200:
                jobs = jobs_response.json()
                
                if isinstance(jobs, list) and len(jobs) > 0:
                    # Find our test job
                    test_job = None
                    for job in jobs:
                        if job.get('filename') == filename:
                            test_job = job
                            break
                    
                    if test_job:
                        # Test GET /api/conversion-jobs/{job_id}
                        job_id = test_job.get('id')
                        if job_id:
                            job_response = self.session.get(f"{BACKEND_URL}/conversion-jobs/{job_id}")
                            
                            if job_response.status_code == 200:
                                job_data = job_response.json()
                                
                                # Verify job has required fields
                                required_fields = ['id', 'filename', 'source_format', 'target_format', 'status', 'created_at']
                                has_all_fields = all(field in job_data for field in required_fields)
                                
                                if has_all_fields:
                                    self.log_result("Conversion Jobs", True,
                                                  f"Job tracking working correctly",
                                                  {"job_id": job_id, "status": job_data.get('status'),
                                                   "filename": job_data.get('filename')})
                                    return True
                                else:
                                    self.log_result("Conversion Jobs", False,
                                                  "Job data missing required fields")
                                    return False
                            else:
                                self.log_result("Conversion Jobs", False,
                                              f"Failed to get specific job: {job_response.status_code}")
                                return False
                        else:
                            self.log_result("Conversion Jobs", False, "Job missing ID field")
                            return False
                    else:
                        self.log_result("Conversion Jobs", False, "Test job not found in jobs list")
                        return False
                else:
                    self.log_result("Conversion Jobs", False, "No conversion jobs found")
                    return False
            else:
                self.log_result("Conversion Jobs", False,
                              f"Failed to get conversion jobs: {jobs_response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Conversion Jobs", False, f"Test failed: {str(e)}")
            return False
    
    def test_error_handling(self):
        """Test error handling for unsupported conversions"""
        try:
            # Test unsupported conversion
            filename = "test_unsupported.jpg"
            content = self.create_test_image("JPEG")
            
            files = {'file': (filename, io.BytesIO(content))}
            data = {'target_format': 'xyz'}  # Unsupported format
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 400:  # Should return bad request for unsupported conversion
                self.log_result("Error Handling", True,
                              "Correctly rejected unsupported conversion with 400 status")
                return True
            elif response.status_code == 500:
                # Also acceptable if it returns 500 with proper error message
                error_text = response.text
                if "not supported" in error_text.lower() or "conversion failed" in error_text.lower():
                    self.log_result("Error Handling", True,
                                  "Correctly rejected unsupported conversion with 500 status and error message")
                    return True
                else:
                    self.log_result("Error Handling", False,
                                  f"Got 500 status but unclear error message: {error_text}")
                    return False
            else:
                self.log_result("Error Handling", False,
                              f"Expected 400 or 500 status for unsupported conversion, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests and return summary"""
        print("🚀 Starting File Conversion API Tests...")
        print("=" * 60)
        
        tests = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("File Upload", self.test_file_upload),
            ("Supported Formats", self.test_supported_formats),
            ("Single File Conversion", self.test_single_file_conversion),
            ("Batch Conversion", self.test_batch_conversion),
            ("Conversion Jobs", self.test_conversion_jobs),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"🏁 Test Summary: {passed}/{total} tests passed")
        
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
    tester = FileConversionTester()
    passed, total, results = tester.run_all_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All tests passed! File conversion API is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())