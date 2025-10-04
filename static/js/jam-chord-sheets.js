/**
 * Jam Chord Sheets Management
 * Handles chord sheet discovery and management
 */

class JamChordSheets {
    constructor() {
        this.jamCore = null;
    }

    /**
     * Initialize chord sheets management
     */
    init(jamCore) {
        this.jamCore = jamCore;
    }

    /**
     * Search for chord sheets on Ultimate Guitar
     */
    async searchChordSheets(songTitle, artist) {
        try {
            const response = await fetch('/api/chord-sheets/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_name: songTitle,
                    artist: artist
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.chord_sheets || [];
            
        } catch (error) {
            console.error('Error searching chord sheets:', error);
            throw error;
        }
    }

    /**
     * Show chord sheet search modal
     */
    showChordSheetModal(songId, songTitle, artist) {
        // This would open a modal to search and select chord sheets
        // For now, we'll just open the search in a new tab
        const searchUrl = `https://www.ultimate-guitar.com/search.php?search_type=title&value=${encodeURIComponent(songTitle + ' ' + artist)}`;
        window.open(searchUrl, '_blank');
    }

    /**
     * Update chord sheet URL for a song in the jam
     */
    async updateChordSheetUrl(songId, chordSheetUrl) {
        if (!this.jamCore || !this.jamCore.getJamId()) {
            throw new Error('Jam not loaded');
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/songs/${songId}/chord-sheet`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chord_sheet_url: chordSheetUrl
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update chord sheet URL');
            }

            return await response.json();
            
        } catch (error) {
            console.error('Error updating chord sheet URL:', error);
            throw error;
        }
    }

    /**
     * Get chord sheet URL for a song
     */
    getChordSheetUrl(songId) {
        if (!window.jamSongs || !window.jamSongs.jamSongs) {
            return null;
        }

        const jamSong = window.jamSongs.jamSongs.find(js => js.song.id === songId);
        return jamSong ? jamSong.song.chord_sheet_url : null;
    }

    /**
     * Open chord sheet in new window
     */
    openChordSheet(songId) {
        const chordSheetUrl = this.getChordSheetUrl(songId);
        if (chordSheetUrl) {
            window.open(chordSheetUrl, '_blank');
        } else {
            this.showMessage('No chord sheet available for this song.', 'info');
        }
    }

    /**
     * Show message to user
     */
    showMessage(message, type = 'info') {
        if (this.jamCore) {
            if (type === 'error') {
                this.jamCore.showError(message);
            } else if (type === 'success') {
                this.jamCore.showSuccess(message);
            } else {
            }
        }
    }
}

// Export for use in other modules
window.JamChordSheets = JamChordSheets;
