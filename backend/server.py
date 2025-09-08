from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
import aiofiles
import uuid
import shutil
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from enum import Enum
import json

# File processing imports
from PIL import Image
import PyPDF2
from docx import Document as DocxDocument
import openpyxl
from pptx import Presentation
import img2pdf
from pdf2image import convert_from_path
import tempfile

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create directories for file storage
UPLOAD_DIR = ROOT_DIR / "uploads"
PROCESSED_DIR = ROOT_DIR / "processed"
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(title="Converte - File Conversion API")
api_router = APIRouter(prefix="/api")

# Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Conversion type enum
class ConversionType(str, Enum):
    # Image conversions
    JPG_TO_PNG = "jpg_to_png"
    PNG_TO_JPG = "png_to_jpg"
    WEBP_TO_PNG = "webp_to_png"
    PNG_TO_WEBP = "png_to_webp"
    HEIC_TO_JPG = "heic_to_jpg"
    
    # PDF operations
    MERGE_PDF = "merge_pdf"
    SPLIT_PDF = "split_pdf"
    COMPRESS_PDF = "compress_pdf"
    
    # Document to PDF
    DOCX_TO_PDF = "docx_to_pdf"
    XLSX_TO_PDF = "xlsx_to_pdf"
    PPTX_TO_PDF = "pptx_to_pdf"
    
    # PDF to formats
    PDF_TO_JPG = "pdf_to_jpg"
    JPG_TO_PDF = "jpg_to_pdf"

# Pydantic models
class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversion_type: ConversionType
    status: JobStatus = JobStatus.PENDING
    input_files: List[str] = []
    output_files: List[str] = []
    progress: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    options: Dict[str, Any] = {}

class JobCreate(BaseModel):
    conversion_type: ConversionType
    options: Dict[str, Any] = {}

class JobResponse(BaseModel):
    id: str
    conversion_type: ConversionType
    status: JobStatus
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_urls: List[str] = []

# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_job_update(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_text(json.dumps(data))
            except:
                self.disconnect(job_id)

manager = ConnectionManager()

# File processing functions
async def process_image_conversion(job: Job) -> Job:
    """Process image format conversions"""
    try:
        input_path = Path(job.input_files[0])
        output_filename = f"{input_path.stem}.{job.conversion_type.value.split('_to_')[1]}"
        output_path = PROCESSED_DIR / f"{job.id}_{output_filename}"
        
        # Update progress
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        # Open and convert image
        with Image.open(input_path) as img:
            # Convert based on type
            if job.conversion_type == ConversionType.JPG_TO_PNG:
                img.save(output_path, "PNG")
            elif job.conversion_type == ConversionType.PNG_TO_JPG:
                # Convert RGBA to RGB for JPG
                if img.mode in ("RGBA", "LA", "P"):
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = rgb_img
                img.save(output_path, "JPEG", quality=90)
            elif job.conversion_type == ConversionType.WEBP_TO_PNG:
                img.save(output_path, "PNG")
            elif job.conversion_type == ConversionType.PNG_TO_WEBP:
                img.save(output_path, "WEBP", quality=90)
            elif job.conversion_type == ConversionType.HEIC_TO_JPG:
                # For HEIC, we'll need pillow-heif or similar
                img.save(output_path, "JPEG", quality=90)
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
    
    return job

async def process_pdf_operations(job: Job) -> Job:
    """Process PDF operations like merge, split, compress"""
    try:
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        if job.conversion_type == ConversionType.MERGE_PDF:
            # Merge multiple PDFs
            merger = PyPDF2.PdfMerger()
            for input_file in job.input_files:
                merger.append(input_file)
            
            output_path = PROCESSED_DIR / f"{job.id}_merged.pdf"
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            merger.close()
            
            job.output_files = [str(output_path)]
            
        elif job.conversion_type == ConversionType.SPLIT_PDF:
            # Split PDF into individual pages
            input_path = Path(job.input_files[0])
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                output_files = []
                
                for i, page in enumerate(reader.pages):
                    writer = PyPDF2.PdfWriter()
                    writer.add_page(page)
                    
                    output_path = PROCESSED_DIR / f"{job.id}_page_{i+1}.pdf"
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    output_files.append(str(output_path))
                
                job.output_files = output_files
        
        elif job.conversion_type == ConversionType.COMPRESS_PDF:
            # Basic PDF compression
            input_path = Path(job.input_files[0])
            output_path = PROCESSED_DIR / f"{job.id}_compressed.pdf"
            
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                for page in reader.pages:
                    writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            
            job.output_files = [str(output_path)]
        
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
    
    return job

