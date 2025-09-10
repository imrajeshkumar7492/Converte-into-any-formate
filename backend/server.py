from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import io
import tempfile
import asyncio
from converters.converter_manager import ConversionManager


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class ConversionJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    source_format: str
    target_format: str
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    file_size: int = 0

class ConversionJobCreate(BaseModel):
    filename: str
    source_format: str
    target_format: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# File conversion endpoints
@api_router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files and return file information"""
    try:
        uploaded_files = []
        
        for file in files:
            # Get file info
            content = await file.read()
            file_size = len(content)
            
            # Extract format from filename
            filename = file.filename or "unknown"
            source_format = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Get supported target formats
            supported_formats = ConversionManager.get_supported_formats(source_format)
            
            # Get additional file info if possible
            file_info = ConversionManager.get_file_info(io.BytesIO(content), source_format)
            
            uploaded_files.append({
                "id": str(uuid.uuid4()),
                "filename": filename,
                "source_format": source_format.upper(),
                "file_size": file_size,
                "supported_formats": [f.upper() for f in supported_formats],
                "file_info": file_info
            })
            
            # Store file temporarily (in production, use proper file storage)
            # For now, we'll store in memory or temporary files
        
        return {
            "message": "Files uploaded successfully",
            "files": uploaded_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.post("/convert")
async def convert_file(
    file: UploadFile = File(...),
    target_format: str = Form(...)
):
    """Convert a single file to target format"""
    try:
        # Read file content
        content = await file.read()
        filename = file.filename or "unknown"
        source_format = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
        
        # Validate conversion is supported
        if not ConversionManager.is_conversion_supported(source_format, target_format.lower()):
            raise HTTPException(
                status_code=400, 
                detail=f"Conversion from {source_format} to {target_format} is not supported"
            )
        
        # Create conversion job record
        job = ConversionJob(
            filename=filename,
            source_format=source_format.upper(),
            target_format=target_format.upper(),
            status="processing",
            file_size=len(content)
        )
        
        # Store job in database
        await db.conversion_jobs.insert_one(job.dict())
        
        # Perform conversion
        try:
            converted_data = ConversionManager.convert_file(
                io.BytesIO(content), 
                source_format, 
                target_format.lower()
            )
            
            # Update job status
            await db.conversion_jobs.update_one(
                {"id": job.id},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            # Generate output filename
            base_name = '.'.join(filename.split('.')[:-1]) if '.' in filename else filename
            output_filename = f"{base_name}.{target_format.lower()}"
            
            # Return converted file
            return StreamingResponse(
                io.BytesIO(converted_data),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename={output_filename}"}
            )
            
        except Exception as conversion_error:
            # Update job with error
            await db.conversion_jobs.update_one(
                {"id": job.id},
                {
                    "$set": {
                        "status": "failed",
                        "error_message": str(conversion_error),
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            raise HTTPException(status_code=500, detail=f"Conversion failed: {str(conversion_error)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion request failed: {str(e)}")

@api_router.post("/convert-batch")
async def convert_batch(
    files: List[UploadFile] = File(...),
    target_formats: str = Form(...)  # JSON string with file-format mapping
):
    """Convert multiple files with different target formats"""
    try:
        import json
        format_mapping = json.loads(target_formats)
        
        results = []
        
        for i, file in enumerate(files):
            content = await file.read()
            filename = file.filename or f"file_{i}"
            source_format = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            
            # Get target format for this file
            target_format = format_mapping.get(filename, format_mapping.get(str(i), 'pdf')).lower()
            
            try:
                converted_data = ConversionManager.convert_file(
                    io.BytesIO(content),
                    source_format,
                    target_format
                )
                
                base_name = '.'.join(filename.split('.')[:-1]) if '.' in filename else filename
                output_filename = f"{base_name}.{target_format}"
                
                results.append({
                    "original_filename": filename,
                    "converted_filename": output_filename,
                    "status": "success",
                    "size": len(converted_data)
                })
                
            except Exception as e:
                results.append({
                    "original_filename": filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch conversion failed: {str(e)}")

@api_router.get("/supported-formats/{source_format}")
async def get_supported_formats(source_format: str):
    """Get supported target formats for a source format"""
    try:
        supported = ConversionManager.get_supported_formats(source_format.lower())
        return {
            "source_format": source_format.upper(),
            "supported_formats": [f.upper() for f in supported]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supported formats: {str(e)}")

@api_router.get("/conversion-jobs")
async def get_conversion_jobs():
    """Get all conversion jobs"""
    try:
        jobs = await db.conversion_jobs.find().sort("created_at", -1).to_list(1000)
        return [ConversionJob(**job) for job in jobs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion jobs: {str(e)}")

@api_router.get("/conversion-jobs/{job_id}")
async def get_conversion_job(job_id: str):
    """Get specific conversion job"""
    try:
        job = await db.conversion_jobs.find_one({"id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return ConversionJob(**job)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion job: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
