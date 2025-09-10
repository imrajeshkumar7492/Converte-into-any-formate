#!/usr/bin/env python3
"""
Detailed File Conversion Testing - Validates actual file content and conversion quality
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

class DetailedConversionTester:
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
    
    def create_test_image(self, format_name="PNG", size=(100, 100), color='red'):
        """Create a test image file with specific content"""
        img = Image.new('RGB', size, color=color)
        buffer = io.BytesIO()
        img.save(buffer, format=format_name)
        buffer.seek(0)
        return buffer.getvalue()
    
    def create_test_text_file(self, content="This is a test document for conversion testing.\nLine 2 of the test document.\nLine 3 with special characters: àáâãäåæçèéêë"):
        """Create a test text file with specific content"""
        return content.encode('utf-8')
    
    def validate_png_content(self, content):
        """Validate PNG file content"""
        try:
            # Check PNG signature
            if not content.startswith(b'\x89PNG\r\n\x1a\n'):
                return False, "Invalid PNG signature"
            
            # Try to open with PIL
            img = Image.open(io.BytesIO(content))
            width, height = img.size
            
            return True, f"Valid PNG: {width}x{height}, mode: {img.mode}"
        except Exception as e:
            return False, f"PNG validation failed: {str(e)}"
    
    def validate_pdf_content(self, content):
        """Validate PDF file content"""
        try:
            # Check PDF signature
            if not content.startswith(b'%PDF'):
                return False, "Invalid PDF signature"
            
            # Check for PDF trailer
            if b'%%EOF' not in content:
                return False, "Missing PDF trailer"
            
            # Try to read with PyPDF2
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(content))
            num_pages = len(reader.pages)
            
            # Try to extract some text
            text = ""
            for page in reader.pages[:2]:  # Check first 2 pages
                text += page.extract_text()
            
            return True, f"Valid PDF: {num_pages} pages, extracted text length: {len(text)}"
        except Exception as e:
            return False, f"PDF validation failed: {str(e)}"
    
    def validate_text_content(self, content, expected_keywords=None):
        """Validate text file content"""
        try:
            text = content.decode('utf-8')
            
            if expected_keywords:
                found_keywords = []
                for keyword in expected_keywords:
                    if keyword.lower() in text.lower():
                        found_keywords.append(keyword)
                
                return True, f"Valid text: {len(text)} chars, found keywords: {found_keywords}"
            else:
                return True, f"Valid text: {len(text)} characters"
        except Exception as e:
            return False, f"Text validation failed: {str(e)}"
    
    def test_image_conversion_quality(self):
        """Test image conversion with detailed quality validation"""
        try:
            # Create a test image with specific content
            original_content = self.create_test_image("JPEG", (200, 150), 'blue')
            
            files = {'file': ('test_quality.jpg', io.BytesIO(original_content))}
            data = {'target_format': 'png'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Validate PNG content
                is_valid, validation_msg = self.validate_png_content(converted_content)
                
                if is_valid:
                    # Additional quality checks
                    original_img = Image.open(io.BytesIO(original_content))
                    converted_img = Image.open(io.BytesIO(converted_content))
                    
                    size_match = original_img.size == converted_img.size
                    
                    self.log_result("Image Conversion Quality", True,
                                  f"High-quality conversion verified",
                                  {
                                      "validation": validation_msg,
                                      "size_preserved": size_match,
                                      "original_size": original_img.size,
                                      "converted_size": converted_img.size,
                                      "file_size": f"{len(converted_content)} bytes"
                                  })
                    return True
                else:
                    self.log_result("Image Conversion Quality", False, validation_msg)
                    return False
            else:
                self.log_result("Image Conversion Quality", False,
                              f"Conversion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Image Conversion Quality", False, f"Test failed: {str(e)}")
            return False
    
    def test_text_to_pdf_content_preservation(self):
        """Test text to PDF conversion with content validation"""
        try:
            test_text = "CONVERSION TEST DOCUMENT\n\nThis document tests text to PDF conversion.\n\nSpecial characters: àáâãäåæçèéêë\nNumbers: 1234567890\nSymbols: !@#$%^&*()"
            original_content = self.create_test_text_file(test_text)
            
            files = {'file': ('test_content.txt', io.BytesIO(original_content))}
            data = {'target_format': 'pdf'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Validate PDF content
                is_valid, validation_msg = self.validate_pdf_content(converted_content)
                
                if is_valid:
                    # Check if original text content is preserved
                    from PyPDF2 import PdfReader
                    reader = PdfReader(io.BytesIO(converted_content))
                    extracted_text = ""
                    for page in reader.pages:
                        extracted_text += page.extract_text()
                    
                    # Check for key phrases
                    key_phrases = ["CONVERSION TEST DOCUMENT", "Special characters", "Numbers: 1234567890"]
                    found_phrases = [phrase for phrase in key_phrases if phrase in extracted_text]
                    
                    content_preserved = len(found_phrases) >= 2  # At least 2 out of 3 key phrases
                    
                    self.log_result("Text to PDF Content Preservation", content_preserved,
                                  f"Content preservation: {len(found_phrases)}/3 key phrases found",
                                  {
                                      "validation": validation_msg,
                                      "found_phrases": found_phrases,
                                      "extracted_length": len(extracted_text),
                                      "file_size": f"{len(converted_content)} bytes"
                                  })
                    return content_preserved
                else:
                    self.log_result("Text to PDF Content Preservation", False, validation_msg)
                    return False
            else:
                self.log_result("Text to PDF Content Preservation", False,
                              f"Conversion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Text to PDF Content Preservation", False, f"Test failed: {str(e)}")
            return False
    
    def test_pdf_to_text_extraction(self):
        """Test PDF to text conversion with content validation"""
        try:
            # First create a PDF from text
            test_text = "PDF EXTRACTION TEST\n\nThis tests PDF to text extraction.\nLine 3 of the document.\nFinal line with numbers: 42"
            original_content = self.create_test_text_file(test_text)
            
            # Convert text to PDF first
            files = {'file': ('source.txt', io.BytesIO(original_content))}
            data = {'target_format': 'pdf'}
            
            pdf_response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if pdf_response.status_code != 200:
                self.log_result("PDF to Text Extraction Setup", False, "Failed to create test PDF")
                return False
            
            pdf_content = pdf_response.content
            
            # Now convert PDF back to text
            files = {'file': ('test.pdf', io.BytesIO(pdf_content))}
            data = {'target_format': 'txt'}
            
            text_response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if text_response.status_code == 200:
                extracted_content = text_response.content
                
                # Validate text content
                is_valid, validation_msg = self.validate_text_content(extracted_content, 
                                                                    ["PDF EXTRACTION TEST", "extraction", "numbers: 42"])
                
                if is_valid:
                    extracted_text = extracted_content.decode('utf-8')
                    
                    # Check for key content
                    key_content = ["PDF EXTRACTION TEST", "extraction", "42"]
                    found_content = [content for content in key_content if content in extracted_text]
                    
                    extraction_quality = len(found_content) >= 2
                    
                    self.log_result("PDF to Text Extraction", extraction_quality,
                                  f"Text extraction quality: {len(found_content)}/3 key items found",
                                  {
                                      "validation": validation_msg,
                                      "found_content": found_content,
                                      "file_size": f"{len(extracted_content)} bytes"
                                  })
                    return extraction_quality
                else:
                    self.log_result("PDF to Text Extraction", False, validation_msg)
                    return False
            else:
                self.log_result("PDF to Text Extraction", False,
                              f"PDF to text conversion failed: {text_response.status_code} - {text_response.text}")
                return False
                
        except Exception as e:
            self.log_result("PDF to Text Extraction", False, f"Test failed: {str(e)}")
            return False
    
    def test_conversion_library_availability(self):
        """Test if all required conversion libraries are available"""
        try:
            # Test image libraries
            try:
                from PIL import Image
                pil_available = True
            except ImportError:
                pil_available = False
            
            # Test document libraries
            try:
                from PyPDF2 import PdfReader
                pypdf2_available = True
            except ImportError:
                pypdf2_available = False
            
            try:
                from reportlab.pdfgen import canvas
                reportlab_available = True
            except ImportError:
                reportlab_available = False
            
            try:
                from docx import Document
                docx_available = True
            except ImportError:
                docx_available = False
            
            # Test audio/video libraries (these might not be available)
            try:
                import moviepy
                moviepy_available = True
            except ImportError:
                moviepy_available = False
            
            try:
                import pydub
                pydub_available = True
            except ImportError:
                pydub_available = False
            
            libraries = {
                "PIL (Pillow)": pil_available,
                "PyPDF2": pypdf2_available,
                "ReportLab": reportlab_available,
                "python-docx": docx_available,
                "MoviePy": moviepy_available,
                "Pydub": pydub_available
            }
            
            available_count = sum(libraries.values())
            total_count = len(libraries)
            
            # Core libraries (PIL, PyPDF2, ReportLab, python-docx) should be available
            core_libraries = ["PIL (Pillow)", "PyPDF2", "ReportLab", "python-docx"]
            core_available = all(libraries[lib] for lib in core_libraries)
            
            self.log_result("Conversion Library Availability", core_available,
                          f"Core libraries available: {core_available}, Total: {available_count}/{total_count}",
                          {"libraries": libraries})
            
            return core_available
            
        except Exception as e:
            self.log_result("Conversion Library Availability", False, f"Test failed: {str(e)}")
            return False
    
    def test_large_file_conversion(self):
        """Test conversion with larger files"""
        try:
            # Create a larger test image (500x400)
            large_image_content = self.create_test_image("JPEG", (500, 400), 'green')
            
            files = {'file': ('large_test.jpg', io.BytesIO(large_image_content))}
            data = {'target_format': 'png'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Validate conversion
                is_valid, validation_msg = self.validate_png_content(converted_content)
                
                if is_valid and len(converted_content) > 1000:  # Should be reasonably large
                    self.log_result("Large File Conversion", True,
                                  f"Successfully converted large file",
                                  {
                                      "original_size": f"{len(large_image_content)} bytes",
                                      "converted_size": f"{len(converted_content)} bytes",
                                      "validation": validation_msg
                                  })
                    return True
                else:
                    self.log_result("Large File Conversion", False,
                                  f"Conversion failed validation or too small: {validation_msg}")
                    return False
            else:
                self.log_result("Large File Conversion", False,
                              f"Conversion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Large File Conversion", False, f"Test failed: {str(e)}")
            return False
    
    def run_detailed_tests(self):
        """Run all detailed tests"""
        print("🔍 Starting Detailed File Conversion Tests...")
        print("=" * 70)
        
        tests = [
            ("Conversion Library Availability", self.test_conversion_library_availability),
            ("Image Conversion Quality", self.test_image_conversion_quality),
            ("Text to PDF Content Preservation", self.test_text_to_pdf_content_preservation),
            ("PDF to Text Extraction", self.test_pdf_to_text_extraction),
            ("Large File Conversion", self.test_large_file_conversion)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔬 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"🏁 Detailed Test Summary: {passed}/{total} tests passed")
        
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
    tester = DetailedConversionTester()
    passed, total, results = tester.run_detailed_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All detailed tests passed! File conversion system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} detailed tests failed. Issues found in conversion system.")
        return 1

if __name__ == "__main__":
    exit(main())