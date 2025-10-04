/**
 * Core Jam Page Functionality
 * Handles basic jam data loading and UI state management
 */


class JamCore {
    constructor() {
        this.jamId = null;
        this.jamSlug = this.getJamSlugFromUrl();
        this.jamData = null;
        this.isLoading = false;
    }

    /**
     * Extract jam slug from URL
     */
    getJamSlugFromUrl() {
        const pathParts = window.location.pathname.split('/');
        return pathParts[pathParts.length - 1];
    }

    /**
     * Load jam data from API
     */
    async loadJamData() {
        if (this.isLoading) return;
        
        this.isLoading = true;
        this.showLoadingState();

        try {
            const response = await fetch(`/api/jams/by-slug/${this.jamSlug}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.jamData = await response.json();
            this.jamId = this.jamData.id;
            
            this.updateJamInfo();
            this.setBackgroundImage(this.jamData.background_image);
            
            // Notify other modules that jam data is loaded
            if (window.jamAttendee) {
                window.jamAttendee.onJamDataLoaded(this.jamData);
            }
            if (window.jamSongs) {
                window.jamSongs.onJamDataLoaded(this.jamData);
            }
            
        } catch (error) {
            console.error('Error loading jam data:', error);
            this.showError('Failed to load jam data. Please try again.');
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Update jam information in the UI
     */
    updateJamInfo() {
        if (!this.jamData) return;

        const jamNameEl = document.getElementById('jamName');
        const jamDescEl = document.getElementById('jamDescription');

        if (jamNameEl) {
            jamNameEl.textContent = this.jamData.name;
        }

        if (jamDescEl) {
            jamDescEl.textContent = this.jamData.description || 'No description available';
        }
    }

    /**
     * Set background image for the jam
     */
    setBackgroundImage(backgroundImage) {
        const backgroundLayer = document.getElementById('backgroundLayer');
        if (!backgroundLayer) return;

        if (backgroundImage) {
            let backgroundUrl;
            if (backgroundImage.startsWith('http')) {
                backgroundUrl = backgroundImage;
            } else if (backgroundImage.startsWith('/static/uploads/')) {
                backgroundUrl = backgroundImage;
            } else {
                backgroundUrl = `/static/uploads/${backgroundImage}`;
            }

            const img = new Image();
            img.onload = () => {
                backgroundLayer.style.backgroundImage = `url('${backgroundUrl}')`;
                backgroundLayer.style.backgroundSize = 'cover';
                backgroundLayer.style.backgroundPosition = 'center';
                backgroundLayer.style.backgroundRepeat = 'no-repeat';
                backgroundLayer.style.backgroundAttachment = 'fixed';
            };
            img.onerror = () => {
                console.warn('Failed to load background image:', backgroundUrl);
                backgroundLayer.style.backgroundImage = '';
            };
            img.src = backgroundUrl;
        } else {
            backgroundLayer.style.backgroundImage = '';
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const jamNameEl = document.getElementById('jamName');
        if (jamNameEl) {
            jamNameEl.textContent = 'Loading Jam...';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const jamNameEl = document.getElementById('jamName');
        if (jamNameEl) {
            jamNameEl.textContent = 'Error loading jam';
        }
        
        // Use modern notification system
        if (window.notificationSystem) {
            window.notificationSystem.error(message, {
                duration: 5000
            });
        } else {
            console.error('Notification system not available:', message);
        }
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        // Use modern notification system
        if (window.notificationSystem) {
            window.notificationSystem.success(message, {
                duration: 3000
            });
        } else {
        }
    }

    /**
     * Get current jam data
     */
    getJamData() {
        return this.jamData;
    }

    /**
     * Get current jam ID
     */
    getJamId() {
        return this.jamId;
    }
}

// Export for use in other modules
window.JamCore = JamCore;
