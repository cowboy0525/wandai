import os
import uuid
from typing import Tuple
from fastapi import UploadFile, HTTPException
from app.core.config import settings

def validate_file(file: UploadFile) -> Tuple[str, str]:
    """Validate uploaded file and return file path and doc ID"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = ('.pdf', '.txt', '.md')
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Generate unique document ID
    doc_id = str(uuid.uuid4())
    
    # Create file path
    file_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")
    
    return file_path, doc_id

def save_uploaded_file(file: UploadFile, file_path: str) -> bytes:
    """Save uploaded file to disk and return content"""
    try:
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def cleanup_file(file_path: str):
    """Remove temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but don't raise - cleanup failures shouldn't break the flow
        print(f"Warning: Failed to cleanup file {file_path}: {str(e)}")

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0
