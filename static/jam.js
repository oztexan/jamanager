// Jam Page JavaScript
class JamPage {
    constructor() {
        this.jamSlug = this.getJamSlugFromUrl();
        this.jam = null;
        this.ws = null;
        this.currentAttendee = null;
        this.init();
    }

    getJamSlugFromUrl() {
        const path = window.location.pathname;
        const parts = path.split('/');
        return parts[parts.length - 1];
    }

    async init() {
        if (!this.jamSlug) {
            this.showError('Invalid jam URL');
            return;
        }

        // Initialize feature flags first
        if (window.featureFlags) {
            await window.featureFlags.initialize();
            window.featureFlags.applyFeatureGates();
        }

        await this.loadJam();
        this.setupWebSocket();
    }

    async loadJam() {
        try {
            const response = await fetch(`/api/jams/by-slug/${this.jamSlug}`);
            if (response.ok) {
                this.jam = await response.json();
                this.jamId = this.jam.id; // Set jamId for API calls
                console.log('Jam loaded, jamId set to:', this.jamId);
                this.displayJam();
                this.initializeBreadcrumbs();
                this.loadSongsForModal(); // Load songs for the add song modal
                
                // Restore attendee from localStorage if available (after jam is loaded)
                this.restoreAttendee();
            } else {
                this.showError('Jam not found');
            }
        } catch (error) {
            this.showError('Failed to load jam: ' + error.message);
        }
    }

    initializeBreadcrumbs() {
        // Initialize breadcrumbs for jam details page
        if (window.breadcrumbManager && this.jam) {
            const jamName = this.jam.name || 'Jam Session';
            window.breadcrumbManager.setBreadcrumbs(
                BreadcrumbManager.getJamDetailsBreadcrumbs(jamName, this.jamSlug)
            );
        }
    }

    setBackgroundImage(backgroundImage) {
        const backgroundLayer = document.getElementById('backgroundLayer');
        if (backgroundImage) {
            backgroundLayer.style.backgroundImage = `url('${backgroundImage}')`;
            backgroundLayer.style.display = 'block';
        } else {
            backgroundLayer.style.backgroundImage = '';
            backgroundLayer.style.display = 'none';
        }
    }


    displayJam() {
        if (!this.jam) return;

        // Update page title
        document.title = `${this.jam.name} - Jamanager`;
        
        // Set background image if available
        this.setBackgroundImage(this.jam.background_image);
        
        // Update header
        document.getElementById('jamTitle').textContent = this.jam.name;
        document.getElementById('jamDescription').textContent = this.jam.description || 'No description';
        
        // Update jam info
        document.getElementById('jamName').textContent = this.jam.name;
        document.getElementById('jamDesc').textContent = this.jam.description || 'No description';
        
        // Update status
        const statusElement = document.getElementById('jamStatus');
        statusElement.textContent = this.jam.status;
        statusElement.className = `jam-status status-${this.jam.status}`;
        
        // Display songs
        this.displaySongs();
        
        // Show content
        document.getElementById('loadingMessage').classList.add('hidden');
        document.getElementById('jamContent').classList.remove('hidden');
    }

