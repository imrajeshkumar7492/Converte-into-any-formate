#!/usr/bin/env python3
"""
Specialized PDF Conversion Testing
Focus on multi-page PDF conversion issues reported by user
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

class PDFConversionTester:
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
    
    def create_multi_page_pdf(self, num_pages=3):
        """Create a multi-page PDF for testing"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            for page_num in range(1, num_pages + 1):
                c.drawString(100, 750, f"Test PDF Document - Page {page_num}")
                c.drawString(100, 730, f"This is page {page_num} of {num_pages}")
                c.drawString(100, 710, "Testing multi-page PDF conversion functionality")
                c.drawString(100, 690, f"Content specific to page {page_num}")
                
                # Add some unique content per page
                for i in range(5):
                    c.drawString(100, 650 - (i * 20), f"Page {page_num} - Line {i + 1}: Sample text content")
                
                if page_num < num_pages:
                    c.showPage()  # Start new page
            
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            # Fallback: create a more complex PDF manually
            pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R 4 0 R 5 0 R]
/Count {num_pages}
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 6 0 R
>>
endobj
4 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 7 0 R
>>
endobj
5 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 8 0 R
>>
endobj
6 0 obj
<<
/Length 80
>>
stream
BT
/F1 12 Tf
100 700 Td
(Multi-page PDF - Page 1) Tj
0 -20 Td
(Testing conversion functionality) Tj
ET
endstream
endobj
7 0 obj
<<
/Length 80
>>
stream
BT
/F1 12 Tf
100 700 Td
(Multi-page PDF - Page 2) Tj
0 -20 Td
(Second page content here) Tj
ET
endstream
endobj
8 0 obj
<<
/Length 80
>>
stream
BT
/F1 12 Tf
100 700 Td
(Multi-page PDF - Page 3) Tj
0 -20 Td
(Third page content here) Tj
ET
endstream
endobj
xref
0 9
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000130 00000 n 
0000000221 00000 n 
0000000312 00000 n 
0000000403 00000 n 
0000000533 00000 n 
0000000663 00000 n 
trailer
<<
/Size 9
/Root 1 0 R
>>
startxref
792
%%EOF"""
            return pdf_content.encode('utf-8')
    
    def create_single_page_pdf(self):
        """Create a single-page PDF for comparison"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            c.drawString(100, 750, "Single Page PDF Document")
            c.drawString(100, 730, "This is a single page PDF for testing")
            c.drawString(100, 710, "Should convert to image formats easily")
            c.save()
            buffer.seek(0)
            return buffer.getvalue()
        except ImportError:
            # Fallback single page PDF
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
/Length 60
>>
stream
BT
/F1 12 Tf
100 700 Td
(Single Page PDF Test) Tj
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
315
%%EOF"""
            return pdf_content
    
    def test_pdf_to_jpg_single_page(self):
        """Test PDF to JPG conversion with single page"""
        try:
            pdf_content = self.create_single_page_pdf()
            
            files = {'file': ('single_page.pdf', io.BytesIO(pdf_content), 'application/pdf')}
            data = {'target_format': 'jpg'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Check if it's a valid JPG
                if len(converted_content) > 100 and converted_content.startswith(b'\xff\xd8\xff'):
                    self.log_result("PDF→JPG Single Page", True,
                                  f"Successfully converted single-page PDF to JPG",
                                  {"size": f"{len(converted_content)} bytes", "format": "Valid JPEG"})
                    return True
                else:
                    self.log_result("PDF→JPG Single Page", False,
                                  f"Converted content doesn't appear to be valid JPG (size: {len(converted_content)} bytes)")
                    return False
            else:
                self.log_result("PDF→JPG Single Page", False,
                              f"Conversion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("PDF→JPG Single Page", False, f"Test failed: {str(e)}")
            return False
    
    def test_pdf_to_jpg_multi_page(self):
        """Test PDF to JPG conversion with multi-page PDF"""
        try:
            pdf_content = self.create_multi_page_pdf(3)
            
            files = {'file': ('multi_page.pdf', io.BytesIO(pdf_content), 'application/pdf')}
            data = {'target_format': 'jpg'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code == 200:
                converted_content = response.content
                
                # Check if it's a valid JPG
                if len(converted_content) > 100 and converted_content.startswith(b'\xff\xd8\xff'):
                    self.log_result("PDF→JPG Multi-Page", True,
                                  f"Multi-page PDF converted to JPG",
                                  {"size": f"{len(converted_content)} bytes", "format": "Valid JPEG", 
                                   "note": "Check if all pages are included or just first page"})
                    return True
                else:
                    self.log_result("PDF→JPG Multi-Page", False,
                                  f"Converted content doesn't appear to be valid JPG (size: {len(converted_content)} bytes)")
                    return False
            else:
                self.log_result("PDF→JPG Multi-Page", False,
                              f"Multi-page PDF to JPG conversion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("PDF→JPG Multi-Page", False, f"Test failed: {str(e)}")
            return False
    
    def test_pdf_to_png_conversions(self):
        """Test PDF to PNG conversions"""
        try:
            test_cases = [
                ("single_page.pdf", self.create_single_page_pdf(), "Single-page PDF→PNG"),
                ("multi_page.pdf", self.create_multi_page_pdf(2), "Multi-page PDF→PNG")
            ]
            
            all_passed = True
            
            for filename, pdf_content, description in test_cases:
                files = {'file': (filename, io.BytesIO(pdf_content), 'application/pdf')}
                data = {'target_format': 'png'}
                
                response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
                
                if response.status_code == 200:
                    converted_content = response.content
                    
                    # Check if it's a valid PNG
                    if len(converted_content) > 100 and converted_content.startswith(b'\x89PNG'):
                        self.log_result(f"PDF→PNG - {description}", True,
                                      f"Successfully converted to PNG",
                                      {"size": f"{len(converted_content)} bytes", "format": "Valid PNG"})
                    else:
                        self.log_result(f"PDF→PNG - {description}", False,
                                      f"Converted content doesn't appear to be valid PNG")
                        all_passed = False
                else:
                    self.log_result(f"PDF→PNG - {description}", False,
                                  f"Conversion failed with status {response.status_code}: {response.text}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_result("PDF→PNG Conversions", False, f"Test failed: {str(e)}")
            return False
    
    def test_pdf_supported_formats(self):
        """Test what formats PDF claims to support"""
        try:
            response = self.session.get(f"{BACKEND_URL}/supported-formats/pdf")
            
            if response.status_code == 200:
                data = response.json()
                supported_formats = data.get('supported_formats', [])
                
                # Check if image formats are listed as supported
                image_formats = ['JPG', 'PNG', 'JPEG', 'BMP', 'TIFF', 'GIF']
                supported_image_formats = [f for f in supported_formats if f in image_formats]
                
                self.log_result("PDF Supported Formats", True,
                              f"PDF supports {len(supported_formats)} formats",
                              {"all_formats": supported_formats, 
                               "image_formats": supported_image_formats,
                               "supports_jpg": "JPG" in supported_formats or "JPEG" in supported_formats,
                               "supports_png": "PNG" in supported_formats})
                
                return len(supported_image_formats) > 0
            else:
                self.log_result("PDF Supported Formats", False,
                              f"Failed to get supported formats: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("PDF Supported Formats", False, f"Test failed: {str(e)}")
            return False
    
    def test_pdf_conversion_errors(self):
        """Test specific error scenarios that might be causing issues"""
        try:
            # Test with corrupted PDF
            corrupted_pdf = b"This is not a PDF file"
            
            files = {'file': ('corrupted.pdf', io.BytesIO(corrupted_pdf), 'application/pdf')}
            data = {'target_format': 'jpg'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            # Should return an error for corrupted PDF
            if response.status_code in [400, 500]:
                self.log_result("PDF Error Handling", True,
                              f"Correctly handled corrupted PDF with status {response.status_code}",
                              {"error_message": response.text[:200]})
                return True
            else:
                self.log_result("PDF Error Handling", False,
                              f"Unexpected response for corrupted PDF: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("PDF Error Handling", False, f"Test failed: {str(e)}")
            return False
    
    def test_batch_pdf_conversions(self):
        """Test batch conversion with multiple PDFs"""
        try:
            # Create multiple PDFs
            test_files = [
                ("pdf1.pdf", self.create_single_page_pdf()),
                ("pdf2.pdf", self.create_multi_page_pdf(2)),
                ("pdf3.pdf", self.create_multi_page_pdf(3))
            ]
            
            # Define target formats
            format_mapping = {
                "pdf1.pdf": "jpg",
                "pdf2.pdf": "png", 
                "pdf3.pdf": "jpg"
            }
            
            files = []
            for filename, content in test_files:
                files.append(('files', (filename, io.BytesIO(content), 'application/pdf')))
            
            data = {'target_formats': json.dumps(format_mapping)}
            
            response = self.session.post(f"{BACKEND_URL}/convert-batch", files=files, data=data)
            
            if response.status_code == 200:
                result_data = response.json()
                results = result_data.get('results', [])
                
                successful_conversions = [r for r in results if r.get('status') == 'success']
                failed_conversions = [r for r in results if r.get('status') == 'failed']
                
                self.log_result("Batch PDF Conversions", len(successful_conversions) > 0,
                              f"Batch conversion: {len(successful_conversions)} success, {len(failed_conversions)} failed",
                              {"successful": [r['original_filename'] for r in successful_conversions],
                               "failed": [f"{r['original_filename']}: {r.get('error', 'Unknown error')}" for r in failed_conversions]})
                
                return len(successful_conversions) > 0
            else:
                self.log_result("Batch PDF Conversions", False,
                              f"Batch conversion failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Batch PDF Conversions", False, f"Test failed: {str(e)}")
            return False
    
    def run_pdf_conversion_tests(self):
        """Run all PDF conversion tests"""
        print("🔍 Starting Specialized PDF Conversion Testing...")
        print("Focus: Multi-page PDF conversion issues reported by user")
        print("=" * 70)
        
        tests = [
            ("PDF Supported Formats Check", self.test_pdf_supported_formats),
            ("PDF→JPG Single Page", self.test_pdf_to_jpg_single_page),
            ("PDF→JPG Multi-Page", self.test_pdf_to_jpg_multi_page),
            ("PDF→PNG Conversions", self.test_pdf_to_png_conversions),
            ("PDF Error Handling", self.test_pdf_conversion_errors),
            ("Batch PDF Conversions", self.test_batch_pdf_conversions)
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
        
        print("\n" + "=" * 70)
        print(f"🏁 PDF Conversion Test Summary: {passed}/{total} tests passed")
        
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
    tester = PDFConversionTester()
    passed, total, results = tester.run_pdf_conversion_tests()
    
    # Analyze results for specific issues
    print("\n" + "=" * 70)
    print("🔍 ANALYSIS OF PDF CONVERSION ISSUES:")
    
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print("\n❌ IDENTIFIED ISSUES:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['message']}")
    
    # Check for specific user-reported issues
    multi_page_issues = [r for r in results if 'Multi-Page' in r['test'] and not r['success']]
    if multi_page_issues:
        print("\n⚠️  MULTI-PAGE PDF ISSUES CONFIRMED:")
        for issue in multi_page_issues:
            print(f"   • {issue['message']}")
    
    jpg_issues = [r for r in results if 'JPG' in r['test'] and not r['success']]
    if jpg_issues:
        print("\n⚠️  PDF→JPG CONVERSION ISSUES CONFIRMED:")
        for issue in jpg_issues:
            print(f"   • {issue['message']}")
    
    if passed == total:
        print("\n🎉 All PDF conversion tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} PDF conversion tests failed.")
        print("This confirms user reports of PDF conversion issues.")
        return 1

if __name__ == "__main__":
    exit(main())