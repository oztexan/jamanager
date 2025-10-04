#!/usr/bin/env python3
"""
Test SQLite database connection and model compatibility
"""

import asyncio
import aiosqlite
import os
from dotenv import load_dotenv

load_dotenv()

async def test_database():
    """Test SQLite database connection and schema"""
    
    db_path = "jamanager.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        async with aiosqlite.connect(db_path) as conn:
            print("✅ Connected to SQLite database")
            
            # Check if songs table exists and has the right columns
            cursor = await conn.execute("PRAGMA table_info(songs)")
            columns = await cursor.fetchall()
            
            print("📋 Songs table columns:")
            for col in columns:
                print(f"  - {col[1]}: {col[2]}")
            
            # Check if there are any old columns that shouldn't be there
            old_columns = ['type', 'chord_chart', 'tags']
            existing_columns = [col[1] for col in columns]
            
            for old_col in old_columns:
                if old_col in existing_columns:
                    print(f"❌ Found old column: {old_col}")
                else:
                    print(f"✅ Old column removed: {old_col}")
            
            # Test a simple query
            cursor = await conn.execute("SELECT COUNT(*) FROM songs")
            count = await cursor.fetchone()
            print(f"📊 Songs count: {count[0]}")
            
            # Test inserting a song
            cursor = await conn.execute("""
                INSERT INTO songs (id, title, artist) 
                VALUES (?, ?, ?) 
                RETURNING id
            """, ("test-song-123", "Test Song", "Test Artist"))
            
            song_id = cursor.lastrowid
            print(f"✅ Successfully inserted song with ID: {song_id}")
            
            # Clean up
            await conn.execute("DELETE FROM songs WHERE id = ?", ("test-song-123",))
            await conn.commit()
            print("✅ Cleaned up test song")
            
            print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_database())