    displaySongs() {
        const songList = document.getElementById('songList');
        songList.innerHTML = '';

        if (!this.jam.songs || this.jam.songs.length === 0) {
            songList.innerHTML = '<li class="song-item"><div class="song-info"><div class="song-title">No songs in queue</div><div class="song-artist">Add some songs to get started!</div></div></li>';
            return;
        }

        // Sort songs by vote count (descending)
        const sortedSongs = [...this.jam.songs].sort((a, b) => b.song.vote_count - a.song.vote_count);

           sortedSongs.forEach((jamSong, index) => {
               const li = document.createElement('li');
               li.className = `song-item ${jamSong.song.chord_sheet_url ? 'has-chord-sheet' : ''}`;
               if (jamSong.song.chord_sheet_url) {
                   li.onclick = () => window.open(jamSong.song.chord_sheet_url, '_blank');
               }
               li.innerHTML = `
                   <div class="song-header">
                       <div class="song-rank">#${index + 1}</div>
                       <div class="song-info">
                       <div class="song-title">
                           ${jamSong.song.title}
                           ${jamSong.song.chord_sheet_url ? '<span class="chord-sheet-indicator">🎸</span>' : ''}
                       </div>
                           <div class="song-artist">${jamSong.song.artist}</div>
                       </div>
                       <div class="song-actions" onclick="event.stopPropagation()">
                           <button class="heart-btn" onclick="toggleHeart('${jamSong.song.id}')" data-song-id="${jamSong.song.id}">
                               <span class="heart-icon">♡</span>
                               <span class="vote-count">${jamSong.song.vote_count}</span>
                           </button>
                           <button class="perform-btn" onclick="${this.currentAttendee ? `registerToPerform('${jamSong.song.id}')` : `registerAttendee()`}" data-song-id="${jamSong.song.id}">
                                   <span class="perform-icon">🎤</span>
                               </button>
                           <button class="chord-sheet-btn" data-song-id="${jamSong.song.id}" data-song-title="${jamSong.song.title}" data-song-artist="${jamSong.song.artist}">
                               <span class="chord-sheet-icon">🎸</span>
                           </button>
                           ${hasPermission('can_play_songs') ? `
                               <button class="btn btn-success play-song-btn" onclick="playSong('${jamSong.song.id}')">Play</button>
                           ` : ''}
                       </div>
                   </div>
                   <div class="song-performers" id="performers-${jamSong.song.id}">
                       <!-- Performers will be loaded here -->
                   </div>
               `;
            songList.appendChild(li);
            
            // Add event listener for chord sheet button
            const chordSheetBtn = li.querySelector('.chord-sheet-btn');
            if (chordSheetBtn) {
                chordSheetBtn.addEventListener('click', () => {
                    const songId = chordSheetBtn.getAttribute('data-song-id');
                    const songTitle = chordSheetBtn.getAttribute('data-song-title');
                    const songArtist = chordSheetBtn.getAttribute('data-song-artist');
                    this.showChordSheetModal(songId, songTitle, songArtist);
                });
            }
            
            // Load performers for this song
            this.loadSongPerformers(jamSong.song.id);
            
            // Check vote status for this song
            this.checkVoteStatus(jamSong.song.id);
            
            // Check perform status for this song
            this.checkPerformStatus(jamSong.song.id);
        });
    }



    async registerAttendee() {
        const name = document.getElementById('attendeeName').value.trim();
        
        if (!name) {
            this.showError('Please enter your name');
            return;
        }

        // Prevent double-clicking by disabling the button
        const registerBtn = document.querySelector('button[onclick="registerAttendee()"]');
        if (registerBtn) {
            registerBtn.disabled = true;
            registerBtn.textContent = 'Registering...';
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/attendees`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    session_id: this.getSessionId()
                })
            });

            if (response.ok) {
                this.currentAttendee = await response.json();
                // Store attendee info in localStorage for persistence
                localStorage.setItem(`attendee_${this.jam.id}`, JSON.stringify(this.currentAttendee));
                // Also store the attendee ID for feature flags
                localStorage.setItem('jam_attendee_id', this.currentAttendee.id);
                // Re-initialize feature flags to update permissions
                if (window.featureFlags) {
                    await window.featureFlags.initialize();
                }
                this.showSuccess(`Welcome ${name}! You're now registered as an attendee.`);
                this.updateAttendeeUI();
                // Update the song list to show proper Perform buttons
                this.displaySongs();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to register as attendee');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        } finally {
            // Re-enable the button
            const registerBtn = document.querySelector('button[onclick="registerAttendee()"]');
            if (registerBtn) {
                registerBtn.disabled = false;
                registerBtn.textContent = 'Join Jam';
            }
        }
    }

    updateAttendeeUI() {
        if (this.currentAttendee) {
            document.getElementById('attendeeRegistration').classList.add('hidden');
            document.getElementById('attendeeInfo').classList.remove('hidden');
            document.getElementById('attendeeDisplayName').textContent = this.currentAttendee.name;
        } else {
            document.getElementById('attendeeRegistration').classList.remove('hidden');
            document.getElementById('attendeeInfo').classList.add('hidden');
        }
    }

