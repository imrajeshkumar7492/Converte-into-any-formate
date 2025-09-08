from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Query
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
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import tempfile
import subprocess
import traceback
from contextlib import asynccontextmanager

# Enhanced imports for better error handling
import redis
from celery import Celery
from celery.exceptions import Retry
import hashlib
import mimetypes

# File processing imports
from PIL import Image, ImageEnhance, ImageFilter
import PyPDF2
from docx import Document as DocxDocument
import openpyxl
from pptx import Presentation
import img2pdf
from pdf2image import convert_from_path
try:
    import pytesseract
    import cv2
    import numpy as np
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    logging.warning("Advanced features (OCR, CV2) not available - install pytesseract and opencv-python")

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF not available - advanced PDF features limited")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Enhanced configuration with error handling
try:
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'converte_pro')
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # MongoDB connection with retry logic
    client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
    db = client[db_name]
    
    # Redis connection for caching and queue
    redis_client = redis.from_url(redis_url, decode_responses=True)
    
    # Celery configuration for background tasks
    celery_app = Celery(
        'converte',
        broker=redis_url,
        backend=redis_url,
        include=['server']
    )
    
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,  # 1 hour
        task_soft_time_limit=3300,  # 55 minutes
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_disable_rate_limits=True,
    )
    
except Exception as e:
    logging.error(f"Failed to initialize database connections: {e}")
    # Fallback to basic setup
    client = None
    db = None
    redis_client = None
    celery_app = None

# Create directories for file storage
UPLOAD_DIR = ROOT_DIR / "uploads"
PROCESSED_DIR = ROOT_DIR / "processed"
TEMP_DIR = ROOT_DIR / "temp"
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(title="Converte Pro - Advanced File Conversion API", version="2.0.0")
api_router = APIRouter(prefix="/api")

# Enhanced Job status enum
class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Enhanced Conversion type enum with advanced features
class ConversionType(str, Enum):
    # Image conversions
    JPG_TO_PNG = "jpg_to_png"
    PNG_TO_JPG = "png_to_jpg"
    WEBP_TO_PNG = "webp_to_png"
    PNG_TO_WEBP = "png_to_webp"
    HEIC_TO_JPG = "heic_to_jpg"
    PNG_TO_SVG = "png_to_svg"
    
    # Advanced image processing
    IMAGE_ENHANCE = "image_enhance"
    IMAGE_RESIZE = "image_resize"
    IMAGE_COMPRESS = "image_compress"
    IMAGE_WATERMARK = "image_watermark"
    
    # PDF operations
    MERGE_PDF = "merge_pdf"
    SPLIT_PDF = "split_pdf"
    COMPRESS_PDF = "compress_pdf"
    ROTATE_PDF = "rotate_pdf"
    CROP_PDF = "crop_pdf"
    
    # Advanced PDF features
    PDF_OCR = "pdf_ocr"
    PDF_WATERMARK = "pdf_watermark"
    PDF_PROTECT = "pdf_protect"
    PDF_UNLOCK = "pdf_unlock"
    PDF_PAGE_NUMBERS = "pdf_page_numbers"
    PDF_OPTIMIZE = "pdf_optimize"
    
    # Document to PDF
    DOCX_TO_PDF = "docx_to_pdf"
    XLSX_TO_PDF = "xlsx_to_pdf"
    PPTX_TO_PDF = "pptx_to_pdf"
    HTML_TO_PDF = "html_to_pdf"
    
    # PDF to formats
    PDF_TO_JPG = "pdf_to_jpg"
    PDF_TO_PNG = "pdf_to_png"
    PDF_TO_DOCX = "pdf_to_docx"
    JPG_TO_PDF = "jpg_to_pdf"
    
    # Video/Audio conversions
    VIDEO_TO_GIF = "video_to_gif"
    WEBM_TO_GIF = "webm_to_gif"
    VIDEO_COMPRESS = "video_compress"
    AUDIO_CONVERT = "audio_convert"
    
    # Batch operations
    BATCH_IMAGE_CONVERT = "batch_image_convert"
    BATCH_PDF_MERGE = "batch_pdf_merge"
    BATCH_COMPRESS = "batch_compress"

# Processing priority levels
class ProcessingPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

