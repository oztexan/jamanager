#!/usr/bin/env python3
"""
Initialize development database with popular songs using SQLAlchemy
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_database, engine
from models.database import Song, Jam, Venue, JamSong, Base
from datetime import date

# Popular cover songs with Ultimate Guitar URLs - Default dev database set
DEFAULT_DEV_SONGS = [
    # Fleetwood Mac
    ("Dreams", "Fleetwood Mac", "https://tabs.ultimate-guitar.com/tab/fleetwood-mac/dreams-chords-39144"),
    
    # Amy Winehouse
    ("Valerie", "Amy Winehouse", "https://tabs.ultimate-guitar.com/tab/amy-winehouse/valerie-chords-39144"),
    
    # Classic Rock
    ("Sweet Child O' Mine", "Guns N' Roses", "https://tabs.ultimate-guitar.com/tab/guns-n-roses/sweet-child-o-mine-chords-176076"),
    ("Hotel California", "Eagles", "https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-46190"),
    ("Wonderwall", "Oasis", "https://tabs.ultimate-guitar.com/tab/oasis/wonderwall-chords-39144"),
    ("Black", "Pearl Jam", "https://tabs.ultimate-guitar.com/tab/pearl-jam/black-chords-1115192"),
    ("Stairway to Heaven", "Led Zeppelin", "https://tabs.ultimate-guitar.com/tab/led-zeppelin/stairway-to-heaven-chords-39144"),
    ("Bohemian Rhapsody", "Queen", "https://tabs.ultimate-guitar.com/tab/queen/bohemian-rhapsody-chords-39144"),
    ("Don't Stop Believin'", "Journey", "https://tabs.ultimate-guitar.com/tab/journey/dont-stop-believin-chords-39144"),
    ("Sweet Caroline", "Neil Diamond", "https://tabs.ultimate-guitar.com/tab/neil-diamond/sweet-caroline-chords-39144"),
    
    # Pop/Rock
    ("I Will Survive", "Gloria Gaynor", "https://tabs.ultimate-guitar.com/tab/gloria-gaynor/i-will-survive-chords-39144"),
    ("Dancing Queen", "ABBA", "https://tabs.ultimate-guitar.com/tab/abba/dancing-queen-chords-39144"),
    ("Billie Jean", "Michael Jackson", "https://tabs.ultimate-guitar.com/tab/michael-jackson/billie-jean-chords-39144"),
    ("Imagine", "John Lennon", "https://tabs.ultimate-guitar.com/tab/john-lennon/imagine-chords-39144"),
    ("Hallelujah", "Leonard Cohen", "https://tabs.ultimate-guitar.com/tab/leonard-cohen/hallelujah-chords-39144"),
    
    # Alternative/Indie
    ("Creep", "Radiohead", "https://tabs.ultimate-guitar.com/tab/radiohead/creep-chords-39144"),
    ("Mr. Brightside", "The Killers", "https://tabs.ultimate-guitar.com/tab/the-killers/mr-brightside-chords-39144"),
    ("Somebody That I Used to Know", "Gotye", "https://tabs.ultimate-guitar.com/tab/gotye/somebody-that-i-used-to-know-chords-39144"),
    ("Ho Hey", "The Lumineers", "https://tabs.ultimate-guitar.com/tab/the-lumineers/ho-hey-chords-39144"),
    ("Riptide", "Vance Joy", "https://tabs.ultimate-guitar.com/tab/vance-joy/riptide-chords-39144"),
    
    # Country/Folk
    ("Wagon Wheel", "Old Crow Medicine Show", "https://tabs.ultimate-guitar.com/tab/old-crow-medicine-show/wagon-wheel-chords-39144"),
    ("Tennessee Whiskey", "Chris Stapleton", "https://tabs.ultimate-guitar.com/tab/chris-stapleton/tennessee-whiskey-chords-39144"),
    ("Jolene", "Dolly Parton", "https://tabs.ultimate-guitar.com/tab/dolly-parton/jolene-chords-39144"),
    ("Ring of Fire", "Johnny Cash", "https://tabs.ultimate-guitar.com/tab/johnny-cash/ring-of-fire-chords-39144"),
    
    # Blues/Soul
    ("Ain't No Sunshine", "Bill Withers", "https://tabs.ultimate-guitar.com/tab/bill-withers/aint-no-sunshine-chords-39144"),
    ("Sitting on the Dock of the Bay", "Otis Redding", "https://tabs.ultimate-guitar.com/tab/otis-redding/sitting-on-the-dock-of-the-bay-chords-39144"),
    ("Georgia on My Mind", "Ray Charles", "https://tabs.ultimate-guitar.com/tab/ray-charles/georgia-on-my-mind-chords-39144"),
    
    # Modern Pop
    ("Shallow", "Lady Gaga & Bradley Cooper", "https://tabs.ultimate-guitar.com/tab/lady-gaga/shallow-chords-39144"),
    ("Perfect", "Ed Sheeran", "https://tabs.ultimate-guitar.com/tab/ed-sheeran/perfect-chords-39144"),
    ("Shape of You", "Ed Sheeran", "https://tabs.ultimate-guitar.com/tab/ed-sheeran/shape-of-you-chords-39144"),
]

async def init_dev_database() -> None:
    """Initialize development database with schema and popular songs"""
    try:
        # Remove existing database file if it exists
        db_path = "jamanager.db"
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Removed existing database file")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database schema created successfully")
        
        # Add sample data
        async for db in get_database():
            try:
                # Create sample venues
                venue1 = Venue(
                    name="The Jazz Club",
                    address="123 Music Street, Sydney NSW 2000",
                    description="Intimate jazz and blues venue"
                )
                venue2 = Venue(
                    name="Rock Arena",
                    address="456 Rock Boulevard, Sydney NSW 2000",
                    description="Large venue for rock concerts"
                )
                
                db.add(venue1)
                db.add(venue2)
                await db.flush()  # Get the IDs
                print(f"✅ Created venue: {venue1.name}")
                print(f"✅ Created venue: {venue2.name}")
                
                # Create popular songs
                songs = []
                for title, artist, chord_sheet_url in DEFAULT_DEV_SONGS:
                    song = Song(
                        title=title,
                        artist=artist,
                        chord_sheet_url=chord_sheet_url,
                        chord_sheet_is_valid=None,
                        chord_sheet_validated_at=None
                    )
                    db.add(song)
                    songs.append(song)
                    print(f"✅ Created song: {title} by {artist}")
                
                await db.flush()  # Get the song IDs
                
                # Create sample jam with proper slug format
                jam = Jam(
                    name="Friday Night Jam",
                    slug="friday-night-jam-the-jazz-club-2025-10-03",
                    description="Weekly jam session",
                    venue_id=venue1.id,
                    jam_date=date(2025, 10, 3),
                    status="waiting"
                )
                db.add(jam)
                await db.flush()  # Get the jam ID
                print(f"✅ Created jam: {jam.name}")
                
                # Add first 4 songs to the jam for testing
                for song in songs[:4]:
                    jam_song = JamSong(
                        jam_id=jam.id,
                        song_id=song.id
                    )
                    db.add(jam_song)
                print(f"✅ Added {len(songs[:4])} songs to jam")
                
                await db.commit()
                print(f"\n🎵 Development Database Initialization Complete:")
                print(f"   Created: {len(songs)} popular songs")
                print(f"   Created: 2 venues")
                print(f"   Created: 1 jam with {len(songs[:4])} songs")
                
            except Exception as e:
                await db.rollback()
                print(f"❌ Error creating sample data: {e}")
                raise
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🎵 Initializing development database with popular cover songs...")
    asyncio.run(init_dev_database())
    print("✅ Done!")
