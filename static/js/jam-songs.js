/**
 * Jam Songs Management
 * Handles song display, voting, and performance registration
 */

console.log('jam-songs.js loaded successfully');

class JamSongs {
    constructor() {
        this.songs = []; // All available songs
        this.jamSongs = []; // Songs in the current jam
        this.userPerformanceRegistrations = {}; // Track user's performance registrations
        this.userVotes = {}; // Track user's votes
        this.performanceLimit = 3; // Default limit
        this.jamCore = null;
        this.attendee = null;
        
        // Sorting and filtering state
        this.sortCriteria = 'performance'; // 'name', 'artist', 'votes', 'performance'
        this.sortDirection = 'asc'; // 'asc', 'desc'
        this.showOnlyMyPerformances = false;
    }

    /**
     * Initialize songs management
     */
    init(jamCore, attendee) {
        this.jamCore = jamCore;
        this.attendee = attendee;
        this.initializeControls();
    }

    /**
     * Initialize sorting and filtering controls
     */
    initializeControls() {
        // Load saved preferences
        this.loadSortingPreferences();
        
        // Set up event listeners
        this.setupControlEventListeners();
        
        // Show/hide performance filter based on user status
        this.updatePerformanceFilterVisibility();
    }

    /**
     * Set up event listeners for sorting and filtering controls
     */
    setupControlEventListeners() {
        // Sorting controls
        const sortCriteriaSelect = document.getElementById('sortCriteria');
        const sortDirectionBtn = document.getElementById('sortDirection');
        const showOnlyMyPerformancesCheckbox = document.getElementById('showOnlyMyPerformances');

        if (sortCriteriaSelect) {
            sortCriteriaSelect.addEventListener('change', (e) => {
                this.sortCriteria = e.target.value;
                this.saveSortingPreferences();
                this.displaySongs();
            });
        }

        if (sortDirectionBtn) {
            sortDirectionBtn.addEventListener('click', () => {
                this.sortDirection = this.sortDirection === 'desc' ? 'asc' : 'desc';
                this.updateSortDirectionUI();
                this.saveSortingPreferences();
                this.displaySongs();
            });
        }

        if (showOnlyMyPerformancesCheckbox) {
            showOnlyMyPerformancesCheckbox.addEventListener('change', (e) => {
                this.showOnlyMyPerformances = e.target.checked;
                this.displaySongs();
            });
        }
    }

    /**
     * Update the sort direction button UI
     */
    updateSortDirectionUI() {
        const sortDirectionBtn = document.getElementById('sortDirection');
        if (sortDirectionBtn) {
            const sortIcon = sortDirectionBtn.querySelector('.sort-icon');
            if (sortIcon) {
                // Enable toggle for all sort criteria
                sortDirectionBtn.disabled = false;
                sortDirectionBtn.classList.remove('disabled');
                
                // Always use down arrow - CSS will rotate it when needed
                sortIcon.textContent = '↓';
                
                if (this.sortDirection === 'desc') {
                    sortDirectionBtn.classList.add('desc');
                    sortDirectionBtn.title = 'Currently: High to Low (click for Low to High)';
                } else {
                    sortDirectionBtn.classList.remove('desc');
                    sortDirectionBtn.title = 'Currently: Low to High (click for High to Low)';
                }
            }
        }
    }

    /**
     * Update performance filter visibility based on user status
     */
    updatePerformanceFilterVisibility() {
        const performanceFilter = document.getElementById('performanceFilter');
        if (performanceFilter) {
            if (this.attendee && this.attendee.getCurrentAttendee()) {
                performanceFilter.classList.remove('hidden');
            } else {
                performanceFilter.classList.add('hidden');
            }
        }
    }

    /**
     * Load sorting preferences from localStorage
     */
    loadSortingPreferences() {
        try {
            const saved = localStorage.getItem('jam_sorting_preferences');
            if (saved) {
                const preferences = JSON.parse(saved);
                this.sortCriteria = preferences.criteria || 'performance';
                this.sortDirection = preferences.direction || 'asc';
            }
        } catch (error) {
            console.error('Error loading sorting preferences:', error);
        }

        // Update UI controls
        const sortCriteriaSelect = document.getElementById('sortCriteria');
        
        if (sortCriteriaSelect) {
            sortCriteriaSelect.value = this.sortCriteria;
        }
        
        // Update sort direction button UI
        this.updateSortDirectionUI();
    }