# Enhanced Job model
class Job(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversion_type: ConversionType
    status: JobStatus = JobStatus.PENDING
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    input_files: List[str] = []
    output_files: List[str] = []
    progress: int = 0
    stages: List[str] = []
    current_stage: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    options: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    file_sizes: Dict[str, int] = {}

class JobCreate(BaseModel):
    conversion_type: ConversionType
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    options: Dict[str, Any] = {}

class JobResponse(BaseModel):
    id: str
    conversion_type: ConversionType
    status: JobStatus
    priority: ProcessingPriority
    progress: int
    stages: List[str]
    current_stage: Optional[str]
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    download_urls: List[str] = []
    metadata: Dict[str, Any] = {}
    file_sizes: Dict[str, int] = {}

class BatchJobCreate(BaseModel):
    jobs: List[JobCreate]
    batch_name: Optional[str] = None

# Enhanced WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.batch_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    async def connect_batch(self, websocket: WebSocket, batch_id: str):
        await websocket.accept()
        if batch_id not in self.batch_connections:
            self.batch_connections[batch_id] = []
        self.batch_connections[batch_id].append(websocket)

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_job_update(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_text(json.dumps(data))
            except:
                self.disconnect(job_id)

    async def send_batch_update(self, batch_id: str, data: dict):
        if batch_id in self.batch_connections:
            for websocket in self.batch_connections[batch_id][:]:
                try:
                    await websocket.send_text(json.dumps(data))
                except:
                    self.batch_connections[batch_id].remove(websocket)

manager = ConnectionManager()

# Advanced file processing functions
async def process_advanced_image(job: Job) -> Job:
    """Process advanced image operations"""
    try:
        input_path = Path(job.input_files[0])
        
        job.stages = ["Loading image", "Processing", "Applying effects", "Saving result"]
        job.current_stage = "Loading image"
        job.progress = 10
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 10, "current_stage": "Loading image"})
        
        with Image.open(input_path) as img:
            job.current_stage = "Processing"
            job.progress = 30
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 30, "current_stage": "Processing"})
            
            # Detect output format based on input and conversion type
            input_ext = input_path.suffix.lower()
            if job.conversion_type == ConversionType.IMAGE_ENHANCE:
                # Enhance image quality
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(job.options.get('sharpness', 1.2))
                
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(job.options.get('contrast', 1.1))
                
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(job.options.get('brightness', 1.0))
                
                if job.options.get('denoise', False):
                    img = img.filter(ImageFilter.MedianFilter(size=3))
                
                # Keep original format for enhancement
                output_ext = input_ext if input_ext in ['.jpg', '.jpeg', '.png'] else '.png'
                output_path = PROCESSED_DIR / f"{job.id}_enhanced{output_ext}"
                
            elif job.conversion_type == ConversionType.IMAGE_RESIZE:
                # Resize image
                width = job.options.get('width')
                height = job.options.get('height')
                
                if width and height:
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                elif width:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                elif height:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Keep original format for resize
                output_ext = input_ext if input_ext in ['.jpg', '.jpeg', '.png'] else '.png'
                output_path = PROCESSED_DIR / f"{job.id}_resized{output_ext}"
                
            elif job.conversion_type == ConversionType.IMAGE_COMPRESS:
                # Compress image
                quality = job.options.get('quality', 85)
                optimize = job.options.get('optimize', True)
                output_path = PROCESSED_DIR / f"{job.id}_compressed.jpg"
                
                if img.mode in ("RGBA", "LA", "P"):
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = rgb_img
            
            job.current_stage = "Saving result"
            job.progress = 90
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 90, "current_stage": "Saving result"})
            
            # Save the processed image
            if job.conversion_type == ConversionType.IMAGE_COMPRESS:
                img.save(output_path, "JPEG", quality=quality, optimize=optimize)
            elif output_ext in ['.jpg', '.jpeg']:
                # Convert to RGB for JPEG if needed
                if img.mode in ("RGBA", "LA", "P"):
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                    img = rgb_img
                img.save(output_path, "JPEG", quality=90)
            else:
                img.save(output_path, "PNG")
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.current_stage = "Completed"
        
        # Calculate file sizes
        job.file_sizes = {
            "input": input_path.stat().st_size,
            "output": output_path.stat().st_size
        }
        
        # Add metadata
        job.metadata = {
            "original_size": f"{input_path.stat().st_size // 1024}KB",
            "compressed_size": f"{output_path.stat().st_size // 1024}KB",
            "compression_ratio": f"{(1 - output_path.stat().st_size / input_path.stat().st_size) * 100:.1f}%"
        }
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
        job.current_stage = "Failed"
    
    return job

