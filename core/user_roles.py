"""
User Role Detection and Management

This module handles determining user roles and providing role-based access control.
"""

from typing import Optional, Dict, Any
from core.feature_flags import UserRole, FeatureFlags
from models.database import Attendee
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.access_config import jam_manager_sessions

class UserRoleManager:
    """Manages user roles and permissions"""
    
    @staticmethod
    async def get_user_role(
        session_id: Optional[str] = None,
        attendee_id: Optional[str] = None,
        jam_id: Optional[str] = None,
        db: Optional[AsyncSession] = None
    ) -> UserRole:
        """
        Determine user role based on available information
        
        Args:
            session_id: Browser session ID (for anonymous users)
            attendee_id: Registered attendee ID
            jam_id: Current jam ID (for context)
            db: Database session
            
        Returns:
            UserRole enum value
        """
        # If we have an attendee_id, check if they're registered
        if attendee_id and db and jam_id:
            try:
                
                result = await db.execute(
                    select(Attendee).where(
                        Attendee.id == attendee_id,
                        Attendee.jam_id == jam_id
                    )
                )
                attendee = result.scalar_one_or_none()
                
                if attendee:
                    return UserRole.REGISTERED_ATTENDEE
            except (ValueError, Exception):
                pass
        
        # Check for jam manager session access first
        if session_id and jam_manager_sessions.has_jam_manager_access(session_id):
            return UserRole.JAM_MANAGER
        
        # Standard role detection
        if attendee_id:
            return UserRole.REGISTERED_ATTENDEE
        elif session_id:
            return UserRole.ANONYMOUS
        else:
            return UserRole.ANONYMOUS
    
    @staticmethod
    def get_role_display_name(role: UserRole) -> str:
        """Get human-readable display name for role"""
        role_names = {
            UserRole.ANONYMOUS: "Anonymous User",
            UserRole.REGISTERED_ATTENDEE: "Muso",
            UserRole.JAM_MANAGER: "Jam Manager"
        }
        return role_names.get(role, "Unknown")
    
    @staticmethod
    def get_role_description(role: UserRole) -> str:
        """Get description of what this role can do"""
        descriptions = {
            UserRole.ANONYMOUS: "Can vote on songs and view jam content",
            UserRole.REGISTERED_ATTENDEE: "Can vote, register to perform, and suggest songs",
            UserRole.JAM_MANAGER: "Full access to jam management and administration"
        }
        return descriptions.get(role, "Unknown permissions")
    
    @staticmethod
    def get_available_actions(role: UserRole) -> Dict[str, bool]:
        """Get dictionary of available actions for a role"""
        return {
            "can_vote": FeatureFlags.is_feature_enabled("vote_anonymous", role) or 
                       FeatureFlags.is_feature_enabled("vote_registered", role) or
                       FeatureFlags.is_feature_enabled("vote_jam_manager", role),
            "can_register_to_perform": FeatureFlags.is_feature_enabled("register_to_perform", role),
            "can_suggest_songs": FeatureFlags.is_feature_enabled("suggest_songs", role),
            "can_view_performers": FeatureFlags.is_feature_enabled("view_performers", role),
            "can_view_qr_code": FeatureFlags.is_feature_enabled("view_qr_code", role),
            "can_manage_jam": FeatureFlags.is_feature_enabled("create_jams", role),
            "can_play_songs": FeatureFlags.is_feature_enabled("play_songs", role),
            "can_view_attendees": FeatureFlags.is_feature_enabled("view_attendees", role),
            "can_manage_attendees": FeatureFlags.is_feature_enabled("manage_attendees", role),
            "can_view_stats": FeatureFlags.is_feature_enabled("view_jam_stats", role),
            "can_access_jam_manager": FeatureFlags.is_feature_enabled("jam_manager_panel", role),
        }

# Convenience functions
async def get_current_user_role(
    session_id: Optional[str] = None,
    attendee_id: Optional[str] = None,
    jam_id: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> UserRole:
    """Convenience function to get current user role"""
    return await UserRoleManager.get_user_role(session_id, attendee_id, jam_id, db)

def check_feature_access(feature_name: str, user_role: UserRole) -> bool:
    """Check if user has access to a specific feature"""
    return FeatureFlags.is_feature_enabled(feature_name, user_role)
