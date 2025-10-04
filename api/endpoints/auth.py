"""
Authentication and user-related API endpoints for the Jamanager application.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_database
from core.user_roles import get_current_user_role, UserRoleManager
from core.auth_middleware import get_user_permissions, get_user_role_dependency
from core.access_config import jam_manager_sessions
from core.feature_flags import UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["auth"])

@router.get("/user/permissions")
async def get_user_permissions_endpoint(
    request: Request,
    user_role: UserRole = Depends(get_user_role_dependency),
    permissions: dict = Depends(get_user_permissions)
):
    """Get current user's permissions and available features"""
    try:
        return {
            "user_role": user_role.value if user_role else "anonymous",
            "permissions": permissions
        }
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error getting user permissions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/feature-flags")
async def get_feature_flags():
    """Get all feature flags"""
    try:
        # This would typically come from a feature flag service
        # For now, return a basic structure
        return {
            "feature_flags": {
                "vote_jam_manager": True,
                "suggest_songs": True,
                "register_to_perform": True,
                "manage_jam": False
            }
        }
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error getting feature flags: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/access-code/verify")
async def verify_access_code(request: Request):
    """Verify jam manager access code"""
    try:
        data = await request.json()
        access_code = data.get("access_code", "").strip()
        
        if access_code == "jam2024":
            # Generate a session ID for this jam manager
            import secrets
            session_id = secrets.token_hex(16)
            jam_manager_sessions.grant_jam_manager_access(session_id)
            
            return {
                "success": True,
                "message": "Access granted",
                "session_id": session_id,
                "user_role": "jam_manager"
            }
        else:
            return {
                "success": False,
                "message": "Invalid access code"
            }
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error verifying access code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/access-code/logout")
async def logout_access_code(request: Request):
    """Logout jam manager session"""
    try:
        # Get session ID from header instead of JSON body
        session_id = request.headers.get("X-Session-ID", "")
        
        if jam_manager_sessions.has_jam_manager_access(session_id):
            jam_manager_sessions.revoke_jam_manager_access(session_id)
            return {"success": True, "message": "Logged out successfully"}
        else:
            return {"success": False, "message": "Session not found"}
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error logging out: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/access-code/status")
async def get_access_code_status(
    request: Request,
    user_role: UserRole = Depends(get_user_role_dependency)
):
    """Check if user has jam manager access"""
    try:
        return {
            "has_access": user_role.value == "jam_manager" if user_role else False,
            "user_role": user_role.value if user_role else "anonymous"
        }
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(f"Error checking access status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
