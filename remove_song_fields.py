#!/usr/bin/env python3
"""
Database migration script to remove genre, chord_chart, and tags fields from songs table
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def remove_song_fields():
    """Remove genre, chord_chart, and tags columns from songs table"""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamanager123@localhost:5432/jamanager")
    
    conn = None
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check which columns exist
        columns_to_remove = ['type', 'chord_chart', 'tags']
        
        for column in columns_to_remove:
            column_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'songs' AND column_name = $1
                );
                """,
                column
            )
            
            if column_exists:
                await conn.execute(f"ALTER TABLE songs DROP COLUMN {column};")
                print(f"✅ Removed column '{column}' from songs table")
            else:
                print(f"ℹ️ Column '{column}' does not exist in songs table")
        
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(remove_song_fields())
