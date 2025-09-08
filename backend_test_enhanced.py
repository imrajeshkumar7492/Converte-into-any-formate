import requests
import sys
import json
import time
import io
from datetime import datetime
from PIL import Image
import tempfile
import os
import PyPDF2

class ConvertProAPITester:
    def __init__(self, base_url="https://convertify-7.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.job_ids = []
        self.batch_ids = []

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
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

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

    def create_test_pdf(self):
        """Create a simple test PDF file"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "Test PDF Document")
        p.drawString(100, 700, "This is a test PDF for conversion testing.")
        p.showPage()
        p.save()
        buffer.seek(0)
        return buffer

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )

    def test_stats_endpoint(self):
        """Test the stats API endpoint"""
        return self.run_test(
            "Stats API Endpoint",
            "GET",
            "stats",
            200
        )

    def test_create_job_with_priority(self, conversion_type="jpg_to_png", priority="normal", options=None):
        """Test job creation with priority and options"""
        if options is None:
            options = {}
            
        success, response = self.run_test(
            f"Create Job ({conversion_type}, priority: {priority})",
            "POST",
            "jobs",
            200,
            data={
                "conversion_type": conversion_type,
                "priority": priority,
                "options": options
            }
        )
        if success and 'id' in response:
            job_id = response['id']
            self.job_ids.append(job_id)
            return job_id
        return None

    def test_create_batch_jobs(self):
        """Test batch job creation"""
        batch_data = {
            "batch_name": "Test Batch",
            "jobs": [
                {
                    "conversion_type": "jpg_to_png",
                    "priority": "normal",
                    "options": {}
                },
                {
                    "conversion_type": "png_to_jpg",
                    "priority": "high",
                    "options": {"quality": 90}
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Batch Jobs",
            "POST",
            "batch-jobs",
            200,
            data=batch_data
        )
        
        if success and 'batch_id' in response:
            batch_id = response['batch_id']
            self.batch_ids.append(batch_id)
            job_ids = response.get('job_ids', [])
            self.job_ids.extend(job_ids)
            return batch_id, job_ids
        return None, []

    def test_upload_files(self, job_id, file_type="image"):
        """Test file upload for a job"""
        if file_type == "image":
            test_file = self.create_test_image('PNG')
            files = {'files': ('test.png', test_file, 'image/png')}
        elif file_type == "pdf":
            try:
                test_file = self.create_test_pdf()
                files = {'files': ('test.pdf', test_file, 'application/pdf')}
            except ImportError:
                # Fallback if reportlab not available
                test_file = io.BytesIO(b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n')
                files = {'files': ('test.pdf', test_file, 'application/pdf')}
        
        success, response = self.run_test(
            f"Upload Files ({file_type})",
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

    def test_get_jobs_list(self):
        """Test getting jobs list with filters"""
        success, response = self.run_test(
            "Get Jobs List",
            "GET",
            "jobs?limit=10",
            200
        )
        return success, response

    def test_cancel_job(self, job_id):
        """Test job cancellation"""
        success, response = self.run_test(
            "Cancel Job",
            "DELETE",
            f"jobs/{job_id}",
            200
        )
        return success

    def test_advanced_image_processing(self):
        """Test advanced image processing features"""
        print(f"\n🎨 Testing Advanced Image Processing")
        
        # Test image enhancement
        job_id = self.test_create_job_with_priority(
            "image_enhance", 
            "high",
            {"sharpness": 1.5, "contrast": 1.2, "brightness": 1.1, "denoise": True}
        )
        if job_id and self.test_upload_files(job_id, "image") and self.test_start_job(job_id):
            return self.monitor_job_completion(job_id, "Image Enhancement")
        return False

    def test_advanced_pdf_operations(self):
        """Test advanced PDF operations"""
        print(f"\n📄 Testing Advanced PDF Operations")
        
        # Test PDF password protection
        job_id = self.test_create_job_with_priority(
            "pdf_protect", 
            "urgent",
            {"password": "test123"}
        )
        if job_id and self.test_upload_files(job_id, "pdf") and self.test_start_job(job_id):
            return self.monitor_job_completion(job_id, "PDF Protection")
        return False

    def test_batch_operations(self):
        """Test batch operations"""
        print(f"\n📦 Testing Batch Operations")
        
        batch_id, job_ids = self.test_create_batch_jobs()
        if not batch_id or not job_ids:
            return False
        
        # Upload files for each job in batch
        success_count = 0
        for job_id in job_ids:
            if self.test_upload_files(job_id, "image") and self.test_start_job(job_id):
                success_count += 1
        
        return success_count == len(job_ids)

    def test_priority_processing(self):
        """Test priority processing system"""
        print(f"\n⚡ Testing Priority Processing")
        
        # Create jobs with different priorities
        priorities = ["low", "normal", "high", "urgent"]
        priority_jobs = []
        
        for priority in priorities:
            job_id = self.test_create_job_with_priority("jpg_to_png", priority)
            if job_id:
                priority_jobs.append((job_id, priority))
        
        # Upload files and start all jobs
        for job_id, priority in priority_jobs:
            self.test_upload_files(job_id, "image")
            self.test_start_job(job_id)
        
        return len(priority_jobs) == len(priorities)

    def monitor_job_completion(self, job_id, job_name="Job"):
        """Monitor job until completion"""
        print(f"⏳ Monitoring {job_name} progress...")
        max_attempts = 15
        
        for attempt in range(max_attempts):
            time.sleep(3)  # Wait 3 seconds between checks
            success, job_data = self.test_get_job_status(job_id)
            
            if success and job_data:
                status = job_data.get('status', 'unknown')
                progress = job_data.get('progress', 0)
                current_stage = job_data.get('current_stage', 'Processing')
                
                print(f"   Attempt {attempt + 1}: Status={status}, Progress={progress}%, Stage={current_stage}")
                
                if status == 'completed':
                    print(f"✅ {job_name} completed successfully!")
                    
                    # Check metadata and file sizes
                    metadata = job_data.get('metadata', {})
                    file_sizes = job_data.get('file_sizes', {})
                    
                    if metadata:
                        print(f"   Metadata: {metadata}")
                    if file_sizes:
                        print(f"   File sizes: {file_sizes}")
                    
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
                    print(f"❌ {job_name} failed: {error_msg}")
                    return False
            else:
                print(f"   Attempt {attempt + 1}: Failed to get job status")

        print(f"❌ {job_name} did not complete within expected time")
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

    def test_job_workflow(self, conversion_type="jpg_to_png", priority="normal", options=None):
        """Test complete job workflow"""
        print(f"\n🔄 Testing Complete Job Workflow for {conversion_type}")
        
        # Step 1: Create job
        job_id = self.test_create_job_with_priority(conversion_type, priority, options)
        if not job_id:
            print("❌ Job creation failed, stopping workflow test")
            return False

        # Step 2: Upload files
        file_type = "pdf" if "pdf" in conversion_type else "image"
        if not self.test_upload_files(job_id, file_type):
            print("❌ File upload failed, stopping workflow test")
            return False

        # Step 3: Start job
        if not self.test_start_job(job_id):
            print("❌ Job start failed, stopping workflow test")
            return False

        # Step 4: Monitor job progress
        return self.monitor_job_completion(job_id, f"{conversion_type} workflow")

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
    print("🚀 Starting Converte Pro API Testing")
    print("=" * 60)
    
    tester = ConvertProAPITester()
    
    # Test basic API functionality
    print("\n📋 BASIC API TESTS")
    print("-" * 30)
    tester.test_root_endpoint()
    tester.test_stats_endpoint()
    tester.test_get_jobs_list()
    
    # Test error handling
    tester.test_invalid_job_operations()
    
    # Test advanced features
    print("\n🔬 ADVANCED FEATURE TESTS")
    print("-" * 30)
    advanced_tests = [
        ("Advanced Image Processing", tester.test_advanced_image_processing),
        ("Advanced PDF Operations", tester.test_advanced_pdf_operations),
        ("Batch Operations", tester.test_batch_operations),
        ("Priority Processing", tester.test_priority_processing)
    ]
    
    advanced_passed = 0
    for test_name, test_func in advanced_tests:
        try:
            if test_func():
                advanced_passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
    
    # Test different conversion workflows
    print("\n🔄 CONVERSION WORKFLOW TESTS")
    print("-" * 30)
    conversion_tests = [
        ("jpg_to_png", "normal", {}),
        ("png_to_jpg", "high", {"quality": 95}),
        ("image_resize", "urgent", {"width": 200, "height": 200}),
        ("image_compress", "normal", {"quality": 80}),
        ("pdf_protect", "high", {"password": "secure123"})
    ]
    
    successful_workflows = 0
    for conversion_type, priority, options in conversion_tests:
        try:
            if tester.test_job_workflow(conversion_type, priority, options):
                successful_workflows += 1
        except Exception as e:
            print(f"❌ Workflow {conversion_type} failed with error: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    print(f"Advanced Features Passed: {advanced_passed}/{len(advanced_tests)}")
    print(f"Successful Workflows: {successful_workflows}/{len(conversion_tests)}")
    
    if tester.job_ids:
        print(f"Created Job IDs: {len(tester.job_ids)} jobs")
    if tester.batch_ids:
        print(f"Created Batch IDs: {tester.batch_ids}")
    
    # Determine overall success
    overall_success = (
        tester.tests_passed >= tester.tests_run * 0.8 and  # 80% test pass rate
        advanced_passed >= len(advanced_tests) * 0.5 and   # 50% advanced features working
        successful_workflows >= len(conversion_tests) * 0.6  # 60% workflows working
    )
    
    if overall_success:
        print("\n🎉 Overall testing SUCCESSFUL! Converte Pro API is working well.")
        return 0
    else:
        print(f"\n⚠️  Some critical issues found. Please review the failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())