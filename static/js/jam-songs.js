/**
 * Jam Songs Management
 * Handles song display, voting, and performance registration
 */


class JamSongs {
    constructor() {
        this.songs = []; // All available songs
        this.jamSongs = []; // Songs in the current jam
        this.userPerformanceRegistrations = {}; // Track user's performance registrations
        this.userVotes = {}; // Track user's votes
        this.allPerformers = {}; // song_id -> array of performer objects
        this.chordSheetStatus = {}; // Track chord sheet availability for each song
        this.performanceLimit = 3; // Default limit
        this.jamCore = null;
        this.attendee = null;
        this.votingInProgress = new Set(); // Track songs currently being voted on
        
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

        // Chord sheet modal event listeners
        const searchChordSheetsBtn = document.getElementById('searchChordSheetsBtn');
        const validateUrlBtn = document.getElementById('validateUrlBtn');

        if (searchChordSheetsBtn) {
            searchChordSheetsBtn.addEventListener('click', () => this.searchChordSheets());
        }

        if (validateUrlBtn) {
            validateUrlBtn.addEventListener('click', () => this.validateUrl());
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
        this.loadAllPerformers(); // Load all performers for all songs
        this.loadChordSheetStatus(); // Load chord sheet status for all songs
    }

    /**
     * Called when attendee is registered
     */
    onAttendeeRegistered(attendee) {
        // Don't overwrite this.attendee - it should remain the attendee module
        // The attendee object is passed as a parameter for reference
        this.loadUserPerformanceRegistrations();
        this.loadUserVotes(); // Load user's votes
        this.loadAllPerformers(); // Load all performers
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
        this.allPerformers = {}; // Clear all performers data
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
                const chordSheetStatus = this.chordSheetStatus[song.id] || { hasChordSheet: false, url: null, isValid: false };
                
                // Only show chord sheet status for registered users (bosses and musos)
                const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
                const showChordSheetStatus = currentAttendee !== null;
                
                const chordSheetIcon = showChordSheetStatus ? this.getChordSheetIcon(chordSheetStatus) : '';
                const isClickable = showChordSheetStatus && chordSheetStatus.hasChordSheet && chordSheetStatus.isValid;

            listItem.innerHTML = `
                <div class="song-order">
                    <span class="order-number">${performanceOrder}</span>
                </div>
                <div class="song-info ${isClickable ? 'clickable' : ''}" 
                     ${isClickable ? `data-chord-sheet-url="${chordSheetStatus.url}"` : ''}
                     title="${isClickable ? 'Click to open chord sheet' : (chordSheetStatus.url && !chordSheetStatus.isValid ? 'Chord sheet URL is broken' : 'No chord sheet available')}">
                    <h4>${song.title} ${chordSheetIcon}</h4>
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
                            ${this.generatePerformersHTML(song.id)}
                        </div>
                    </div>
                </div>
                <div class="song-actions">
                    <button class="btn ${isPerforming ? 'btn-warning' : 'btn-info'} ${this.attendee && this.attendee.getCurrentAttendee() ? '' : 'hidden'}" 
                            data-action="perform" 
                            data-song-id="${song.id}">
                        ${isPerforming ? 'Unregister' : 'Perform'}
                    </button>
                    <button class="btn btn-secondary ${this.attendee && this.attendee.getCurrentAttendee() ? '' : 'hidden'}" 
                            data-action="chord-sheet" 
                            data-song-id="${song.id}"
                            title="Edit chord sheet for this song">
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
        
        // Add chord sheet click handler for clickable song-info areas
        container.querySelectorAll('.song-info.clickable').forEach(element => {
            element.addEventListener('click', (event) => {
                // Don't trigger if clicking on action buttons or heart
                if (event.target.closest('button') || event.target.closest('.heart-toggle')) {
                    return;
                }
                const url = element.dataset.chordSheetUrl;
                if (url) {
                    window.open(url, '_blank');
                }
            });
        });
    }

    /**
     * Handle vote action
     */
    async handleVote(songId) {
        // Prevent rapid successive clicks on the same song
        if (this.votingInProgress.has(songId)) {
            return;
        }
        
        // Get heart element for later use
        const heartElement = document.querySelector(`[data-song-id="${songId}"][data-action="vote"]`);
        
        // Get current attendee from the attendee module
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        if (!currentAttendee || !currentAttendee.id) {
            this.showMessage('Please register to vote.', 'info');
            return;
        }

        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.showMessage('Jam not loaded yet. Please try again.', 'error');
            return;
        }

        // Mark this song as having a vote in progress
        this.votingInProgress.add(songId);

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
            // Vote notification removed - heart visual state is sufficient feedback
            
            // Use the API response to determine the new vote state
            const newVoteState = result.voted; // true if voted, false if not voted
            
            // Update local vote state
            this.userVotes[songId] = newVoteState;
            
            // Update heart visual state based on API response
            if (heartElement) {
                if (newVoteState) {
                    heartElement.classList.add('voted');
                } else {
                    heartElement.classList.remove('voted');
                }
            }
            
            // Update vote counts without reloading the entire jam data
            // This preserves the local vote state while updating the counts
            this.updateVoteCounts();
            
        } catch (error) {
            console.error('Error voting:', error);
            this.showMessage(error.message || 'An error occurred while voting.', 'error');
        } finally {
            // Remove from voting in progress set
            this.votingInProgress.delete(songId);
        }
    }

    /**
     * Check if user has voted on a song
     */
    isVoted(songId) {
        return this.userVotes[songId] || false;
    }

    /**
     * Update vote counts without reloading entire jam data
     * This preserves local vote state while updating counts
     */
    async updateVoteCounts() {
        if (!this.jamCore || !this.jamCore.getJamId()) {
            return;
        }

        try {
            // Get fresh jam data to update vote counts
            const response = await fetch(`/api/jams/by-slug/${this.jamCore.jamSlug}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const jamData = await response.json();
            
            // Update vote counts for each song without affecting local vote state
            jamData.songs.forEach(jamSong => {
                const songId = jamSong.song.id;
                const voteCountElement = document.getElementById(`voteCount-${songId}`);
                if (voteCountElement) {
                    voteCountElement.textContent = jamSong.song.vote_count || 0;
                }
            });
            
        } catch (error) {
            console.error('Error updating vote counts:', error);
        }
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
            this.loadAllPerformers(); // Reload all performers
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
     * Get chord sheet icon based on status
     */
    getChordSheetIcon(status) {
        
        if (status.hasChordSheet && status.isValid) {
            return '<span class="chord-sheet-icon available" title="Chord sheet available">✓</span>';
        } else if (status.url && !status.isValid) {
            return '<span class="chord-sheet-icon broken" title="Chord sheet URL is broken or inaccessible">⚠</span>';
        } else {
            return '<span class="chord-sheet-icon unavailable" title="No chord sheet available">⚠</span>';
        }
    }

    /**
     * Load chord sheet status for all songs in the jam
     */
    async loadChordSheetStatus() {
        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.chordSheetStatus = {};
            return;
        }

        try {
            // Process songs sequentially to avoid Safari issues with Promise.all
            for (const jamSong of this.jamSongs) {
                const songId = jamSong.song.id;
                try {
                    
                    const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/chord-sheets/${songId}`);
                    if (response.ok) {
                        const chordSheet = await response.json();
                        // Check if we have a jam-specific chord sheet or a valid default one
                        if (chordSheet && chordSheet.chord_sheet_url) {
                            // Use database validation result if available, otherwise validate
                            let isValid = chordSheet.chord_sheet_is_valid;
                            if (isValid === null || isValid === undefined) {
                                isValid = await this.validateChordSheetUrl(chordSheet.chord_sheet_url, songId);
                            }
                            this.chordSheetStatus[songId] = {
                                hasChordSheet: isValid,
                                url: chordSheet.chord_sheet_url,
                                isJamSpecific: true,
                                isValid: isValid
                            };
                        } else if (jamSong.song.chord_sheet_url) {
                            // Fall back to default song chord sheet
                            let isValid = jamSong.song.chord_sheet_is_valid;
                            if (isValid === null || isValid === undefined) {
                                isValid = await this.validateChordSheetUrl(jamSong.song.chord_sheet_url, songId);
                            }
                            this.chordSheetStatus[songId] = {
                                hasChordSheet: isValid,
                                url: jamSong.song.chord_sheet_url,
                                isJamSpecific: false,
                                isValid: isValid
                            };
                        } else {
                            this.chordSheetStatus[songId] = {
                                hasChordSheet: false,
                                url: null,
                                isJamSpecific: false,
                                isValid: false
                            };
                        }
                    } else {
                        // No jam-specific chord sheet, check default
                        if (jamSong.song.chord_sheet_url) {
                            let isValid = jamSong.song.chord_sheet_is_valid;
                            if (isValid === null || isValid === undefined) {
                                isValid = await this.validateChordSheetUrl(jamSong.song.chord_sheet_url, songId);
                            }
                            this.chordSheetStatus[songId] = {
                                hasChordSheet: isValid,
                                url: jamSong.song.chord_sheet_url,
                                isJamSpecific: false,
                                isValid: isValid
                            };
                        } else {
                            this.chordSheetStatus[songId] = {
                                hasChordSheet: false,
                                url: null,
                                isJamSpecific: false,
                                isValid: false
                            };
                        }
                    }
                } catch (error) {
                    console.error(`🔍 Error loading chord sheet status for song ${songId}:`, error);
                    this.chordSheetStatus[songId] = {
                        hasChordSheet: false,
                        url: null,
                        isJamSpecific: false,
                        isValid: false
                    };
                }
            }
            
            // Force a display update after loading status
            setTimeout(() => {
                this.displaySongs();
            }, 100);
            
        } catch (error) {
            console.error('🔍 Error loading chord sheet status:', error);
        }
    }

    /**
     * Validate if a chord sheet URL is accessible (using database validation results)
     */
    async validateChordSheetUrl(url, songId = null) {
        if (!url) {
            return false;
        }
        
        try {
            const jamId = this.jamCore.getJamId();
            
            const requestBody = { url: url };
            if (songId) {
                requestBody.song_id = songId;
            }
            
            const response = await fetch(`/api/jams/${jamId}/chord-sheets/validate-url`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
            
            if (response.ok) {
                const result = await response.json();
                const isValid = result.valid === true;
                return isValid;
            } else {
                return false;
            }
        } catch (error) {
            console.error('🔍 Error validating chord sheet URL:', error);
            return false;
        }
    }

    /**
     * Load all performers for all songs in the jam
     */
    async loadAllPerformers() {
        if (!this.jamCore || !this.jamCore.getJamId()) {
            this.allPerformers = {};
            return;
        }

        try {
            // Load performers for each song in the jam
            const promises = this.jamSongs.map(async (jamSong) => {
                const songId = jamSong.song.id;
                try {
                    const response = await fetch(`/api/jams/${this.jamCore.getJamId()}/songs/${songId}/performers`);
                    if (response.ok) {
                        const performers = await response.json();
                        this.allPerformers[songId] = performers;
                    } else {
                        this.allPerformers[songId] = [];
                    }
                } catch (error) {
                    console.error(`Error loading performers for song ${songId}:`, error);
                    this.allPerformers[songId] = [];
                }
            });

            await Promise.all(promises);
            
        } catch (error) {
            console.error('Error loading all performers:', error);
        }
    }

    /**
     * Generate HTML for performers display
     */
    generatePerformersHTML(songId) {
        const performers = this.allPerformers[songId] || [];
        const currentAttendee = this.attendee ? this.attendee.getCurrentAttendee() : null;
        
        if (performers.length === 0) {
            return '';
        }
        
        return performers.map(performer => {
            const isCurrentUser = currentAttendee && currentAttendee.id === performer.attendee_id;
            const displayName = isCurrentUser ? 'You' : performer.name;
            return `<span class="performer-tag">${displayName} (${performer.instrument})</span>`;
        }).join(' ');
    }

    /**
     * Handle chord sheet action
     */
    handleChordSheet(songId) {
        // Show chord sheet editor modal instead of directly opening
        this.showChordSheetModal(songId);
    }

    /**
     * Show chord sheet editor modal
     */
    async showChordSheetModal(songId) {
        const jamSong = this.jamSongs.find(js => js.song.id === songId);
        if (!jamSong) {
            this.showMessage('Song not found.', 'error');
            return;
        }
        
        // Set current song for chord sheet editing
        this.currentChordSheetSongId = songId;
        
        // Load current chord sheet (jam-specific or default)
        await this.loadCurrentChordSheet(songId);
        
        // Show modal
        document.getElementById('chordSheetModal').classList.remove('hidden');
    }

    /**
     * Load current chord sheet for a song
     */
    async loadCurrentChordSheet(songId) {
        try {
            const jamId = this.jamCore.getJamId();
            const response = await fetch(`/api/jams/${jamId}/chord-sheets/${songId}`);
            
            if (response.ok) {
                const chordSheet = await response.json();
                if (chordSheet && chordSheet.chord_sheet_url) {
                    document.getElementById('chordSheetUrlInput').value = chordSheet.chord_sheet_url;
                } else {
                    document.getElementById('chordSheetUrlInput').value = '';
                }
            } else {
                console.error('Failed to load chord sheet:', response.statusText);
            }
        } catch (error) {
            console.error('Error loading chord sheet:', error);
        }
    }

    /**
     * Close chord sheet modal
     */
    closeChordSheetModal() {
        const urlInput = document.getElementById('chordSheetUrlInput');
        document.getElementById('chordSheetModal').classList.add('hidden');
        this.currentChordSheetSongId = null;
        this.clearChordSheetForm();
    }

    /**
     * Clear chord sheet form
     */
    clearChordSheetForm() {
        document.getElementById('chordSheetUrlInput').value = '';
        document.getElementById('urlValidationResult').classList.add('hidden');
        document.getElementById('chordSheetSearchResults').classList.add('hidden');
    }

    /**
     * Save chord sheet
     */
    async saveChordSheet() {
        const url = document.getElementById('chordSheetUrlInput').value.trim();
        
        if (!url) {
            this.showMessage('Please enter a chord sheet URL.', 'error');
            return;
        }

        try {
            const jamId = this.jamCore.getJamId();
            const songId = this.currentChordSheetSongId;
            
            const response = await fetch(`/api/jams/${jamId}/chord-sheets`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    song_id: songId,
                    chord_sheet_url: url
                })
            });

            if (response.ok) {
                this.showMessage('Chord sheet saved successfully!', 'success');
                this.closeChordSheetModal();
                // Validate the URL and save to database
                const isValid = await this.validateChordSheetUrl(url, songId);
                this.chordSheetStatus[songId] = {
                    hasChordSheet: isValid,
                    url: url,
                    isJamSpecific: true,
                    isValid: isValid
                };
                // Refresh the song display to show updated chord sheet
                this.displaySongs();
            } else {
                const error = await response.json();
                this.showMessage(`Failed to save chord sheet: ${error.detail}`, 'error');
            }
        } catch (error) {
            console.error('Error saving chord sheet:', error);
            this.showMessage('Failed to save chord sheet.', 'error');
        }
    }


    /**
     * Search for chord sheets using Ultimate Guitar
     */
    async searchChordSheets() {
        const jamSong = this.jamSongs.find(js => js.song.id === this.currentChordSheetSongId);
        if (!jamSong) {
            this.showMessage('Song not found.', 'error');
            return;
        }

        const searchBtn = document.getElementById('searchChordSheetsBtn');
        const btnText = document.getElementById('searchChordSheetsBtnText');
        const spinner = document.getElementById('searchChordSheetsSpinner');
        const resultsDiv = document.getElementById('chordSheetSearchResults');
        const messageDiv = document.getElementById('chordSheetSearchMessage');
        const linksDiv = document.getElementById('chordSheetSearchLinks');

        // Show loading state
        searchBtn.disabled = true;
        btnText.textContent = 'Searching...';
        spinner.classList.remove('hidden');
        resultsDiv.classList.remove('hidden');
        messageDiv.textContent = 'Searching Ultimate Guitar...';

        try {
            const jamId = this.jamCore.getJamId();
            const response = await fetch(`/api/jams/${jamId}/chord-sheets/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    song_title: jamSong.song.title,
                    artist_name: jamSong.song.artist
                })
            });