    /**
     * Save sorting preferences to localStorage
     */
    saveSortingPreferences() {
        try {
            const preferences = {
                criteria: this.sortCriteria,
                direction: this.sortDirection
            };
            localStorage.setItem('jam_sorting_preferences', JSON.stringify(preferences));
        } catch (error) {
            console.error('Error saving sorting preferences:', error);
        }
    }

    /**
     * Called when jam data is loaded
     */
    onJamDataLoaded(jamData) {
        this.jamSongs = jamData.songs || [];
        
        // Add a small delay to ensure DOM is ready
        setTimeout(() => {
            this.displaySongs();
        }, 100);
        
        this.loadAllSongs(); // Load all songs for the add song modal
        this.loadUserPerformanceRegistrations(); // Load user's performance registrations
    }

    /**
     * Called when attendee is registered
     */
    onAttendeeRegistered(attendee) {
        // Don't overwrite this.attendee - it should remain the attendee module
        // The attendee object is passed as a parameter for reference
        this.loadUserPerformanceRegistrations();
        this.loadUserVotes(); // Load user's votes
        this.updatePerformanceFilterVisibility(); // Show performance filter
        this.displaySongs(); // Re-render to show perform buttons
    }

    /**
     * Called when attendee is cleared
     */
    onAttendeeCleared() {
        this.attendee = null;
        this.userPerformanceRegistrations = {};
        this.userVotes = {}; // Clear user votes
        this.showOnlyMyPerformances = false; // Reset filter
        this.updatePerformanceFilterVisibility(); // Hide performance filter
        this.displaySongs(); // Re-render to hide perform buttons
    }

    /**
     * Load all available songs
     */
    async loadAllSongs() {
        try {
            const response = await fetch('/api/songs');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.songs = await response.json();
        } catch (error) {
            console.error('Error loading all songs:', error);
            this.showMessage('Failed to load available songs.', 'error');
        }
    }

    /**
     * Display songs in the UI
     */
    displaySongs() {
        const songListElement = document.getElementById('songsList');
        if (!songListElement) {
            return;
        }

        // Store current voted state before clearing
        const currentVotedState = {};
        songListElement.querySelectorAll('[data-action="vote"]').forEach(element => {
            const songId = element.dataset.songId;
            currentVotedState[songId] = element.classList.contains('voted');
        });

        songListElement.innerHTML = ''; // Clear existing songs

        if (this.jamSongs.length === 0) {
            songListElement.innerHTML = '<li class="empty-list-message">No songs in the queue yet.</li>';
            return;
        }

        // Filter songs if needed
        let filteredSongs = this.jamSongs;
        if (this.showOnlyMyPerformances) {
            filteredSongs = this.jamSongs.filter(jamSong => 
                this.userPerformanceRegistrations[jamSong.song.id]
            );
        }

        if (filteredSongs.length === 0) {
            songListElement.innerHTML = '<li class="empty-list-message">No songs match your filter criteria.</li>';
            return;
        }

        // Calculate performance order for all songs (regardless of current sort)
        const allSongsWithOrder = this.calculatePerformanceOrder(this.jamSongs);
        
        // Create a map of song ID to performance order for quick lookup
        const orderMap = {};
        allSongsWithOrder.forEach(jamSong => {
            orderMap[jamSong.song.id] = jamSong.performanceOrder;
        });

        // Sort songs based on current criteria and direction
        const sortedSongs = this.sortSongs(filteredSongs);

        sortedSongs.forEach(jamSong => {
            const song = jamSong.song;
            const listItem = document.createElement('li');
            listItem.className = 'song-item';
            listItem.dataset.songId = song.id;

            const isVoted = this.isVoted(song.id) || currentVotedState[song.id];
            const isPerforming = this.userPerformanceRegistrations[song.id];
            const performanceOrder = orderMap[song.id] || '';

            listItem.innerHTML = `
                <div class="song-order">
                    <span class="order-number">${performanceOrder}</span>
                </div>
                <div class="song-info">
                    <h4>${song.title}</h4>
                    <p class="song-artist">Artist: ${song.artist}</p>
                    <div class="song-meta">
                        <div class="vote-count">
                            <span id="voteCount-${song.id}">${song.vote_count || 0}</span>
                            <div class="heart-toggle ${isVoted ? 'voted' : ''}" 
                                 data-action="vote" 
                                 data-song-id="${song.id}"
                                 title="${isVoted ? 'Remove vote' : 'Vote for this song'}">
                            </div>
                        </div>
                        <div class="performers" id="performers-${song.id}">
                            ${isPerforming ? `<span class="performer-tag">You (${this.userPerformanceRegistrations[song.id].instrument})</span>` : ''}
                        </div>
                    </div>
                </div>
                <div class="song-actions">
                    <button class="btn ${isPerforming ? 'btn-warning' : 'btn-info'} ${this.attendee ? '' : 'hidden'}" 
                            data-action="perform" 
                            data-song-id="${song.id}">
                        ${isPerforming ? 'Unregister' : 'Perform'}
                    </button>
                    <button class="btn btn-secondary" 
                            data-action="chord-sheet" 
                            data-song-id="${song.id}">
                        Chord Sheet
                    </button>
                </div>
            `;
            songListElement.appendChild(listItem);
        });

        this.addSongActionListeners(songListElement);
    }

