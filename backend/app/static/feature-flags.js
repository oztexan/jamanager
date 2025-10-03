/**
 * Feature Flags and User Role Management
 * 
 * This module handles feature flags and user role detection on the frontend.
 */

class FeatureFlagsManager {
    constructor() {
        this.userRole = null;
        this.permissions = {};
        this.enabledFeatures = [];
        this.sessionId = this.getSessionId();
    }

    /**
     * Initialize feature flags by fetching user permissions
     */
    async initialize() {
        try {
            const response = await fetch('/api/user/permissions', {
                headers: {
                    'X-Session-ID': this.sessionId,
                    'X-Attendee-ID': this.getAttendeeId()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.userRole = data.user_role;
                this.permissions = data.permissions;
                this.enabledFeatures = data.enabled_features;
                
                console.log('🎭 User Role:', data.role_display_name);
                console.log('🔑 Permissions:', this.permissions);
                console.log('🚀 Enabled Features:', this.enabledFeatures);
                
                return data;
            } else {
                console.warn('Failed to fetch user permissions, defaulting to anonymous');
                this.setAnonymousRole();
            }
        } catch (error) {
            console.error('Error initializing feature flags:', error);
            this.setAnonymousRole();
        }
    }

    /**
     * Set anonymous user role as fallback
     */
    setAnonymousRole() {
        this.userRole = 'anonymous';
        this.permissions = {
            can_vote: true,
            can_register_to_perform: false,
            can_suggest_songs: false,
            can_view_performers: true,
            can_view_qr_code: true,
            can_manage_jam: false,
            can_play_songs: false,
            can_view_attendees: false,
            can_manage_attendees: false,
            can_view_stats: false,
            can_access_jam_manager: false
        };
        this.enabledFeatures = ['vote_anonymous', 'view_performers', 'view_qr_code'];
    }

    /**
     * Check if a specific permission is enabled
     */
    hasPermission(permission) {
        return this.permissions[permission] === true;
    }

    /**
     * Check if a specific feature is enabled
     */
    hasFeature(feature) {
        return this.enabledFeatures.includes(feature);
    }

    /**
     * Get current user role
     */
    getRole() {
        return this.userRole;
    }

    /**
     * Get role display name
     */
    getRoleDisplayName() {
        const roleNames = {
            'anonymous': 'Anonymous User',
            'registered_attendee': 'Muso',
            'jam_manager': 'Jam Manager'
        };
        return roleNames[this.userRole] || 'Unknown';
    }

    /**
     * Check if user is anonymous
     */
    isAnonymous() {
        return this.userRole === 'anonymous';
    }

    /**
     * Check if user is registered attendee
     */
    isRegisteredAttendee() {
        return this.userRole === 'registered_attendee';
    }

    /**
     * Check if user is jam manager
     */
    isJamManager() {
        // Check both the API role and localStorage for jam manager access
        return this.userRole === 'jam_manager' || localStorage.getItem('jamManagerAccess') === 'true';
    }

    /**
     * Get session ID from localStorage
     */
    getSessionId() {
        let sessionId = localStorage.getItem('jam_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('jam_session_id', sessionId);
        }
        return sessionId;
    }

    /**
     * Get attendee ID from localStorage
     */
    getAttendeeId() {
        return localStorage.getItem('jam_attendee_id');
    }

    /**
     * Set attendee ID in localStorage
     */
    setAttendeeId(attendeeId) {
        localStorage.setItem('jam_attendee_id', attendeeId);
        // Re-initialize to get updated permissions
        this.initialize();
    }

    /**
     * Clear attendee ID (logout)
     */
    clearAttendeeId() {
        localStorage.removeItem('jam_attendee_id');
        this.setAnonymousRole();
    }

    /**
     * Get headers for API requests
     */
    getApiHeaders() {
        return {
            'X-Session-ID': this.sessionId,
            'X-Attendee-ID': this.getAttendeeId() || ''
        };
    }

    /**
     * Show/hide elements based on permissions
     */
    applyFeatureGates() {
        // Hide/show elements based on permissions
        const elements = {
            '.perform-btn': this.hasPermission('can_register_to_perform'),
            '.suggest-song-btn': this.hasPermission('can_suggest_songs'),
            '.manage-jam-btn': this.hasPermission('can_manage_jam'),
            '.play-song-btn': this.hasPermission('can_play_songs'),
            '.jam-manager-btn': this.hasPermission('can_access_jam_manager'),
            '.attendee-list': this.hasPermission('can_view_attendees')
        };

        Object.entries(elements).forEach(([selector, shouldShow]) => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                el.style.display = shouldShow ? '' : 'none';
            });
        });

        // Update button text based on role
        if (this.isAnonymous()) {
            const performBtns = document.querySelectorAll('.perform-btn');
            performBtns.forEach(btn => {
                btn.textContent = 'Register to Perform';
                btn.onclick = () => registerAttendee();
            });
        }
    }

    /**
     * Get user role badge HTML
     */
    getRoleBadge() {
        const roleColors = {
            'anonymous': '#718096',
            'registered_attendee': '#38a169',
            'jam_manager': '#d69e2e'
        };

        const color = roleColors[this.userRole] || '#718096';
        
        return `
            <div class="user-role-badge" style="
                display: inline-block;
                background: ${color};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-left: 10px;
            ">
                ${this.getRoleDisplayName()}
            </div>
        `;
    }
}

// Global instance
const featureFlags = new FeatureFlagsManager();
window.featureFlags = featureFlags;

// Convenience functions
function hasPermission(permission) {
    return featureFlags.hasPermission(permission);
}

function hasFeature(feature) {
    return featureFlags.hasFeature(feature);
}

function isAnonymous() {
    return featureFlags.isAnonymous();
}

function isRegisteredAttendee() {
    return featureFlags.isRegisteredAttendee();
}

function isJamManager() {
    return featureFlags.isJamManager();
}

function getApiHeaders() {
    return featureFlags.getApiHeaders();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    await featureFlags.initialize();
    featureFlags.applyFeatureGates();
    
    // Add role badge to header if it exists
    const header = document.querySelector('.jam-header');
    if (header) {
        const roleBadge = featureFlags.getRoleBadge();
        header.insertAdjacentHTML('beforeend', roleBadge);
    }
});
