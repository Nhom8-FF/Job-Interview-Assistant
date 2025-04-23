#!/usr/bin/env python
"""
Setup script to ensure fonts are properly configured for the InterviewAI application.
This script:
1. Checks if the required fonts exist in the fonts directory
2. If not, attempts to copy them from matplotlib 
3. Verifies the fonts can be loaded by ReportLab
"""

import os
import sys
import importlib
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup_fonts")

def check_environment():
    """
    Check if the necessary dependencies are installed
    """
    required_packages = ["reportlab", "matplotlib"]
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            logger.info(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ {package} is not installed")
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install them using: pip install " + " ".join(missing_packages))
        return False
    
    return True

def check_fonts_directory():
    """
    Check if the fonts directory exists and create it if needed
    """
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    
    if not os.path.exists(fonts_dir):
        try:
            os.makedirs(fonts_dir)
            logger.info(f"Created fonts directory: {fonts_dir}")
        except Exception as e:
            logger.error(f"Failed to create fonts directory: {e}")
            return False
    else:
        logger.info(f"Fonts directory exists: {fonts_dir}")
    
    return True

def check_font_files():
    """
    Check if the required font files exist
    """
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    required_fonts = ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]
    missing_fonts = []
    
    for font in required_fonts:
        font_path = os.path.join(fonts_dir, font)
        if os.path.exists(font_path):
            logger.info(f"✅ Font exists: {font}")
        else:
            missing_fonts.append(font)
            logger.warning(f"❓ Font missing: {font}")
    
    return missing_fonts

def copy_matplotlib_fonts(missing_fonts):
    """
    Copy missing fonts from matplotlib
    """
    try:
        import matplotlib
        import shutil
        
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        mpl_ttf_dir = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
        
        if not os.path.exists(mpl_ttf_dir):
            logger.error(f"Matplotlib fonts directory not found: {mpl_ttf_dir}")
            return False
        
        success = True
        for font in missing_fonts:
            src = os.path.join(mpl_ttf_dir, font)
            dst = os.path.join(fonts_dir, font)
            
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                    if os.path.exists(dst):
                        logger.info(f"✅ Successfully copied font: {font}")
                    else:
                        logger.error(f"❌ Failed to copy font: {font}")
                        success = False
                except Exception as e:
                    logger.error(f"❌ Error copying font {font}: {e}")
                    success = False
            else:
                logger.error(f"❌ Font not found in matplotlib: {src}")
                success = False
        
        return success
    
    except Exception as e:
        logger.error(f"❌ Error copying matplotlib fonts: {e}")
        return False

def test_font_loading():
    """
    Test if the fonts can be loaded by ReportLab
    """
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
        font_file = os.path.join(fonts_dir, "DejaVuSans.ttf")
        
        if not os.path.exists(font_file):
            logger.error(f"❌ Font file not found for testing: {font_file}")
            return False
        
        # Try to register the font
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_file))
        logger.info("✅ Successfully registered font with ReportLab")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Error testing font loading: {e}")
        return False

def main():
    """
    Main function
    """
    print("Setting up fonts for InterviewAI application...\n")
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed. Please install the required packages.")
        return False
    
    # Check fonts directory
    if not check_fonts_directory():
        print("\n❌ Failed to set up fonts directory.")
        return False
    
    # Check font files
    missing_fonts = check_font_files()
    
    # Copy missing fonts if needed
    if missing_fonts:
        print(f"\nCopying missing fonts from matplotlib: {', '.join(missing_fonts)}")
        if not copy_matplotlib_fonts(missing_fonts):
            print("\n⚠️ Some fonts could not be copied from matplotlib.")
            print("You may need to download them manually from https://dejavu-fonts.github.io/")
            print("and place them in the 'fonts' directory.")
    
    # Test font loading
    if test_font_loading():
        print("\n✅ Font setup completed successfully!")
    else:
        print("\n⚠️ Font loading test failed.")
        print("The application may fall back to default fonts.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 