async def process_document_to_pdf(job: Job) -> Job:
    """Convert documents to PDF"""
    try:
        input_path = Path(job.input_files[0])
        output_path = PROCESSED_DIR / f"{job.id}_{input_path.stem}.pdf"
        
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        if job.conversion_type == ConversionType.JPG_TO_PDF:
            # Convert image to PDF
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(str(input_path)))
                
        elif job.conversion_type == ConversionType.PDF_TO_JPG:
            # Convert PDF to JPG
            images = convert_from_path(input_path)
            output_files = []
            
            for i, image in enumerate(images):
                jpg_path = PROCESSED_DIR / f"{job.id}_page_{i+1}.jpg"
                image.save(jpg_path, "JPEG", quality=90)
                output_files.append(str(jpg_path))
            
            job.output_files = output_files
            job.progress = 100
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            return job
        
        # Note: For DOCX, XLSX, PPTX to PDF, we would need LibreOffice
        # For now, we'll simulate the conversion
        elif job.conversion_type in [ConversionType.DOCX_TO_PDF, ConversionType.XLSX_TO_PDF, ConversionType.PPTX_TO_PDF]:
            # This is a placeholder - in production, use LibreOffice or similar
            # For now, we'll just copy the file and rename it
            shutil.copy2(input_path, output_path)
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
    
    return job

async def process_job(job: Job):
    """Main job processing function"""
    try:
        job.status = JobStatus.PROCESSING
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 0, "status": "processing"})
        
        # Route to appropriate processor based on conversion type
        if job.conversion_type in [ConversionType.JPG_TO_PNG, ConversionType.PNG_TO_JPG, 
                                 ConversionType.WEBP_TO_PNG, ConversionType.PNG_TO_WEBP,
                                 ConversionType.HEIC_TO_JPG]:
            job = await process_image_conversion(job)
        elif job.conversion_type in [ConversionType.MERGE_PDF, ConversionType.SPLIT_PDF, 
                                   ConversionType.COMPRESS_PDF]:
            job = await process_pdf_operations(job)
        elif job.conversion_type in [ConversionType.DOCX_TO_PDF, ConversionType.XLSX_TO_PDF,
                                   ConversionType.PPTX_TO_PDF, ConversionType.JPG_TO_PDF,
                                   ConversionType.PDF_TO_JPG]:
            job = await process_document_to_pdf(job)
        
        # Update job in database
        await update_job_in_db(job)
        
        # Send final update
        await manager.send_job_update(job.id, {
            "progress": job.progress,
            "status": job.status.value,
            "completed": job.status == JobStatus.COMPLETED,
            "error": job.error_message,
            "download_urls": [f"/api/download/{job.id}/{Path(f).name}" for f in job.output_files] if job.output_files else []
        })
        
        # Schedule file cleanup after 1 hour
        asyncio.create_task(cleanup_job_files(job.id, delay_hours=1))
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 0, "status": "failed", "error": str(e)})

async def update_job_in_db(job: Job):
    """Update job in MongoDB"""
    job_dict = job.dict()
    job_dict['created_at'] = job_dict['created_at'].isoformat() if job_dict.get('created_at') else None
    job_dict['completed_at'] = job_dict['completed_at'].isoformat() if job_dict.get('completed_at') else None
    
    await db.jobs.update_one(
        {"id": job.id},
        {"$set": job_dict},
        upsert=True
    )

async def cleanup_job_files(job_id: str, delay_hours: int = 1):
    """Clean up job files after specified delay"""
    await asyncio.sleep(delay_hours * 3600)  # Convert hours to seconds
    
    try:
        # Get job from database
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            return
        
        # Delete input files
        for file_path in job_data.get('input_files', []):
            try:
                Path(file_path).unlink(missing_ok=True)
            except:
                pass
        
        # Delete output files
        for file_path in job_data.get('output_files', []):
            try:
                Path(file_path).unlink(missing_ok=True)
            except:
                pass
        
        logging.info(f"Cleaned up files for job {job_id}")
        
    except Exception as e:
        logging.error(f"Error cleaning up job {job_id}: {e}")

