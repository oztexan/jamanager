// Jamanger Application - Main JavaScript
class JamangerApp {
    constructor() {
        this.currentJam = null;
        this.ws = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeBreadcrumbs();
        this.loadRecentJams();
        this.loadTodaysJams();
        this.loadVenues();
        this.ensureAllModalsHidden();
        this.checkAccessStatus();
    }

    isJamManager() {
        // Check if user has jam manager access
        return localStorage.getItem('jamManagerAccess') === 'true';
    }

    initializeBreadcrumbs() {
        // Initialize breadcrumbs for the home page
        if (window.breadcrumbManager) {
            if (this.isJamManager()) {
                window.breadcrumbManager.setBreadcrumbs(BreadcrumbManager.getHomeBreadcrumbs());
                window.breadcrumbManager.show();
            } else {
                window.breadcrumbManager.hide();
            }
        }
    }

    updateBreadcrumbs() {
        // Update breadcrumb visibility based on current access status
        if (window.breadcrumbManager) {
            if (this.isJamManager()) {
                window.breadcrumbManager.setBreadcrumbs(BreadcrumbManager.getHomeBreadcrumbs());
                window.breadcrumbManager.show();
            } else {
                window.breadcrumbManager.hide();
            }
        }
    }

    ensureAllModalsHidden() {
        // Ensure all modals are hidden on page load
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
            console.log('Hidden modal:', modal.id);
        });
        console.log('All modals should be hidden now');
    }

    setupEventListeners() {
        // Modal close on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideAllModals();
            }
        });

        // Enter key handlers (removed jamSlug handler since Join Jam modal was removed)

        // Access code dialog keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const accessCodeModal = document.getElementById('accessCodeModal');
                if (!accessCodeModal.classList.contains('hidden')) {
                    this.verifyAccessCode();
                }
            } else if (e.key === 'Escape') {
                const accessCodeModal = document.getElementById('accessCodeModal');
                if (!accessCodeModal.classList.contains('hidden')) {
                    this.closeAccessDialog();
                }
            }
        });
    }

    // Modal Management
    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    showModal(modalId) {
        this.hideAllModals();
        document.getElementById(modalId).classList.remove('hidden');
    }


    joinJam(slug) {
        window.location.href = `/jam/${slug}`;
    }

    // Create Jam
    showCreateJamModal() {
        this.showModal('createJamModal');
        this.clearForm('createJam');
    }

    hideCreateJamModal() {
        document.getElementById('createJamModal').classList.add('hidden');
    }

    async loadVenues() {
        try {
            const response = await fetch('/api/venues');
            if (response.ok) {
                const venues = await response.json();
                const venueSelect = document.getElementById('jamVenue');
                venueSelect.innerHTML = '<option value="">Select a venue...</option>';
                venues.forEach(venue => {
                    const option = document.createElement('option');
                    option.value = venue.id;
                    option.textContent = venue.name;
                    venueSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading venues:', error);
        }
    }

    async createJam() {
        console.log('createJam called');
        const name = document.getElementById('jamName').value.trim();
        const venueId = document.getElementById('jamVenue').value;
        const jamDate = document.getElementById('jamDate').value;
        const description = document.getElementById('jamDescription').value.trim();
        const backgroundImage = document.getElementById('jamBackgroundImage').files[0];

        console.log('Jam data:', { name, venueId, jamDate, description, backgroundImage });

        if (!name) {
            this.showError('createJamError', 'Jam name is required');
            return;
        }

        if (!venueId) {
            this.showError('createJamError', 'Venue is required');
            return;
        }

        if (!jamDate) {
            this.showError('createJamError', 'Date is required');
            return;
        }

        try {
            console.log('Sending request to /api/jams');
            
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('name', name);
            formData.append('description', description);
            formData.append('venue_id', venueId);
            formData.append('jam_date', jamDate);
            
            if (backgroundImage) {
                formData.append('background_image', backgroundImage);
            }

            const response = await fetch('/api/jams', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);
            if (response.ok) {
                const jam = await response.json();
                console.log('Jam created successfully:', jam);
                this.showSuccess('createJamSuccess', `Jam "${name}" created successfully!`);
                setTimeout(() => {
                    this.hideCreateJamModal();
                    this.joinJam(jam.slug);
                }, 1500);
            } else {
                const error = await response.json();
                console.error('Error creating jam:', error);
                this.showError('createJamError', error.detail || 'Failed to create jam');
            }
        } catch (error) {
            console.error('Network error:', error);
            this.showError('createJamError', 'Network error: ' + error.message);
        }
    }

    // Create Song
    showCreateSongModal() {
        this.showModal('createSongModal');
        this.clearForm('createSong');
    }

    hideCreateSongModal() {
        document.getElementById('createSongModal').classList.add('hidden');
    }

    async createSong() {
        const title = document.getElementById('songTitle').value.trim();
        const artist = document.getElementById('songArtist').value.trim();
        const type = document.getElementById('songType').value;
        const chordChart = document.getElementById('songChords').value.trim();
        const tagsInput = document.getElementById('songTags').value.trim();

        if (!title || !artist) {
            this.showError('createSongError', 'Title and artist are required');
            return;
        }

        const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()) : [];

        try {
            const response = await fetch('/api/songs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    title: title,
                    artist: artist,
                    type: type,
                    chord_chart: chordChart,
                    tags: tags
                })
            });

            if (response.ok) {
                const song = await response.json();
                this.showSuccess('createSongSuccess', `Song "${title}" by ${artist} added successfully!`);
                setTimeout(() => {
                    this.hideCreateSongModal();
                }, 1500);
            } else {
                const error = await response.json();
                this.showError('createSongError', error.detail || 'Failed to create song');
            }
        } catch (error) {
            this.showError('createSongError', 'Network error: ' + error.message);
        }
    }

    // Song Library
    showSongLibrary() {
        window.location.href = '/songs';
    }

    // Jam Management
    showJamManagement() {
        window.location.href = '/jams';
    }

    // Jam Manager Panel
    showJamManagerPanel() {
        window.location.href = '/jam-manager';
    }

    // Recent Jams
    async loadRecentJams() {
        try {
            const response = await fetch('/api/jams');
            if (response.ok) {
                const jams = await response.json();
                this.displayRecentJams(jams);
            }
        } catch (error) {
            console.error('Failed to load recent jams:', error);
        }
    }

    async loadTodaysJams() {
        try {
            console.log('🔄 Loading today\'s jams...');
            const response = await fetch('/api/jams');
            if (response.ok) {
                const jams = await response.json();
                console.log('📊 API returned jams:', jams.length);
                this.displayTodaysJams(jams);
            } else {
                console.error('❌ API error:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('❌ Error loading today\'s jams:', error);
        }
    }

    // Access Code System
    async checkAccessStatus() {
        try {
            const sessionId = this.getSessionId();
            const response = await fetch('/api/access-code/status', {
                headers: {
                    'X-Session-ID': sessionId
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                // Update localStorage based on server response
                if (data.has_access) {
                    localStorage.setItem('jamManagerAccess', 'true');
                } else {
                    localStorage.removeItem('jamManagerAccess');
                }
                this.updateLockButton(data.has_access);
                this.updateBreadcrumbs();
            }
        } catch (error) {
            console.error('Error checking access status:', error);
        }
    }

    updateLockButton(hasAccess) {
        const lockButton = document.getElementById('lockButton');
        if (lockButton) {
            if (hasAccess) {
                lockButton.textContent = '🔓';
                lockButton.classList.add('unlocked');
                lockButton.title = 'Logout from Jam Manager';
            } else {
                lockButton.textContent = '🔒';
                lockButton.classList.remove('unlocked');
                lockButton.title = 'Jam Manager Access';
            }
        }
        
        // Show/hide jam manager features
        this.updateJamManagerFeatures(hasAccess);
    }

    updateJamManagerFeatures(hasAccess) {
        const jamManagerFeatures = document.querySelectorAll('.jam-manager-feature');
        jamManagerFeatures.forEach(feature => {
            if (hasAccess) {
                feature.style.display = '';
            } else {
                feature.style.display = 'none';
            }
        });

        // Show/hide anonymous message
        const anonymousMessage = document.getElementById('anonymousMessage');
        if (anonymousMessage) {
            if (hasAccess) {
                anonymousMessage.classList.add('hidden');
            } else {
                anonymousMessage.classList.remove('hidden');
            }
        }

        // Show/hide jams today section (visible to all users)
        const jamsTodaySection = document.getElementById('jamsTodaySection');
        if (jamsTodaySection) {
            jamsTodaySection.style.display = '';
        }
    }

    async verifyAccessCode() {
        const accessCodeInput = document.getElementById('accessCodeInput');
        const messageDiv = document.getElementById('accessCodeMessage');
        const accessCode = accessCodeInput.value.trim();
        
        if (!accessCode) {
            this.showAccessMessage('Please enter an access code', 'error');
            return;
        }

        try {
            const sessionId = this.getSessionId();
            const response = await fetch('/api/access-code/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': sessionId
                },
                body: JSON.stringify({ access_code: accessCode })
            });

            if (response.ok) {
                const data = await response.json();
                // Set localStorage to indicate jam manager access
                localStorage.setItem('jamManagerAccess', 'true');
                this.showAccessMessage('Access granted! You now have jam manager privileges.', 'success');
                this.updateLockButton(true);
                this.updateBreadcrumbs();
                setTimeout(() => {
                    this.closeAccessDialog();
                }, 1500);
            } else {
                const error = await response.json();
                this.showAccessMessage(error.detail || 'Invalid access code', 'error');
            }
        } catch (error) {
            this.showAccessMessage('Network error: ' + error.message, 'error');
        }
    }

    async logoutJamManager() {
        try {
            const sessionId = this.getSessionId();
            const response = await fetch('/api/access-code/logout', {
                method: 'POST',
                headers: {
                    'X-Session-ID': sessionId
                }
            });

            if (response.ok) {
                // Clear localStorage to remove jam manager access
                localStorage.removeItem('jamManagerAccess');
                this.updateLockButton(false);
                this.updateBreadcrumbs();
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    }

    showAccessMessage(message, type) {
        const messageDiv = document.getElementById('accessCodeMessage');
        messageDiv.textContent = message;
        messageDiv.className = `access-message ${type}`;
        messageDiv.classList.remove('hidden');
    }

    closeAccessDialog() {
        const modal = document.getElementById('accessCodeModal');
        const input = document.getElementById('accessCodeInput');
        const message = document.getElementById('accessCodeMessage');
        
        modal.classList.add('hidden');
        input.value = '';
        message.classList.add('hidden');
    }

    getSessionId() {
        let sessionId = localStorage.getItem('jam_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('jam_session_id', sessionId);
        }
        return sessionId;
    }

    displayRecentJams(jams) {
        const list = document.getElementById('recentJamsList');
        list.innerHTML = '';

        if (jams.length === 0) {
            list.innerHTML = '<li class="jam-item"><p>No jams found. Create your first jam!</p></li>';
            return;
        }

        jams.forEach(jam => {
            const li = document.createElement('li');
            li.className = 'jam-item';
            li.onclick = () => this.joinJam(jam.slug);
            
            const songCount = jam.song_count || 0;
            const status = jam.status || 'waiting';
            const venue = jam.venue_name || 'Unknown Venue';
            
            li.innerHTML = `
                <h4>${jam.name}</h4>
                <p>${jam.description || 'No description'} • ${venue} • ${songCount} songs • ${status}</p>
            `;
            
            list.appendChild(li);
        });
    }

    displayTodaysJams(jams) {
        console.log('🎵 displayTodaysJams called with:', jams.length, 'jams');
        
        // Set today's date in Sydney timezone
        const today = new Date();
        const sydneyDate = new Date(today.toLocaleString("en-US", {timeZone: "Australia/Sydney"}));
        const todayFormatted = sydneyDate.toLocaleDateString('en-AU', {
            day: '2-digit',
            month: 'short',
            year: 'numeric'
        });
        
        console.log('📅 Today formatted:', todayFormatted);
        console.log('📅 Sydney date:', sydneyDate.toDateString());
        
        // Update the date display
        const todayDateElement = document.getElementById('todayDate');
        if (todayDateElement) {
            todayDateElement.textContent = todayFormatted;
            console.log('✅ Date element updated');
        } else {
            console.error('❌ todayDate element not found');
        }
        
        // Filter jams for today
        const todayJams = jams.filter(jam => {
            if (!jam.jam_date) {
                console.log('❌ Jam has no date:', jam.name);
                return false;
            }
            const jamDate = new Date(jam.jam_date);
            console.log('📅 Jam date:', jam.name, jam.jam_date, jamDate.toDateString());
            return jamDate.toDateString() === sydneyDate.toDateString();
        });
        
        console.log('🎵 Today jams found:', todayJams.length);
        
        const list = document.getElementById('jamsTodayList');
        const noJamsMessage = document.getElementById('noJamsToday');
        
        console.log('📋 List element:', list);
        console.log('💬 No jams message element:', noJamsMessage);
        
        if (todayJams.length === 0) {
            console.log('📭 No jams today, showing empty message');
            list.innerHTML = '';
            noJamsMessage.style.display = 'block';
            return;
        }
        
        console.log('🎵 Showing jams, hiding empty message');
        noJamsMessage.style.display = 'none';
        list.innerHTML = '';
        
        todayJams.forEach(jam => {
            console.log('🎵 Creating tile for:', jam.name);
            const tile = document.createElement('div');
            tile.className = 'jam-tile';
            tile.onclick = () => this.joinJam(jam.slug);
            
            const venue = jam.venue_name ? `📍 ${jam.venue_name}` : '📍 Location TBD';
            
            tile.innerHTML = `
                <h3>${jam.name}</h3>
                <p>${venue}</p>
            `;
            
            list.appendChild(tile);
        });
        
        console.log('✅ Jams display complete');
    }

    // Utility Functions
    showError(elementId, message) {
        const errorElement = document.getElementById(elementId);
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
        
        // Hide success message if shown
        const successId = elementId.replace('Error', 'Success');
        document.getElementById(successId).classList.add('hidden');
    }

    showSuccess(elementId, message) {
        const successElement = document.getElementById(elementId);
        successElement.textContent = message;
        successElement.classList.remove('hidden');
        
        // Hide error message if shown
        const errorId = elementId.replace('Success', 'Error');
        document.getElementById(errorId).classList.add('hidden');
    }

    clearForm(formType) {
        // Clear error/success messages
        document.getElementById(`${formType}Error`).classList.add('hidden');
        document.getElementById(`${formType}Success`).classList.add('hidden');
        
        // Clear form fields
        if (formType === 'createJam') {
            document.getElementById('jamName').value = '';
            document.getElementById('jamVenue').value = '';
            document.getElementById('jamDate').value = '';
            document.getElementById('jamDescription').value = '';
            document.getElementById('jamBackgroundImage').value = '';
        } else if (formType === 'createSong') {
            document.getElementById('songTitle').value = '';
            document.getElementById('songArtist').value = '';
            document.getElementById('songType').value = 'rock';
            document.getElementById('songChords').value = '';
            document.getElementById('songTags').value = '';
        }
    }
}

// Global functions for onclick handlers


function joinJam(slug) {
    app.joinJam(slug);
}

function showCreateJamModal() {
    app.showCreateJamModal();
}

function hideCreateJamModal() {
    app.hideCreateJamModal();
}

function createJam() {
    app.createJam();
}

function showCreateSongModal() {
    app.showCreateSongModal();
}

function hideCreateSongModal() {
    app.hideCreateSongModal();
}

function createSong() {
    app.createSong();
}

function showSongLibrary() {
    app.showSongLibrary();
}

function showJamManagement() {
    app.showJamManagement();
}

function showJamManagerPanel() {
    app.showJamManagerPanel();
}

function loadRecentJams() {
    app.loadRecentJams();
}

// Initialize the app first
const app = new JamangerApp();

// Access Code Dialog Functions
function toggleAccessDialog() {
    const lockButton = document.getElementById('lockButton');
    const hasAccess = lockButton.classList.contains('unlocked');
    
    if (hasAccess) {
        // Logout
        app.logoutJamManager();
    } else {
        // Show access dialog
        const modal = document.getElementById('accessCodeModal');
        modal.classList.remove('hidden');
        document.getElementById('accessCodeInput').focus();
    }
}

function verifyAccessCode() {
    app.verifyAccessCode();
}

function closeAccessDialog() {
    app.closeAccessDialog();
}