"""
Feature Flag Management API Endpoints

This module provides API endpoints for managing feature flags at different scopes.
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
from database import get_database

router = APIRouter(prefix="/api/feature-flags", tags=["feature-flags"])

# Pydantic models for API requests/responses
class FeatureFlagRequest(BaseModel):
    feature_name: str
    enabled: bool
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class FeatureFlagResponse(BaseModel):
    feature_name: str
    enabled: bool
    scope: str
    target_id: Optional[str]
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    created_at: datetime
    created_by: Optional[str]

class FeatureFlagListResponse(BaseModel):
    feature_name: str
    effective_value: bool
    configurations: list[FeatureFlagResponse]

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

@router.get("/user/{user_id}")
async def get_user_feature_flags(
    user_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database),
    jam_id: Optional[str] = None
):
    """Get effective feature flags for a specific user"""
    # Get current user role
    session_id = request.headers.get("X-Session-ID")
    attendee_id = request.headers.get("X-Attendee-ID")
    user_role = await get_current_user_role(session_id, attendee_id, jam_id, db)
    
    # Only allow users to view their own flags or jam managers to view any
    if user_role != UserRole.JAM_MANAGER and user_id != "current":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if user_id == "current":
        # Get current user's flags
        user_flags = feature_manager.get_user_feature_flags(user_role, jam_id=jam_id)
    else:
        # Get specific user's flags (jam manager only)
        user_flags = feature_manager.get_user_feature_flags(user_role, user_id, jam_id)
    
    return {
        "user_id": user_id,
        "user_role": user_role.value,
        "jam_id": jam_id,
        "feature_flags": user_flags
    }

@router.post("/user/{user_id}")
async def set_user_feature_flag(
    user_id: str,
    request: FeatureFlagRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Set a feature flag for a specific user"""
    # Get current user role
    session_id = http_request.headers.get("X-Session-ID")
    attendee_id = http_request.headers.get("X-Attendee-ID")
    current_user_role = await get_current_user_role(session_id, attendee_id, None, db)
    
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can set user feature flags")
    
    config = set_user_feature_flag(
        feature_name=request.feature_name,
        user_id=user_id,
        enabled=request.enabled,
        expires_at=request.expires_at,
        created_by="api_user"  # TODO: Get actual user ID
    )
    
    return FeatureFlagResponse(
        feature_name=config.feature_name,
        enabled=config.enabled,
        scope=config.scope.value,
        target_id=config.target_id,
        expires_at=config.expires_at,
        metadata=config.metadata,
        created_at=config.created_at,
        created_by=config.created_by
    )

@router.post("/jam/{jam_id}")
async def set_jam_feature_flag(
    jam_id: str,
    request: FeatureFlagRequest,
    current_user_role: UserRole = Depends(get_current_user_role)
):
    """Set a feature flag for a specific jam"""
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can set jam feature flags")
    
    config = set_jam_feature_flag(
        feature_name=request.feature_name,
        jam_id=jam_id,
        enabled=request.enabled,
        expires_at=request.expires_at,
        created_by="api_user"  # TODO: Get actual user ID
    )
    
    return FeatureFlagResponse(
        feature_name=config.feature_name,
        enabled=config.enabled,
        scope=config.scope.value,
        target_id=config.target_id,
        expires_at=config.expires_at,
        metadata=config.metadata,
        created_at=config.created_at,
        created_by=config.created_by
    )

@router.post("/role/{role}")
async def set_role_feature_flag(
    role: str,
    request: FeatureFlagRequest,
    current_user_role: UserRole = Depends(get_current_user_role)
):
    """Set a feature flag for a specific role"""
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
    
    return FeatureFlagResponse(
        feature_name=config.feature_name,
        enabled=config.enabled,
        scope=config.scope.value,
        target_id=config.target_id,
        expires_at=config.expires_at,
        metadata=config.metadata,
        created_at=config.created_at,
        created_by=config.created_by
    )

@router.post("/global")
async def set_global_feature_flag(
    request: FeatureFlagRequest,
    current_user_role: UserRole = Depends(get_current_user_role)
):
    """Set a global feature flag"""
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can set global feature flags")
    
    config = set_global_feature_flag(
        feature_name=request.feature_name,
        enabled=request.enabled,
        expires_at=request.expires_at,
        created_by="api_user"  # TODO: Get actual user ID
    )
    
    return FeatureFlagResponse(
        feature_name=config.feature_name,
        enabled=config.enabled,
        scope=config.scope.value,
        target_id=config.target_id,
        expires_at=config.expires_at,
        metadata=config.metadata,
        created_at=config.created_at,
        created_by=config.created_by
    )

@router.delete("/{feature_name}/{scope}/{target_id}")
async def remove_feature_flag(
    feature_name: str,
    scope: str,
    target_id: str,
    current_user_role: UserRole = Depends(get_current_user_role)
):
    """Remove a feature flag configuration"""
    if current_user_role != UserRole.JAM_MANAGER:
        raise HTTPException(status_code=403, detail="Only jam managers can remove feature flags")
    
    try:
        config_scope = ConfigScope(scope)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid scope: {scope}")
    
    success = feature_manager.remove_config(feature_name, config_scope, target_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Feature flag configuration not found")
    
    return {"message": "Feature flag configuration removed successfully"}

@router.get("/effective")
async def get_effective_feature_flags(
    request: Request,
    user_role: UserRole = Depends(get_current_user_role),
    user_id: Optional[str] = None,
    jam_id: Optional[str] = None
):
    """Get effective feature flags for current context"""
    # Get user_id from headers if not provided
    if not user_id:
        user_id = request.headers.get("X-Attendee-ID")
    
    # Get jam_id from path params if not provided
    if not jam_id and hasattr(request, 'path_params'):
        jam_id = request.path_params.get('jam_id')
    
    effective_flags = feature_manager.get_user_feature_flags(user_role, user_id, jam_id)
    
    return {
        "user_role": user_role.value,
        "user_id": user_id,
        "jam_id": jam_id,
        "effective_feature_flags": effective_flags
    }
