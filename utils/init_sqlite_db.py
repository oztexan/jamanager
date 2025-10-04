#!/usr/bin/env python3
"""
SQLite database initialization script
"""

import asyncio
import aiosqlite
import os
from datetime import date

async def init_sqlite_database():
    """Initialize SQLite database with schema and sample data"""
    
    db_path = "backend/jamanager.db"
    
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

async def create_sample_data(db):
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
    
    # Create sample songs (simplified)
    songs_data = [
        ("Sweet Child O' Mine", "Guns N' Roses"),
        ("Hotel California", "Eagles"),
        ("Wonderwall", "Oasis"),
        ("Black", "Pearl Jam")
    ]
    
    song_ids = []
    for song_data in songs_data:
        cursor = await db.execute(
            "INSERT INTO songs (title, artist) VALUES (?, ?) RETURNING id",
            song_data
        )
        song_id = await cursor.fetchone()
        song_ids.append(song_id[0])
        print(f"✅ Created song: {song_data[0]} by {song_data[1]}")
    
    # Create sample jam
    cursor = await db.execute(
        "INSERT INTO jams (name, slug, description, venue_id, jam_date) VALUES (?, ?, ?, ?, ?) RETURNING id",
        ("Friday Night Jam", "friday-night-jam", "Weekly jam session", venue_ids[0], "2025-10-03")
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
