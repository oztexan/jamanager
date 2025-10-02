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
        await this.loadSongs();
        await this.loadQRCode();
        this.setupWebSocket();
        
        // Restore attendee from localStorage if available
        this.restoreAttendee();
    }

    async loadJam() {
        try {
            const response = await fetch(`/api/jams/by-slug/${this.jamSlug}`);
            if (response.ok) {
                this.jam = await response.json();
                this.displayJam();
                this.initializeBreadcrumbs();
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

    async loadSongs() {
        try {
            const response = await fetch('/api/songs');
            if (response.ok) {
                const songs = await response.json();
                this.populateSongSelect(songs);
            }
        } catch (error) {
            console.error('Failed to load songs:', error);
        }
    }

    displayJam() {
        if (!this.jam) return;

        // Update page title
        document.title = `${this.jam.name} - Jamanger`;
        
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
               li.className = 'song-item';
               li.innerHTML = `
                   <div class="song-header">
                       <div class="song-rank">#${index + 1}</div>
                       <div class="song-info">
                           <div class="song-title">${jamSong.song.title}</div>
                           <div class="song-artist">${jamSong.song.artist}</div>
                       </div>
                       <div class="song-actions">
                           <button class="heart-btn" onclick="toggleHeart('${jamSong.song.id}')" data-song-id="${jamSong.song.id}">
                               <span class="heart-icon">♡</span>
                               <span class="vote-count">${jamSong.song.vote_count}</span>
                           </button>
                           ${hasPermission('can_register_to_perform') && this.currentAttendee ? `
                               <button class="perform-btn" onclick="registerToPerform('${jamSong.song.id}')" data-song-id="${jamSong.song.id}">
                                   <span class="perform-icon">🎤</span>
                               </button>
                           ` : ''}
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
            
            // Load performers for this song
            this.loadSongPerformers(jamSong.song.id);
            
            // Check vote status for this song
            this.checkVoteStatus(jamSong.song.id);
            
            // Check perform status for this song
            this.checkPerformStatus(jamSong.song.id);
        });
    }

    populateSongSelect(songs) {
        const select = document.getElementById('songSelect');
        select.innerHTML = '<option value="">Choose a song...</option>';
        
        songs.forEach(song => {
            const option = document.createElement('option');
            option.value = song.id;
            option.textContent = `${song.title} - ${song.artist}`;
            select.appendChild(option);
        });
    }

    async loadQRCode() {
        if (!this.jam) return;

        try {
            const response = await fetch(`/api/jams/${this.jam.id}/qr`);
            if (response.ok) {
                const blob = await response.blob();
                const imageUrl = URL.createObjectURL(blob);
                
                const qrImg = document.getElementById('qrCode');
                const qrLoading = document.getElementById('qrLoading');
                const jamUrl = document.getElementById('jamUrl');
                
                qrImg.src = imageUrl;
                qrImg.style.display = 'block';
                qrLoading.style.display = 'none';
                jamUrl.textContent = window.location.href;
            }
        } catch (error) {
            console.error('Failed to load QR code:', error);
            document.getElementById('qrLoading').textContent = 'Failed to generate QR code';
        }
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
            // Unregister from performing
            await this.unregisterFromPerform(songId);
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
}

// Global functions for onclick handlers
function addSongToJam() {
    jamPage.addSongToJam();
}

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

function confirmPerformRegistration() {
    jamPage.confirmPerformRegistration();
}

function clearAttendee() {
    jamPage.clearAttendee();
}

// Initialize the jam page
const jamPage = new JamPage();
