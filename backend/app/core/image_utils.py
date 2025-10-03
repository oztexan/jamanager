"""
Image Upload and Processing Utilities

This module handles image uploads and processing for jam backgrounds.
"""

import os
import shutil
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
from app.core.jam_config import JamConfig

class ImageUploader:
    """Handles image uploads and processing"""
    
    @staticmethod
    def validate_image(file: UploadFile) -> Tuple[bool, str]:
        """Validate uploaded image file"""
        # Check file size
        if file.size and file.size > JamConfig.MAX_IMAGE_SIZE:
            return False, f"File size exceeds maximum allowed size of {JamConfig.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB"
        
        # Check content type
        if not JamConfig.is_valid_image_type(file.content_type):
            return False, f"Invalid file type. Allowed types: {', '.join(JamConfig.ALLOWED_IMAGE_TYPES)}"
        
        return True, "Valid"
    
    @staticmethod
    def save_image(file: UploadFile, jam_id: str) -> str:
        """Save uploaded image and return the relative path"""
        # Ensure upload directory exists
        JamConfig.ensure_upload_dir()
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        import secrets
        unique_filename = f"jam_{jam_id}_{secrets.token_hex(4)}{file_extension}"
        
        # Create full path
        upload_path = JamConfig.get_upload_path()
        file_path = os.path.join(upload_path, unique_filename)
        
        # Save file
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Return relative path for web access
            return f"/static/uploads/{unique_filename}"
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
    
    @staticmethod
    def delete_image(image_path: str) -> bool:
        """Delete an uploaded image file"""
        if not image_path or not image_path.startswith('/static/uploads/'):
            return False
        
        try:
            # Convert web path to file system path
            filename = os.path.basename(image_path)
            file_path = os.path.join(JamConfig.get_upload_path(), filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def get_image_info(image_path: str) -> dict:
        """Get information about an uploaded image"""
        if not image_path or not image_path.startswith('/static/uploads/'):
            return {"exists": False}
        
        try:
            filename = os.path.basename(image_path)
            file_path = os.path.join(JamConfig.get_upload_path(), filename)
            
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    "exists": True,
                    "size": stat.st_size,
                    "path": image_path
                }
            else:
                return {"exists": False}
                
        except Exception:
            return {"exists": False}
