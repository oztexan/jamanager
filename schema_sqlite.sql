-- Jamanager Database Schema (SQLite)
-- This is the consolidated schema for the simplified song model

-- Venues table
CREATE TABLE IF NOT EXISTS venues (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL UNIQUE,
    address TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Songs table (simplified - no genre, chord_chart, or tags)
CREATE TABLE IF NOT EXISTS songs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    chord_sheet_url TEXT, -- URL to Ultimate Guitar chord sheet
    vote_count INTEGER DEFAULT 0,
    times_played INTEGER DEFAULT 0,
    last_played TIMESTAMP,
    play_history TEXT DEFAULT '[]', -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jams table
CREATE TABLE IF NOT EXISTS jams (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    venue_id TEXT NOT NULL REFERENCES venues(id),
    jam_date DATE NOT NULL,
    background_image TEXT, -- Path to uploaded image
    current_song_id TEXT REFERENCES songs(id),
    status TEXT DEFAULT 'waiting', -- waiting, playing, paused, ended
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jam Songs junction table
CREATE TABLE IF NOT EXISTS jam_songs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    jam_id TEXT NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id TEXT NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    captains TEXT DEFAULT '[]', -- JSON string
    played BOOLEAN DEFAULT 0,
    played_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jam_id, song_id)
);

-- Attendees table
CREATE TABLE IF NOT EXISTS attendees (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    jam_id TEXT NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    session_id TEXT, -- For anonymous users
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jam_id, name)
);

-- Votes table
CREATE TABLE IF NOT EXISTS votes (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    jam_id TEXT NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id TEXT NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    attendee_id TEXT REFERENCES attendees(id) ON DELETE CASCADE,
    session_id TEXT, -- For anonymous users
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jam_id, song_id, attendee_id), -- One vote per attendee per song
    UNIQUE(jam_id, song_id, session_id) -- One vote per session per song
);

-- Performance Registrations table
CREATE TABLE IF NOT EXISTS performance_registrations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    jam_id TEXT NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id TEXT NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    attendee_id TEXT NOT NULL REFERENCES attendees(id) ON DELETE CASCADE,
    instrument TEXT, -- Optional instrument specification
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(jam_id, song_id, attendee_id) -- One registration per attendee per song
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jams_slug ON jams(slug);
CREATE INDEX IF NOT EXISTS idx_jams_date ON jams(jam_date);
CREATE INDEX IF NOT EXISTS idx_jam_songs_jam_id ON jam_songs(jam_id);
CREATE INDEX IF NOT EXISTS idx_jam_songs_song_id ON jam_songs(song_id);
CREATE INDEX IF NOT EXISTS idx_attendees_jam_id ON attendees(jam_id);
CREATE INDEX IF NOT EXISTS idx_votes_jam_id ON votes(jam_id);
CREATE INDEX IF NOT EXISTS idx_votes_song_id ON votes(song_id);
CREATE INDEX IF NOT EXISTS idx_votes_session_id ON votes(session_id);
CREATE INDEX IF NOT EXISTS idx_performance_registrations_jam_id ON performance_registrations(jam_id);
CREATE INDEX IF NOT EXISTS idx_performance_registrations_song_id ON performance_registrations(song_id);
CREATE INDEX IF NOT EXISTS idx_performance_registrations_attendee_id ON performance_registrations(attendee_id);

-- Create updated_at trigger function
CREATE TRIGGER IF NOT EXISTS update_venues_updated_at 
    AFTER UPDATE ON venues 
    BEGIN 
        UPDATE venues SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_songs_updated_at 
    AFTER UPDATE ON songs 
    BEGIN 
        UPDATE songs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_jams_updated_at 
    AFTER UPDATE ON jams 
    BEGIN 
        UPDATE jams SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER IF NOT EXISTS update_jam_songs_updated_at 
    AFTER UPDATE ON jam_songs 
    BEGIN 
        UPDATE jam_songs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