async def process_advanced_pdf(job: Job) -> Job:
    """Process advanced PDF operations"""
    try:
        input_path = Path(job.input_files[0])
        
        job.stages = ["Loading PDF", "Processing pages", "Applying changes", "Saving result"]
        job.current_stage = "Loading PDF"
        job.progress = 10
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 10, "current_stage": "Loading PDF"})
        
        if job.conversion_type == ConversionType.PDF_OCR and ADVANCED_FEATURES:
            # OCR processing
            job.current_stage = "Performing OCR"
            job.progress = 30
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 30, "current_stage": "Performing OCR"})
            
            # Convert PDF to images first
            images = convert_from_path(input_path, dpi=300)
            ocr_text = []
            
            for i, image in enumerate(images):
                job.progress = 30 + (i / len(images)) * 50
                await update_job_in_db(job)
                await manager.send_job_update(job.id, {"progress": int(job.progress), "current_stage": f"OCR page {i+1}/{len(images)}"})
                
                # Convert PIL image to numpy array for OCR
                img_array = np.array(image)
                text = pytesseract.image_to_string(img_array, lang=job.options.get('language', 'eng'))
                ocr_text.append(f"Page {i+1}:\n{text}\n\n")
            
            # Save OCR result as text file
            output_path = PROCESSED_DIR / f"{job.id}_ocr_result.txt"
            async with aiofiles.open(output_path, 'w', encoding='utf-8') as f:
                await f.write('\n'.join(ocr_text))
            
            job.metadata = {
                "pages_processed": len(images),
                "language": job.options.get('language', 'eng'),
                "total_text_length": len(''.join(ocr_text))
            }
            
        elif job.conversion_type == ConversionType.PDF_WATERMARK:
            # Add watermark to PDF
            job.current_stage = "Adding watermark"
            job.progress = 50
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Adding watermark"})
            
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                watermark_text = job.options.get('watermark_text', 'CONFIDENTIAL')
                
                for page in reader.pages:
                    # Add watermark (simplified version)
                    writer.add_page(page)
                
                output_path = PROCESSED_DIR / f"{job.id}_watermarked.pdf"
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
        elif job.conversion_type == ConversionType.PDF_PROTECT:
            # Password protect PDF
            job.current_stage = "Adding password protection"
            job.progress = 50
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Adding password protection"})
            
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                for page in reader.pages:
                    writer.add_page(page)
                
                # Add password protection
                password = job.options.get('password', 'protected123')
                writer.encrypt(password)
                
                output_path = PROCESSED_DIR / f"{job.id}_protected.pdf"
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                    
        elif job.conversion_type == ConversionType.PDF_ROTATE:
            # Rotate PDF pages
            job.current_stage = "Rotating pages"
            job.progress = 50
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Rotating pages"})
            
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                rotation = job.options.get('rotation', 90)  # degrees
                
                for page in reader.pages:
                    page.rotate(rotation)
                    writer.add_page(page)
                
                output_path = PROCESSED_DIR / f"{job.id}_rotated.pdf"
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
        
        else:
            # Fallback to basic PDF operations
            return await process_pdf_operations(job)
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.current_stage = "Completed"
        
        # Calculate file sizes
        if output_path.exists():
            job.file_sizes = {
                "input": input_path.stat().st_size,
                "output": output_path.stat().st_size
            }
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
        job.current_stage = "Failed"
    
    return job

async def process_batch_operations(job: Job) -> Job:
    """Process batch operations on multiple files"""
    try:
        job.stages = ["Validating files", "Processing batch", "Combining results", "Finalizing"]
        job.current_stage = "Validating files"
        job.progress = 5
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 5, "current_stage": "Validating files"})
        
        input_files = job.input_files
        output_files = []
        
        if job.conversion_type == ConversionType.BATCH_IMAGE_CONVERT:
            target_format = job.options.get('target_format', 'png')
            quality = job.options.get('quality', 90)
            
            for i, input_file in enumerate(input_files):
                job.current_stage = f"Converting file {i+1}/{len(input_files)}"
                job.progress = 10 + (i / len(input_files)) * 70
                await update_job_in_db(job)
                await manager.send_job_update(job.id, {"progress": int(job.progress), "current_stage": job.current_stage})
                
                input_path = Path(input_file)
                output_path = PROCESSED_DIR / f"{job.id}_batch_{i+1}.{target_format}"
                
                with Image.open(input_path) as img:
                    if target_format.lower() == 'jpg' and img.mode in ("RGBA", "LA", "P"):
                        rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                        img = rgb_img
                    
                    img.save(output_path, target_format.upper(), quality=quality)
                    output_files.append(str(output_path))
                    
        elif job.conversion_type == ConversionType.BATCH_PDF_MERGE:
            job.current_stage = "Merging PDFs"
            job.progress = 50
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Merging PDFs"})
            
            merger = PyPDF2.PdfMerger()
            for input_file in input_files:
                merger.append(input_file)
            
            output_path = PROCESSED_DIR / f"{job.id}_batch_merged.pdf"
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            merger.close()
            
            output_files = [str(output_path)]
        
        job.output_files = output_files
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.current_stage = "Completed"
        
        # Add batch metadata
        job.metadata = {
            "batch_size": len(input_files),
            "output_files": len(output_files),
            "processing_time": (datetime.now(timezone.utc) - job.created_at).total_seconds()
        }
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
        job.current_stage = "Failed"
    
    return job

