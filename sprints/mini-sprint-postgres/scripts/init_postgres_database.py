#!/usr/bin/env python3
"""
PostgreSQL Database Initialization Script for Jamanager
Creates schema and populates with development data
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from models.database import Base, Venue, Song, Jam, Attendee, JamSong, Vote, PerformanceRegistration, JamChordSheet

async def init_postgres_database():
    """Initialize PostgreSQL database with schema and dev data"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    print(f"🔗 Connecting to PostgreSQL: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url, echo=False)
        
        # Create all tables
        print("📋 Creating database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Database schema created successfully")
        
        # Create session
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        # Populate with dev data
        print("📊 Populating with development data...")
        await populate_dev_data(async_session)
        
        # Fix JSON compatibility issues
        print("🔧 Fixing JSON field compatibility...")
        await fix_json_compatibility(engine)
        
        print("✅ PostgreSQL database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL database: {e}")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()

async def populate_dev_data(async_session):
    """Populate database with development data"""
    
    async with async_session() as session:
        try:
            # Clear existing data
            print("🧹 Clearing existing data...")
            await session.execute(text("DELETE FROM jam_chord_sheets"))
            await session.execute(text("DELETE FROM performance_registrations"))
            await session.execute(text("DELETE FROM votes"))
            await session.execute(text("DELETE FROM jam_songs"))
            await session.execute(text("DELETE FROM attendees"))
            await session.execute(text("DELETE FROM jams"))
            await session.execute(text("DELETE FROM songs"))
            await session.execute(text("DELETE FROM venues"))
            await session.commit()
            
            # Create venues
            print("🏢 Creating venues...")
            venues_data = [
                {
                    "id": "venue-1",
                    "name": "The Blue Note",
                    "address": "123 Jazz Street, Melbourne VIC 3000",
                    "description": "Intimate jazz venue with great acoustics"
                },
                {
                    "id": "venue-2", 
                    "name": "The Acoustic Corner",
                    "address": "456 Folk Lane, Sydney NSW 2000",
                    "description": "Cozy venue perfect for acoustic performances"
                },
                {
                    "id": "venue-3",
                    "name": "The Electric Lounge",
                    "address": "789 Rock Road, Brisbane QLD 4000", 
                    "description": "Modern venue with state-of-the-art sound system"
                }
            ]
            
            for venue_data in venues_data:
                venue = Venue(**venue_data)
                session.add(venue)
            
            await session.commit()
            
            # Create songs
            print("🎵 Creating songs...")
            songs_data = [
                {
                    "id": "ab0324b91d6f9bf6720656e75abeba70",
                    "title": "Riptide",
                    "artist": "Vance Joy",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/vance-joy/riptide-chords-39144",
                    "chord_sheet_is_valid": False,
                    "times_played": 0,
                    "play_history": []
                },
                {
                    "id": "d6babf876c41df9045b7d4cc0092b9e0",
                    "title": "Shallow",
                    "artist": "Lady Gaga & Bradley Cooper",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/lady-gaga/shallow-chords-39144",
                    "chord_sheet_is_valid": False,
                    "times_played": 0,
                    "play_history": []
                },
                {
                    "id": "c7e8f9a1b2c3d4e5f6a7b8c9d0e1f2a3",
                    "title": "Ho Hey",
                    "artist": "The Lumineers",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/the-lumineers/ho-hey-chords-39144",
                    "chord_sheet_is_valid": False,
                    "times_played": 0,
                    "play_history": []
                },
                {
                    "id": "f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d",
                    "title": "Wonderwall",
                    "artist": "Oasis",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/oasis/wonderwall-chords-39144",
                    "chord_sheet_is_valid": False,
                    "times_played": 0,
                    "play_history": []
                },
                {
                    "id": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e",
                    "title": "Hotel California",
                    "artist": "Eagles",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-39144",
                    "chord_sheet_is_valid": False,
                    "times_played": 0,
                    "play_history": []
                }
            ]
            
            for song_data in songs_data:
                song = Song(**song_data)
                session.add(song)
            
            await session.commit()
            
            # Create jams
            print("🎤 Creating jams...")
            from datetime import datetime, timedelta
            
            jams_data = [
                {
                    "id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "name": "Country Folk Gathering",
                    "slug": "country-folk-gathering-2025-10-09",
                    "description": "A cozy evening of country and folk music",
                    "venue_id": "venue-1",
                    "jam_date": datetime.now().date(),
                    "background_image": "/static/uploads/backgrounds/country-folk-bg.jpg",
                    "status": "active"
                },
                {
                    "id": "f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d",
                    "name": "Acoustic Night",
                    "slug": "acoustic-night-2025-10-10",
                    "description": "Unplugged performances in an intimate setting",
                    "venue_id": "venue-2",
                    "jam_date": (datetime.now() + timedelta(days=1)).date(),
                    "background_image": "/static/uploads/backgrounds/acoustic-bg.jpg",
                    "status": "active"
                },
                {
                    "id": "a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e",
                    "name": "Rock & Roll Jam",
                    "slug": "rock-roll-jam-2025-10-11",
                    "description": "High-energy rock performances",
                    "venue_id": "venue-3",
                    "jam_date": (datetime.now() + timedelta(days=2)).date(),
                    "background_image": "/static/uploads/backgrounds/rock-bg.jpg",
                    "status": "active"
                },
                {
                    "id": "b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f",
                    "name": "Jazz Fusion Session",
                    "slug": "jazz-fusion-session-2025-10-12",
                    "description": "Experimental jazz and fusion music",
                    "venue_id": "venue-1",
                    "jam_date": (datetime.now() + timedelta(days=3)).date(),
                    "background_image": None,
                    "status": "active"
                },
                {
                    "id": "c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a",
                    "name": "Blues Night",
                    "slug": "blues-night-2025-10-13",
                    "description": "Deep blues and soul music",
                    "venue_id": "venue-2",
                    "jam_date": (datetime.now() + timedelta(days=4)).date(),
                    "background_image": "/static/uploads/backgrounds/blues-bg.jpg",
                    "status": "active"
                }
            ]
            
            for jam_data in jams_data:
                jam = Jam(**jam_data)
                session.add(jam)
            
            await session.commit()
            
            # Create attendees
            print("👥 Creating attendees...")
            attendees_data = [
                {
                    "id": "attendee-1",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "name": "Alice",
                    "session_id": "session_alice_001"
                },
                {
                    "id": "attendee-2",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "name": "Bob",
                    "session_id": "session_bob_002"
                },
                {
                    "id": "attendee-3",
                    "jam_id": "f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d",
                    "name": "Charlie",
                    "session_id": "session_charlie_003"
                }
            ]
            
            for attendee_data in attendees_data:
                attendee = Attendee(**attendee_data)
                session.add(attendee)
            
            await session.commit()
            
            # Create jam songs
            print("🎼 Creating jam songs...")
            jam_songs_data = [
                {
                    "id": "js-1",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "ab0324b91d6f9bf6720656e75abeba70",
                    "order": 1
                },
                {
                    "id": "js-2",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "d6babf876c41df9045b7d4cc0092b9e0",
                    "order": 2
                },
                {
                    "id": "js-3",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "c7e8f9a1b2c3d4e5f6a7b8c9d0e1f2a3",
                    "order": 3
                }
            ]
            
            for jam_song_data in jam_songs_data:
                jam_song = JamSong(**jam_song_data)
                session.add(jam_song)
            
            await session.commit()
            
            # Create votes
            print("🗳️ Creating votes...")
            votes_data = [
                {
                    "id": "vote-1",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "ab0324b91d6f9bf6720656e75abeba70",
                    "attendee_id": "attendee-1",
                    "session_id": "session_alice_001"
                },
                {
                    "id": "vote-2",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "d6babf876c41df9045b7d4cc0092b9e0",
                    "attendee_id": "attendee-2",
                    "session_id": "session_bob_002"
                }
            ]
            
            for vote_data in votes_data:
                vote = Vote(**vote_data)
                session.add(vote)
            
            await session.commit()
            
            # Create performance registrations
            print("🎸 Creating performance registrations...")
            perf_regs_data = [
                {
                    "id": "perf-1",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "ab0324b91d6f9bf6720656e75abeba70",
                    "attendee_id": "attendee-1",
                    "instrument": "guitar"
                },
                {
                    "id": "perf-2",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "d6babf876c41df9045b7d4cc0092b9e0",
                    "attendee_id": "attendee-2",
                    "instrument": "vocals"
                }
            ]
            
            for perf_reg_data in perf_regs_data:
                perf_reg = PerformanceRegistration(**perf_reg_data)
                session.add(perf_reg)
            
            await session.commit()
            
            # Create jam chord sheets
            print("📄 Creating jam chord sheets...")
            jam_chord_sheets_data = [
                {
                    "id": "jcs-1",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "ab0324b91d6f9bf6720656e75abeba70",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/vance-joy/riptide-chords-39144",
                    "chord_sheet_is_valid": False,
                    "title": "Riptide - Vance Joy",
                    "rating": 4.5,
                    "created_by": "attendee-1"
                },
                {
                    "id": "jcs-2",
                    "jam_id": "e810f23f-74a8-4339-83ed-21cc1b54ba3b",
                    "song_id": "d6babf876c41df9045b7d4cc0092b9e0",
                    "chord_sheet_url": "https://tabs.ultimate-guitar.com/tab/lady-gaga/shallow-chords-39144",
                    "chord_sheet_is_valid": False,
                    "title": "Shallow - Lady Gaga & Bradley Cooper",
                    "rating": 4.8,
                    "created_by": "attendee-2"
                }
            ]
            
            for jcs_data in jam_chord_sheets_data:
                jcs = JamChordSheet(**jcs_data)
                session.add(jcs)
            
            await session.commit()
            
            print("✅ Development data populated successfully!")
            
        except Exception as e:
            print(f"❌ Error populating dev data: {e}")
            await session.rollback()
            raise

async def fix_json_compatibility(engine):
    """Fix JSON field compatibility issues in PostgreSQL"""
    try:
        async with engine.begin() as conn:
            # Fix play_history fields that might be stored as strings instead of JSON
            result = await conn.execute(text("""
                UPDATE songs 
                SET play_history = '[]'::json 
                WHERE play_history::text = '"[]"'
            """))
            print(f"🔧 Fixed {result.rowcount} JSON field compatibility issues")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not fix JSON compatibility: {e}")

if __name__ == "__main__":
    success = asyncio.run(init_postgres_database())
    sys.exit(0 if success else 1)