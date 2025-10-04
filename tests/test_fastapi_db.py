#!/usr/bin/env python3
"""
Test FastAPI database connection
"""

import asyncio
from core.database import get_database, AsyncSessionLocal
from models.database import Song

async def test_fastapi_db() -> None:
    """Test FastAPI database connection"""
    
    try:
        print("🔍 Testing FastAPI database connection...")
        
        # Test the database dependency
        async for db in get_database():
            print("✅ Database dependency works")
            
            # Test a simple query
            from sqlalchemy import select
            result = await db.execute(select(Song))
            songs = result.scalars().all()
            print(f"✅ Found {len(songs)} songs in database")
            
            for song in songs:
                print(f"  - {song.title} by {song.artist}")
            
            break
        
        print("✅ FastAPI database test completed successfully")
        
    except Exception as e:
        print(f"❌ FastAPI database test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastapi_db())
