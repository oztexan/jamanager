/**
 * Main Jam UI Controller
 * Coordinates all jam page modules and handles global UI interactions
 */

console.log('jam-main.js loaded successfully');
console.log('Document ready state:', document.readyState);
console.log('DOM loaded?', document.readyState === 'loading' ? 'No' : 'Yes');

class JamUI {
    constructor() {
        this.jamCore = null;
        this.attendee = null;
        this.songs = null;
        this.websocket = null;
        this.chordSheets = null;
    }

    /**
     * Initialize the jam UI
     */
    async init() {
        try {
            console.log('JamMain: Starting initialization...');
            // Initialize core modules
            this.jamCore = new JamCore();
            console.log('JamMain: JamCore created');
            this.attendee = new JamAttendee();
            console.log('JamMain: JamAttendee created');
            this.songs = new JamSongs();
            console.log('JamMain: JamSongs created');
            this.websocket = new JamWebSocket();
            this.chordSheets = new JamChordSheets();

            // Make modules globally available BEFORE initializing
            window.jamAttendee = this.attendee;
            window.jamSongs = this.songs;
            console.log('JamMain: Modules made globally available');

            // Initialize modules
            this.attendee.init(this.jamCore);
            console.log('JamMain: JamAttendee initialized');
            this.songs.init(this.jamCore, this.attendee);
            console.log('JamMain: JamSongs initialized');
            this.chordSheets.init(this.jamCore);

            // Load jam data
            console.log('JamMain: Loading jam data...');
            await this.jamCore.loadJamData();
            console.log('JamMain: Jam data loaded');

            // Initialize WebSocket if jam is loaded
            if (this.jamCore.getJamId()) {
                console.log('JamMain: Initializing WebSocket with jam ID:', this.jamCore.getJamId());
                this.websocket.init(this.jamCore.getJamId());
            }

            // Setup global event listeners
            this.setupEventListeners();

            console.log('Jam UI initialized successfully');

        } catch (error) {
            console.error('Error initializing Jam UI:', error);
            this.showError('Failed to initialize jam page. Please refresh and try again.');
        }
    }

    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Modal close handlers
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (event) => {
                if (event.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });

        // Close modal buttons
        document.querySelectorAll('[data-action="close-modal"]').forEach(button => {
            button.addEventListener('click', (event) => {
                const modal = event.target.closest('.modal');
                if (modal) {
                    modal.classList.add('hidden');
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    /**
     * Close all open modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

    /**
     * Show share modal
     */
    showShareModal() {
        const modal = document.getElementById('shareModal');
        if (modal) {
            modal.classList.remove('hidden');
            this.loadShareContent();
        }
    }

    /**
     * Close share modal
     */
    closeShareModal() {
        const modal = document.getElementById('shareModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    /**
     * Load share content (URL and QR code)
     */
    async loadShareContent() {
        const jamUrlInput = document.getElementById('shareUrl');
        if (jamUrlInput) {
            jamUrlInput.value = window.location.href;
        }

        const qrCodeImg = document.getElementById('qrCode');
        const qrLoading = document.getElementById('qrLoading');

        if (qrCodeImg && qrLoading && this.jamCore && this.jamCore.getJamId()) {
            qrLoading.style.display = 'block';
            qrCodeImg.classList.add('hidden'); // Hide QR code initially

            try {
                const qrUrl = `/api/jams/${this.jamCore.getJamId()}/qr`;
                const response = await fetch(qrUrl);
                
                if (response.ok) {
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    
                    qrCodeImg.src = imageUrl;
                    qrCodeImg.classList.remove('hidden'); // Remove hidden class instead of setting display
                    qrLoading.style.display = 'none';
                } else {
                    qrLoading.textContent = `Failed to generate QR code (${response.status})`;
                }
            } catch (error) {
                console.error('Error generating QR code:', error);
                qrLoading.textContent = 'Error generating QR code.';
            }
        }
    }

    /**
     * Copy jam URL to clipboard
     */
    async copyUrl() {
        const jamUrlInput = document.getElementById('shareUrl');
        if (jamUrlInput) {
            try {
                await navigator.clipboard.writeText(jamUrlInput.value);
                this.showMessage('Jam URL copied to clipboard!', 'success');
            } catch (err) {
                console.error('Failed to copy URL: ', err);
                this.showMessage('Failed to copy URL. Please copy manually.', 'error');
            }
        }
    }

    /**
     * Show add song modal
     */
    showAddSongModal() {
        if (this.songs) {
            this.songs.showAddSongModal();
        }
    }

    /**
     * Close add song modal
     */
    closeAddSongModal() {
        if (this.songs) {
            this.songs.closeAddSongModal();
        }
    }

    /**
     * Add song to jam
     */
    addSongToJam() {
        if (this.songs) {
            this.songs.addSongToJam();
        }
    }

    /**
     * Register user
     */
    registerUser() {
        if (this.attendee) {
            this.attendee.registerUser();
        }
    }


    /**
     * Show performance modal
     */
    showPerformModal(songId) {
        if (this.songs) {
            this.songs.showPerformModal(songId);
        }
    }

    /**
     * Close performance modal
     */
    closePerformModal() {
        if (this.songs) {
            this.songs.closePerformModal();
        }
    }

    /**
     * Confirm performance registration
     */
    confirmPerformRegistration() {
        if (this.songs) {
            this.songs.confirmPerformRegistration();
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (this.jamCore) {
            this.jamCore.showError(message);
        }
    }

    /**
     * Show success message
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

    /**
     * Get current jam data
     */
    getJamData() {
        return this.jamCore ? this.jamCore.getJamData() : null;
    }

    /**
     * Get current attendee
     */
    getCurrentAttendee() {
        return this.attendee ? this.attendee.getCurrentAttendee() : null;
    }
}

// Global jam UI instance
let jamUI = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOMContentLoaded event fired');
    try {
        console.log('Creating JamUI instance...');
        jamUI = new JamUI();
        console.log('JamUI instance created, calling init...');
        await jamUI.init();
        console.log('JamUI init completed');
        
        // Make jamUI globally available for onclick handlers
        window.jamUI = jamUI;
        console.log('jamUI made globally available');
    } catch (error) {
        console.error('Error during JamUI initialization:', error);
    }
});


// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (jamUI && jamUI.websocket) {
        jamUI.websocket.disconnect();
    }
});
