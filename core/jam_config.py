"""
Jam Configuration Settings

This module handles configuration for jam appearance and behavior.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class JamConfig:
    """Configuration for jam appearance and behavior"""
    
    # Background settings
    DEFAULT_BACKGROUND_COLOR = "#1a1a2e"  # Default dark background
    BLUR_INTENSITY = int(os.getenv("JAM_BLUR_INTENSITY", "10"))  # CSS blur value in pixels
    
    # Foreground transparency settings
    FOREGROUND_TRANSPARENCY = float(os.getenv("JAM_FOREGROUND_TRANSPARENCY", "0.95"))  # 0.0 = fully transparent, 1.0 = fully opaque
    
    # Image upload settings
    UPLOAD_DIR = os.getenv("JAM_UPLOAD_DIR", "backend/app/static/uploads")
    MAX_IMAGE_SIZE = int(os.getenv("JAM_MAX_IMAGE_SIZE", "5242880"))  # 5MB in bytes
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
    
    # Slug generation settings
    MAX_SLUG_LENGTH = int(os.getenv("JAM_MAX_SLUG_LENGTH", "100"))
    
    @classmethod
    def get_upload_path(cls) -> str:
        """Get the full path to the upload directory"""
        return os.path.join(os.getcwd(), cls.UPLOAD_DIR)
    
    @classmethod
    def ensure_upload_dir(cls) -> None:
        """Ensure the upload directory exists"""
        upload_path = cls.get_upload_path()
        os.makedirs(upload_path, exist_ok=True)
    
    @classmethod
    def is_valid_image_type(cls, content_type: str) -> bool:
        """Check if the content type is an allowed image type"""
        return content_type.lower() in cls.ALLOWED_IMAGE_TYPES
    
    @classmethod
    def get_background_css(cls, background_image: Optional[str] = None) -> str:
        """Generate CSS for background styling"""
        if background_image:
            return f"""
                background-image: url('{background_image}');
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                filter: blur({cls.BLUR_INTENSITY}px);
            """
        else:
            return f"background-color: {cls.DEFAULT_BACKGROUND_COLOR};"
    
    @classmethod
    def get_foreground_css(cls) -> str:
        """Generate CSS for foreground transparency"""
        return f"background-color: rgba(255, 255, 255, {cls.FOREGROUND_TRANSPARENCY});"