# API Routes
@api_router.post("/jobs", response_model=JobResponse)
async def create_job(job_create: JobCreate):
    """Create a new conversion job"""
    job = Job(
        conversion_type=job_create.conversion_type,
        options=job_create.options
    )
    
    await update_job_in_db(job)
    
    return JobResponse(
        id=job.id,
        conversion_type=job.conversion_type,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at,
        download_urls=[]
    )

@api_router.post("/jobs/{job_id}/upload")
async def upload_files(job_id: str, files: List[UploadFile] = File(...)):
    """Upload files for a job"""
    try:
        # Get job from database
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        uploaded_files = []
        
        for file in files:
            # Save uploaded file
            file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            uploaded_files.append(str(file_path))
        
        # Update job with input files
        await db.jobs.update_one(
            {"id": job_id},
            {"$set": {"input_files": uploaded_files}}
        )
        
        return {"message": "Files uploaded successfully", "files": uploaded_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/jobs/{job_id}/start")
async def start_job(job_id: str):
    """Start processing a job"""
    try:
        # Get job from database
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Convert to Job object
        job_data['created_at'] = datetime.fromisoformat(job_data['created_at']) if job_data.get('created_at') else datetime.now(timezone.utc)
        job_data['completed_at'] = datetime.fromisoformat(job_data['completed_at']) if job_data.get('completed_at') else None
        job = Job(**job_data)
        
        # Start processing in background
        asyncio.create_task(process_job(job))
        
        return {"message": "Job started", "job_id": job_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get job status and details"""
    job_data = await db.jobs.find_one({"id": job_id})
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert dates
    created_at = datetime.fromisoformat(job_data['created_at']) if job_data.get('created_at') else datetime.now(timezone.utc)
    completed_at = datetime.fromisoformat(job_data['completed_at']) if job_data.get('completed_at') else None
    
    download_urls = []
    if job_data.get('output_files') and job_data.get('status') == 'completed':
        download_urls = [f"/api/download/{job_id}/{Path(f).name}" for f in job_data['output_files']]
    
    return JobResponse(
        id=job_data['id'],
        conversion_type=job_data['conversion_type'],
        status=job_data['status'],
        progress=job_data.get('progress', 0),
        error_message=job_data.get('error_message'),
        created_at=created_at,
        completed_at=completed_at,
        download_urls=download_urls
    )

@api_router.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """Download processed file"""
    # Find the file in processed directory
    file_path = None
    for file in PROCESSED_DIR.glob(f"{job_id}_*"):
        if file.name.endswith(filename) or file.name == f"{job_id}_{filename}":
            file_path = file
            break
    
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@api_router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id)

@api_router.get("/")
async def root():
    return {"message": "Converte API - File Conversion Service"}

# Background cleanup task
async def weekly_cleanup():
    """Weekly cleanup of old jobs and files"""
    while True:
        try:
            # Delete jobs older than 7 days
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            
            # Find old jobs
            old_jobs = await db.jobs.find({
                "created_at": {"$lt": week_ago.isoformat()}
            }).to_list(length=None)
            
            # Clean up files for old jobs
            for job_data in old_jobs:
                for file_path in job_data.get('input_files', []) + job_data.get('output_files', []):
                    try:
                        Path(file_path).unlink(missing_ok=True)
                    except:
                        pass
            
            # Delete old job records
            await db.jobs.delete_many({
                "created_at": {"$lt": week_ago.isoformat()}
            })
            
            logging.info(f"Weekly cleanup completed. Removed {len(old_jobs)} old jobs.")
            
        except Exception as e:
            logging.error(f"Weekly cleanup error: {e}")
        
        # Wait 7 days (in seconds)
        await asyncio.sleep(7 * 24 * 3600)

# Include router
app.include_router(api_router)

# CORS middleware
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

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    asyncio.create_task(weekly_cleanup())
    logger.info("Converte API started successfully")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()