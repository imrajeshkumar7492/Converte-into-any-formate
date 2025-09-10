import os
import tempfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cv2
import numpy as np
from typing import BinaryIO
import io
import base64

class ImageConverter:
    @staticmethod
    def convert_image(input_file: BinaryIO, source_format: str, target_format: str, 
                     quality: int = 95, max_width: int = None, max_height: int = None) -> bytes:
        """Convert image from one format to another"""
        try:
            # Load image
            input_file.seek(0)
            image = Image.open(input_file)
            
            # Apply resizing if specified
            if max_width or max_height:
                image = ImageConverter._resize_image(image, max_width, max_height)
            
            # Handle transparency for formats that don't support it
            if target_format.upper() in ['JPEG', 'JPG', 'BMP'] and image.mode in ['RGBA', 'LA']:
                # Create white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                else:
                    background.paste(image)
                image = background
            
            # Convert mode if necessary
            if target_format.upper() == 'PNG' and image.mode != 'RGBA':
                image = image.convert('RGBA')
            elif target_format.upper() in ['JPEG', 'JPG'] and image.mode != 'RGB':
                image = image.convert('RGB')
            elif target_format.upper() == 'BMP' and image.mode not in ['RGB', 'P']:
                image = image.convert('RGB')
            
            # Save to bytes
            output_buffer = io.BytesIO()
            
            # Handle special formats
            if target_format.upper() == 'ICO':
                # ICO format requires specific sizes
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                image.save(output_buffer, format='ICO', sizes=sizes)
            elif target_format.upper() == 'SVG':
                # For SVG conversion, we'll create a simple SVG with base64 embedded image
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_data = img_buffer.getvalue()
                img_b64 = base64.b64encode(img_data).decode()
                
                svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{image.width}" height="{image.height}" xmlns="http://www.w3.org/2000/svg">
    <image href="data:image/png;base64,{img_b64}" width="{image.width}" height="{image.height}"/>
</svg>'''
                return svg_content.encode('utf-8')
            elif target_format.upper() == 'WEBP':
                # WebP format with high quality
                if image.mode in ['RGBA', 'LA']:
                    image.save(output_buffer, format='WEBP', quality=quality, method=6)
                else:
                    image = image.convert('RGB')
                    image.save(output_buffer, format='WEBP', quality=quality, method=6)
            elif target_format.upper() == 'TIFF':
                # TIFF format with compression
                if image.mode in ['RGBA', 'LA']:
                    image.save(output_buffer, format='TIFF', compression='tiff_lzw')
                else:
                    image = image.convert('RGB')
                    image.save(output_buffer, format='TIFF', compression='tiff_lzw')
            elif target_format.upper() == 'BMP':
                # BMP format
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(output_buffer, format='BMP')
            elif target_format.upper() == 'GIF':
                # GIF format with optimization
                if image.mode != 'P':
                    image = image.convert('P', palette=Image.ADAPTIVE, colors=256)
                image.save(output_buffer, format='GIF', optimize=True)
            else:
                # Standard formats
                format_name = 'JPEG' if target_format.upper() == 'JPG' else target_format.upper()
                
                # Quality settings for JPEG
                save_kwargs = {}
                if format_name == 'JPEG':
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                elif format_name == 'PNG':
                    save_kwargs['optimize'] = True
                
                image.save(output_buffer, format=format_name, **save_kwargs)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")
    
    @staticmethod
    def _resize_image(image: Image.Image, max_width: int = None, max_height: int = None) -> Image.Image:
        """Resize image while maintaining aspect ratio"""
        if not max_width and not max_height:
            return image
        
        original_width, original_height = image.size
        
        # Calculate new dimensions
        if max_width and max_height:
            # Both dimensions specified - fit within bounds
            ratio = min(max_width / original_width, max_height / original_height)
        elif max_width:
            # Only width specified
            ratio = max_width / original_width
        else:
            # Only height specified
            ratio = max_height / original_height
        
        # Only resize if the image is larger than the target
        if ratio < 1:
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    @staticmethod
    def convert_to_pdf(input_file: BinaryIO, source_format: str) -> bytes:
        """Convert image to PDF"""
        try:
            input_file.seek(0)
            image = Image.open(input_file)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='PDF', quality=95)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Image to PDF conversion failed: {str(e)}")