import requests
import sys
import json
import time
import io
from datetime import datetime
from PIL import Image
import tempfile
import os

class ConvertAPITester:
    def __init__(self, base_url="https://convertify-7.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.job_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
        if headers is None:
            headers = {'Content-Type': 'application/json'} if not files else {}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def create_test_image(self, format='PNG', size=(100, 100)):
        """Create a test image file"""
        img = Image.new('RGB', size, color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format=format)
        img_bytes.seek(0)
        return img_bytes

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_create_job(self, conversion_type="jpg_to_png"):
        """Test job creation"""
        success, response = self.run_test(
            f"Create Job ({conversion_type})",
            "POST",
            "jobs",
            200,
            data={
                "conversion_type": conversion_type,
                "options": {}
            }
        )
        if success and 'id' in response:
            job_id = response['id']
            self.job_ids.append(job_id)
            return job_id
        return None

    def test_upload_files(self, job_id, file_type="image"):
        """Test file upload for a job"""
        if file_type == "image":
            test_file = self.create_test_image('PNG')
            files = {'files': ('test.png', test_file, 'image/png')}
        
        success, response = self.run_test(
            "Upload Files",
            "POST",
            f"jobs/{job_id}/upload",
            200,
            files=files
        )
        return success

    def test_start_job(self, job_id):
        """Test starting a job"""
        success, response = self.run_test(
            "Start Job Processing",
            "POST",
            f"jobs/{job_id}/start",
            200
        )
        return success

    def test_get_job_status(self, job_id):
        """Test getting job status"""
        success, response = self.run_test(
            "Get Job Status",
            "GET",
            f"jobs/{job_id}",
            200
        )
        return success, response

    def test_job_workflow(self, conversion_type="jpg_to_png"):
        """Test complete job workflow"""
        print(f"\n🔄 Testing Complete Job Workflow for {conversion_type}")
        
        # Step 1: Create job
        job_id = self.test_create_job(conversion_type)
        if not job_id:
            print("❌ Job creation failed, stopping workflow test")
            return False

        # Step 2: Upload files
        if not self.test_upload_files(job_id):
            print("❌ File upload failed, stopping workflow test")
            return False

        # Step 3: Start job
        if not self.test_start_job(job_id):
            print("❌ Job start failed, stopping workflow test")
            return False

        # Step 4: Monitor job progress
        print("⏳ Monitoring job progress...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)  # Wait 2 seconds between checks
            success, job_data = self.test_get_job_status(job_id)
            
            if success and job_data:
                status = job_data.get('status', 'unknown')
                progress = job_data.get('progress', 0)
                print(f"   Attempt {attempt + 1}: Status={status}, Progress={progress}%")
                
                if status == 'completed':
                    print("✅ Job completed successfully!")
                    
                    # Test download URLs if available
                    download_urls = job_data.get('download_urls', [])
                    if download_urls:
                        print(f"   Download URLs available: {len(download_urls)}")
                        # Test first download URL
                        download_url = download_urls[0]
                        self.test_download_file(download_url)
                    
                    return True
                elif status == 'failed':
                    error_msg = job_data.get('error_message', 'Unknown error')
                    print(f"❌ Job failed: {error_msg}")
                    return False
            else:
                print(f"   Attempt {attempt + 1}: Failed to get job status")

        print("❌ Job did not complete within expected time")
        return False

    def test_download_file(self, download_url):
        """Test file download"""
        full_url = f"https://convertify-7.preview.emergentagent.com{download_url}"
        
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                print(f"✅ Download test passed - File size: {len(response.content)} bytes")
                return True
            else:
                print(f"❌ Download test failed - Status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Download test failed - Error: {str(e)}")
            return False

    def test_invalid_job_operations(self):
        """Test error handling for invalid operations"""
        print(f"\n🚫 Testing Error Handling")
        
        # Test getting non-existent job
        self.run_test(
            "Get Non-existent Job",
            "GET",
            "jobs/invalid-job-id",
            404
        )
        
        # Test uploading to non-existent job
        test_file = self.create_test_image('PNG')
        files = {'files': ('test.png', test_file, 'image/png')}
        self.run_test(
            "Upload to Non-existent Job",
            "POST",
            "jobs/invalid-job-id/upload",
            404,
            files=files
        )
        
        # Test starting non-existent job
        self.run_test(
            "Start Non-existent Job",
            "POST",
            "jobs/invalid-job-id/start",
            404
        )

def main():
    print("🚀 Starting Converte API Testing")
    print("=" * 50)
    
    tester = ConvertAPITester()
    
    # Test basic API functionality
    tester.test_root_endpoint()
    
    # Test error handling
    tester.test_invalid_job_operations()
    
    # Test different conversion workflows
    conversion_types = [
        "jpg_to_png",
        "png_to_jpg", 
        "webp_to_png",
        "png_to_webp"
    ]
    
    successful_workflows = 0
    for conversion_type in conversion_types:
        if tester.test_job_workflow(conversion_type):
            successful_workflows += 1
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    print(f"Successful Workflows: {successful_workflows}/{len(conversion_types)}")
    
    if tester.job_ids:
        print(f"Created Job IDs: {tester.job_ids}")
    
    # Return appropriate exit code
    if tester.tests_passed == tester.tests_run and successful_workflows == len(conversion_types):
        print("\n🎉 All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())