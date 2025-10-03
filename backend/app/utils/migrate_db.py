"""
Database Migration Script

This script adds the new columns to the jams table for enhanced jam creation.
"""

import asyncio
import asyncpg
from database import get_database_url

async def migrate_database():
    """Add new columns to the jams table"""
    
    # Get database URL
    database_url = get_database_url()
    
    # Connect to database
    conn = await asyncpg.connect(database_url)
    
    try:
        # Add new columns to jams table
        await conn.execute("""
            ALTER TABLE jams 
            ADD COLUMN IF NOT EXISTS location VARCHAR(255),
            ADD COLUMN IF NOT EXISTS jam_date DATE,
            ADD COLUMN IF NOT EXISTS background_image VARCHAR(500)
        """)
        
        print("✅ Successfully added new columns to jams table:")
        print("   - location (VARCHAR(255))")
        print("   - jam_date (DATE)")
        print("   - background_image (VARCHAR(500))")
        
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_database())