    restoreAttendee() {
        try {
            const storedAttendee = localStorage.getItem(`attendee_${this.jam.id}`);
            if (storedAttendee) {
                this.currentAttendee = JSON.parse(storedAttendee);
                // Validate that the attendee object has required properties
                if (this.currentAttendee && this.currentAttendee.id && this.currentAttendee.name) {
                    // Also store the attendee ID for feature flags
                    localStorage.setItem('jam_attendee_id', this.currentAttendee.id);
                    // Re-initialize feature flags to update permissions
                    if (window.featureFlags) {
                        window.featureFlags.initialize();
                    }
                    this.updateAttendeeUI();
                    // Update the song list to show proper Perform buttons
                    this.displaySongs();
                    console.log(`Restored attendee: ${this.currentAttendee.name}`);
                } else {
                    console.warn('Invalid attendee data in localStorage, clearing...');
                    this.currentAttendee = null;
                    localStorage.removeItem(`attendee_${this.jam.id}`);
                }
            }
        } catch (error) {
            console.error('Error restoring attendee:', error);
            // Clear invalid data
            this.currentAttendee = null;
            localStorage.removeItem(`attendee_${this.jam.id}`);
        }
    }

    clearAttendee() {
        this.currentAttendee = null;
        localStorage.removeItem(`attendee_${this.jam.id}`);
        // Also remove the attendee ID for feature flags
        localStorage.removeItem('jam_attendee_id');
        // Re-initialize feature flags to update permissions
        if (window.featureFlags) {
            window.featureFlags.initialize();
        }
        this.updateAttendeeUI();
        this.displaySongs();
    }


