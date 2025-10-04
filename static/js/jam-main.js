/**
 * Main Jam UI Controller
 * Coordinates all jam page modules and handles global UI interactions
 */


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
            // Initialize core modules
            this.jamCore = new JamCore();
            this.attendee = new JamAttendee();
            this.songs = new JamSongs();
            this.websocket = new JamWebSocket();
            this.chordSheets = new JamChordSheets();

            // Make modules globally available BEFORE initializing
            window.jamAttendee = this.attendee;
            window.jamSongs = this.songs;

            // Initialize modules
            this.attendee.init(this.jamCore);
            this.songs.init(this.jamCore, this.attendee);
            this.chordSheets.init(this.jamCore);

            // Load jam data
            await this.jamCore.loadJamData();

            // Initialize WebSocket if jam is loaded
            if (this.jamCore.getJamId()) {
                this.websocket.init(this.jamCore.getJamId());
            }

            // Setup global event listeners
            this.setupEventListeners();


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
     * Chord sheet modal methods - delegate to jamSongs
     */
    closeChordSheetModal() {
        if (this.songs) {
            this.songs.closeChordSheetModal();
        } else {
            console.error('songs is not available');
        }
    }

    saveChordSheet() {
        if (this.songs) {
            this.songs.saveChordSheet();
        } else {
            console.error('songs is not available');
        }
    }

    deleteChordSheet() {
        if (this.songs) {
            this.songs.deleteChordSheet();
        } else {
            console.error('songs is not available');
        }
    }

    selectChordSheet(url) {
        if (this.songs) {
            this.songs.selectChordSheet(url);
        } else {
            console.error('songs is not available');
        }
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
    try {
        jamUI = new JamUI();
        await jamUI.init();
        
        // Make jamUI globally available for onclick handlers
        window.jamUI = jamUI;
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
