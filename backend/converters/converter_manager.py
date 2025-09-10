import os
import tempfile
from typing import BinaryIO, Dict, Any
from .image_converter import ImageConverter
from .document_converter import DocumentConverter
from .audio_converter import AudioConverter
from .video_converter import VideoConverter

class ConversionManager:
    """Main conversion manager that routes conversions to appropriate converters"""
    
    # Define supported format mappings
    FORMAT_CATEGORIES = {
        'image': ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'gif', 'svg', 'ico'],
        'document': ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'],
        'spreadsheet': ['xls', 'xlsx', 'csv', 'ods'],
        'presentation': ['ppt', 'pptx', 'odp'],
        'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'ogv', 'm4v'],
        'audio': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'wma', 'aiff', 'au'],
        'archive': ['zip', 'rar', '7z', 'tar', 'gz', 'bz2']
    }
    
    @classmethod
    def get_format_category(cls, format_name: str) -> str:
        """Get the category of a format"""
        format_lower = format_name.lower()
        for category, formats in cls.FORMAT_CATEGORIES.items():
            if format_lower in formats:
                return category
        return 'unknown'
    
    @classmethod
    def is_conversion_supported(cls, source_format: str, target_format: str) -> bool:
        """Check if conversion between formats is supported"""
        source_cat = cls.get_format_category(source_format)
        target_cat = cls.get_format_category(target_format)
        
        # Same category conversions are generally supported
        if source_cat == target_cat and source_cat != 'unknown':
            return True
        
        # Special cross-category conversions we support
        cross_conversions = {
            ('image', 'document'),  # Image to PDF
            ('document', 'image'),  # PDF to Image
            ('video', 'audio'),     # Video to Audio
            ('video', 'image'),     # Video to GIF
        }
        
        return (source_cat, target_cat) in cross_conversions or (target_cat, source_cat) in cross_conversions
    
    @classmethod
    def convert_file(cls, input_file: BinaryIO, source_format: str, target_format: str) -> bytes:
        """Convert file from source format to target format"""
        
        if not cls.is_conversion_supported(source_format, target_format):
            raise Exception(f"Conversion from {source_format} to {target_format} is not supported")
        
        source_cat = cls.get_format_category(source_format)
        target_cat = cls.get_format_category(target_format)
        
        try:
            # Image conversions (most reliable)
            if source_cat == 'image' and target_cat == 'image':
                return ImageConverter.convert_image(input_file, source_format, target_format)
            
            elif source_cat == 'image' and target_cat == 'document' and target_format.lower() == 'pdf':
                return ImageConverter.convert_to_pdf(input_file, source_format)
            
            # Document conversions (reliable)
            elif source_cat == 'document':
                if target_format.lower() == 'txt':
                    if source_format.lower() == 'pdf':
                        return DocumentConverter.convert_pdf_to_text(input_file)
                    elif source_format.lower() in ['doc', 'docx']:
                        return DocumentConverter.convert_docx_to_txt(input_file)
                
                elif target_format.lower() == 'pdf':
                    if source_format.lower() in ['doc', 'docx']:
                        return DocumentConverter.convert_docx_to_pdf(input_file)
                    elif source_format.lower() == 'txt':
                        return DocumentConverter.convert_txt_to_pdf(input_file)
                
                elif target_format.lower() in ['doc', 'docx']:
                    if source_format.lower() == 'pdf':
                        return DocumentConverter.convert_pdf_to_docx(input_file)
            
            # Spreadsheet conversions (reliable)
            elif source_cat == 'spreadsheet':
                if target_format.lower() == 'csv':
                    if source_format.lower() in ['xls', 'xlsx']:
                        return DocumentConverter.convert_excel_to_csv(input_file)
                elif target_format.lower() in ['xls', 'xlsx']:
                    if source_format.lower() == 'csv':
                        return DocumentConverter.convert_csv_to_excel(input_file)
            
            # Audio conversions (may need FFmpeg)
            elif source_cat == 'audio' and target_cat == 'audio':
                try:
                    return AudioConverter.convert_audio(input_file, source_format, target_format)
                except Exception as audio_error:
                    # If audio conversion fails, provide helpful error
                    raise Exception(f"Audio conversion failed (FFmpeg may be required): {str(audio_error)}")
            
            # Video conversions (may need FFmpeg)
            elif source_cat == 'video':
                try:
                    if target_cat == 'video':
                        return VideoConverter.convert_video(input_file, source_format, target_format)
                    elif target_cat == 'audio':
                        return VideoConverter.extract_audio_from_video(input_file, source_format, target_format)
                    elif target_format.lower() == 'gif':
                        return VideoConverter.convert_video_to_gif(input_file, source_format)
                except Exception as video_error:
                    # If video conversion fails, provide helpful error
                    raise Exception(f"Video conversion failed (FFmpeg may be required): {str(video_error)}")
            
            else:
                raise Exception(f"Conversion from {source_format} to {target_format} is not implemented yet")
                
        except Exception as e:
            raise Exception(f"Conversion failed: {str(e)}")
    
    @classmethod
    def get_file_info(cls, input_file: BinaryIO, source_format: str) -> Dict[str, Any]:
        """Get information about a file"""
        source_cat = cls.get_format_category(source_format)
        
        try:
            if source_cat == 'audio':
                return AudioConverter.get_audio_info(input_file, source_format)
            elif source_cat == 'video':
                return VideoConverter.get_video_info(input_file, source_format)
            else:
                input_file.seek(0)
                size = len(input_file.read())
                return {'size_bytes': size, 'category': source_cat}
        except Exception as e:
            return {'error': str(e)}
    
    @classmethod
    def get_supported_formats(cls, source_format: str) -> list:
        """Get list of supported target formats for a given source format"""
        source_cat = cls.get_format_category(source_format)
        supported = []
        
        # Add all formats from same category
        if source_cat in cls.FORMAT_CATEGORIES:
            supported.extend([f for f in cls.FORMAT_CATEGORIES[source_cat] if f != source_format.lower()])
        
        # Add cross-category conversions
        if source_cat == 'image':
            supported.append('pdf')
        elif source_cat == 'video':
            supported.extend(['mp3', 'wav', 'aac', 'gif'])
        elif source_cat == 'document' and source_format.lower() == 'pdf':
            supported.extend(['jpg', 'png'])
        
        return sorted(list(set(supported)))