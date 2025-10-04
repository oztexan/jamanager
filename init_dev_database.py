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
from datetime import date, datetime, timedelta

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

async def init_dev_database():
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
                venues = [
                    Venue(
                        name="The Jazz Club",
                        address="123 Music Street, Sydney NSW 2000",
                        description="Intimate jazz and blues venue"
                    ),
                    Venue(
                        name="Rock Arena",
                        address="456 Rock Boulevard, Sydney NSW 2000",
                        description="Large venue for rock concerts"
                    ),
                    Venue(
                        name="Acoustic Corner",
                        address="789 Folk Lane, Sydney NSW 2000",
                        description="Cozy acoustic music venue"
                    ),
                    Venue(
                        name="The Underground",
                        address="321 Alternative Ave, Sydney NSW 2000",
                        description="Underground music scene"
                    )
                ]
                
                for venue in venues:
                    db.add(venue)
                await db.flush()  # Get the IDs
                for venue in venues:
                    print(f"✅ Created venue: {venue.name}")
                
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
                
                # Create diverse sample jams
                today = date.today()
                jams_data = [
                    {
                        "name": "Today's Acoustic Session",
                        "description": "Join us for an intimate acoustic jam session featuring folk and indie favorites",
                        "venue_id": venues[2].id,  # Acoustic Corner
                        "jam_date": today,
                        "status": "active",
                        "background_image": "/static/uploads/acoustic-bg.jpg",
                        "songs": songs[15:20]  # Alternative/Indie songs
                    },
                    {
                        "name": "Rock Night at The Underground",
                        "description": "Loud guitars, heavy drums, and classic rock anthems",
                        "venue_id": venues[3].id,  # The Underground
                        "jam_date": today + timedelta(days=1),
                        "status": "waiting",
                        "background_image": "/static/uploads/rock-bg.jpg",
                        "songs": songs[2:8]  # Classic Rock songs
                    },
                    {
                        "name": "Jazz & Blues Evening",
                        "description": "Smooth jazz and soulful blues in an intimate setting",
                        "venue_id": venues[0].id,  # The Jazz Club
                        "jam_date": today + timedelta(days=2),
                        "status": "waiting",
                        "background_image": "/static/uploads/jazz-bg.jpg",
                        "songs": songs[54:58]  # Blues/Soul songs
                    },
                    {
                        "name": "Pop Hits Showcase",
                        "description": "Modern pop hits and chart-toppers for everyone to sing along",
                        "venue_id": venues[1].id,  # Rock Arena
                        "jam_date": today + timedelta(days=3),
                        "status": "waiting",
                        "background_image": "/static/uploads/pop-bg.jpg",
                        "songs": songs[59:63]  # Modern Pop songs
                    },
                    {
                        "name": "Country & Folk Gathering",
                        "description": "Boots, banjos, and beautiful storytelling through music",
                        "venue_id": venues[2].id,  # Acoustic Corner
                        "jam_date": today + timedelta(days=4),
                        "status": "waiting",
                        "background_image": "/static/uploads/country-bg.jpg",
                        "songs": songs[48:53]  # Country/Folk songs
                    }
                ]
                
                created_jams = []
                for jam_data in jams_data:
                    jam = Jam(
                        name=jam_data["name"],
                        slug=f"{jam_data['name'].lower().replace(' ', '-').replace('&', 'and')}-{jam_data['venue_id']}-{jam_data['jam_date']}",
                        description=jam_data["description"],
                        venue_id=jam_data["venue_id"],
                        jam_date=jam_data["jam_date"],
                        status=jam_data["status"],
                        background_image=jam_data["background_image"]
                    )
                    db.add(jam)
                    created_jams.append((jam, jam_data["songs"]))
                    print(f"✅ Created jam: {jam.name} ({jam_data['jam_date']})")
                
                await db.flush()  # Get the jam IDs
                
                # Add songs to each jam
                for jam, jam_songs in created_jams:
                    for song in jam_songs:
                        jam_song = JamSong(
                            jam_id=jam.id,
                            song_id=song.id
                        )
                        db.add(jam_song)
                    print(f"✅ Added {len(jam_songs)} songs to {jam.name}")
                
                await db.commit()
                print(f"\n🎵 Development Database Initialization Complete:")
                print(f"   Created: {len(songs)} popular songs")
                print(f"   Created: {len(venues)} venues")
                print(f"   Created: {len(created_jams)} diverse jams")
                print(f"   Today's jam: 'Today's Acoustic Session' (active)")
                print(f"   Jams with background images: {len([j for j in jams_data if j['background_image']])}")
                
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
