"""
FIA v3.0 - File Validation Utilities
File validation for training material uploads
"""

import mimetypes
from typing import List, Tuple
from fastapi import UploadFile, HTTPException
from pathlib import Path


# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
ALLOWED_EXTENSIONS = {'.pdf', '.ppt', '.pptx'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
}


class FileValidationError(Exception):
    """Custom exception for file validation errors"""
    pass


async def validate_training_file(file: UploadFile) -> Tuple[str, str]:
    """
    Validate uploaded training file
    
    Args:
        file: FastAPI UploadFile object
        
    Returns:
        Tuple of (file_extension, mime_type)
        
    Raises:
        FileValidationError: If file validation fails
    """
    
    # Check if file is provided
    if not file or not file.filename:
        raise FileValidationError("No file provided")
    
    # Get file extension
    file_extension = Path(file.filename).suffix.lower()
    
    # Validate file extension
    if file_extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content to check size
    content = await file.read()
    file_size = len(content)
    
    # Reset file position for later reading
    await file.seek(0)
    
    # Validate file size
    if file_size == 0:
        raise FileValidationError("File is empty")
    
    if file_size > MAX_FILE_SIZE:
        max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise FileValidationError(f"File too large. Maximum size: {max_size_mb}MB")
    
    # Guess MIME type from filename
    guessed_mime_type, _ = mimetypes.guess_type(file.filename)
    
    # Use provided content type or guessed type
    mime_type = file.content_type or guessed_mime_type
    
    # Validate MIME type
    if mime_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"Invalid file type. Expected: PDF, PPT, or PPTX"
        )
    
    return file_extension, mime_type


def get_file_type_from_extension(extension: str) -> str:
    """
    Get standardized file type from extension
    
    Args:
        extension: File extension (e.g., '.pdf', '.pptx')
        
    Returns:
        Standardized file type string
    """
    extension_map = {
        '.pdf': 'pdf',
        '.ppt': 'ppt',
        '.pptx': 'pptx'
    }
    
    return extension_map.get(extension.lower(), 'unknown')


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"