"""
Feature Flag Configuration Management

This module provides different ways to configure feature flags:
1. Role-based defaults (what we have now)
2. Per-user overrides
3. Per-jam settings
4. Global system settings
5. Environment-based configuration
"""

from enum import Enum
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import os
from app.core.feature_flags import UserRole, FeatureFlags

class ConfigScope(Enum):
    """Scope levels for feature flag configuration"""
    GLOBAL = "global"           # System-wide settings
    ROLE = "role"              # Role-based defaults
    USER = "user"              # Per-user overrides
    JAM = "jam"                # Per-jam settings
    ENVIRONMENT = "environment" # Environment-based (dev/staging/prod)

@dataclass
class FeatureFlagConfig:
    """Configuration for a specific feature flag"""
    feature_name: str
    enabled: bool
    scope: ConfigScope
    target_id: Optional[str] = None  # user_id, jam_id, role_name, etc.
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

class FeatureFlagManager:
    """Manages feature flag configurations at different scopes"""
    
    def __init__(self):
        self.configs: Dict[str, List[FeatureFlagConfig]] = {}
        self.load_environment_configs()
    
    def load_environment_configs(self):
        """Load feature flags from environment variables"""
        # Example: FEATURE_FLAGS='{"vote_anonymous": true, "suggest_songs": false}'
        env_flags = os.getenv('FEATURE_FLAGS')
        if env_flags:
            try:
                flags = json.loads(env_flags)
                for feature_name, enabled in flags.items():
                    self.set_feature_flag(
                        feature_name=feature_name,
                        enabled=enabled,
                        scope=ConfigScope.ENVIRONMENT,
                        target_id="system"
                    )
            except json.JSONDecodeError:
                print("Warning: Invalid FEATURE_FLAGS environment variable")
    
    def set_feature_flag(
        self,
        feature_name: str,
        enabled: bool,
        scope: ConfigScope,
        target_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> FeatureFlagConfig:
        """Set a feature flag configuration"""
        
        config = FeatureFlagConfig(
            feature_name=feature_name,
            enabled=enabled,
            scope=scope,
            target_id=target_id,
            expires_at=expires_at,
            metadata=metadata or {},
            created_by=created_by
        )
        
        if feature_name not in self.configs:
            self.configs[feature_name] = []
        
        # Remove existing config for same scope/target
        self.configs[feature_name] = [
            c for c in self.configs[feature_name]
            if not (c.scope == scope and c.target_id == target_id)
        ]
        
        self.configs[feature_name].append(config)
        return config
    
    def get_feature_flag(
        self,
        feature_name: str,
        user_role: UserRole,
        user_id: Optional[str] = None,
        jam_id: Optional[str] = None
    ) -> bool:
        """
        Get feature flag value with precedence:
        1. User-specific override
        2. Jam-specific setting
        3. Role-based default
        4. Global setting
        5. Environment setting
        6. Feature flag default
        """
        
        # Check for expired configs
        self._cleanup_expired_configs(feature_name)
        
        configs = self.configs.get(feature_name, [])
        
        # Priority order (highest to lowest)
        priority_order = [
            (ConfigScope.USER, user_id),
            (ConfigScope.JAM, jam_id),
            (ConfigScope.ROLE, user_role.value),
            (ConfigScope.GLOBAL, "system"),
            (ConfigScope.ENVIRONMENT, "system")
        ]
        
        for scope, target_id in priority_order:
            for config in configs:
                if config.scope == scope and config.target_id == target_id:
                    return config.enabled
        
        # Fall back to feature flag default
        feature_info = FeatureFlags.get_feature_info(feature_name)
        if feature_info:
            return user_role in feature_info.enabled_for
        
        return False
    
    def _cleanup_expired_configs(self, feature_name: str):
        """Remove expired configurations"""
        if feature_name in self.configs:
            now = datetime.now()
            self.configs[feature_name] = [
                config for config in self.configs[feature_name]
                if config.expires_at is None or config.expires_at > now
            ]
    
    def get_user_feature_flags(
        self,
        user_role: UserRole,
        user_id: Optional[str] = None,
        jam_id: Optional[str] = None
    ) -> Dict[str, bool]:
        """Get all feature flags for a user"""
        all_features = FeatureFlags.get_all_features()
        result = {}
        
        for feature_name in all_features.keys():
            result[feature_name] = self.get_feature_flag(
                feature_name, user_role, user_id, jam_id
            )
        
        return result
    
    def list_configs(self, feature_name: Optional[str] = None) -> Dict[str, List[FeatureFlagConfig]]:
        """List all configurations, optionally filtered by feature"""
        if feature_name:
            return {feature_name: self.configs.get(feature_name, [])}
        return self.configs.copy()
    
    def remove_config(
        self,
        feature_name: str,
        scope: ConfigScope,
        target_id: Optional[str] = None
    ) -> bool:
        """Remove a specific configuration"""
        if feature_name not in self.configs:
            return False
        
        original_count = len(self.configs[feature_name])
        self.configs[feature_name] = [
            config for config in self.configs[feature_name]
            if not (config.scope == scope and config.target_id == target_id)
        ]
        
        return len(self.configs[feature_name]) < original_count

# Global instance
feature_flag_manager = FeatureFlagManager()

# Convenience functions
def set_user_feature_flag(
    feature_name: str,
    user_id: str,
    enabled: bool,
    expires_at: Optional[datetime] = None,
    created_by: Optional[str] = None
) -> FeatureFlagConfig:
    """Set a feature flag for a specific user"""
    return feature_flag_manager.set_feature_flag(
        feature_name=feature_name,
        enabled=enabled,
        scope=ConfigScope.USER,
        target_id=user_id,
        expires_at=expires_at,
        created_by=created_by
    )

def set_jam_feature_flag(
    feature_name: str,
    jam_id: str,
    enabled: bool,
    expires_at: Optional[datetime] = None,
    created_by: Optional[str] = None
) -> FeatureFlagConfig:
    """Set a feature flag for a specific jam"""
    return feature_flag_manager.set_feature_flag(
        feature_name=feature_name,
        enabled=enabled,
        scope=ConfigScope.JAM,
        target_id=jam_id,
        expires_at=expires_at,
        created_by=created_by
    )

def set_role_feature_flag(
    feature_name: str,
    role: UserRole,
    enabled: bool,
    expires_at: Optional[datetime] = None,
    created_by: Optional[str] = None
) -> FeatureFlagConfig:
    """Set a feature flag for a specific role"""
    return feature_flag_manager.set_feature_flag(
        feature_name=feature_name,
        enabled=enabled,
        scope=ConfigScope.ROLE,
        target_id=role.value,
        expires_at=expires_at,
        created_by=created_by
    )

def set_global_feature_flag(
    feature_name: str,
    enabled: bool,
    expires_at: Optional[datetime] = None,
    created_by: Optional[str] = None
) -> FeatureFlagConfig:
    """Set a global feature flag"""
    return feature_flag_manager.set_feature_flag(
        feature_name=feature_name,
        enabled=enabled,
        scope=ConfigScope.GLOBAL,
        target_id="system",
        expires_at=expires_at,
        created_by=created_by
    )

def get_feature_flag_value(
    feature_name: str,
    user_role: UserRole,
    user_id: Optional[str] = None,
    jam_id: Optional[str] = None
) -> bool:
    """Get the effective value of a feature flag"""
    return feature_flag_manager.get_feature_flag(
        feature_name, user_role, user_id, jam_id
    )
