#!/usr/bin/env python3
"""
Test script to verify SQLite database is working
"""

import asyncio
import aiosqlite
import os

async def test_database():
    """Test the SQLite database connection and data"""
    
    db_path = "backend/jamanager.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        async with aiosqlite.connect(db_path) as db:
            print("✅ Connected to SQLite database")
            
            # Test basic queries
            cursor = await db.execute("SELECT COUNT(*) FROM songs")
            song_count = await cursor.fetchone()
            print(f"✅ Songs in database: {song_count[0]}")
            
            cursor = await db.execute("SELECT COUNT(*) FROM jams")
            jam_count = await cursor.fetchone()
            print(f"✅ Jams in database: {jam_count[0]}")
            
            cursor = await db.execute("SELECT COUNT(*) FROM venues")
            venue_count = await cursor.fetchone()
            print(f"✅ Venues in database: {venue_count[0]}")
            
            # Test a sample query
            cursor = await db.execute("SELECT title, artist FROM songs LIMIT 3")
            songs = await cursor.fetchall()
            print("✅ Sample songs:")
            for song in songs:
                print(f"   - {song[0]} by {song[1]}")
            
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database())
    if success:
        print("\n🎉 Database test completed successfully!")
    else:
        print("\n💥 Database test failed!")
