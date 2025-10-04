#!/usr/bin/env python3
"""
SQLite database initialization script
"""

import asyncio
import aiosqlite
import os
from datetime import date

async def init_sqlite_database() -> None:
    """Initialize SQLite database with schema and sample data"""
    
    db_path = "jamanager.db"
    
    try:
        # Remove existing database file
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ Removed existing database file")
        
        # Read and execute the schema file
        with open('schema_sqlite.sql', 'r') as f:
            schema_sql = f.read()
        
        async with aiosqlite.connect(db_path) as db:
            # Execute schema
            await db.executescript(schema_sql)
            await db.commit()
            print("✅ Database schema created successfully")
            
            # Create sample data
            await create_sample_data(db)
            
        print("✅ SQLite database initialization completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def create_sample_data(db) -> None:
    """Create sample data for testing"""
    
    # Create sample venues
    venues_data = [
        ("The Jazz Club", "123 Music Street, Sydney NSW 2000", "Intimate jazz and blues venue"),
        ("Rock Arena", "456 Rock Boulevard, Sydney NSW 2000", "Large venue for rock concerts")
    ]
    
    venue_ids = []
    for venue_data in venues_data:
        cursor = await db.execute(
            "INSERT INTO venues (name, address, description) VALUES (?, ?, ?) RETURNING id",
            venue_data
        )
        venue_id = await cursor.fetchone()
        venue_ids.append(venue_id[0])
        print(f"✅ Created venue: {venue_data[0]}")
    
    # Create popular cover songs for development
    songs_data = [
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
    
    song_ids = []
    for song_data in songs_data:
        title, artist, chord_sheet_url = song_data
        cursor = await db.execute(
            "INSERT INTO songs (title, artist, chord_sheet_url) VALUES (?, ?, ?) RETURNING id",
            (title, artist, chord_sheet_url)
        )
        song_id = await cursor.fetchone()
        song_ids.append(song_id[0])
        print(f"✅ Created song: {title} by {artist}")
    
    # Create sample jam with proper slug format (name-venue-date)
    cursor = await db.execute(
        "INSERT INTO jams (name, slug, description, venue_id, jam_date) VALUES (?, ?, ?, ?, ?) RETURNING id",
        ("Friday Night Jam", "friday-night-jam-the-jazz-club-2025-10-03", "Weekly jam session", venue_ids[0], "2025-10-03")
    )
    jam_id = await cursor.fetchone()
    jam_id = jam_id[0]
    print(f"✅ Created jam: Friday Night Jam")
    
    # Add songs to jam
    for song_id in song_ids:
        await db.execute(
            "INSERT INTO jam_songs (jam_id, song_id) VALUES (?, ?)",
            (jam_id, song_id)
        )
    print(f"✅ Added {len(song_ids)} songs to jam")
    
    await db.commit()
    print("✅ Sample data created successfully")

if __name__ == "__main__":
    asyncio.run(init_sqlite_database())