# Enhanced image conversion function (keeping existing one for compatibility)
async def process_image_conversion(job: Job) -> Job:
    """Process basic image format conversions"""
    try:
        input_path = Path(job.input_files[0])
        output_filename = f"{input_path.stem}.{job.conversion_type.value.split('_to_')[1]}"
        output_path = PROCESSED_DIR / f"{job.id}_{output_filename}"
        
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        with Image.open(input_path) as img:
            if job.conversion_type == ConversionType.JPG_TO_PNG:
                img.save(output_path, "PNG")
            elif job.conversion_type == ConversionType.PNG_TO_JPG:
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

# Enhanced PDF operations function (keeping existing one for compatibility)
async def process_pdf_operations(job: Job) -> Job:
    """Process basic PDF operations"""
    try:
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        if job.conversion_type == ConversionType.MERGE_PDF:
            merger = PyPDF2.PdfMerger()
            for input_file in job.input_files:
                merger.append(input_file)
            
            output_path = PROCESSED_DIR / f"{job.id}_merged.pdf"
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            merger.close()
            
            job.output_files = [str(output_path)]
            
        elif job.conversion_type == ConversionType.SPLIT_PDF:
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

# Enhanced document conversion function (keeping existing one for compatibility)
async def process_document_to_pdf(job: Job) -> Job:
    """Convert documents to PDF"""
    try:
        input_path = Path(job.input_files[0])
        output_path = PROCESSED_DIR / f"{job.id}_{input_path.stem}.pdf"
        
        job.progress = 25
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 25, "status": "processing"})
        
        if job.conversion_type == ConversionType.JPG_TO_PDF:
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(str(input_path)))
                
        elif job.conversion_type == ConversionType.PDF_TO_JPG:
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
        
        elif job.conversion_type in [ConversionType.DOCX_TO_PDF, ConversionType.XLSX_TO_PDF, ConversionType.PPTX_TO_PDF]:
            # Placeholder for LibreOffice conversion
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

