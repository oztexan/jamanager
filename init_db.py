#!/usr/bin/env python3
"""
Database initialization script for Jamanger FastAPI app
Run this to create tables and add sample data
"""

import asyncio
import uuid
from datetime import datetime
from database import init_database, AsyncSessionLocal
from models import Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration

async def create_sample_data():
    """Create sample data for testing"""
    async with AsyncSessionLocal() as session:
        # Create sample songs
        songs_data = [
            {
                "title": "Sweet Child O' Mine",
                "artist": "Guns N' Roses",
                "type": "rock",
                "chord_chart": "D C G D",
                "tags": ["classic", "guitar", "popular"],
                "vote_count": 15
            },
            {
                "title": "Hotel California",
                "artist": "Eagles",
                "type": "rock",
                "chord_chart": "Am E G D F C Dm E",
                "tags": ["classic", "acoustic", "popular"],
                "vote_count": 12
            },
            {
                "title": "Wonderwall",
                "artist": "Oasis",
                "type": "rock",
                "chord_chart": "Em G D C Em G D C",
                "tags": ["90s", "acoustic", "popular"],
                "vote_count": 8
            },
            {
                "title": "Black",
                "artist": "Pearl Jam",
                "type": "grunge",
                "chord_chart": "Am F C G",
                "tags": ["grunge", "emotional", "popular"],
                "vote_count": 10
            }
        ]
        
        songs = []
        for song_data in songs_data:
            song = Song(**song_data)
            session.add(song)
            songs.append(song)
        
        await session.flush()  # Get the IDs
        
        # Create a sample jam
        jam = Jam(
            name="Friday Night Jam",
            slug="friday-night-jam",
            description="Our weekly jam session",
            status="waiting"
        )
        session.add(jam)
        await session.flush()
        
        # Add songs to the jam
        for i, song in enumerate(songs):
            jam_song = JamSong(
                jam_id=jam.id,
                song_id=song.id,
                captains=[] if i % 2 == 0 else ["captain1", "captain2"],
                played=False
            )
            session.add(jam_song)
        
        await session.commit()
        print("✅ Sample data created successfully!")
        print(f"Created jam: {jam.name} (slug: {jam.slug})")
        print(f"Created {len(songs)} songs")

async def main():
    """Main initialization function"""
    print("🚀 Initializing Jamanger database...")
    
    # Create tables
    await init_database()
    print("✅ Database tables created")
    
    # Create sample data
    await create_sample_data()
    
    print("🎉 Database initialization complete!")
    print("\nYou can now start the FastAPI server with:")
    print("uvicorn main:app --reload --port 8000")

if __name__ == "__main__":
    asyncio.run(main())

