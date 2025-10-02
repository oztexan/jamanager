#!/usr/bin/env python3
"""
Database initialization script for Jamanager FastAPI app
Run this to create tables and add sample data
"""

import asyncio
from datetime import datetime
from jamanager.database import init_database, AsyncSessionLocal
from jamanager.models import Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration, Venue

async def create_sample_data():
    """Create sample data for testing"""
    async with AsyncSessionLocal() as session:
        # Create sample venues
        venues_data = [
            {
                "name": "The Blue Note",
                "address": "123 Music Street, Sydney NSW 2000",
                "description": "Intimate jazz and blues venue"
            },
            {
                "name": "Rock Arena",
                "address": "456 Rock Boulevard, Sydney NSW 2000", 
                "description": "Large venue for rock concerts"
            }
        ]
        
        venues = []
        for venue_data in venues_data:
            venue = Venue(**venue_data)
            session.add(venue)
            venues.append(venue)
        
        await session.flush()  # Get the IDs
        
        # Create sample songs
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
            venue_id=venues[0].id,  # Use the first venue
            jam_date=datetime.now(),
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
        print(f"Created {len(venues)} venues")
        print(f"Created jam: {jam.name} (slug: {jam.slug}) at {venues[0].name}")
        print(f"Created {len(songs)} songs")

async def main():
    """Main initialization function"""
    print("🚀 Initializing Jamanager database...")
    
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

