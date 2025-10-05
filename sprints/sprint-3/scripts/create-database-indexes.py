#!/usr/bin/env python3
"""
Database Index Creation Script for Sprint 3
Creates performance-optimized indexes for frequently queried columns.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from core.database import AsyncSessionLocal

async def create_performance_indexes():
    """Create database indexes for performance optimization."""
    
    print("🚀 Sprint 3: Creating Database Indexes")
    print("=" * 50)
    
    # Define indexes to create
    indexes = [
        # Jam table indexes
        ("jams", "idx_jams_slug", "CREATE INDEX IF NOT EXISTS idx_jams_slug ON jams(slug)"),
        ("jams", "idx_jams_venue_id", "CREATE INDEX IF NOT EXISTS idx_jams_venue_id ON jams(venue_id)"),
        ("jams", "idx_jams_created_at", "CREATE INDEX IF NOT EXISTS idx_jams_created_at ON jams(created_at DESC)"),
        ("jams", "idx_jams_status", "CREATE INDEX IF NOT EXISTS idx_jams_status ON jams(status)"),
        
        # JamSong table indexes
        ("jam_songs", "idx_jam_songs_jam_id", "CREATE INDEX IF NOT EXISTS idx_jam_songs_jam_id ON jam_songs(jam_id)"),
        ("jam_songs", "idx_jam_songs_song_id", "CREATE INDEX IF NOT EXISTS idx_jam_songs_song_id ON jam_songs(song_id)"),
        ("jam_songs", "idx_jam_songs_played", "CREATE INDEX IF NOT EXISTS idx_jam_songs_played ON jam_songs(played)"),
        
        # Vote table indexes
        ("votes", "idx_votes_jam_id", "CREATE INDEX IF NOT EXISTS idx_votes_jam_id ON votes(jam_id)"),
        ("votes", "idx_votes_song_id", "CREATE INDEX IF NOT EXISTS idx_votes_song_id ON votes(song_id)"),
        ("votes", "idx_votes_attendee_id", "CREATE INDEX IF NOT EXISTS idx_votes_attendee_id ON votes(attendee_id)"),
        ("votes", "idx_votes_jam_song", "CREATE INDEX IF NOT EXISTS idx_votes_jam_song ON votes(jam_id, song_id)"),
        
        # Song table indexes
        ("songs", "idx_songs_title", "CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title)"),
        ("songs", "idx_songs_artist", "CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)"),
        ("songs", "idx_songs_times_played", "CREATE INDEX IF NOT EXISTS idx_songs_times_played ON songs(times_played DESC)"),
        
        # Venue table indexes
        ("venues", "idx_venues_name", "CREATE INDEX IF NOT EXISTS idx_venues_name ON venues(name)"),
        
        # JamChordSheet table indexes
        ("jam_chord_sheets", "idx_jam_chord_sheets_jam_id", "CREATE INDEX IF NOT EXISTS idx_jam_chord_sheets_jam_id ON jam_chord_sheets(jam_id)"),
        ("jam_chord_sheets", "idx_jam_chord_sheets_song_id", "CREATE INDEX IF NOT EXISTS idx_jam_chord_sheets_song_id ON jam_chord_sheets(song_id)"),
        ("jam_chord_sheets", "idx_jam_chord_sheets_jam_song", "CREATE INDEX IF NOT EXISTS idx_jam_chord_sheets_jam_song ON jam_chord_sheets(jam_id, song_id)"),
    ]
    
    async with AsyncSessionLocal() as db:
        created_count = 0
        skipped_count = 0
        
        for table, index_name, sql in indexes:
            try:
                # Check if index already exists
                check_result = await db.execute(text(f"PRAGMA index_list('{table}')"))
                existing_indexes = [row[1] for row in check_result.fetchall()]
                
                if index_name in existing_indexes:
                    print(f"   ⏭️  {index_name} already exists")
                    skipped_count += 1
                else:
                    await db.execute(text(sql))
                    await db.commit()
                    print(f"   ✅ Created {index_name}")
                    created_count += 1
                    
            except Exception as e:
                print(f"   ❌ Failed to create {index_name}: {e}")
                await db.rollback()
        
        print(f"\n📊 Index Creation Summary:")
        print(f"   Created: {created_count} indexes")
        print(f"   Skipped: {skipped_count} indexes")
        print(f"   Total: {len(indexes)} indexes")
        
        # Show current index status
        print(f"\n📋 Current Index Status:")
        tables = ["jams", "songs", "venues", "jam_songs", "votes", "jam_chord_sheets"]
        
        for table in tables:
            result = await db.execute(text(f"PRAGMA index_list('{table}')"))
            indexes = result.fetchall()
            print(f"   {table}: {len(indexes)} indexes")

async def main():
    """Main function to create database indexes."""
    try:
        await create_performance_indexes()
        print("\n✅ Database index creation complete!")
        print("\n🎯 Performance Benefits:")
        print("   - Faster jam lookups by slug")
        print("   - Optimized venue and song queries")
        print("   - Improved vote counting performance")
        print("   - Better sorting and filtering")
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")

if __name__ == "__main__":
    asyncio.run(main())

