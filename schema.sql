-- Jamanager Database Schema
-- This is the consolidated schema for the simplified song model

-- Create database (run this manually if needed)
-- CREATE DATABASE jamanager;

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Venues table
CREATE TABLE IF NOT EXISTS venues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    address VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Songs table (simplified - no genre, chord_chart, or tags)
CREATE TABLE IF NOT EXISTS songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    chord_sheet_url VARCHAR(500), -- URL to Ultimate Guitar chord sheet
    vote_count INTEGER DEFAULT 0,
    times_played INTEGER DEFAULT 0,
    last_played TIMESTAMP,
    play_history JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jams table
CREATE TABLE IF NOT EXISTS jams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    venue_id UUID NOT NULL REFERENCES venues(id),
    jam_date DATE NOT NULL,
    background_image VARCHAR(500), -- Path to uploaded image
    current_song_id UUID REFERENCES songs(id),
    status VARCHAR(50) DEFAULT 'waiting', -- waiting, playing, paused, ended
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Jam Songs junction table
CREATE TABLE IF NOT EXISTS jam_songs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jam_id UUID NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    captains JSONB DEFAULT '[]'::jsonb, -- Array of captain names
    played BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(jam_id, song_id)
);

-- Attendees table
CREATE TABLE IF NOT EXISTS attendees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jam_id UUID NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    session_id VARCHAR(255), -- For anonymous users
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(jam_id, name)
);

-- Votes table
CREATE TABLE IF NOT EXISTS votes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jam_id UUID NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    attendee_id UUID REFERENCES attendees(id) ON DELETE CASCADE,
    session_id VARCHAR(255), -- For anonymous users
    voted_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(jam_id, song_id, attendee_id), -- One vote per attendee per song
    UNIQUE(jam_id, song_id, session_id) -- One vote per session per song
);

-- Performance Registrations table
CREATE TABLE IF NOT EXISTS performance_registrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    jam_id UUID NOT NULL REFERENCES jams(id) ON DELETE CASCADE,
    song_id UUID NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    attendee_id UUID NOT NULL REFERENCES attendees(id) ON DELETE CASCADE,
    instrument VARCHAR(100), -- Optional instrument specification
    registered_at TIMESTAMP DEFAULT NOW(),
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
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_venues_updated_at BEFORE UPDATE ON venues FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_songs_updated_at BEFORE UPDATE ON songs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_jams_updated_at BEFORE UPDATE ON jams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