    async addSongToJam() {
        const songSelect = document.getElementById('songSelect');
        const songId = songSelect.value;
        
        if (!songId) {
            this.showError('Please select a song');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    song_id: songId
                })
            });

            if (response.ok) {
                this.showSuccess('Song added to jam!');
                songSelect.value = '';
                await this.loadJam(); // Reload jam data
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to add song');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    async voteForSong(songId) {
        if (!this.currentAttendee) {
            this.showError('Please register as an attendee first');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/vote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    attendee_id: this.currentAttendee.id
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showSuccess(`Vote recorded! Total votes: ${result.voteCount}`);
                await this.loadJam(); // Reload jam data
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to vote');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    async toggleHeart(songId) {
        if (!hasPermission('can_vote')) {
            this.showError('You do not have permission to vote');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/heart`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getApiHeaders()
                },
                body: JSON.stringify({
                    session_id: this.getSessionId()
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.updateHeartButton(songId, result.voteCount, result.action === 'added');
                this.updateSongVoteCount(songId, result.voteCount);
                // Re-sort songs to reflect new vote counts
                this.resortSongs();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to toggle heart');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    updateHeartButton(songId, voteCount, isHearted) {
        const heartBtn = document.querySelector(`[data-song-id="${songId}"]`);
        if (heartBtn) {
            const heartIcon = heartBtn.querySelector('.heart-icon');
            const voteCountSpan = heartBtn.querySelector('.vote-count');
            
            heartIcon.textContent = isHearted ? '♥' : '♡';
            heartIcon.style.color = isHearted ? '#e53e3e' : '#718096';
            voteCountSpan.textContent = voteCount;
        }
    }

    async checkVoteStatus(songId) {
        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/vote-status`, {
                headers: {
                    'X-Session-ID': this.getSessionId()
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                // Update heart button based on vote status
                const heartBtn = document.querySelector(`[data-song-id="${songId}"]`);
                if (heartBtn) {
                    const heartIcon = heartBtn.querySelector('.heart-icon');
                    heartIcon.textContent = data.hasVoted ? '♥' : '♡';
                    heartIcon.style.color = data.hasVoted ? '#e53e3e' : '#718096';
                }
            }
        } catch (error) {
            console.error('Failed to check vote status:', error);
        }
    }

    async checkPerformStatus(songId) {
        if (!this.currentAttendee || !this.currentAttendee.id) {
            return;
        }
        
        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/performers`, {
                headers: {
                    'X-Session-ID': this.getSessionId(),
                    'X-Attendee-ID': this.currentAttendee.id
                }
            });
            if (response.ok) {
                const data = await response.json();
                const isRegistered = data.some(performer => 
                    performer && 
                    performer.attendee_id === this.currentAttendee.id
                );
                this.updatePerformButton(songId, isRegistered);
                this.updateSongRowHighlight(songId, isRegistered);
            }
        } catch (error) {
            console.error('Failed to check perform status:', error);
        }
    }

    updatePerformButton(songId, isRegistered) {
        const performBtn = document.querySelector(`.perform-btn[data-song-id="${songId}"]`);
        if (performBtn) {
            const performIcon = performBtn.querySelector('.perform-icon');
            if (performIcon) {
                performIcon.textContent = isRegistered ? '🎤' : '🎤';
                performIcon.className = isRegistered ? 'perform-icon registered' : 'perform-icon';
            }
        }
    }

    updateSongRowHighlight(songId, isPerforming) {
        // Find the song item that contains this song ID
        const allSongItems = document.querySelectorAll('.song-item');
        for (let item of allSongItems) {
            const performBtn = item.querySelector(`.perform-btn[data-song-id="${songId}"]`);
            if (performBtn) {
                if (isPerforming) {
                    item.classList.add('performing');
                } else {
                    item.classList.remove('performing');
                }
                break;
            }
        }
    }

    async checkIfPerforming(songId) {
        if (!this.currentAttendee || !this.currentAttendee.id) {
            return false;
        }
        
        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/performers`, {
                headers: {
                    'X-Session-ID': this.getSessionId(),
                    'X-Attendee-ID': this.currentAttendee.id
                }
            });
            
            if (response.ok) {
                const performers = await response.json();
                const isPerforming = performers.some(p => 
                    p && 
                    p.attendee_id === this.currentAttendee.id
                );
                return isPerforming;
            }
        } catch (error) {
            console.error('Failed to check if performing:', error);
        }
        return false;
    }

    async unregisterFromPerform(songId) {
        if (!this.currentAttendee || !this.currentAttendee.id) {
            this.showError('Please register as an attendee first');
            return;
        }
        
        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/register`, {
                method: 'DELETE',
                headers: {
                    'X-Session-ID': this.getSessionId(),
                    'X-Attendee-ID': this.currentAttendee.id
                }
            });

            if (response.ok) {
                const result = await response.json();
                await this.loadSongPerformers(songId);
                this.updatePerformButton(songId, false);
                this.updateSongRowHighlight(songId, false);
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to unregister from performing');
            }
        } catch (error) {
            console.error('Error unregistering from perform:', error);
            this.showError('Failed to unregister from performing');
        }
    }

    updateSongVoteCount(songId, voteCount) {
        // Update the vote count in the jam data
        if (this.jam && this.jam.songs) {
            const jamSong = this.jam.songs.find(js => js.song.id === songId);
            if (jamSong) {
                jamSong.song.vote_count = voteCount;
            }
        }
    }

    resortSongs() {
        const songList = document.getElementById('songList');
        const songItems = Array.from(songList.children);
        
        // Sort by vote count (descending)
        songItems.sort((a, b) => {
            const aVotes = parseInt(a.querySelector('.vote-count').textContent) || 0;
            const bVotes = parseInt(b.querySelector('.vote-count').textContent) || 0;
            return bVotes - aVotes;
        });
        
        // Update rank numbers and reorder
        songItems.forEach((item, index) => {
            const rankElement = item.querySelector('.song-rank');
            if (rankElement) {
                rankElement.textContent = `#${index + 1}`;
            }
            songList.appendChild(item);
        });
    }

    getSessionId() {
        // Generate a simple session ID for anonymous voting
        let sessionId = localStorage.getItem('jam_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('jam_session_id', sessionId);
        }
        return sessionId;
    }

    getSongTitle(songId) {
        const song = this.jam.songs.find(js => js.song.id === songId);
        return song ? song.song.title : 'Unknown Song';
    }

    async registerToPerform(songId) {
        if (!hasPermission('can_register_to_perform')) {
            this.showError('You do not have permission to register to perform');
            return;
        }

        if (!this.currentAttendee) {
            this.showError('Please register as an attendee first');
            return;
        }

        // Check if user is already registered to perform on this song
        const isAlreadyPerforming = await this.checkIfPerforming(songId);
        
        if (isAlreadyPerforming) {
            // Show confirmation modal before unregistering
            this.showUnregisterConfirmModal(songId);
        } else {
            // Register to perform - show modal
            this.currentPerformSongId = songId;
            const modal = document.getElementById('performModal');
            modal.classList.remove('hidden');
            const instrumentInput = document.getElementById('instrumentInput');
            instrumentInput.focus();
        }
    }

    async confirmPerformRegistration() {
        const instrument = document.getElementById('instrumentInput').value.trim();
        const songId = this.currentPerformSongId;

        if (!songId) {
            this.showError('No song selected for performance');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.getSessionId(),
                    'X-Attendee-ID': this.currentAttendee.id
                },
                body: JSON.stringify({
                    attendee_id: this.currentAttendee.id,
                    instrument: instrument
                })
            });

            if (response.ok) {
                const result = await response.json();
                await this.loadSongPerformers(songId);
                this.updatePerformButton(songId, true);
                this.closePerformModal();
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to register for performance');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    closePerformModal() {
        const modal = document.getElementById('performModal');
        modal.classList.add('hidden');
        document.getElementById('instrumentInput').value = '';
        this.currentPerformSongId = null;
    }

    async loadSongPerformers(songId) {
        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/performers`);
            if (response.ok) {
                const performers = await response.json();
                this.displaySongPerformers(songId, performers);
            }
        } catch (error) {
            console.error('Failed to load performers:', error);
        }
    }

    displaySongPerformers(songId, performers) {
        const performersContainer = document.getElementById(`performers-${songId}`);
        if (!performersContainer) return;

        if (performers.length === 0) {
            performersContainer.innerHTML = '';
            performersContainer.style.display = 'none';
            return;
        }

        const performersList = performers.map(perf => 
            `<span class="performer-tag">${perf.attendee_name}${perf.instrument ? ` (${perf.instrument})` : ''}</span>`
        ).join(', ');

        performersContainer.innerHTML = `
            <div class="performers-list">
                <strong>Performers:</strong> ${performersList}
            </div>
        `;
        performersContainer.style.display = 'block';
    }

    async playSong(songId) {
        if (!hasPermission('can_play_songs')) {
            this.showError('You do not have permission to play songs');
            return;
        }

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/songs/${songId}/play`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...getApiHeaders()
                }
            });

            if (response.ok) {
                this.showSuccess('Song marked as played!');
                await this.loadJam(); // Reload jam data
            } else {
                const error = await response.json();
                this.showError(error.detail || 'Failed to mark song as played');
            }
        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    setupWebSocket() {
        if (!this.jam) return;

        const wsUrl = `ws://localhost:8000/ws/${this.jam.id}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to jam WebSocket');
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('WebSocket message:', data);
            
            if (data.event === 'song-voted') {
                this.showSuccess(`Song voted! New vote count: ${data.data.voteCount}`);
                this.loadJam(); // Reload jam data
            } else if (data.event === 'song-played') {
                this.showSuccess('Song marked as played!');
                this.loadJam(); // Reload jam data
            } else if (data.event === 'heart-toggled') {
                this.updateHeartButton(data.data.songId, data.data.voteCount, data.data.action === 'added');
                this.loadJam(); // Reload jam data to update ordering
            } else if (data.event === 'performance-registered') {
                this.loadSongPerformers(data.data.songId);
                // Update perform button and highlight if it's the current user
                if (this.currentAttendee && data.data.attendeeName) {
                    this.checkPerformStatus(data.data.songId);
                }
            } else if (data.event === 'performance-unregistered') {
                this.loadSongPerformers(data.data.songId);
                // Update perform button and highlight if it's the current user
                if (this.currentAttendee && data.data.attendeeName) {
                    this.checkPerformStatus(data.data.songId);
                }
            } else if (data.event === 'chord-sheet-updated') {
                // Update the song data in the local jam object
                if (this.jam && this.jam.songs) {
                    const songIndex = this.jam.songs.findIndex(js => js.song.id === data.data.songId);
                    if (songIndex !== -1) {
                        this.jam.songs[songIndex].song.chord_sheet_url = data.data.chordSheetUrl;
                        console.log('Updated song data via WebSocket:', this.jam.songs[songIndex].song);
                    }
                }
                // Refresh the song display
                this.displaySongs();
                this.showSuccess(`Chord sheet updated for "${data.data.songTitle}" by ${data.data.songArtist}`);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        container.appendChild(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }

    // Chord Sheet Modal Functions
    showChordSheetModal(songId, songTitle, songArtist) {
        this.currentChordSheetSongId = songId;
        this.currentChordSheetSongTitle = songTitle;
        this.currentChordSheetSongArtist = songArtist;

        // Populate modal with song info
        document.getElementById('chordSheetSongTitle').textContent = songTitle;
        document.getElementById('chordSheetSongArtist').textContent = songArtist;
        document.getElementById('chordSheetModalTitle').textContent = `Find Chord Sheet: ${songTitle}`;

        // Hide any previous results
        document.getElementById('chordSheetModalResults').classList.add('hidden');

        // Show the modal
        document.getElementById('chordSheetModal').classList.remove('hidden');
    }

     async findChordSheetForSong() {
         if (!this.currentChordSheetSongTitle || !this.currentChordSheetSongArtist) {
             this.showChordSheetModalMessage('Song information not available', 'error');
             return;
         }

         const btn = document.getElementById('findChordSheetModalBtn');
         const btnText = document.getElementById('chordSheetModalBtnText');
         const spinner = document.getElementById('chordSheetModalSpinner');
         const results = document.getElementById('chordSheetModalResults');
         const message = document.getElementById('chordSheetModalMessage');
         const links = document.getElementById('chordSheetModalLinks');
         const selected = document.getElementById('chordSheetModalSelected');

         // Show loading state
         btn.disabled = true;
         btnText.textContent = 'Searching...';
         spinner.classList.remove('hidden');
         results.classList.remove('hidden');
         selected.classList.add('hidden');
         message.textContent = 'Searching Ultimate Guitar for chord sheets...';
         links.innerHTML = '';

         try {
             const response = await fetch('/api/search-chord-sheets', {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify({
                     song_name: this.currentChordSheetSongTitle,
                     artist_name: this.currentChordSheetSongArtist
                 })
             });

             if (response.ok) {
                 const data = await response.json();
                 
                 if (data.chord_sheets && data.chord_sheets.length > 0) {
                     message.textContent = `Found ${data.chord_sheets.length} chord sheet(s) for "${this.currentChordSheetSongTitle}" by ${this.currentChordSheetSongArtist}`;
                     
                     // Sort by votes (highest to lowest) and show top 3 results
                     const sortedResults = data.chord_sheets.sort((a, b) => b.votes - a.votes);
                     const topResults = sortedResults.slice(0, 3);
                     topResults.forEach((sheet, index) => {
                         const linkDiv = document.createElement('div');
                         linkDiv.className = 'chord-sheet-link';
                         linkDiv.innerHTML = `
                             <div class="chord-sheet-info">
                                 <div class="chord-sheet-title">${sheet.title}</div>
                                 <div class="chord-sheet-rating">⭐ ${sheet.rating.toFixed(2)} (${sheet.votes} votes)</div>
                             </div>
                             <div class="chord-sheet-external">🔗</div>
                         `;
                         linkDiv.onclick = () => this.selectChordSheet(sheet.url, sheet.title);
                         links.appendChild(linkDiv);
                     });
                 } else {
                     message.textContent = `No chord sheets found for "${this.currentChordSheetSongTitle}" by ${this.currentChordSheetSongArtist}`;
                 }
             } else {
                 const error = await response.json();
                 message.textContent = `Error: ${error.detail || 'Failed to search for chord sheets'}`;
             }
         } catch (error) {
             message.textContent = `Network error: ${error.message}`;
         } finally {
             // Reset button state
             btn.disabled = false;
             btnText.textContent = 'Find Chord Sheet';
             spinner.classList.add('hidden');
         }
     }

    showChordSheetModalMessage(text, type = 'info') {
        const message = document.getElementById('chordSheetModalMessage');
        const results = document.getElementById('chordSheetModalResults');
        
        message.textContent = text;
        message.className = `chord-sheet-message ${type}`;
        results.classList.remove('hidden');
    }

     selectChordSheet(url, title) {
         this.selectedChordSheetUrl = url;
         this.selectedChordSheetTitle = title;
         
         // Show the selected chord sheet section
         const selected = document.getElementById('chordSheetModalSelected');
         const selectedUrl = document.getElementById('selectedChordSheetUrl');
         
         selectedUrl.textContent = title;
         selected.classList.remove('hidden');
         
         // Scroll to the selected section
         selected.scrollIntoView({ behavior: 'smooth' });
     }

     async saveChordSheetForSong() {
         if (!this.selectedChordSheetUrl || !this.currentChordSheetSongId) {
             this.showChordSheetModalMessage('No chord sheet selected', 'error');
             return;
         }

         const btn = document.getElementById('saveChordSheetBtn');
         const btnText = document.getElementById('saveChordSheetBtnText');
         const spinner = document.getElementById('saveChordSheetSpinner');

         // Show loading state
         btn.disabled = true;
         btnText.textContent = 'Saving...';
         spinner.classList.remove('hidden');

         try {
             const response = await fetch(`/api/jams/${this.jamId}/songs/${this.currentChordSheetSongId}/chord-sheet`, {
                 method: 'PUT',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify({
                     chord_sheet_url: this.selectedChordSheetUrl
                 })
             });

             if (response.ok) {
                 const data = await response.json();
                 
                 // Update the song data in the local jam object
                 if (this.jam && this.jam.songs) {
                     const songIndex = this.jam.songs.findIndex(js => js.song.id === this.currentChordSheetSongId);
                     if (songIndex !== -1) {
                         this.jam.songs[songIndex].song.chord_sheet_url = this.selectedChordSheetUrl;
                         console.log('Updated song data:', this.jam.songs[songIndex].song);
                     }
                 }
                 
                 // Refresh the song display
                 this.displaySongs();
                 
                 this.showChordSheetModalMessage('Chord sheet saved successfully!', 'success');
                 
                 // Close modal after a short delay
                 setTimeout(() => {
                     this.closeChordSheetModal();
                 }, 1500);
             } else {
                 const error = await response.json();
                 this.showChordSheetModalMessage(`Error: ${error.detail || 'Failed to save chord sheet'}`, 'error');
             }
         } catch (error) {
             this.showChordSheetModalMessage(`Network error: ${error.message}`, 'error');
         } finally {
             // Reset button state
             btn.disabled = false;
             btnText.textContent = 'Save Chord Sheet';
             spinner.classList.add('hidden');
         }
     }

     closeChordSheetModal() {
         document.getElementById('chordSheetModal').classList.add('hidden');
         this.currentChordSheetSongId = null;
         this.currentChordSheetSongTitle = null;
         this.currentChordSheetSongArtist = null;
         this.selectedChordSheetUrl = null;
         this.selectedChordSheetTitle = null;
         
         // Hide all sections
         document.getElementById('chordSheetModalResults').classList.add('hidden');
         document.getElementById('chordSheetModalSelected').classList.add('hidden');
     }

     showUnregisterConfirmModal(songId) {
         this.currentUnregisterSongId = songId;
         
         // Get song details
         const song = this.jam.songs.find(js => js.song.id === songId);
         if (song) {
             document.getElementById('unregisterSongTitle').textContent = song.song.title;
             document.getElementById('unregisterSongArtist').textContent = song.song.artist;
         }
         
         // Show the modal
         document.getElementById('unregisterConfirmModal').classList.remove('hidden');
     }

     closeUnregisterConfirmModal() {
         document.getElementById('unregisterConfirmModal').classList.add('hidden');
         this.currentUnregisterSongId = null;
     }

     async confirmUnregisterFromPerform() {
         if (!this.currentUnregisterSongId) {
             this.showError('No song selected for unregistering');
             return;
         }
         
         // Close the modal first
         this.closeUnregisterConfirmModal();
         
         // Perform the unregister
         await this.unregisterFromPerform(this.currentUnregisterSongId);
     }

     // Share Modal Functions
     showShareModal() {
         const modal = document.getElementById('shareModal');
         modal.classList.remove('hidden');
         
         // Generate QR code and set URL
         this.generateShareContent();
     }

     closeShareModal() {
         document.getElementById('shareModal').classList.add('hidden');
     }

     generateShareContent() {
         const jamUrl = `${window.location.origin}/jams/${this.jamSlug}`;
         const qrCodeImg = document.getElementById('shareQrCode');
         const qrLoading = document.getElementById('shareQrLoading');
         const urlInput = document.getElementById('shareJamUrl');
         
         // Set the URL
         urlInput.value = jamUrl;
         
         // Generate QR code
         qrLoading.style.display = 'block';
         qrCodeImg.style.display = 'none';
         
         // Use a simple QR code generation (you might want to use a proper QR library)
         const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(jamUrl)}`;
         qrCodeImg.src = qrCodeUrl;
         qrCodeImg.onload = () => {
             qrLoading.style.display = 'none';
             qrCodeImg.style.display = 'block';
         };
     }

     copyJamUrl() {
         const urlInput = document.getElementById('shareJamUrl');
         urlInput.select();
         urlInput.setSelectionRange(0, 99999); // For mobile devices
         
         try {
             document.execCommand('copy');
             this.showSuccess('URL copied to clipboard!');
         } catch (err) {
             // Fallback for modern browsers
             navigator.clipboard.writeText(urlInput.value).then(() => {
                 this.showSuccess('URL copied to clipboard!');
             }).catch(() => {
                 this.showError('Failed to copy URL');
             });
         }
     }

     // Add Song Modal Functions
     showAddSongModal() {
         const modal = document.getElementById('addSongModal');
         modal.classList.remove('hidden');
         
         // Load songs if not already loaded
         if (document.getElementById('modalSongSelect').options.length <= 1) {
             this.loadSongsForModal();
         }
     }

     closeAddSongModal() {
         document.getElementById('addSongModal').classList.add('hidden');
         // Reset selection
         document.getElementById('modalSongSelect').value = '';
     }

     async loadSongsForModal() {
         try {
             console.log('Loading songs for modal...');
             const response = await fetch('/api/songs');
             if (response.ok) {
                 const songs = await response.json();
                 console.log('Loaded songs:', songs.length);
                 this.populateModalSongSelect(songs);
             } else {
                 console.error('Failed to fetch songs:', response.status);
             }
         } catch (error) {
             console.error('Failed to load songs for modal:', error);
         }
     }

     populateModalSongSelect(songs) {
         const select = document.getElementById('modalSongSelect');
         
         // Clear existing options except the first one
         select.innerHTML = '<option value="">Choose a song...</option>';
         
         // Filter out songs already in the jam
         const jamSongIds = this.jam.songs ? this.jam.songs.map(js => js.song.id) : [];
         const availableSongs = songs.filter(song => !jamSongIds.includes(song.id));
         
         console.log(`Total songs: ${songs.length}, Already in jam: ${jamSongIds.length}, Available: ${availableSongs.length}`);
         
         if (availableSongs.length === 0) {
             const option = document.createElement('option');
             option.value = "";
             option.textContent = "No songs available (all songs already in jam)";
             option.disabled = true;
             select.appendChild(option);
         } else {
             availableSongs.forEach(song => {
                 const option = document.createElement('option');
                 option.value = song.id;
                 option.textContent = `${song.title} - ${song.artist}`;
                 select.appendChild(option);
             });
         }
     }

     async addSongToJamFromModal() {
         const songSelect = document.getElementById('modalSongSelect');
         const songId = songSelect.value;
         
         if (!songId) {
             this.showError('Please select a song');
             return;
         }
         
         try {
             const response = await fetch(`/api/jams/${this.jamId}/songs`, {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json',
                     ...getApiHeaders()
                 },
                 body: JSON.stringify({ song_id: songId })
             });
             
             if (response.ok) {
                 this.showSuccess('Song added to jam!');
                 this.closeAddSongModal();
                 await this.loadJam(); // Reload jam data
             } else {
                 const error = await response.json();
                 this.showError(error.detail || 'Failed to add song to jam');
             }
         } catch (error) {
             this.showError('Network error: ' + error.message);
         }
     }
}

