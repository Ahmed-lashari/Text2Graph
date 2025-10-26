"""
File and data validation utilities.
"""
from typing import Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile
from config.config import FILE_CONFIG


def validate_file(uploaded_file: UploadedFile) -> Dict[str, any]:
    """
    Validate uploaded file.
    
    Returns:
        Dict with 'valid' boolean and optional 'error' message
    """
    # Check file extension
    filename = uploaded_file.name.lower()
    valid_ext = any(filename.endswith(ext) for ext in FILE_CONFIG["allowed_extensions"])
    
    if not valid_ext:
        return {
            "valid": False,
            "error": f"Invalid file type. Allowed: {', '.join(FILE_CONFIG['allowed_extensions'])}"
        }
    
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > FILE_CONFIG["max_file_size_mb"]:
        return {
            "valid": False,
            "error": f"File too large. Max size: {FILE_CONFIG['max_file_size_mb']}MB"
        }
    
    return {"valid": True}