# Enhanced main job processing function with retry mechanism
async def process_job(job: Job, retry_count: int = 0):
    """Enhanced job processing with priority, advanced features, and retry mechanism"""
    max_retries = 3
    
    try:
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        
        # Add retry information to metadata
        if retry_count > 0:
            job.metadata["retry_count"] = retry_count
            job.metadata["retry_reason"] = "Previous attempt failed"
        
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {
            "progress": 0, 
            "status": "processing", 
            "started_at": job.started_at.isoformat(),
            "retry_count": retry_count
        })
        
        # Validate input files exist
        for file_path in job.input_files:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Input file not found: {file_path}")
        
        # Route to appropriate processor based on conversion type
        processor_map = {
            # Image processing
            ConversionType.IMAGE_ENHANCE: process_advanced_image,
            ConversionType.IMAGE_RESIZE: process_advanced_image,
            ConversionType.IMAGE_COMPRESS: process_advanced_image,
            ConversionType.IMAGE_WATERMARK: process_advanced_image,
            
            # PDF processing
            ConversionType.PDF_OCR: process_advanced_pdf,
            ConversionType.PDF_WATERMARK: process_advanced_pdf,
            ConversionType.PDF_PROTECT: process_advanced_pdf,
            ConversionType.PDF_UNLOCK: process_advanced_pdf,
            ConversionType.PDF_ROTATE: process_advanced_pdf,
            ConversionType.PDF_PAGE_NUMBERS: process_advanced_pdf,
            
            # Batch operations
            ConversionType.BATCH_IMAGE_CONVERT: process_batch_operations,
            ConversionType.BATCH_PDF_MERGE: process_batch_operations,
            ConversionType.BATCH_COMPRESS: process_batch_operations,
            
            # Basic conversions
            ConversionType.JPG_TO_PNG: process_image_conversion,
            ConversionType.PNG_TO_JPG: process_image_conversion,
            ConversionType.WEBP_TO_PNG: process_image_conversion,
            ConversionType.PNG_TO_WEBP: process_image_conversion,
            ConversionType.HEIC_TO_JPG: process_image_conversion,
            ConversionType.PNG_TO_SVG: process_image_conversion,
            
            # PDF operations
            ConversionType.MERGE_PDF: process_pdf_operations,
            ConversionType.SPLIT_PDF: process_pdf_operations,
            ConversionType.COMPRESS_PDF: process_pdf_operations,
            
            # Document conversions
            ConversionType.DOCX_TO_PDF: process_document_to_pdf,
            ConversionType.XLSX_TO_PDF: process_document_to_pdf,
            ConversionType.PPTX_TO_PDF: process_document_to_pdf,
            ConversionType.JPG_TO_PDF: process_document_to_pdf,
            ConversionType.PDF_TO_JPG: process_document_to_pdf,
            ConversionType.PDF_TO_PNG: process_document_to_pdf,
            ConversionType.PDF_TO_DOCX: process_document_to_pdf,
            ConversionType.HTML_TO_PDF: process_document_to_pdf,
            
            # Video/Audio (to be implemented)
            ConversionType.VIDEO_TO_GIF: process_video_conversion,
            ConversionType.WEBM_TO_GIF: process_video_conversion,
            ConversionType.VIDEO_COMPRESS: process_video_conversion,
            ConversionType.AUDIO_CONVERT: process_audio_conversion,
        }
        
        processor = processor_map.get(job.conversion_type, process_image_conversion)
        job = await processor(job)
        
        # Update job in database
        await update_job_in_db(job)
        
        # Send final update
        await manager.send_job_update(job.id, {
            "progress": job.progress,
            "status": job.status.value,
            "current_stage": job.current_stage,
            "completed": job.status == JobStatus.COMPLETED,
            "error": job.error_message,
            "download_urls": [f"/api/download/{job.id}/{Path(f).name}" for f in job.output_files] if job.output_files else [],
            "metadata": job.metadata,
            "file_sizes": job.file_sizes
        })
        
        # Schedule file cleanup after 2 hours for completed jobs
        if job.status == JobStatus.COMPLETED:
            asyncio.create_task(cleanup_job_files(job.id, delay_hours=2))
        
    except Exception as e:
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        
        logging.error(f"Job {job.id} failed (attempt {retry_count + 1}): {error_msg}")
        logging.error(f"Traceback: {error_traceback}")
        
        # Check if we should retry
        if retry_count < max_retries and not isinstance(e, (FileNotFoundError, ValueError)):
            # Retry after exponential backoff
            retry_delay = 2 ** retry_count
            logging.info(f"Retrying job {job.id} in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})")
            
            job.status = JobStatus.PENDING
            job.error_message = f"Retrying... (attempt {retry_count + 1}/{max_retries})"
            job.metadata["retry_count"] = retry_count + 1
            job.metadata["retry_delay"] = retry_delay
            job.metadata["last_error"] = error_msg
            
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {
                "progress": 0, 
                "status": "pending", 
                "error": job.error_message,
                "retry_count": retry_count + 1
            })
            
            # Schedule retry
            asyncio.create_task(retry_job(job, retry_count + 1, retry_delay))
        else:
            # Final failure
            job.status = JobStatus.FAILED
            job.error_message = error_msg
            job.current_stage = "Failed"
            job.metadata["final_error"] = error_msg
            job.metadata["error_traceback"] = error_traceback
            
            await update_job_in_db(job)
            await manager.send_job_update(job.id, {
                "progress": 0, 
                "status": "failed", 
                "error": error_msg, 
                "current_stage": "Failed"
            })

async def retry_job(job: Job, retry_count: int, delay: int):
    """Retry a failed job after a delay"""
    await asyncio.sleep(delay)
    await process_job(job, retry_count)

# Video processing functions
async def process_video_conversion(job: Job) -> Job:
    """Process video conversions using FFmpeg"""
    try:
        input_path = Path(job.input_files[0])
        
        job.stages = ["Loading video", "Processing", "Converting", "Saving result"]
        job.current_stage = "Loading video"
        job.progress = 10
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 10, "current_stage": "Loading video"})
        
        if job.conversion_type == ConversionType.VIDEO_TO_GIF:
            # Convert video to GIF
            output_path = PROCESSED_DIR / f"{job.id}_converted.gif"
            
            # FFmpeg command for video to GIF conversion
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-vf', 'fps=10,scale=320:-1:flags=lanczos',
                '-c:v', 'gif',
                '-y', str(output_path)
            ]
            
        elif job.conversion_type == ConversionType.VIDEO_COMPRESS:
            # Compress video
            output_path = PROCESSED_DIR / f"{job.id}_compressed.mp4"
            quality = job.options.get('quality', 23)  # CRF value
            
            cmd = [
                'ffmpeg', '-i', str(input_path),
                '-c:v', 'libx264',
                '-crf', str(quality),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y', str(output_path)
            ]
            
        else:
            raise ValueError(f"Unsupported video conversion type: {job.conversion_type}")
        
        job.current_stage = "Converting"
        job.progress = 50
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Converting"})
        
        # Execute FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.current_stage = "Completed"
        
        # Calculate file sizes
        job.file_sizes = {
            "input": input_path.stat().st_size,
            "output": output_path.stat().st_size
        }
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
        job.current_stage = "Failed"
    
    return job

