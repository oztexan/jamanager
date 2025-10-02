"""
Authentication and Authorization Middleware

This module provides decorators and middleware for protecting API endpoints
based on user roles and feature flags.
"""

from functools import wraps
from typing import Optional, List, Callable, Any
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from feature_flags import UserRole, FeatureFlags
from user_roles import UserRoleManager, get_current_user_role
from database import get_database
import json

# Security scheme for API authentication (if needed in future)
security = HTTPBearer(auto_error=False)

class FeatureGate:
    """Feature gate decorator for protecting endpoints"""
    
    def __init__(self, required_features: List[str], allowed_roles: Optional[List[UserRole]] = None):
        """
        Initialize feature gate
        
        Args:
            required_features: List of feature names required to access endpoint
            allowed_roles: Optional list of allowed roles (if None, checks features only)
        """
        self.required_features = required_features
        self.allowed_roles = allowed_roles or list(UserRole)
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator implementation"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and database session from kwargs
            request = None
            db = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, AsyncSession):
                    db = arg
            
            for key, value in kwargs.items():
                if isinstance(value, Request):
                    request = value
                elif isinstance(value, AsyncSession):
                    db = value
            
            if not request or not db:
                raise HTTPException(status_code=500, detail="Request or database session not found")
            
            # Extract user information from request
            session_id = request.headers.get("X-Session-ID")
            attendee_id = request.headers.get("X-Attendee-ID")
            jam_id = kwargs.get("jam_id")  # Usually from path parameter
            
            # Get user role
            user_role = await get_current_user_role(session_id, attendee_id, jam_id, db)
            
            # Check if role is allowed
            if user_role not in self.allowed_roles:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied. Required role: {[role.value for role in self.allowed_roles]}"
                )
            
            # Check if user has required features
            for feature in self.required_features:
                if not FeatureFlags.is_feature_enabled(feature, user_role):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Feature '{feature}' not available for your role"
                    )
            
            # Add user role to kwargs for use in endpoint
            kwargs['user_role'] = user_role
            
            return await func(*args, **kwargs)
        
        return wrapper

# Convenience decorators for common access patterns
def anonymous_only(func: Callable) -> Callable:
    """Allow only anonymous users"""
    return FeatureGate([], [UserRole.ANONYMOUS])(func)

def registered_only(func: Callable) -> Callable:
    """Allow only registered attendees"""
    return FeatureGate([], [UserRole.REGISTERED_ATTENDEE])(func)

def jam_manager_only(func: Callable) -> Callable:
    """Allow only jam managers"""
    return FeatureGate([], [UserRole.JAM_MANAGER])(func)

def can_vote(func: Callable) -> Callable:
    """Allow users who can vote (anonymous or registered)"""
    return FeatureGate([], [UserRole.ANONYMOUS, UserRole.REGISTERED_ATTENDEE])(func)

def can_register_to_perform(func: Callable) -> Callable:
    """Allow users who can register to perform"""
    return FeatureGate(["register_to_perform"], [UserRole.REGISTERED_ATTENDEE])(func)

def can_suggest_songs(func: Callable) -> Callable:
    """Allow users who can suggest songs"""
    return FeatureGate(["suggest_songs"], [UserRole.REGISTERED_ATTENDEE])(func)

def can_manage_jam(func: Callable) -> Callable:
    """Allow users who can manage jam"""
    return FeatureGate(["create_jams"], [UserRole.JAM_MANAGER])(func)

def can_play_songs(func: Callable) -> Callable:
    """Allow users who can mark songs as played"""
    return FeatureGate(["play_songs"], [UserRole.JAM_MANAGER])(func)

# Dependency for getting current user role
async def get_user_role_dependency(
    request: Request,
    db: AsyncSession = Depends(get_database)
) -> UserRole:
    """FastAPI dependency to get current user role"""
    session_id = request.headers.get("X-Session-ID")
    attendee_id = request.headers.get("X-Attendee-ID")
    
    # Try to get jam_id from path parameters
    jam_id = None
    if hasattr(request, 'path_params'):
        jam_id = request.path_params.get('jam_id')
    
    return await get_current_user_role(session_id, attendee_id, jam_id, db)

# Dependency for getting user permissions
async def get_user_permissions(
    user_role: UserRole = Depends(get_user_role_dependency)
) -> dict:
    """FastAPI dependency to get user permissions"""
    return UserRoleManager.get_available_actions(user_role)
