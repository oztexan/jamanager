"""
Simplified Feature Flag Management API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from feature_flags import UserRole, FeatureFlags
from feature_flag_config import (
    FeatureFlagManager, ConfigScope, set_user_feature_flag, set_jam_feature_flag,
    set_role_feature_flag, set_global_feature_flag, get_feature_flag_value
)
from user_roles import get_current_user_role
from jamanager.database import get_database

router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])

# Pydantic models for API requests/responses
class FeatureFlagRequest(BaseModel):
    feature_name: str
    enabled: bool
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

# Global feature flag manager instance
feature_manager = FeatureFlagManager()

@router.get("/")
async def list_all_feature_flags():
    """List all available feature flags and their configurations"""
    all_features = FeatureFlags.get_all_features()
    result = {}
    
    for feature_name in all_features.keys():
        configs = feature_manager.list_configs(feature_name).get(feature_name, [])
        result[feature_name] = {
            "feature_info": {
                "name": all_features[feature_name].name,
                "description": all_features[feature_name].description,
                "default_enabled_for": [role.value for role in all_features[feature_name].enabled_for]
            },
            "configurations": [
                {
                    "scope": config.scope.value,
                    "target_id": config.target_id,
                    "enabled": config.enabled,
                    "expires_at": config.expires_at,
                    "metadata": config.metadata,
                    "created_at": config.created_at,
                    "created_by": config.created_by
                }
                for config in configs
            ]
        }
    
    return result

@router.get("/effective")
async def get_effective_feature_flags(
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Get effective feature flags for current context"""
    # Get user information from headers
    session_id = request.headers.get("X-Session-ID")
    attendee_id = request.headers.get("X-Attendee-ID")
    jam_id = request.path_params.get('jam_id') if hasattr(request, 'path_params') else None
    
    # Get user role
    user_role = await get_current_user_role(session_id, attendee_id, jam_id, db)
    
    # Get effective feature flags
    effective_flags = feature_manager.get_user_feature_flags(user_role, attendee_id, jam_id)
    
    return {
        "user_role": user_role.value,
        "user_id": attendee_id,
        "jam_id": jam_id,
        "effective_feature_flags": effective_flags
    }

@router.post("/global")
async def set_global_feature_flag(
    request: FeatureFlagRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Set a global feature flag"""
    # Get current user role
    session_id = http_request.headers.get("X-Session-ID")
    attendee_id = http_request.headers.get("X-Attendee-ID")
    current_user_role = await get_current_user_role(session_id, attendee_id, None, db)
    
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can set global feature flags")
    
    config = set_global_feature_flag(
        feature_name=request.feature_name,
        enabled=request.enabled,
        expires_at=request.expires_at,
        created_by="api_user"  # TODO: Get actual user ID
    )
    
    return {
        "feature_name": config.feature_name,
        "enabled": config.enabled,
        "scope": config.scope.value,
        "target_id": config.target_id,
        "expires_at": config.expires_at,
        "metadata": config.metadata,
        "created_at": config.created_at,
        "created_by": config.created_by
    }

@router.post("/role/{role}")
async def set_role_feature_flag(
    role: str,
    request: FeatureFlagRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Set a feature flag for a specific role"""
    # Get current user role
    session_id = http_request.headers.get("X-Session-ID")
    attendee_id = http_request.headers.get("X-Attendee-ID")
    current_user_role = await get_current_user_role(session_id, attendee_id, None, db)
    
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can set role feature flags")
    
    try:
        user_role = UserRole(role)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    
    config = set_role_feature_flag(
        feature_name=request.feature_name,
        role=user_role,
        enabled=request.enabled,
        expires_at=request.expires_at,
        created_by="api_user"  # TODO: Get actual user ID
    )
    
    return {
        "feature_name": config.feature_name,
        "enabled": config.enabled,
        "scope": config.scope.value,
        "target_id": config.target_id,
        "expires_at": config.expires_at,
        "metadata": config.metadata,
        "created_at": config.created_at,
        "created_by": config.created_by
    }