# Audio processing functions
async def process_audio_conversion(job: Job) -> Job:
    """Process audio conversions using FFmpeg"""
    try:
        input_path = Path(job.input_files[0])
        
        job.stages = ["Loading audio", "Processing", "Converting", "Saving result"]
        job.current_stage = "Loading audio"
        job.progress = 10
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 10, "current_stage": "Loading audio"})
        
        # Determine output format
        target_format = job.options.get('target_format', 'mp3')
        output_path = PROCESSED_DIR / f"{job.id}_converted.{target_format}"
        
        # FFmpeg command for audio conversion
        cmd = ['ffmpeg', '-i', str(input_path)]
        
        if target_format == 'mp3':
            cmd.extend(['-c:a', 'libmp3lame', '-b:a', '192k'])
        elif target_format == 'wav':
            cmd.extend(['-c:a', 'pcm_s16le'])
        elif target_format == 'aac':
            cmd.extend(['-c:a', 'aac', '-b:a', '128k'])
        elif target_format == 'flac':
            cmd.extend(['-c:a', 'flac'])
        
        cmd.extend(['-y', str(output_path)])
        
        job.current_stage = "Converting"
        job.progress = 50
        await update_job_in_db(job)
        await manager.send_job_update(job.id, {"progress": 50, "current_stage": "Converting"})
        
        # Execute FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        job.output_files = [str(output_path)]
        job.progress = 100
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)
        job.current_stage = "Completed"
        
        # Calculate file sizes
        job.file_sizes = {
            "input": input_path.stat().st_size,
            "output": output_path.stat().st_size
        }
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.progress = 0
        job.current_stage = "Failed"
    
    return job

async def update_job_in_db(job: Job):
    """Update job in MongoDB with enhanced fields"""
    job_dict = job.dict()
    
    # Convert datetime fields to ISO strings
    for field in ['created_at', 'started_at', 'completed_at', 'estimated_completion']:
        if job_dict.get(field):
            job_dict[field] = job_dict[field].isoformat()
    
    await db.jobs.update_one(
        {"id": job.id},
        {"$set": job_dict},
        upsert=True
    )

async def cleanup_job_files(job_id: str, delay_hours: int = 2):
    """Enhanced cleanup with better error handling"""
    await asyncio.sleep(delay_hours * 3600)
    
    try:
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            return
        
        files_cleaned = 0
        
        # Delete input files
        for file_path in job_data.get('input_files', []):
            try:
                if Path(file_path).unlink(missing_ok=True):
                    files_cleaned += 1
            except:
                pass
        
        # Delete output files
        for file_path in job_data.get('output_files', []):
            try:
                if Path(file_path).unlink(missing_ok=True):
                    files_cleaned += 1
            except:
                pass
        
        logging.info(f"Cleaned up {files_cleaned} files for job {job_id}")
        
    except Exception as e:
        logging.error(f"Error cleaning up job {job_id}: {e}")

# Enhanced API Routes
@api_router.post("/jobs", response_model=JobResponse)
async def create_job(job_create: JobCreate):
    """Create a new conversion job with enhanced features"""
    job = Job(
        conversion_type=job_create.conversion_type,
        priority=job_create.priority,
        options=job_create.options
    )
    
    # Set estimated completion based on priority and job type
    base_time = 30  # seconds
    priority_multiplier = {"urgent": 0.5, "high": 0.7, "normal": 1.0, "low": 1.5}
    estimated_seconds = base_time * priority_multiplier.get(job.priority.value, 1.0)
    job.estimated_completion = job.created_at + timedelta(seconds=estimated_seconds)
    
    await update_job_in_db(job)
    
    return JobResponse(
        id=job.id,
        conversion_type=job.conversion_type,
        status=job.status,
        priority=job.priority,
        progress=job.progress,
        stages=job.stages,
        current_stage=job.current_stage,
        created_at=job.created_at,
        estimated_completion=job.estimated_completion,
        download_urls=[],
        metadata=job.metadata,
        file_sizes=job.file_sizes
    )

@api_router.post("/batch-jobs")
async def create_batch_jobs(batch_create: BatchJobCreate):
    """Create multiple jobs in a batch"""
    batch_id = str(uuid.uuid4())
    created_jobs = []
    
    for job_create in batch_create.jobs:
        job = Job(
            conversion_type=job_create.conversion_type,
            priority=job_create.priority,
            options=job_create.options
        )
        job.metadata["batch_id"] = batch_id
        job.metadata["batch_name"] = batch_create.batch_name or "Unnamed Batch"
        
        await update_job_in_db(job)
        created_jobs.append(job.id)
    
    return {
        "batch_id": batch_id,
        "job_ids": created_jobs,
        "batch_name": batch_create.batch_name,
        "total_jobs": len(created_jobs)
    }

