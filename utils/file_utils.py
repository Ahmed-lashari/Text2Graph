"""
File handling utilities.
"""
import hashlib
from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
from config.config import UPLOADS_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)


def save_uploaded_file(uploaded_file: UploadedFile) -> Path:
    """
    Save uploaded file to disk.
    
    Args:
        uploaded_file: Streamlit UploadedFile
    
    Returns:
        Path to saved file
    """
    try:
        file_path = UPLOADS_DIR / uploaded_file.name
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Saved file: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise


def get_file_hash(uploaded_file: UploadedFile) -> str:
    """
    Get MD5 hash of uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile
    
    Returns:
        MD5 hash string
    """
    file_hash = hashlib.md5()
    file_hash.update(uploaded_file.getbuffer())
    return file_hash.hexdigest()