    /**
     * Sort songs based on current criteria and direction
     */
    sortSongs(songs) {
        return [...songs].sort((a, b) => {
            let comparison = 0;
            
            switch (this.sortCriteria) {
                case 'name':
                    comparison = a.song.title.localeCompare(b.song.title);
                    break;
                case 'artist':
                    comparison = a.song.artist.localeCompare(b.song.artist);
                    break;
                case 'votes':
                    comparison = (a.song.vote_count || 0) - (b.song.vote_count || 0);
                    break;
                case 'performance':
                    // Performance order: vote count desc, then song name asc
                    const voteComparison = (b.song.vote_count || 0) - (a.song.vote_count || 0);
                    if (voteComparison !== 0) {
                        comparison = voteComparison;
                    } else {
                        comparison = a.song.title.localeCompare(b.song.title);
                    }
                    break;
                default:
                    comparison = (a.song.vote_count || 0) - (b.song.vote_count || 0);
            }
            
            // Apply direction
            return this.sortDirection === 'desc' ? -comparison : comparison;
        });
    }

    /**
     * Calculate performance order for songs (vote count desc, then song name asc)
     */
    calculatePerformanceOrder(songs) {
        // Sort by performance order criteria: vote count desc, then song name asc
        const performanceOrderedSongs = [...songs].sort((a, b) => {
            // First by vote count (descending)
            const voteComparison = (b.song.vote_count || 0) - (a.song.vote_count || 0);
            if (voteComparison !== 0) {
                return voteComparison;
            }
            // Then by song name (ascending)
            return a.song.title.localeCompare(b.song.title);
        });

        // Add order numbers
        performanceOrderedSongs.forEach((jamSong, index) => {
            jamSong.performanceOrder = index + 1;
        });

        return performanceOrderedSongs;
    }

    /**
     * Add event listeners to song action buttons
     */
    addSongActionListeners(container) {
        container.querySelectorAll('[data-action="vote"]').forEach(element => {
            element.addEventListener('click', (event) => this.handleVote(event.target.dataset.songId));
        });
        
        container.querySelectorAll('button[data-action="perform"]').forEach(button => {
            button.addEventListener('click', (event) => this.showPerformModal(event.target.dataset.songId));
        });
        
        container.querySelectorAll('button[data-action="chord-sheet"]').forEach(button => {
            button.addEventListener('click', (event) => this.handleChordSheet(event.target.dataset.songId));
        });
    }

