"""
Access Code Configuration for Jam Manager Privileges

This module handles the access code system for granting jam manager privileges
to anonymous users.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AccessConfig:
    """Configuration for access codes and jam manager privileges"""
    
    # Default access code (should be overridden in production)
    DEFAULT_ACCESS_CODE = "jam2024"
    
    @classmethod
    def get_access_code(cls) -> str:
        """Get the access code from environment or use default"""
        return os.getenv("JAM_MANAGER_ACCESS_CODE", cls.DEFAULT_ACCESS_CODE)
    
    @classmethod
    def validate_access_code(cls, provided_code: str) -> bool:
        """Validate if the provided access code is correct"""
        if not provided_code:
            return False
        
        correct_code = cls.get_access_code()
        return provided_code.strip() == correct_code
    
    @classmethod
    def is_access_code_enabled(cls) -> bool:
        """Check if access code system is enabled"""
        return os.getenv("ENABLE_ACCESS_CODE", "true").lower() == "true"

# Session management for jam manager privileges
class JamManagerSession:
    """Manages jam manager session state"""
    
    def __init__(self) -> None:
        self.active_sessions = {}  # session_id -> timestamp
    
    def grant_jam_manager_access(self, session_id: str) -> bool:
        """Grant jam manager access to a session"""
        if not AccessConfig.is_access_code_enabled():
            return False
        
        self.active_sessions[session_id] = {
            "granted_at": __import__('datetime').datetime.now(),
            "access_level": "jam_manager"
        }
        return True
    
    def revoke_jam_manager_access(self, session_id: str) -> bool:
        """Revoke jam manager access from a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False
    
    def has_jam_manager_access(self, session_id: str) -> bool:
        """Check if session has jam manager access"""
        if not AccessConfig.is_access_code_enabled():
            return False
        
        return session_id in self.active_sessions
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get session information"""
        return self.active_sessions.get(session_id)

# Global session manager
jam_manager_sessions = JamManagerSession()
