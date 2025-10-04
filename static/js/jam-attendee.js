/**
 * Jam Attendee Management
 * Handles user registration, authentication, and session management
 */

class JamAttendee {
    constructor() {
        this.currentAttendee = null;
        this.sessionId = null;
        this.jamCore = null;
        this.isJamManager = false;
    }

    /**
     * Initialize attendee management
     */
    init(jamCore) {
        this.jamCore = jamCore;
        // Don't set session ID yet - wait for jam data to be loaded
        this.updateAttendeeUI();
    }

    /**
     * Get or create session ID
     */
    getOrCreateSessionId() {
        // First check if we have an existing session for this jam in localStorage
        const storedData = localStorage.getItem('jam_attendee');
        console.log('CHECKING LOCALSTORAGE FOR EXISTING SESSION:', storedData);
        
        if (storedData) {
            try {
                const data = JSON.parse(storedData);
                console.log('PARSED STORED DATA:', data);
                console.log('CURRENT JAM ID:', this.jamCore ? this.jamCore.getJamId() : 'jamCore not available');
                
                // Only use stored session if it's for the current jam
                if (data.jam_id === this.jamCore.getJamId() && data.session_id) {
                    console.log('RESTORING EXISTING SESSION:', data.session_id);
                    return data.session_id;
                } else {
                    console.log('STORED SESSION NOT FOR CURRENT JAM - stored jam_id:', data.jam_id, 'current jam_id:', this.jamCore.getJamId());
                }
            } catch (error) {
                console.error('Error parsing stored session data:', error);
            }
        }
        
        // Generate a new session ID if no existing session found
        const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
        console.log('NEW SESSION ID GENERATED:', sessionId);
        return sessionId;
    }


    /**
     * Called when jam data is loaded
     */
    onJamDataLoaded(jamData) {
        // Now that jam data is loaded, we can restore session and check for existing registration
        this.sessionId = this.getOrCreateSessionId();
        this.restoreAttendee();
        
        // Check if user is already registered in this jam
        this.checkExistingRegistration();
        // Check if user is a jam manager
        this.checkJamManagerPermissions();
    }

    /**
     * Check if user is already registered in this jam
     * This is called after jam data is loaded to check for existing registration
     */
    async checkExistingRegistration() {
        if (!this.jamCore || !this.jamCore.getJamId()) return;

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/attendees?session_id=${this.sessionId}`);
            if (response.ok) {
                const attendees = await response.json();
                console.log('CHECKING EXISTING REGISTRATION - session_id:', this.sessionId, 'attendees found:', attendees);
                if (attendees.length > 0) {
                    this.currentAttendee = attendees[0];
                    const dataToStore = {
                        jam_id: this.jamCore.getJamId(),
                        session_id: this.sessionId,
                        attendee: this.currentAttendee
                    };
                    console.log('STORING TO LOCALSTORAGE:', dataToStore);
                    localStorage.setItem('jam_attendee', JSON.stringify(dataToStore));
                    this.updateAttendeeUI();
                    
                    // Notify other modules about existing registration
                    if (window.jamSongs) {
                        window.jamSongs.onAttendeeRegistered(this.currentAttendee);
                    }
                }
            }
        } catch (error) {
            console.error('Error checking existing registration:', error);
        }
    }

    /**
     * Check if user has jam manager permissions
     */
    async checkJamManagerPermissions() {
        try {
            const response = await fetch('/api/user/permissions', {
                headers: {
                    'X-Session-ID': this.sessionId
                }
            });
            if (response.ok) {
                const permissions = await response.json();
                this.isJamManager = permissions.has_access && permissions.user_role === 'jam_manager';
                this.updateAttendeeUI();
            }
        } catch (error) {
            console.error('Error checking jam manager permissions:', error);
        }
    }

    /**
     * Register user as attendee
     */
    async registerUser() {
        const nameInput = document.getElementById('userName');
        const name = nameInput ? nameInput.value.trim() : '';

        if (!name) {
            this.showMessage('Please enter your name.', 'error');
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/attendees`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    name, 
                    session_id: this.sessionId 
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to register attendee');
            }

            const result = await response.json();
            this.currentAttendee = {
                id: result.attendee_id, 
                name: name 
            };
            const dataToStore = {
                jam_id: this.jamCore.getJamId(),
                session_id: this.sessionId,
                attendee: this.currentAttendee
            };
            console.log('STORING TO LOCALSTORAGE (REGISTER):', dataToStore);
            localStorage.setItem('jam_attendee', JSON.stringify(dataToStore));
            
            this.updateAttendeeUI();
            this.showMessage('Registered successfully!', 'success');
            