    /**
     * Handle vote action
     */
    async handleVote(songId) {
        // Toggle visual state immediately
        const heartElement = document.querySelector(`[data-song-id="${songId}"][data-action="vote"]`);
        if (heartElement) {
            heartElement.classList.toggle('voted');
        }

        // Update local vote state
        this.userVotes[songId] = !this.userVotes[songId];

        // Get current attendee from the attendee module
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!currentAttendee || !currentAttendee.id) {
            this.showMessage('Please register to vote.', 'info');
            // Revert local state
            this.userVotes[songId] = !this.userVotes[songId];
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            // Revert local state
            this.userVotes[songId] = !this.userVotes[songId];
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    song_id: songId, 
                    attendee_id: currentAttendee.id 
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to cast vote');
            }

            const result = await response.json();
            this.showMessage(result.message, 'success');
            
            // Reload jam data to update votes
            if (this.jamCore) {
                await this.jamCore.loadJamData();
            }
            
        } catch (error) {
            console.error('Error voting:', error);
            this.showMessage(error.message || 'An error occurred while voting.', 'error');
            
            // Revert visual state and local state on error
            if (heartElement) {
                heartElement.classList.toggle('voted');
            }
            this.userVotes[songId] = !this.userVotes[songId];
        }
    }

    /**
     * Check if user has voted on a song
     */
    isVoted(songId) {
        return this.userVotes[songId] || false;
    }

    /**
     * Load user's votes
     */
    async loadUserVotes() {
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!currentAttendee || !currentAttendee.id || !this.jamCore || !this.jamCore.getJamId()) {
            this.userVotes = {};
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/votes?attendee_id=${currentAttendee.id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const votes = await response.json();
            this.userVotes = votes.reduce((acc, vote) => {
                acc[vote.song_id] = true;
                return acc;
            }, {});
            
            // Re-render to update heart states
            this.displaySongs();
            
        } catch (error) {
            console.error('Error loading user votes:', error);
            this.userVotes = {};
        }
    }

    /**
     * Show performance registration modal
     */
    showPerformModal(songId) {
        if (!this.attendee) {
            this.showMessage('Please register to perform.', 'info');
            return;
        }

        // Check if already performing - if so, unregister directly
        if (this.userPerformanceRegistrations[songId]) {
            this.unregisterFromPerformance(songId);
            return;
        }

        // Check performance limit for new registrations
        const currentPerformances = Object.keys(this.userPerformanceRegistrations).length;
        if (currentPerformances >= this.performanceLimit) {
            this.showMessage(`You can only register to perform on ${this.performanceLimit} songs.`, 'error');
            return;
        }

        this.currentSongForPerform = songId;
        const modal = document.getElementById('performModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    /**
     * Close performance registration modal
     */
    closePerformModal() {
        const modal = document.getElementById('performModal');
        if (modal) {
            modal.classList.add('hidden');
        }
        
        const instrumentInput = document.getElementById('instrumentInput');
        if (instrumentInput) {
            instrumentInput.value = '';
        }
    }

    /**
     * Unregister from performance
     */
    async unregisterFromPerformance(songId) {
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!currentAttendee || !currentAttendee.id) {
            this.showMessage('Error: Please register to perform or missing attendee info.', 'error');
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/perform`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_id: songId,
                    attendee_id: currentAttendee.id
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to unregister from performance');
            }

            const result = await response.json();
            this.showMessage(result.message, 'success');
            
            // Reload jam data to update performance registrations
            if (this.jamCore) {
                await this.jamCore.loadJamData();
            }

        } catch (error) {
            console.error('Error unregistering from performance:', error);
            this.showMessage(error.message || 'An error occurred while unregistering from performance.', 'error');
        }
    }

    /**
     * Confirm performance registration
     */
    async confirmPerformRegistration() {
        const songId = this.currentSongForPerform;
        const instrumentInput = document.getElementById('instrumentInput');
        const instrument = instrumentInput ? instrumentInput.value.trim() : '';

        // Get current attendee from the attendee module
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!songId || !currentAttendee || !currentAttendee.id) {
            this.showMessage('Error: Please register to perform or missing song info.', 'error');
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/perform`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    song_id: songId,
                    attendee_id: currentAttendee.id,
                    instrument: instrument || 'Unknown'
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to register to perform');
            }

            this.showMessage('Registered to perform!', 'success');
            this.closePerformModal();
            this.loadUserPerformanceRegistrations();
            this.displaySongs(); // Re-render to update perform buttons
            
        } catch (error) {
            console.error('Error registering to perform:', error);
            this.showMessage(error.message || 'An error occurred during performance registration.', 'error');
        }
    }

    /**
     * Load user's performance registrations
     */
    async loadUserPerformanceRegistrations() {
        // Get current attendee from the attendee module
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!currentAttendee || !currentAttendee.id || !this.jamCore || !this.jamCore.getJamId()) {
            this.userPerformanceRegistrations = {};
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/performers?attendee_id=${currentAttendee.id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const registrations = await response.json();
            this.userPerformanceRegistrations = registrations.reduce((acc, reg) => {
                acc[reg.song_id] = reg;
                return acc;
            }, {});
            
            this.displaySongs(); // Re-render to update perform buttons
            
        } catch (error) {
            console.error('Error loading user performance registrations:', error);
            this.showMessage('Failed to load your performance registrations.', 'error');
        }
    }

    /**
     * Handle chord sheet action
     */
    handleChordSheet(songId) {
        const jamSong = this.jamSongs.find(js => js.song.id === songId);
        if (!jamSong || !jamSong.song.chord_sheet_url) {
            this.showMessage('No chord sheet available for this song.', 'info');
            return;
        }
        
        window.open(jamSong.song.chord_sheet_url, '_blank');
    }

    /**
     * Show add song modal
     */
    async showAddSongModal() {
        if (!this.attendee) {
            this.showMessage('Please register to add songs.', 'info');
            return;
        }
        
        // Ensure songs are loaded before populating the modal
        if (!this.songs || this.songs.length === 0) {
            await this.loadAllSongs();
        }
        
        this.populateAddSongModal();
        const modal = document.getElementById('addSongModal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }

    /**
     * Close add song modal
     */
    closeAddSongModal() {
        const modal = document.getElementById('addSongModal');
        if (modal) {
            modal.classList.add('hidden');
        }
    }

    /**
     * Populate add song modal with available songs
     */
    populateAddSongModal() {
        const selectElement = document.getElementById('songSelect');
        if (!selectElement) return;

        selectElement.innerHTML = ''; // Clear existing options

        const jamSongIds = new Set(this.jamSongs.map(js => js.song.id));
        console.log('Debug - Jam song IDs:', Array.from(jamSongIds));
        console.log('Debug - All song IDs:', this.songs.map(s => s.id));
        const availableSongs = this.songs.filter(song => !jamSongIds.has(song.id));
        console.log('Debug - Available song IDs:', availableSongs.map(s => s.id));

        if (availableSongs.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No more songs to add';
            option.disabled = true;
            selectElement.appendChild(option);
            // Disable the Add Song button in the modal
            const addSongButton = document.querySelector('#addSongModal .btn-primary');
            if (addSongButton) {
                addSongButton.disabled = true;
            }
            return;
        }

        // Enable the Add Song button in the modal
        const addSongButton = document.querySelector('#addSongModal .btn-primary');
        if (addSongButton) {
            addSongButton.disabled = false;
        }

        availableSongs.forEach(song => {
            const option = document.createElement('option');
            option.value = song.id;
            option.textContent = `${song.title} - ${song.artist}`;
            selectElement.appendChild(option);
        });
    }

    /**
     * Add song to jam
     */
    async addSongToJam() {
        const selectElement = document.getElementById('songSelect');
        const songId = selectElement ? selectElement.value : '';

        if (!songId) {
            this.showMessage('Please select a song.', 'error');
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/songs`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song_id: songId })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to add song');
            }

            this.showMessage('Song added successfully!', 'success');
            this.closeAddSongModal();
            
            // Reload jam data to update song list
            console.log('Reloading jam data after adding song...');
            if (this.jamCore) {
                await this.jamCore.loadJamData();
            }
            
        } catch (error) {
            console.error('Error adding song:', error);
            this.showMessage(error.message || 'An error occurred while adding the song.', 'error');
        }
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
window.JamSongs = JamSongs;





