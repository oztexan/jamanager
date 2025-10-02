"""
Feature Flags System for Jamanger Application

This module defines feature flags that control what functionality is available
to different user types in the application.
"""

from enum import Enum
from typing import Dict, List, Set
from dataclasses import dataclass

class UserRole(Enum):
    """User roles in the system"""
    ANONYMOUS = "anonymous"
    REGISTERED_ATTENDEE = "registered_attendee"  # Musos
    JAM_MANAGER = "jam_manager"

@dataclass
class FeatureFlag:
    """Individual feature flag definition"""
    name: str
    description: str
    enabled_for: Set[UserRole]
    default_enabled: bool = False

class FeatureFlags:
    """Feature flags configuration"""
    
    # Define all available features
    FEATURES = {
        # Voting Features
        "vote_anonymous": FeatureFlag(
            name="vote_anonymous",
            description="Allow anonymous users to vote on songs",
            enabled_for={UserRole.ANONYMOUS},
            default_enabled=True
        ),
        "vote_registered": FeatureFlag(
            name="vote_registered", 
            description="Allow registered attendees to vote on songs",
            enabled_for={UserRole.REGISTERED_ATTENDEE},
            default_enabled=True
        ),
        
        # Performance Registration Features
        "register_to_perform": FeatureFlag(
            name="register_to_perform",
            description="Allow users to register to perform on songs",
            enabled_for={UserRole.REGISTERED_ATTENDEE},
            default_enabled=True
        ),
        "view_performers": FeatureFlag(
            name="view_performers",
            description="Allow users to see who's registered to perform",
            enabled_for={UserRole.ANONYMOUS, UserRole.REGISTERED_ATTENDEE, UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # Song Management Features
        "suggest_songs": FeatureFlag(
            name="suggest_songs",
            description="Allow users to suggest new songs for the jam",
            enabled_for={UserRole.REGISTERED_ATTENDEE},
            default_enabled=True
        ),
        "add_existing_songs": FeatureFlag(
            name="add_existing_songs",
            description="Allow users to add existing songs to jam",
            enabled_for={UserRole.REGISTERED_ATTENDEE, UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # Jam Management Features
        "create_jams": FeatureFlag(
            name="create_jams",
            description="Allow users to create new jam sessions",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        "manage_jam_queue": FeatureFlag(
            name="manage_jam_queue",
            description="Allow users to reorder and manage song queue",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        "play_songs": FeatureFlag(
            name="play_songs",
            description="Allow users to mark songs as played",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # Attendee Management Features
        "view_attendees": FeatureFlag(
            name="view_attendees",
            description="Allow users to view list of attendees",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        "manage_attendees": FeatureFlag(
            name="manage_attendees",
            description="Allow users to remove or manage attendees",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # QR Code Features
        "view_qr_code": FeatureFlag(
            name="view_qr_code",
            description="Allow users to view QR code for jam access",
            enabled_for={UserRole.ANONYMOUS, UserRole.REGISTERED_ATTENDEE, UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # Analytics Features
        "view_jam_stats": FeatureFlag(
            name="view_jam_stats",
            description="Allow users to view jam statistics and analytics",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        
        # Admin Features
        "jam_manager_panel": FeatureFlag(
            name="jam_manager_panel",
            description="Allow access to jam manager panel",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
        "manage_song_library": FeatureFlag(
            name="manage_song_library",
            description="Allow users to manage the global song library",
            enabled_for={UserRole.JAM_MANAGER},
            default_enabled=True
        ),
    }
    
    @classmethod
    def is_feature_enabled(cls, feature_name: str, user_role: UserRole) -> bool:
        """Check if a feature is enabled for a specific user role"""
        if feature_name not in cls.FEATURES:
            return False
        
        feature = cls.FEATURES[feature_name]
        return user_role in feature.enabled_for
    
    @classmethod
    def get_enabled_features(cls, user_role: UserRole) -> List[str]:
        """Get all features enabled for a specific user role"""
        return [
            feature_name for feature_name, feature in cls.FEATURES.items()
            if user_role in feature.enabled_for
        ]
    
    @classmethod
    def get_feature_info(cls, feature_name: str) -> FeatureFlag:
        """Get information about a specific feature"""
        return cls.FEATURES.get(feature_name)
    
    @classmethod
    def get_all_features(cls) -> Dict[str, FeatureFlag]:
        """Get all available features"""
        return cls.FEATURES.copy()

# Convenience functions for common checks
def can_vote(user_role: UserRole) -> bool:
    """Check if user can vote (either anonymous or registered)"""
    return (FeatureFlags.is_feature_enabled("vote_anonymous", user_role) or 
            FeatureFlags.is_feature_enabled("vote_registered", user_role))

def can_register_to_perform(user_role: UserRole) -> bool:
    """Check if user can register to perform"""
    return FeatureFlags.is_feature_enabled("register_to_perform", user_role)

def can_manage_jam(user_role: UserRole) -> bool:
    """Check if user can manage jam (jam manager features)"""
    return user_role == UserRole.JAM_MANAGER

def can_suggest_songs(user_role: UserRole) -> bool:
    """Check if user can suggest songs"""
    return FeatureFlags.is_feature_enabled("suggest_songs", user_role)
