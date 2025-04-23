import os
import sys
import platform
from pathlib import Path
import matplotlib
import logging

def find_font(font_name):
    """
    Find a font file in various locations.
    
    Args:
        font_name (str): Name of the font file (e.g., 'DejaVuSans.ttf')
    
    Returns:
        str: Path to the font file or None if not found
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("font_utils")
    
    # 1. Check in the local fonts directory
    local_font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
    local_font_path = os.path.join(local_font_dir, font_name)
    
    if os.path.exists(local_font_path):
        logger.info(f"Found font in local directory: {local_font_path}")
        return local_font_path
    
    # 2. Check in system font directories based on OS
    system_font_dirs = []
    
    if platform.system() == 'Windows':
        system_font_dirs = [
            os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Fonts'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
        ]
    elif platform.system() == 'Darwin':  # macOS
        system_font_dirs = [
            '/Library/Fonts',
            '/System/Library/Fonts',
            os.path.expanduser('~/Library/Fonts')
        ]
    else:  # Linux/Unix
        system_font_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts')
        ]
    
    for font_dir in system_font_dirs:
        if os.path.exists(font_dir):
            # Check for the font file directly in the directory
            font_path = os.path.join(font_dir, font_name)
            if os.path.exists(font_path):
                logger.info(f"Found font in system directory: {font_path}")
                return font_path
            
            # Also search subdirectories (common in Linux)
            for root, dirs, files in os.walk(font_dir):
                if font_name in files:
                    font_path = os.path.join(root, font_name)
                    logger.info(f"Found font in system subdirectory: {font_path}")
                    return font_path
    
    # 3. Check in matplotlib's font directory
    try:
        matplotlib_font_dir = matplotlib.font_manager.findSystemFonts(fontpaths=matplotlib.mpl_data_path)
        for font_path in matplotlib_font_dir:
            if os.path.basename(font_path) == font_name:
                logger.info(f"Found font in matplotlib: {font_path}")
                return font_path
                
        # Try direct path to matplotlib fonts
        matplotlib_ttf_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
        matplotlib_font_path = os.path.join(matplotlib_ttf_dir, font_name)
        if os.path.exists(matplotlib_font_path):
            logger.info(f"Found font in matplotlib ttf directory: {matplotlib_font_path}")
            return matplotlib_font_path
    except Exception as e:
        logger.warning(f"Error searching matplotlib fonts: {e}")
    
    # If we get here, font wasn't found
    logger.warning(f"Font {font_name} not found in any location")
    return None

def copy_matplotlib_font_to_local(font_name):
    """
    Copy a font from matplotlib's font directory to the local fonts directory
    
    Args:
        font_name (str): Name of the font file (e.g., 'DejaVuSans.ttf')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import shutil
        
        # Create fonts directory if it doesn't exist
        local_font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
        os.makedirs(local_font_dir, exist_ok=True)
        
        # Target path
        target_path = os.path.join(local_font_dir, font_name)
        
        # Find matplotlib's font path
        matplotlib_ttf_dir = os.path.join(matplotlib.get_data_path(), 'fonts', 'ttf')
        source_path = os.path.join(matplotlib_ttf_dir, font_name)
        
        if os.path.exists(source_path):
            shutil.copy2(source_path, target_path)
            print(f"Successfully copied {font_name} from matplotlib to {target_path}")
            return True
        else:
            print(f"Could not find {font_name} in matplotlib fonts")
            return False
    except Exception as e:
        print(f"Error copying font: {e}")
        return False 