import io
import pandas as pd
import PyPDF2
from PIL import Image
import docx
import base64
import streamlit as st

def process_file(uploaded_file):
    """
    Process different file types and extract content
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        
    Returns:
        str: Extracted content from the file, or None if processing fails
    """
    try:
        if uploaded_file is None:
            return None
            
        if not hasattr(uploaded_file, 'name') or not uploaded_file.name:
            st.error("File name is missing or invalid")
            return None
            
        file_extension = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ""
        
        # Validate file extension
        if not file_extension:
            st.error("Cannot determine file type. Please ensure the file has a valid extension.")
            return None
        
        # Process based on file extension
        if file_extension in ['txt']:
            # Text file processing
            content = uploaded_file.getvalue().decode('utf-8')
            return content
            
        elif file_extension in ['pdf']:
            # PDF processing
            return process_pdf(uploaded_file)
            
        elif file_extension in ['docx']:
            # DOCX processing
            return process_docx(uploaded_file)
            
        elif file_extension in ['xlsx', 'xls']:
            # Excel processing
            return process_excel(uploaded_file)
            
        elif file_extension in ['jpg', 'jpeg', 'png']:
            # Image processing
            return process_image(uploaded_file)
            
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return None
            
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def process_pdf(file):
    """Extract text content from PDF files"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
        text = ""
        
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
                
        if not text.strip():
            return "PDF file contains no extractable text content."
        
        return text
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def process_docx(file):
    """Extract text content from DOCX files"""
    try:
        doc = docx.Document(io.BytesIO(file.getvalue()))
        text = ""
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
                
        if not text.strip():
            return "DOCX file contains no text content."
        
        return text
    except Exception as e:
        st.error(f"Error processing DOCX: {str(e)}")
        return None

def process_excel(file):
    """Extract data from Excel files"""
    try:
        df = pd.read_excel(io.BytesIO(file.getvalue()))
        
        # Convert dataframe to string representation
        if df.empty:
            return "Excel file contains no data."
            
        # Convert to string representation
        excel_content = "Excel File Content:\n"
        excel_content += df.to_string(index=False, max_rows=100, max_cols=20)
        
        return excel_content
    except Exception as e:
        st.error(f"Error processing Excel: {str(e)}")
        return None

def process_image(file):
    """Process image files using OCR or return description"""
    try:
        # For now, we'll just acknowledge the image type
        # In a full implementation, you would use OCR libraries
        image = Image.open(io.BytesIO(file.getvalue()))
        width, height = image.size
        mode = image.mode
        
        image_info = f"Image file uploaded. Format: {file.type}, Size: {width}x{height}, Mode: {mode}.\n"
        image_info += "Please describe the content of your image for analysis."
        
        return image_info
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None
