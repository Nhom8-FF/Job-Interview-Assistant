#!/usr/bin/env python
"""
Script to copy DejaVu Sans fonts from matplotlib to local font directory
"""

import os
import shutil
import matplotlib
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def copy_matplotlib_fonts():
    """
    Copy DejaVu fonts from matplotlib to local directory
    """
    # Find the matplotlib fonts directory
    try:
        mpl_ttf_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
        logger.info(f"Found matplotlib fonts at: {mpl_ttf_dir}")
        
        # Check if it exists
        if not os.path.exists(mpl_ttf_dir):
            logger.error(f"Matplotlib TTF directory doesn't exist: {mpl_ttf_dir}")
            return False
            
        # Create fonts directory if it doesn't exist
        local_font_dir = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(local_font_dir, exist_ok=True)
        
        # Fonts to copy
        fonts = ['DejaVuSans.ttf', 'DejaVuSans-Bold.ttf']
        
        # Copy each font
        success = True
        for font in fonts:
            src = os.path.join(mpl_ttf_dir, font)
            dst = os.path.join(local_font_dir, font)
            
            if os.path.exists(src):
                logger.info(f"Copying {font} from {src} to {dst}")
                shutil.copy2(src, dst)
                if os.path.exists(dst):
                    logger.info(f"Successfully copied {font}")
                else:
                    logger.error(f"Failed to copy {font}")
                    success = False
            else:
                logger.error(f"Font file doesn't exist: {src}")
                success = False
                
        return success
    
    except Exception as e:
        logger.error(f"Error copying fonts: {e}")
        return False

if __name__ == "__main__":
    print("Copying DejaVu fonts from matplotlib...")
    if copy_matplotlib_fonts():
        print("✅ Success! Fonts have been copied to the local fonts directory")
    else:
        print("❌ Error copying fonts. See logs for details.") 