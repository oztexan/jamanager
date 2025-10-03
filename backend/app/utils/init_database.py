#!/usr/bin/env python3
"""
Database initialization script using the consolidated schema
"""

import asyncio
import asyncpg
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

async def init_database():
    """Initialize database with the consolidated schema"""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamanager123@localhost:5432/jamanager")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Read and execute the schema file
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        await conn.execute(schema_sql)
        print("✅ Database schema created successfully")
        
        # Create sample data
        await create_sample_data(conn)
        
        print("✅ Database initialization completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            await conn.close()

async def create_sample_data(conn):
    """Create sample data for testing"""
    
    # Create sample venues
    venues_data = [
        {
            "name": "The Jazz Club",
            "address": "123 Music Street, Sydney NSW 2000",
            "description": "Intimate jazz and blues venue"
        },
        {
            "name": "Rock Arena",
            "address": "456 Rock Boulevard, Sydney NSW 2000", 
            "description": "Large venue for rock concerts"
        }
    ]
    
    venue_ids = []
    for venue_data in venues_data:
        venue_id = await conn.fetchval(
            "INSERT INTO venues (name, address, description) VALUES ($1, $2, $3) RETURNING id",
            venue_data["name"], venue_data["address"], venue_data["description"]
        )
        venue_ids.append(venue_id)
        print(f"✅ Created venue: {venue_data['name']}")
    
    # Create sample songs (simplified)
    songs_data = [
        {
            "title": "Sweet Child O' Mine",
            "artist": "Guns N' Roses",
            "vote_count": 0
        },
        {
            "title": "Hotel California",
            "artist": "Eagles",
            "vote_count": 0
        },
        {
            "title": "Wonderwall",
            "artist": "Oasis",
            "vote_count": 0
        },
        {
            "title": "Black",
            "artist": "Pearl Jam",
            "vote_count": 0
        }
    ]
    
    song_ids = []
    for song_data in songs_data:
        song_id = await conn.fetchval(
            "INSERT INTO songs (title, artist, vote_count) VALUES ($1, $2, $3) RETURNING id",
            song_data["title"], song_data["artist"], song_data["vote_count"]
        )
        song_ids.append(song_id)
        print(f"✅ Created song: {song_data['title']} by {song_data['artist']}")
    
    # Create sample jam
    jam_id = await conn.fetchval(
        "INSERT INTO jams (name, slug, description, venue_id, jam_date) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        "Friday Night Jam",
        "friday-night-jam",
        "Weekly jam session",
        venue_ids[0],
        date(2025, 10, 3)
    )
    print(f"✅ Created jam: Friday Night Jam")
    
    # Add songs to jam
    for song_id in song_ids:
        await conn.execute(
            "INSERT INTO jam_songs (jam_id, song_id) VALUES ($1, $2)",
            jam_id, song_id
        )
    print(f"✅ Added {len(song_ids)} songs to jam")
    
    print("✅ Sample data created successfully")

if __name__ == "__main__":
    asyncio.run(init_database())
