#!/usr/bin/env python3
"""
Edge Case Testing - Tests problematic conversions and edge cases
"""

import requests
import json
import io
import os
from PIL import Image

# Get backend URL from environment
BACKEND_URL = "https://clean-embed.preview.emergentagent.com/api"

class EdgeCaseTester:
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
    
    def test_unsupported_format_combinations(self):
        """Test various unsupported format combinations"""
        try:
            # Test image to unsupported format
            image_content = self.create_test_image("JPEG")
            
            unsupported_tests = [
                ("test.jpg", image_content, "xyz", "Image to completely unsupported format"),
                ("test.jpg", image_content, "mp3", "Image to audio format"),
                ("test.jpg", image_content, "docx", "Image to document format (should fail)"),
            ]
            
            failed_as_expected = 0
            total_tests = len(unsupported_tests)
            
            for filename, content, target_format, description in unsupported_tests:
                files = {'file': (filename, io.BytesIO(content))}
                data = {'target_format': target_format}
                
                response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
                
                if response.status_code in [400, 500]:  # Should fail
                    failed_as_expected += 1
                    print(f"   ✓ {description}: Correctly rejected ({response.status_code})")
                else:
                    print(f"   ✗ {description}: Unexpectedly succeeded ({response.status_code})")
            
            success = failed_as_expected == total_tests
            self.log_result("Unsupported Format Combinations", success,
                          f"Correctly rejected {failed_as_expected}/{total_tests} unsupported conversions")
            return success
            
        except Exception as e:
            self.log_result("Unsupported Format Combinations", False, f"Test failed: {str(e)}")
            return False
    
    def test_empty_file_handling(self):
        """Test handling of empty files"""
        try:
            # Test with empty file
            empty_content = b""
            
            files = {'file': ('empty.txt', io.BytesIO(empty_content))}
            data = {'target_format': 'pdf'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code in [400, 500]:
                self.log_result("Empty File Handling", True,
                              f"Correctly handled empty file with error ({response.status_code})")
                return True
            elif response.status_code == 200:
                # If it succeeds, check if the result is reasonable
                converted_content = response.content
                if len(converted_content) > 100:  # Should have some PDF structure
                    self.log_result("Empty File Handling", True,
                                  f"Successfully converted empty file to PDF ({len(converted_content)} bytes)")
                    return True
                else:
                    self.log_result("Empty File Handling", False,
                                  f"Empty file conversion produced suspiciously small result ({len(converted_content)} bytes)")
                    return False
            else:
                self.log_result("Empty File Handling", False,
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Empty File Handling", False, f"Test failed: {str(e)}")
            return False
    
    def test_corrupted_file_handling(self):
        """Test handling of corrupted files"""
        try:
            # Test with corrupted image file (wrong header)
            corrupted_content = b"This is not a real image file but pretends to be one"
            
            files = {'file': ('corrupted.jpg', io.BytesIO(corrupted_content))}
            data = {'target_format': 'png'}
            
            response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
            
            if response.status_code in [400, 500]:
                self.log_result("Corrupted File Handling", True,
                              f"Correctly handled corrupted file with error ({response.status_code})")
                return True
            elif response.status_code == 200:
                self.log_result("Corrupted File Handling", False,
                              "Corrupted file conversion unexpectedly succeeded")
                return False
            else:
                self.log_result("Corrupted File Handling", False,
                              f"Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Corrupted File Handling", False, f"Test failed: {str(e)}")
            return False
    
    def test_format_case_sensitivity(self):
        """Test format case sensitivity"""
        try:
            image_content = self.create_test_image("JPEG")
            
            # Test different case variations
            case_tests = [
                ("test.jpg", "PNG", "Uppercase target format"),
                ("test.jpg", "png", "Lowercase target format"),
                ("test.jpg", "Png", "Mixed case target format"),
            ]
            
            successful_conversions = 0
            total_tests = len(case_tests)
            
            for filename, target_format, description in case_tests:
                files = {'file': (filename, io.BytesIO(image_content))}
                data = {'target_format': target_format}
                
                response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
                
                if response.status_code == 200:
                    converted_content = response.content
                    if len(converted_content) > 100:  # Reasonable size
                        successful_conversions += 1
                        print(f"   ✓ {description}: Success ({len(converted_content)} bytes)")
                    else:
                        print(f"   ✗ {description}: Too small ({len(converted_content)} bytes)")
                else:
                    print(f"   ✗ {description}: Failed ({response.status_code})")
            
            success = successful_conversions == total_tests
            self.log_result("Format Case Sensitivity", success,
                          f"Successfully handled {successful_conversions}/{total_tests} case variations")
            return success
            
        except Exception as e:
            self.log_result("Format Case Sensitivity", False, f"Test failed: {str(e)}")
            return False
    
    def test_working_format_matrix(self):
        """Test a matrix of known working format combinations"""
        try:
            # Test combinations that should definitely work
            working_tests = [
                ("test.jpg", self.create_test_image("JPEG"), "png", "JPG to PNG"),
                ("test.png", self.create_test_image("PNG"), "jpg", "PNG to JPG"),
                ("test.jpg", self.create_test_image("JPEG"), "pdf", "JPG to PDF"),
                ("test.txt", b"Test document content", "pdf", "TXT to PDF"),
            ]
            
            successful_conversions = 0
            total_tests = len(working_tests)
            
            for filename, content, target_format, description in working_tests:
                files = {'file': (filename, io.BytesIO(content))}
                data = {'target_format': target_format}
                
                response = self.session.post(f"{BACKEND_URL}/convert", files=files, data=data)
                
                if response.status_code == 200:
                    converted_content = response.content
                    if len(converted_content) > 50:  # Reasonable size
                        successful_conversions += 1
                        print(f"   ✓ {description}: Success ({len(converted_content)} bytes)")
                    else:
                        print(f"   ✗ {description}: Too small ({len(converted_content)} bytes)")
                else:
                    print(f"   ✗ {description}: Failed ({response.status_code}) - {response.text[:100]}")
            
            success = successful_conversions == total_tests
            self.log_result("Working Format Matrix", success,
                          f"Successfully converted {successful_conversions}/{total_tests} known working combinations")
            return success
            
        except Exception as e:
            self.log_result("Working Format Matrix", False, f"Test failed: {str(e)}")
            return False
    
    def run_edge_case_tests(self):
        """Run all edge case tests"""
        print("🔍 Starting Edge Case Tests...")
        print("=" * 50)
        
        tests = [
            ("Working Format Matrix", self.test_working_format_matrix),
            ("Unsupported Format Combinations", self.test_unsupported_format_combinations),
            ("Format Case Sensitivity", self.test_format_case_sensitivity),
            ("Empty File Handling", self.test_empty_file_handling),
            ("Corrupted File Handling", self.test_corrupted_file_handling),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test execution failed: {str(e)}")
        
        print("\n" + "=" * 50)
        print(f"🏁 Edge Case Test Summary: {passed}/{total} tests passed")
        
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
    tester = EdgeCaseTester()
    passed, total, results = tester.run_edge_case_tests()
    
    # Return exit code based on results
    if passed == total:
        print("\n🎉 All edge case tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} edge case tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())