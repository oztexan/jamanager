#!/usr/bin/env python3
"""
Reset database script - clears all data and reinitializes with fresh sample data
"""

import asyncio
from jamanager.database import AsyncSessionLocal, engine
from jamanager.models import Base

async def clear_database() -> None:
    """Clear all data from the database"""
    print("🗑️  Clearing existing data...")
    
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ All tables dropped")
        
        # Recreate all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables recreated")

async def main() -> None:
    """Main reset function"""
    print("🔄 Resetting JaManager database...")
    
    # Clear existing data
    await clear_database()
    
    # Reinitialize with fresh data
    print("🚀 Reinitializing with fresh data...")
    from init_db import create_sample_data
    await create_sample_data()
    
    print("🎉 Database reset complete!")
    print("All songs now start with 0 votes as expected.")

if __name__ == "__main__":
    asyncio.run(main())
