#!/usr/bin/env python3
"""
Development Data Initialization Script for Jamanager

This script populates the database with comprehensive test data for development.
Run this script to set up a rich dataset for testing all features.

Usage:
    python scripts/init_dev_data.py
"""

import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from sqlalchemy import delete, select

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_database
from models.database import (
    Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration, Venue
)

# Comprehensive test data
TEST_SONGS = [
    # Classic Rock
    {"title": "Wonderwall", "artist": "Oasis", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/oasis/wonderwall-crd-257797"},
    {"title": "Hotel California", "artist": "Eagles", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/eagles/hotel-california-crd-257797"},
    {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/guns-n-roses/sweet-child-o-mine-crd-257797"},
    {"title": "Bohemian Rhapsody", "artist": "Queen", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/queen/bohemian-rhapsody-crd-257797"},
    {"title": "Stairway to Heaven", "artist": "Led Zeppelin", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/led-zeppelin/stairway-to-heaven-crd-257797"},
    {"title": "Smoke on the Water", "artist": "Deep Purple", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/deep-purple/smoke-on-the-water-crd-257797"},
    {"title": "Sweet Home Alabama", "artist": "Lynyrd Skynyrd", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/lynyrd-skynyrd/sweet-home-alabama-crd-257797"},
    {"title": "Free Bird", "artist": "Lynyrd Skynyrd", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/lynyrd-skynyrd/free-bird-crd-257797"},
    
    # Pop/Rock
    {"title": "Don't Stop Believin'", "artist": "Journey", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/journey/dont-stop-believin-crd-257797"},
    {"title": "Livin' on a Prayer", "artist": "Bon Jovi", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/bon-jovi/livin-on-a-prayer-crd-257797"},
    {"title": "Eye of the Tiger", "artist": "Survivor", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/survivor/eye-of-the-tiger-crd-257797"},
    {"title": "We Will Rock You", "artist": "Queen", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/queen/we-will-rock-you-crd-257797"},
    
    # Acoustic/Folk
    {"title": "Black", "artist": "Pearl Jam", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/pearl-jam/black-crd-257797"},
    {"title": "Wish You Were Here", "artist": "Pink Floyd", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/pink-floyd/wish-you-were-here-crd-257797"},
    {"title": "Tears in Heaven", "artist": "Eric Clapton", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/eric-clapton/tears-in-heaven-crd-257797"},
    {"title": "Hallelujah", "artist": "Leonard Cohen", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/leonard-cohen/hallelujah-crd-257797"},
    
    # Modern Rock
    {"title": "Creep", "artist": "Radiohead", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/radiohead/creep-crd-257797"},
    {"title": "Zombie", "artist": "The Cranberries", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/the-cranberries/zombie-crd-257797"},
    {"title": "Basket Case", "artist": "Green Day", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/green-day/basket-case-crd-257797"},
    {"title": "All the Small Things", "artist": "Blink-182", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/blink-182/all-the-small-things-crd-257797"},
    
    # Blues/Rock
    {"title": "Crossroads", "artist": "Cream", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/cream/crossroads-crd-257797"},
    {"title": "The Thrill Is Gone", "artist": "B.B. King", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/bb-king/the-thrill-is-gone-crd-257797"},
    {"title": "Pride and Joy", "artist": "Stevie Ray Vaughan", "chord_sheet_url": "https://www.ultimate-guitar.com/tab/stevie-ray-vaughan/pride-and-joy-crd-257797"},
]

TEST_VENUES = [
    {
        "name": "Main Stage",
        "address": "123 Music Street, City, State 12345",
        "description": "Large performance venue with professional sound system and stage lighting"
    },
    {
        "name": "Coffee House",
        "address": "456 Acoustic Ave, City, State 12345",
        "description": "Intimate coffee shop perfect for acoustic performances and open mic nights"
    },
    {
        "name": "Studio A",
        "address": "789 Recording Blvd, City, State 12345",
        "description": "Professional recording studio with practice space and rehearsal rooms"
    },
    {
        "name": "The Underground",
        "address": "321 Basement St, City, State 12345",
        "description": "Underground venue for alternative and indie music performances"
    },
    {
        "name": "Jazz Club",
        "address": "654 Swing Lane, City, State 12345",
        "description": "Sophisticated jazz club with piano and intimate seating"
    }
]

TEST_JAMS = [
    {
        "name": "Friday Night Jam",
        "slug": "friday-night-jam-main-stage-2025-10-04",
        "description": "Weekly community jam session - all skill levels welcome",
        "venue_name": "Main Stage",
        "jam_date": date.today(),
        "status": "waiting"
    },
    {
        "name": "Acoustic Evening",
        "slug": "acoustic-evening-coffee-house-2025-10-04",
        "description": "Intimate acoustic performance night with open mic",
        "venue_name": "Coffee House",
        "jam_date": date.today(),
        "status": "waiting"
    },
    {
        "name": "Rock Workshop",
        "slug": "rock-workshop-studio-a-2025-10-05",
        "description": "Learn rock techniques and jam together",
        "venue_name": "Studio A",
        "jam_date": date.today() + timedelta(days=1),
        "status": "waiting"
    },
    {
        "name": "Jazz Night",
        "slug": "jazz-night-club-2025-10-03",
        "description": "Smooth jazz and improvisation session",
        "venue_name": "Jazz Club",
        "jam_date": date.today() - timedelta(days=1),
        "status": "ended"
    },
    {
        "name": "Underground Sessions",
        "slug": "underground-sessions-2025-10-06",
        "description": "Alternative and indie music showcase",
        "venue_name": "The Underground",
        "jam_date": date.today() + timedelta(days=2),
        "status": "waiting"
    }
]

TEST_ATTENDEES = [
    {"name": "Alice Johnson"},
    {"name": "Bob Smith"},
    {"name": "Carol Davis"},
    {"name": "David Wilson"},
    {"name": "Eve Brown"},
    {"name": "Frank Miller"},
    {"name": "Grace Lee"},
    {"name": "Henry Taylor"},
]

async def clear_existing_data(db) -> None:
    """Clear all existing data from the database"""
    print("🗑️  Clearing existing data...")
    
    # Delete in reverse order of dependencies
    await db.execute(delete(PerformanceRegistration))
    await db.execute(delete(Vote))
    await db.execute(delete(Attendee))
    await db.execute(delete(JamSong))
    await db.execute(delete(Jam))
    await db.execute(delete(Song))
    await db.execute(delete(Venue))
    
    await db.commit()
    print("   ✅ Cleared all existing data")

async def create_venues(db) -> None:
    """Create test venues"""
    print("🏢 Creating venues...")
    
    venues = []
    for venue_data in TEST_VENUES:
        venue = Venue(**venue_data)
        db.add(venue)
        venues.append(venue)
    
    await db.commit()
    print(f"   ✅ Created {len(venues)} venues")
    return venues

async def create_songs(db) -> None:
    """Create test songs"""
    print("🎵 Creating songs...")
    
    songs = []
    for song_data in TEST_SONGS:
        song = Song(**song_data)
        db.add(song)
        songs.append(song)
    
    await db.commit()
    print(f"   ✅ Created {len(songs)} songs")
    return songs

async def create_jams(db, venues) -> None:
    """Create test jams"""
    print("🎪 Creating jams...")
    
    # Create venue lookup
    venue_lookup = {venue.name: venue for venue in venues}
    
    jams = []
    for jam_data in TEST_JAMS:
        venue = venue_lookup[jam_data["venue_name"]]
        jam = Jam(
            name=jam_data["name"],
            slug=jam_data["slug"],
            description=jam_data["description"],
            venue_id=venue.id,
            jam_date=jam_data["jam_date"],
            status=jam_data["status"]
        )
        db.add(jam)
        jams.append(jam)
    
    await db.commit()
    print(f"   ✅ Created {len(jams)} jams")
    return jams

async def create_attendees(db, jams) -> None:
    """Create test attendees"""
    print("👥 Creating attendees...")
    
    attendees = []
    # Create attendees for each jam
    for jam in jams:
        for attendee_data in TEST_ATTENDEES[:3]:  # 3 attendees per jam
            attendee = Attendee(
                name=attendee_data["name"],
                jam_id=jam.id
            )
            db.add(attendee)
            attendees.append(attendee)
    
    await db.commit()
    print(f"   ✅ Created {len(attendees)} attendees")
    return attendees

async def create_jam_songs(db, jams, songs) -> None:
    """Create jam-song relationships with some sample data"""
    print("🎼 Creating jam-song relationships...")
    
    # Add some songs to specific jams
    jam_song_assignments = [
        # Friday Night Jam - Classic rock songs
        ("Friday Night Jam", ["Wonderwall", "Hotel California", "Sweet Child O' Mine", "Bohemian Rhapsody"]),
        # Acoustic Evening - Acoustic/folk songs
        ("Acoustic Evening", ["Black", "Wish You Were Here", "Tears in Heaven", "Hallelujah"]),
        # Jazz Night - Some blues/jazz songs
        ("Jazz Night", ["The Thrill Is Gone", "Crossroads", "Pride and Joy"]),
    ]
    
    jam_lookup = {jam.name: jam for jam in jams}
    song_lookup = {song.title: song for song in songs}
    
    jam_songs_created = 0
    for jam_name, song_titles in jam_song_assignments:
        jam = jam_lookup.get(jam_name)
        if not jam:
            continue
            
        for song_title in song_titles:
            song = song_lookup.get(song_title)
            if not song:
                continue
                
            jam_song = JamSong(
                jam_id=jam.id,
                song_id=song.id,
                captains="",
                played=False
            )
            db.add(jam_song)
            jam_songs_created += 1
    
    await db.commit()
    print(f"   ✅ Created {jam_songs_created} jam-song relationships")

async def create_sample_votes(db, jams, songs, attendees) -> None:
    """Create some sample votes"""
    print("🗳️  Creating sample votes...")
    
    # Get jam-songs for voting
    jam_song_result = await db.execute(select(JamSong))
    jam_songs = jam_song_result.scalars().all()
    
    votes_created = 0
    for i, jam_song in enumerate(jam_songs[:5]):  # Vote on first 5 jam-songs
        # Each jam-song gets 2-4 random votes
        num_votes = 2 + (i % 3)
        for j in range(num_votes):
            attendee = attendees[j % len(attendees)]
            vote = Vote(
                jam_id=jam_song.jam_id,
                song_id=jam_song.song_id,
                attendee_id=attendee.id
            )
            db.add(vote)
            votes_created += 1
    
    await db.commit()
    print(f"   ✅ Created {votes_created} sample votes")

async def create_sample_performances(db, jams, songs, attendees) -> None:
    """Create some sample performance registrations"""
    print("🎤 Creating sample performance registrations...")
    
    # Get jam-songs for performance registration
    jam_song_result = await db.execute(select(JamSong))
    jam_songs = jam_song_result.scalars().all()
    
    instruments = ["Guitar", "Bass", "Drums", "Vocals", "Piano", "Saxophone"]
    
    performances_created = 0
    for i, jam_song in enumerate(jam_songs[:3]):  # Register for first 3 jam-songs
        # Each jam-song gets 1-2 performers
        num_performers = 1 + (i % 2)
        for j in range(num_performers):
            attendee = attendees[j % len(attendees)]
            instrument = instruments[j % len(instruments)]
            
            performance = PerformanceRegistration(
                jam_id=jam_song.jam_id,
                song_id=jam_song.song_id,
                attendee_id=attendee.id,
                instrument=instrument
            )
            db.add(performance)
            performances_created += 1
    
    await db.commit()
    print(f"   ✅ Created {performances_created} performance registrations")

async def main() -> None:
    """Main function to initialize development data"""
    print("🚀 Initializing Jamanager Development Data")
    print("=" * 50)
    
    async for db in get_database():
        try:
            # Clear existing data
            await clear_existing_data(db)
            
            # Create new data
            venues = await create_venues(db)
            songs = await create_songs(db)
            jams = await create_jams(db, venues)
            attendees = await create_attendees(db, jams)
            await create_jam_songs(db, jams, songs)
            await create_sample_votes(db, jams, songs, attendees)
            await create_sample_performances(db, jams, songs, attendees)
            
            print("\n🎉 Development data initialization complete!")
            print(f"   📊 Created:")
            print(f"      - {len(venues)} venues")
            print(f"      - {len(songs)} songs")
            print(f"      - {len(jams)} jams")
            print(f"      - {len(attendees)} attendees")
            print(f"      - Sample votes and performance registrations")
            print(f"\n🌐 You can now test the application at http://localhost:8000")
            
        except Exception as e:
            print(f"❌ Error initializing development data: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(main())