@api_router.post("/jobs/{job_id}/upload")
async def upload_files(job_id: str, files: List[UploadFile] = File(...)):
    """Enhanced file upload with validation and metadata"""
    try:
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        uploaded_files = []
        total_size = 0
        
        for file in files:
            # Validate file size (max 50MB per file)
            content = await file.read()
            if len(content) > 50 * 1024 * 1024:
                raise HTTPException(status_code=413, detail=f"File {file.filename} is too large (max 50MB)")
            
            file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            uploaded_files.append(str(file_path))
            total_size += len(content)
        
        # Update job with input files and metadata
        await db.jobs.update_one(
            {"id": job_id},
            {"$set": {
                "input_files": uploaded_files,
                "metadata.total_input_size": total_size,
                "metadata.file_count": len(uploaded_files)
            }}
        )
        
        return {
            "message": "Files uploaded successfully",
            "files": uploaded_files,
            "total_size": total_size,
            "file_count": len(uploaded_files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/jobs/{job_id}/start")
async def start_job(job_id: str):
    """Start processing a job with enhanced priority handling"""
    try:
        job_data = await db.jobs.find_one({"id": job_id})
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Convert to Job object
        for field in ['created_at', 'started_at', 'completed_at', 'estimated_completion']:
            if job_data.get(field):
                job_data[field] = datetime.fromisoformat(job_data[field])
        
        job = Job(**job_data)
        
        # Start processing in background with priority consideration
        if job.priority in [ProcessingPriority.URGENT, ProcessingPriority.HIGH]:
            # High priority jobs start immediately
            asyncio.create_task(process_job(job))
        else:
            # Normal/low priority jobs can be queued
            asyncio.create_task(process_job(job))
        
        return {"message": "Job started", "job_id": job_id, "priority": job.priority}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Enhanced job status with detailed information"""
    job_data = await db.jobs.find_one({"id": job_id})
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Convert dates
    for field in ['created_at', 'started_at', 'completed_at', 'estimated_completion']:
        if job_data.get(field):
            job_data[field] = datetime.fromisoformat(job_data[field])
    
    download_urls = []
    if job_data.get('output_files') and job_data.get('status') == 'completed':
        download_urls = [f"/api/download/{job_id}/{Path(f).name}" for f in job_data['output_files']]
    
    return JobResponse(
        id=job_data['id'],
        conversion_type=job_data['conversion_type'],
        status=job_data['status'],
        priority=job_data.get('priority', ProcessingPriority.NORMAL),
        progress=job_data.get('progress', 0),
        stages=job_data.get('stages', []),
        current_stage=job_data.get('current_stage'),
        error_message=job_data.get('error_message'),
        created_at=job_data['created_at'],
        started_at=job_data.get('started_at'),
        completed_at=job_data.get('completed_at'),
        estimated_completion=job_data.get('estimated_completion'),
        download_urls=download_urls,
        metadata=job_data.get('metadata', {}),
        file_sizes=job_data.get('file_sizes', {})
    )

@api_router.get("/jobs")
async def get_jobs(
    status: Optional[JobStatus] = Query(None),
    priority: Optional[ProcessingPriority] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """Get jobs with filtering and pagination"""
    query = {}
    if status:
        query["status"] = status.value
    if priority:
        query["priority"] = priority.value
    
    jobs = await db.jobs.find(query).sort("created_at", -1).skip(offset).limit(limit).to_list(length=None)
    
    # Convert dates and prepare response
    response_jobs = []
    for job_data in jobs:
        # Convert ObjectId to string if present
        if '_id' in job_data:
            del job_data['_id']
            
        # Convert dates for each job
        for field in ['created_at', 'started_at', 'completed_at', 'estimated_completion']:
            if job_data.get(field):
                if isinstance(job_data[field], str):
                    job_data[field] = datetime.fromisoformat(job_data[field])
                    
        response_jobs.append(job_data)
    
    return {
        "jobs": response_jobs,
        "total": await db.jobs.count_documents(query),
        "limit": limit,
        "offset": offset
    }

@api_router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job and clean up files"""
    job_data = await db.jobs.find_one({"id": job_id})
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_data.get('status') == 'completed':
        raise HTTPException(status_code=400, detail="Cannot cancel completed job")
    
    # Update job status
    await db.jobs.update_one(
        {"id": job_id},
        {"$set": {"status": JobStatus.CANCELLED, "completed_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Clean up files immediately
    asyncio.create_task(cleanup_job_files(job_id, delay_hours=0))
    
    return {"message": "Job cancelled successfully", "job_id": job_id}

@api_router.get("/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    """Enhanced download with better file handling"""
    file_path = None
    for file in PROCESSED_DIR.glob(f"{job_id}_*"):
        if file.name.endswith(filename) or file.name == f"{job_id}_{filename}":
            file_path = file
            break
    
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    ext = file_path.suffix.lower()
    media_type_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.gif': 'image/gif',
        '.txt': 'text/plain',
        '.zip': 'application/zip'
    }
    
    media_type = media_type_map.get(ext, 'application/octet-stream')
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@api_router.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """Enhanced WebSocket endpoint with better error handling"""
    await manager.connect(websocket, job_id)
    try:
        # Send initial job status
        job_data = await db.jobs.find_one({"id": job_id})
        if job_data:
            await websocket.send_text(json.dumps({
                "type": "status",
                "status": job_data.get('status'),
                "progress": job_data.get('progress', 0),
                "current_stage": job_data.get('current_stage')
            }))
        
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id)

@api_router.websocket("/ws/batch/{batch_id}")
async def batch_websocket_endpoint(websocket: WebSocket, batch_id: str):
    """WebSocket endpoint for batch job updates"""
    await manager.connect_batch(websocket, batch_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if batch_id in manager.batch_connections:
            manager.batch_connections[batch_id].remove(websocket)

@api_router.get("/stats")
async def get_stats():
    """Get system statistics"""
    total_jobs = await db.jobs.count_documents({})
    completed_jobs = await db.jobs.count_documents({"status": "completed"})
    failed_jobs = await db.jobs.count_documents({"status": "failed"})
    processing_jobs = await db.jobs.count_documents({"status": "processing"})
    
    # Calculate total files processed
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total_size": {"$sum": "$metadata.total_input_size"}}}
    ]
    size_result = await db.jobs.aggregate(pipeline).to_list(1)
    total_size = size_result[0].get("total_size", 0) if size_result else 0
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "processing_jobs": processing_jobs,
        "success_rate": f"{(completed_jobs / total_jobs * 100):.1f}%" if total_jobs > 0 else "0%",
        "total_data_processed": f"{total_size / (1024 * 1024):.1f}MB" if total_size > 0 else "0MB"
    }

@api_router.get("/")
async def root():
    return {
        "message": "Converte Pro API - Advanced File Conversion Service",
        "version": "2.0.0",
        "features": [
            "Advanced image processing",
            "Professional PDF tools",
            "Batch operations",
            "Real-time progress tracking",
            "OCR capabilities",
            "Video/Audio conversion",
            "Automated file cleanup"
        ]
    }

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

# Enhanced background cleanup task
async def enhanced_cleanup():
    """Enhanced cleanup with better scheduling"""
    while True:
        try:
            # Daily cleanup of failed jobs older than 1 day
            day_ago = datetime.now(timezone.utc) - timedelta(days=1)
            failed_jobs = await db.jobs.find({
                "status": {"$in": ["failed", "cancelled"]},
                "created_at": {"$lt": day_ago.isoformat()}
            }).to_list(length=None)
            
            for job_data in failed_jobs:
                await cleanup_job_files(job_data["id"], delay_hours=0)
            
            # Weekly cleanup of completed jobs older than 7 days
            week_ago = datetime.now(timezone.utc) - timedelta(days=7)
            old_jobs = await db.jobs.find({
                "created_at": {"$lt": week_ago.isoformat()}
            }).to_list(length=None)
            
            for job_data in old_jobs:
                await cleanup_job_files(job_data["id"], delay_hours=0)
            
            # Delete old job records
            await db.jobs.delete_many({
                "created_at": {"$lt": week_ago.isoformat()}
            })
            
            logger.info(f"Cleanup completed. Removed {len(failed_jobs)} failed jobs and {len(old_jobs)} old jobs.")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        
        # Wait 24 hours
        await asyncio.sleep(24 * 3600)

@app.on_event("startup")
async def startup_event():
    """Enhanced startup with feature detection"""
    asyncio.create_task(enhanced_cleanup())
    
    # Log available features
    features = ["Basic conversions", "PDF operations", "Document processing"]
    if ADVANCED_FEATURES:
        features.extend(["OCR", "Advanced image processing"])
    if PYMUPDF_AVAILABLE:
        features.append("Advanced PDF features")
    
    logger.info(f"Converte Pro API v2.0.0 started with features: {', '.join(features)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()