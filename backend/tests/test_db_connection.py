#!/usr/bin/env python3
"""
Test database connection and model compatibility
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test_database():
    """Test database connection and schema"""
    
    DATABASE_URL = "postgresql://postgres:jamanager123@localhost:5432/jamanager"
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check if songs table exists and has the right columns
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'songs' 
            ORDER BY ordinal_position
        """)
        
        print("📋 Songs table columns:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        # Check if there are any old columns that shouldn't be there
        old_columns = ['type', 'chord_chart', 'tags']
        existing_columns = [col['column_name'] for col in columns]
        
        for old_col in old_columns:
            if old_col in existing_columns:
                print(f"❌ Found old column: {old_col}")
            else:
                print(f"✅ Old column removed: {old_col}")
        
        # Test a simple query
        count = await conn.fetchval("SELECT COUNT(*) FROM songs")
        print(f"📊 Songs count: {count}")
        
        # Test inserting a song
        song_id = await conn.fetchval("""
            INSERT INTO songs (title, artist) 
            VALUES ($1, $2) 
            RETURNING id
        """, "Test Song", "Test Artist")
        
        print(f"✅ Successfully inserted song with ID: {song_id}")
        
        # Clean up
        await conn.execute("DELETE FROM songs WHERE id = $1", song_id)
        print("✅ Cleaned up test song")
        
        await conn.close()
        print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_database())
