#!/usr/bin/env python3
"""
Add chord_sheet_url column to songs table
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def add_chord_sheet_url_column():
    """Add chord_sheet_url column to songs table"""
    
    # Database connection
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamanager123@localhost:5432/jamanager")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Check if column already exists
        check_query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'songs' AND column_name = 'chord_sheet_url'
        """
        result = await conn.fetch(check_query)
        
        if result:
            print("✅ Column 'chord_sheet_url' already exists")
        else:
            # Add the column
            alter_query = """
            ALTER TABLE songs 
            ADD COLUMN chord_sheet_url VARCHAR(500)
            """
            await conn.execute(alter_query)
            print("✅ Added 'chord_sheet_url' column to songs table")
        
        await conn.close()
        print("✅ Database migration completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(add_chord_sheet_url_column())
