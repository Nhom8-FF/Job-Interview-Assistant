# 3D Job Interview Assistant

A modern job interview assistance chatbot using Python, Streamlit, and the Gemini API with file analysis capabilities.

## Features

- Modern 3D interface with interactive elements
- Dark/light mode toggle
- Responsive design for all device types
- Integration with Gemini API
- File upload and analysis (images, text, docx, PDF, Excel)
- Job interview assistance dialogues
- Context-aware responses
- Document parsing and content extraction
- History tracking of conversations

## Installation & Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install streamlit google-generativeai PyPDF2 python-docx pandas pillow
   ```
3. Run the application:
   ```
   python -m streamlit run app.py
   ```

## Usage

1. Launch the application in your browser
2. Use the sidebar to upload relevant documents (resume, job descriptions, etc.)
3. Toggle between light and dark mode as preferred
4. Chat with the assistant to get interview help
5. Use the Document Analysis tab to get insights on your uploaded documents
6. Use the Interview Tips tab to get customized advice for different interview types

## Document Analysis

The application supports the following file types:
- Text files (.txt)
- PDFs (.pdf)
- Word documents (.docx)
- Excel files (.xlsx, .xls)
- Images (.jpg, .jpeg, .png)

## Integration

This model can be integrated into other projects by:
1. Importing the key modules (file_processor.py, gemini_helper.py)
2. Using the process_file() function for document analysis
3. Using the initialize_gemini() and generate_response() functions for AI interactions

## Credits

- Built with Streamlit and the Gemini API
- Uses unsplash.com images for the UI