// Global functions for onclick handlers

function voteForSong(songId) {
    jamPage.voteForSong(songId);
}

function playSong(songId) {
    jamPage.playSong(songId);
}

function registerAttendee() {
    jamPage.registerAttendee();
}

function registerToPerform(songId) {
    jamPage.registerToPerform(songId);
}

function toggleHeart(songId) {
    jamPage.toggleHeart(songId);
}

function closePerformModal() {
    jamPage.closePerformModal();
}

function showChordSheetModal(songId, songTitle, songArtist) {
    jamPage.showChordSheetModal(songId, songTitle, songArtist);
}

function findChordSheetForSong() {
    jamPage.findChordSheetForSong();
}

function closeChordSheetModal() {
    jamPage.closeChordSheetModal();
}

function saveChordSheetForSong() {
    jamPage.saveChordSheetForSong();
}

function confirmPerformRegistration() {
    jamPage.confirmPerformRegistration();
}

function clearAttendee() {
    jamPage.clearAttendee();
}

function closeUnregisterConfirmModal() {
    jamPage.closeUnregisterConfirmModal();
}

function confirmUnregisterFromPerform() {
    jamPage.confirmUnregisterFromPerform();
}

function showShareModal() {
    jamPage.showShareModal();
}

function closeShareModal() {
    jamPage.closeShareModal();
}

function copyJamUrl() {
    jamPage.copyJamUrl();
}

function showAddSongModal() {
    jamPage.showAddSongModal();
}

function closeAddSongModal() {
    jamPage.closeAddSongModal();
}

function addSongToJamFromModal() {
    jamPage.addSongToJamFromModal();
}

// Initialize the jam page
const jamPage = new JamPage();
