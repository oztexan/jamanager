from typing import List, Dict, Optional, Union
#!/usr/bin/env python3
"""
Database migration script to add jam_chord_sheets table.
Run this script to add the new table to your existing database.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import engine, Base
from models.database import JamChordSheet

async def migrate_database() -> None:
    """Add the jam_chord_sheets table to the database."""
    try:
        print("🔄 Starting database migration...")
        
        # Create the jam_chord_sheets table
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, tables=[JamChordSheet.__table__])
        
        print("✅ Successfully added jam_chord_sheets table to the database!")
        print("📋 The new table includes:")
        print("   - id: Primary key")
        print("   - jam_id: Foreign key to jams table")
        print("   - song_id: Foreign key to songs table") 
        print("   - chord_sheet_url: Jam-specific chord sheet URL")
        print("   - title: Optional title for the chord sheet")
        print("   - rating: Optional rating from Ultimate Guitar")
        print("   - created_by: Foreign key to attendees table")
        print("   - created_at, updated_at: Timestamps")
        print("   - Unique constraint on jam_id + song_id")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(migrate_database())