            if (response.ok) {
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    messageDiv.textContent = `Found ${data.total_found} chord sheets, showing top ${data.results.length}:`;
                    
                    linksDiv.innerHTML = data.results.map((result, index) => `
                        <div class="chord-sheet-option" data-url="${result.url}" data-title="${result.title}" data-rating="${result.rating}">
                            <div class="chord-sheet-info">
                                <div class="chord-sheet-title">${result.title}</div>
                                <div class="chord-sheet-rating">Rating: ${result.rating} (${result.votes} votes)</div>
                            </div>
                            <div class="chord-sheet-actions">
                                <button class="btn-outline select-chord-sheet-btn" data-url="${result.url}">Select</button>
                                <button class="btn-outline preview-chord-sheet-btn" data-url="${result.url}">Preview</button>
                            </div>
                        </div>
                    `).join('');

                    // Add event listeners for the new buttons
                    linksDiv.querySelectorAll('.select-chord-sheet-btn').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const url = e.target.getAttribute('data-url');
                            this.selectChordSheet(url);
                        });
                    });

                    linksDiv.querySelectorAll('.preview-chord-sheet-btn').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const url = e.target.getAttribute('data-url');
                            window.open(url, '_blank');
                        });
                    });
                } else {
                    messageDiv.textContent = 'No chord sheets found for this song.';
                    linksDiv.innerHTML = '';
                }
            } else {
                const error = await response.json();
                messageDiv.textContent = `Search failed: ${error.detail}`;
                linksDiv.innerHTML = '';
            }
        } catch (error) {
            console.error('Error searching chord sheets:', error);
            messageDiv.textContent = 'Search failed. Please try again.';
            linksDiv.innerHTML = '';
        } finally {
            // Reset button state
            searchBtn.disabled = false;
            btnText.textContent = 'Search Ultimate Guitar';
            spinner.classList.add('hidden');
        }
    }

    /**
     * Select a chord sheet from search results
     */
    async selectChordSheet(url) {
        document.getElementById('chordSheetUrlInput').value = url;
        
        // Update visual selection
        document.querySelectorAll('.chord-sheet-option').forEach(option => {
            option.classList.remove('selected');
        });
        
        const selectedOption = document.querySelector(`[data-url="${url}"]`);
        if (selectedOption) {
            selectedOption.classList.add('selected');
        }
        
        // Pre-validate the selected URL and save to database
        await this.validateChordSheetUrl(url, this.currentChordSheetSongId);
    }

    /**
     * Validate chord sheet URL
     */
    async validateUrl() {
        const url = document.getElementById('chordSheetUrlInput').value.trim();
        const resultDiv = document.getElementById('urlValidationResult');
        
        
        if (!url) {
            resultDiv.classList.add('hidden');
            return;
        }

        resultDiv.classList.remove('hidden');
        resultDiv.textContent = 'Validating...';
        resultDiv.className = 'validation-result';

        try {
            // Use the validation method with song ID
            const isValid = await this.validateChordSheetUrl(url, this.currentChordSheetSongId);
            
            if (isValid) {
                resultDiv.textContent = '✓ URL is valid and accessible';
                resultDiv.className = 'validation-result success';
            } else {
                resultDiv.textContent = '✗ URL is not accessible or invalid';
                resultDiv.className = 'validation-result error';
            }
        } catch (error) {
            console.error('Error validating URL:', error);
            resultDiv.textContent = '✗ Validation failed';
            resultDiv.className = 'validation-result error';
        }
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
        const availableSongs = this.songs.filter(song => !jamSongIds.has(song.id));

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
            }
        }
    }
}

// Export for use in other modules
window.JamSongs = JamSongs;





