/**
 * Jam WebSocket Management
 * Handles real-time updates for the jam session
 */

class JamWebSocket {
    constructor() {
        this.socket = null;
        this.jamId = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // Start with 1 second
        this.isConnected = false;
    }

    /**
     * Initialize WebSocket connection
     */
    init(jamId) {
        this.jamId = jamId;
        this.connect();
    }

    /**
     * Connect to WebSocket
     */
    connect() {
        if (!this.jamId) {
            console.error('Cannot connect: jamId not set');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.jamId}`;
        
        console.log('Connecting to WebSocket:', wsUrl);
        
        try {
            this.socket = new WebSocket(wsUrl);
            this.setupEventListeners();
        } catch (error) {
            console.error('Failed to create WebSocket connection:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Setup WebSocket event listeners
     */
    setupEventListeners() {
        if (!this.socket) return;

        this.socket.onopen = (event) => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.reconnectDelay = 1000;
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.isConnected = false;
            
            // Only attempt to reconnect if it wasn't a clean close
            if (event.code !== 1000) {
                this.scheduleReconnect();
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.isConnected = false;
        };
    }

    /**
     * Handle incoming WebSocket messages
     */
    handleMessage(message) {
        console.log('WebSocket message received:', message);
        
        // Handle the new message format with event and data fields
        const event = message.event;
        const data = message.data || message; // Fallback to old format for compatibility
        
        switch (event) {
            case 'vote_update':
                this.handleVoteUpdate(data);
                break;
            case 'song_added':
                this.handleSongAdded(data);
                break;
            case 'performance_registered':
                this.handlePerformanceRegistered(data);
                break;
            case 'attendee_registered':
                this.handleAttendeeRegistered(data);
                break;
            default:
                console.log('Unknown message type:', event);
        }
    }

    /**
     * Handle vote update
     */
    handleVoteUpdate(data) {
        console.log('Vote update received:', data);
        console.log('Updating heart for song_id:', data.song_id, 'voted:', data.voted, 'attendee_id:', data.attendee_id);
        
        // Check if this vote is from the current user
        const currentAttendee = window.jamAttendee ? window.jamAttendee.getCurrentAttendee() : null;
        const isCurrentUserVote = currentAttendee && currentAttendee.id === data.attendee_id;
        
        console.log('Current attendee:', currentAttendee);
        console.log('Is current user vote:', isCurrentUserVote);
        
        // Only update the heart visual state if this is the current user's vote
        if (isCurrentUserVote) {
            const heartElement = document.querySelector(`[data-song-id="${data.song_id}"] .heart-toggle`);
            console.log('Found heart element:', heartElement);
            
            if (heartElement) {
                if (data.voted) {
                    heartElement.classList.add('voted');
                    console.log('Added voted class to heart');
                } else {
                    heartElement.classList.remove('voted');
                    console.log('Removed voted class from heart');
                }
            } else {
                console.log('Heart element not found for song_id:', data.song_id);
            }
        } else {
            console.log('Not current user vote - skipping heart visual update');
        }
        
        // Always reload jam data to get updated vote counts and refresh the entire song list
        if (window.jamUI && window.jamUI.jamCore) {
            console.log('Reloading jam data...');
            window.jamUI.jamCore.loadJamData();
        } else {
            console.log('jamUI or jamCore not available');
        }
    }

    /**
     * Handle song added
     */
    handleSongAdded(data) {
        // Reload jam data to get the new song
        if (window.jamCore) {
            window.jamCore.loadJamData();
        }
    }

    /**
     * Handle performance registration
     */
    handlePerformanceRegistered(data) {
        // Update performers display
        const performersEl = document.getElementById(`performers-${data.song_id}`);
        if (performersEl) {
            // This would need to be implemented based on the actual data structure
            console.log('Performance registered for song:', data.song_id);
        }
    }

    /**
     * Handle attendee registration
     */
    handleAttendeeRegistered(data) {
        console.log('New attendee registered:', data.attendee_name);
        // Could show a notification or update attendee count
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
        
        console.log(`Scheduling reconnection attempt ${this.reconnectAttempts} in ${delay}ms`);
        
        setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Send message through WebSocket
     */
    send(data) {
        if (this.socket && this.isConnected) {
            this.socket.send(JSON.stringify(data));
        } else {
            console.warn('WebSocket not connected, cannot send message:', data);
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.socket) {
            this.socket.close(1000, 'User disconnected');
            this.socket = null;
        }
        this.isConnected = false;
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            connected: this.isConnected,
            attempts: this.reconnectAttempts,
            maxAttempts: this.maxReconnectAttempts
        };
    }
}

// Export for use in other modules
window.JamWebSocket = JamWebSocket;