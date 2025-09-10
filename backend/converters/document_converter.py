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