            // Notify other modules
            if (window.jamSongs) {
                window.jamSongs.onAttendeeRegistered(this.currentAttendee);
            }

        } catch (error) {
            console.error('Error registering attendee:', error);
            this.showMessage(error.message || 'An error occurred during registration.', 'error');
        }
    }


    /**
     * Clear attendee data
     */
    clearAttendee() {
        localStorage.removeItem('jam_attendee');
        this.currentAttendee = null;
        this.updateAttendeeUI();
        
        // Clear name input
        const nameInput = document.getElementById('userName');
        if (nameInput) {
            nameInput.value = '';
        }
        
        // Notify other modules
        if (window.jamSongs) {
            window.jamSongs.onAttendeeCleared();
        }
    }

    /**
     * Restore attendee from localStorage (only if for the same jam and session)
     */
    restoreAttendee() {
        const storedData = localStorage.getItem('jam_attendee');
        console.log('RESTORE ATTENDEE - storedData:', storedData);
        console.log('RESTORE ATTENDEE - jamCore available:', !!this.jamCore);
        console.log('RESTORE ATTENDEE - current sessionId:', this.sessionId);
        
        if (storedData && this.jamCore && this.jamCore.getJamId()) {
            try {
                const data = JSON.parse(storedData);
                console.log('RESTORE ATTENDEE - parsed data:', data);
                console.log('RESTORE ATTENDEE - jam_id match:', data.jam_id === this.jamCore.getJamId());
                console.log('RESTORE ATTENDEE - session_id match:', data.session_id === this.sessionId);
                
                // Only restore if the stored attendee is for the current jam AND same session
                if (data.jam_id === this.jamCore.getJamId() && data.session_id === this.sessionId) {
                    console.log('RESTORING ATTENDEE:', data.attendee);
                    this.currentAttendee = data.attendee;
                    
                    // Notify other modules about restored attendee
                    if (window.jamSongs) {
                        window.jamSongs.onAttendeeRegistered(this.currentAttendee);
                    }
                } else {
                    console.log('CLEARING LOCALSTORAGE - different jam or session');
                    // Clear localStorage if it's for a different jam or session
                    localStorage.removeItem('jam_attendee');
                }
            } catch (error) {
                console.error('Error parsing stored attendee:', error);
                localStorage.removeItem('jam_attendee');
            }
        } else {
            console.log('RESTORE ATTENDEE - no stored data or jamCore not available');
        }
    }

    /**
     * Update attendee UI based on current state
     */
    updateAttendeeUI() {
        const anonymousDiv = document.getElementById('anonymousUser');
        const registeredDiv = document.getElementById('registeredUser');
        const displayNameSpan = document.getElementById('userDisplayName');
        const addSongBtn = document.getElementById('addSongBtn');

        // Show Add Song button for both registered musos AND jam managers
        const shouldShowAddSong = this.currentAttendee || this.isJamManager;

        if (this.currentAttendee) {
            // Show registered state
            if (anonymousDiv) anonymousDiv.classList.add('hidden');
            if (registeredDiv) registeredDiv.classList.remove('hidden');
            if (displayNameSpan) displayNameSpan.textContent = this.currentAttendee.name;
        } else if (this.isJamManager) {
            // Show jam manager state (no attendee registration needed)
            if (anonymousDiv) anonymousDiv.classList.add('hidden');
            if (registeredDiv) registeredDiv.classList.remove('hidden');
            if (displayNameSpan) displayNameSpan.textContent = 'Jam Manager';
        } else {
            // Show anonymous state
            if (anonymousDiv) anonymousDiv.classList.remove('hidden');
            if (registeredDiv) registeredDiv.classList.add('hidden');
            if (displayNameSpan) displayNameSpan.textContent = '';
        }

        // Show/hide Add Song button based on permissions
        if (addSongBtn) {
            if (shouldShowAddSong) {
                addSongBtn.classList.remove('hidden');
            } else {
                addSongBtn.classList.add('hidden');
            }
        }
    }

    /**
     * Get current attendee
     */
    getCurrentAttendee() {
        return this.currentAttendee;
    }

    /**
     * Check if user is registered
     */
    isRegistered() {
        return this.currentAttendee !== null;
    }

    /**
     * Show message to user
     */
    showMessage(message, type = 'info') {
        // Use modern notification system directly
        if (window.notificationSystem) {
            if (type === 'error') {
                window.notificationSystem.error(message);
            } else if (type === 'success') {
                window.notificationSystem.success(message);
            } else if (type === 'warning') {
                window.notificationSystem.warning(message);
            } else {
                window.notificationSystem.info(message);
            }
        } else if (this.jamCore) {
            // Fallback to old system
            if (type === 'error') {
                this.jamCore.showError(message);
            } else if (type === 'success') {
                this.jamCore.showSuccess(message);
            } else {
                console.log(`Info: ${message}`);
            }
        }
    }
}

// Export for use in other modules
window.JamAttendee = JamAttendee;