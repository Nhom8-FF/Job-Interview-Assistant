import os
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from PIL import Image
import streamlit as st
import logging

# Import font utilities
try:
    from fonts.font_utils import find_font, copy_matplotlib_font_to_local
except ImportError:
    # Fallback if the module can't be imported
    from pathlib import Path
    import matplotlib

    def find_font(font_name):
        """Simple fallback function if the main utility can't be imported"""
        # Try local directory first
        local_path = os.path.join(os.path.dirname(__file__), "fonts", font_name)
        if os.path.exists(local_path):
            return local_path
            
        # Try matplotlib fonts
        try:
            mpl_font_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
            mpl_font_path = os.path.join(mpl_font_dir, font_name)
            if os.path.exists(mpl_font_path):
                return mpl_font_path
        except:
            pass
            
        return None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("badge_generator")

# Register font with robust error handling
try:
    # Find DejaVuSans font
    font_path = find_font("DejaVuSans.ttf")
    
    if font_path and os.path.exists(font_path):
        logger.info(f"Registering font from path: {font_path}")
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
    else:
        logger.warning("DejaVuSans.ttf font not found, using fallback fonts")
        # No need to register fallback fonts as ReportLab has built-in defaults
except Exception as e:
    logger.error(f"Error registering font: {e}")

def generate_icon(icon_type, size=50, color='blue'):
    """Generate a simple icon using matplotlib"""
    fig, ax = plt.subplots(figsize=(1, 1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    if icon_type == "star":
        ax.scatter(0.5, 0.5, s=size*10, marker='*', color=color)
    elif icon_type == "circle":
        ax.scatter(0.5, 0.5, s=size*10, marker='o', color=color)
    elif icon_type == "triangle":
        ax.scatter(0.5, 0.5, s=size*10, marker='^', color=color)
    elif icon_type == "square":
        ax.scatter(0.5, 0.5, s=size*10, marker='s', color=color)
    elif icon_type == "diamond":
        ax.scatter(0.5, 0.5, s=size*10, marker='D', color=color)
    
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True, dpi=100)
    plt.close(fig)
    img_buf.seek(0)
    return Image.open(img_buf)

def create_badge(
    badge_text="Certificate of Achievement", 
    recipient_name="John Doe", 
    awarded_for="Outstanding Performance", 
    badge_color="#4CAF50", 
    text_color="#FFFFFF",
    border_color="#2E7D32",
    icon_type="star",
    icon_color="gold"
):
    """Create a customizable badge and return as base64 encoded PNG"""
    # Create a PDF canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(400, 200))
    
    # Set background color
    c.setFillColor(colors.HexColor(badge_color))
    c.rect(0, 0, 400, 200, fill=True, stroke=False)
    
    # Add border
    c.setStrokeColor(colors.HexColor(border_color))
    c.setLineWidth(5)
    c.rect(5, 5, 390, 190, fill=False, stroke=True)
    
    # Add icon
    icon = generate_icon(icon_type, color=icon_color)
    icon_buffer = io.BytesIO()
    icon.save(icon_buffer, format='PNG')
    icon_buffer.seek(0)
    c.drawImage(ImageReader(icon_buffer), 15, 130, width=50, height=50)
    
    # Set font - use DejaVuSans if registered, otherwise fall back to Helvetica
    font_name = "DejaVuSans" if "DejaVuSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    
    # Add text
    c.setFont(font_name, 16)
    c.setFillColor(colors.HexColor(text_color))
    c.drawCentredString(220, 160, badge_text)
    
    c.setFont(font_name, 20)
    c.drawCentredString(220, 110, recipient_name)
    
    c.setFont(font_name, 14)
    c.drawCentredString(220, 70, "for")
    
    c.setFont(font_name, 16)
    c.drawCentredString(220, 40, awarded_for)
    
    # Save the canvas
    c.save()
    buffer.seek(0)
    
    # Convert PDF to PNG
    pdf_img = Image.open(buffer)
    png_buffer = io.BytesIO()
    pdf_img.save(png_buffer, format='PNG')
    png_buffer.seek(0)
    
    # Return as base64 string
    return base64.b64encode(png_buffer.getvalue()).decode('utf-8')

def badge_generator_page():
    st.title("Achievement Badge Generator")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Badge Settings")
        
        badge_text = st.text_input("Badge Title", "Certificate of Achievement")
        recipient_name = st.text_input("Recipient Name", "Your Name")
        awarded_for = st.text_input("Awarded For", "Outstanding Performance")
        
        st.subheader("Style Settings")
        badge_color = st.color_picker("Badge Background Color", "#4CAF50")
        text_color = st.color_picker("Text Color", "#FFFFFF")
        border_color = st.color_picker("Border Color", "#2E7D32")
        
        icon_type = st.selectbox(
            "Icon Type", 
            ["star", "circle", "triangle", "square", "diamond"]
        )
        
        icon_color = st.color_picker("Icon Color", "#FFD700")
    
    with col2:
        st.subheader("Preview")
        
        badge_base64 = create_badge(
            badge_text=badge_text,
            recipient_name=recipient_name,
            awarded_for=awarded_for,
            badge_color=badge_color,
            text_color=text_color,
            border_color=border_color,
            icon_type=icon_type,
            icon_color=icon_color
        )
        
        st.image(f"data:image/png;base64,{badge_base64}", width=400)
        
        st.download_button(
            label="Download Badge",
            data=base64.b64decode(badge_base64),
            file_name="achievement_badge.png",
            mime="image/png"
        )

if __name__ == "__main__":
    badge_generator_page() 