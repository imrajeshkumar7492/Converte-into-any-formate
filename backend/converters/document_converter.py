import os
import io
import tempfile
from typing import BinaryIO
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
from docx.shared import Inches
import openpyxl
from openpyxl.utils import get_column_letter
import csv
from pptx import Presentation
from PIL import Image
import fitz  # PyMuPDF for PDF to image conversion

class DocumentConverter:
    @staticmethod
    def convert_pdf_to_text(input_file: BinaryIO) -> bytes:
        """Convert PDF to plain text"""
        try:
            input_file.seek(0)
            reader = PdfReader(input_file)
            text_content = ""
            
            for page in reader.pages:
                text_content += page.extract_text() + "\n\n"
            
            return text_content.encode('utf-8')
        except Exception as e:
            raise Exception(f"PDF to text conversion failed: {str(e)}")
    
    @staticmethod
    def convert_pdf_to_docx(input_file: BinaryIO) -> bytes:
        """Convert PDF to DOCX"""
        try:
            input_file.seek(0)
            reader = PdfReader(input_file)
            
            # Create new document
            doc = Document()
            
            for page_num, page in enumerate(reader.pages):
                if page_num > 0:
                    doc.add_page_break()
                
                text = page.extract_text()
                doc.add_paragraph(text)
            
            output_buffer = io.BytesIO()
            doc.save(output_buffer)
            
            return output_buffer.getvalue()
        except Exception as e:
            raise Exception(f"PDF to DOCX conversion failed: {str(e)}")
    
    @staticmethod
    def convert_docx_to_pdf(input_file: BinaryIO) -> bytes:
        """Convert DOCX to PDF using reportlab"""
        try:
            input_file.seek(0)
            doc = Document(input_file)
            
            output_buffer = io.BytesIO()
            c = canvas.Canvas(output_buffer, pagesize=letter)
            width, height = letter
            
            y = height - 50  # Start from top with margin
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    # Simple text wrapping
                    words = text.split()
                    line = ""
                    for word in words:
                        test_line = line + word + " "
                        if len(test_line) * 6 > width - 100:  # Rough character width estimation
                            if line:
                                c.drawString(50, y, line.strip())
                                y -= 15
                                line = word + " "
                            else:
                                c.drawString(50, y, word)
                                y -= 15
                        else:
                            line = test_line
                    
                    if line.strip():
                        c.drawString(50, y, line.strip())
                        y -= 15
                    
                    y -= 5  # Extra space between paragraphs
                    
                    # Check if we need a new page
                    if y < 50:
                        c.showPage()
                        y = height - 50
            
            c.save()
            return output_buffer.getvalue()
        except Exception as e:
            raise Exception(f"DOCX to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def convert_docx_to_txt(input_file: BinaryIO) -> bytes:
        """Convert DOCX to plain text"""
        try:
            input_file.seek(0)
            doc = Document(input_file)
            
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
            
            return text_content.encode('utf-8')
        except Exception as e:
            raise Exception(f"DOCX to text conversion failed: {str(e)}")
    
    @staticmethod
    def convert_txt_to_pdf(input_file: BinaryIO) -> bytes:
        """Convert plain text to PDF"""
        try:
            input_file.seek(0)
            text_content = input_file.read().decode('utf-8')
            
            output_buffer = io.BytesIO()
            c = canvas.Canvas(output_buffer, pagesize=letter)
            width, height = letter
            
            lines = text_content.split('\n')
            y = height - 50
            
            for line in lines:
                if y < 50:  # Start new page
                    c.showPage()
                    y = height - 50
                
                # Handle long lines
                if len(line) * 6 > width - 100:
                    words = line.split()
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + " "
                        if len(test_line) * 6 > width - 100:
                            if current_line:
                                c.drawString(50, y, current_line.strip())
                                y -= 15
                                current_line = word + " "
                            else:
                                c.drawString(50, y, word)
                                y -= 15
                        else:
                            current_line = test_line
                    
                    if current_line.strip():
                        c.drawString(50, y, current_line.strip())
                        y -= 15
                else:
                    c.drawString(50, y, line)
                    y -= 15
            
            c.save()
            return output_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Text to PDF conversion failed: {str(e)}")
    
    @staticmethod
    def convert_excel_to_csv(input_file: BinaryIO) -> bytes:
        """Convert Excel to CSV"""
        try:
            input_file.seek(0)
            workbook = openpyxl.load_workbook(input_file)
            worksheet = workbook.active
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            for row in worksheet.iter_rows(values_only=True):
                # Convert None values to empty strings
                clean_row = [str(cell) if cell is not None else '' for cell in row]
                writer.writerow(clean_row)
            
            return output.getvalue().encode('utf-8')
        except Exception as e:
            raise Exception(f"Excel to CSV conversion failed: {str(e)}")
    
    @staticmethod
    def convert_csv_to_excel(input_file: BinaryIO) -> bytes:
        """Convert CSV to Excel"""
        try:
            input_file.seek(0)
            csv_content = input_file.read().decode('utf-8')
            
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            
            # Parse CSV
            csv_reader = csv.reader(io.StringIO(csv_content))
            for row_num, row in enumerate(csv_reader, 1):
                for col_num, value in enumerate(row, 1):
                    worksheet.cell(row=row_num, column=col_num, value=value)
            
            output_buffer = io.BytesIO()
            workbook.save(output_buffer)
            
            return output_buffer.getvalue()
        except Exception as e:
            raise Exception(f"CSV to Excel conversion failed: {str(e)}")
    
    @staticmethod
    def convert_pdf_to_image(input_file: BinaryIO, target_format: str = 'png') -> bytes:
        """Convert PDF to image (JPG/PNG) - handles multi-page PDFs by converting first page"""
        try:
            # Try using PyMuPDF (fitz) first - better for PDF to image conversion
            try:
                import fitz  # PyMuPDF
                from PIL import Image
                
                input_file.seek(0)
                pdf_data = input_file.read()
                
                # Open PDF with PyMuPDF
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                
                # Get first page (for now, we'll convert only the first page)
                # TODO: In future, could create multi-page image or ZIP of images
                page = pdf_document[0]
                
                # Render page to image
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Convert to target format
                output_buffer = io.BytesIO()
                
                if target_format.lower() in ['jpg', 'jpeg']:
                    # Convert to RGB for JPEG (remove alpha channel)
                    if image.mode in ['RGBA', 'LA']:
                        background = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'RGBA':
                            background.paste(image, mask=image.split()[-1])
                        else:
                            background.paste(image)
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    image.save(output_buffer, format='JPEG', quality=95, optimize=True)
                else:  # PNG
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    image.save(output_buffer, format='PNG', optimize=True)
                
                pdf_document.close()
                return output_buffer.getvalue()
                
            except (ImportError, Exception) as e:
                # Fallback: Use reportlab to create a simple image representation
                # This is a basic fallback - not ideal but better than nothing
                from PIL import Image, ImageDraw, ImageFont
                
                input_file.seek(0)
                reader = PdfReader(input_file)
                
                # Extract text from first page
                first_page = reader.pages[0]
                text_content = first_page.extract_text()
                
                # Create a simple image with the text
                # Create a white image
                img_width, img_height = 800, 1000
                image = Image.new('RGB', (img_width, img_height), 'white')
                draw = ImageDraw.Draw(image)
                
                # Try to use a default font
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
                except:
                    font = ImageFont.load_default()
                
                # Draw text on image (simple word wrapping)
                y_position = 50
                words = text_content.split()
                line = ""
                
                for word in words:
                    test_line = line + word + " "
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] > img_width - 100:  # Line too long
                        if line:
                            draw.text((50, y_position), line.strip(), fill='black', font=font)
                            y_position += 20
                            line = word + " "
                        else:
                            draw.text((50, y_position), word, fill='black', font=font)
                            y_position += 20
                    else:
                        line = test_line
                    
                    if y_position > img_height - 100:  # Image full
                        break
                
                if line.strip():
                    draw.text((50, y_position), line.strip(), fill='black', font=font)
                
                # Save as target format
                output_buffer = io.BytesIO()
                
                if target_format.lower() in ['jpg', 'jpeg']:
                    image.save(output_buffer, format='JPEG', quality=95)
                else:  # PNG
                    image.save(output_buffer, format='PNG')
                
                return output_buffer.getvalue()
                
        except Exception as e:
            raise Exception(f"PDF to image conversion failed: {str(e)}")
    
    @staticmethod
    def convert_pdf_to_jpg(input_file: BinaryIO) -> bytes:
        """Convert PDF to JPG"""
        return DocumentConverter.convert_pdf_to_image(input_file, 'jpg')
    
    @staticmethod
    def convert_pdf_to_png(input_file: BinaryIO) -> bytes:
        """Convert PDF to PNG"""
        return DocumentConverter.convert_pdf_to_image(input_file, 'png')