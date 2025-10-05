#!/usr/bin/env python3
"""
Performance Analysis Script for Sprint 3
Analyzes current database queries and identifies optimization opportunities.
"""

import asyncio
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from core.database import AsyncSessionLocal
from models.database import Jam, Song, Venue, JamSong, Vote

async def analyze_query_performance():
    """Analyze the performance of key database queries."""
    
    print("🔍 Sprint 3: Performance Analysis")
    print("=" * 50)
    
    async with AsyncSessionLocal() as db:
        # Test 1: Get all jams with song counts (current implementation)
        print("\n📊 Test 1: Get All Jams with Song Counts")
        start_time = time.time()
        
        result = await db.execute(select(Jam).order_by(Jam.created_at.desc()))
        jams = result.scalars().all()
        
        jam_list = []
        for jam in jams:
            # Get song count for each jam (N+1 query problem)
            song_count_result = await db.execute(
                select(func.count(JamSong.id)).where(JamSong.jam_id == jam.id)
            )
            song_count = song_count_result.scalar()
            
            # Get venue information (N+1 query problem)
            venue_result = await db.execute(select(Venue).where(Venue.id == jam.venue_id))
            venue = venue_result.scalar_one_or_none()
            
            jam_list.append({
                "id": str(jam.id),
                "name": jam.name,
                "song_count": song_count,
                "venue_name": venue.name if venue else "Unknown"
            })
        
        current_time = time.time() - start_time
        print(f"   Current Implementation: {current_time:.3f}s for {len(jams)} jams")
        print(f"   Queries executed: {1 + len(jams) * 2} (1 + {len(jams)}*2)")
        
        # Test 2: Optimized version with joins
        print("\n📊 Test 2: Optimized Get All Jams")
        start_time = time.time()
        
        # Single query with joins and aggregation
        optimized_result = await db.execute(
            select(
                Jam.id,
                Jam.name,
                Jam.slug,
                Jam.description,
                Jam.venue_id,
                Venue.name.label('venue_name'),
                Jam.jam_date,
                Jam.background_image,
                Jam.status,
                Jam.created_at,
                Jam.updated_at,
                func.count(JamSong.id).label('song_count')
            )
            .join(Venue, Jam.venue_id == Venue.id)
            .outerjoin(JamSong, Jam.id == JamSong.jam_id)
            .group_by(Jam.id, Venue.name)
            .order_by(Jam.created_at.desc())
        )
        
        optimized_jams = optimized_result.all()
        optimized_time = time.time() - start_time
        
        print(f"   Optimized Implementation: {optimized_time:.3f}s for {len(optimized_jams)} jams")
        print(f"   Queries executed: 1")
        print(f"   Performance improvement: {((current_time - optimized_time) / current_time * 100):.1f}%")
        
        # Test 3: Get jam by slug with songs (current implementation)
        print("\n📊 Test 3: Get Jam by Slug with Songs")
        if jams:
            test_jam = jams[0]
            start_time = time.time()
            
            # Current implementation
            jam_result = await db.execute(
                select(Jam, Venue)
                .join(Venue, Jam.venue_id == Venue.id)
                .where(Jam.slug == test_jam.slug)
            )
            jam_data = jam_result.first()
            
            if jam_data:
                jam, venue = jam_data
                
                # Get jam songs with song details
                jam_songs_result = await db.execute(
                    select(JamSong, Song)
                    .join(Song, JamSong.song_id == Song.id)
                    .where(JamSong.jam_id == jam.id)
                )
                jam_songs_data = jam_songs_result.all()
                
                # Get vote counts for each song (N+1 query problem)
                songs = []
                for jam_song, song in jam_songs_data:
                    vote_count_result = await db.execute(
                        select(func.count(Vote.id))
                        .where(Vote.jam_id == jam.id, Vote.song_id == song.id)
                    )
                    vote_count = vote_count_result.scalar() or 0
                    songs.append({
                        "song_id": song.id,
                        "title": song.title,
                        "vote_count": vote_count
                    })
            
            current_time = time.time() - start_time
            print(f"   Current Implementation: {current_time:.3f}s")
            print(f"   Queries executed: 2 + {len(songs)} (for vote counts)")
            
            # Test 4: Database statistics
            print("\n📊 Test 4: Database Statistics")
            
            # Count records
            jam_count = await db.execute(select(func.count(Jam.id)))
            song_count = await db.execute(select(func.count(Song.id)))
            venue_count = await db.execute(select(func.count(Venue.id)))
            vote_count = await db.execute(select(func.count(Vote.id)))
            
            print(f"   Total Jams: {jam_count.scalar()}")
            print(f"   Total Songs: {song_count.scalar()}")
            print(f"   Total Venues: {venue_count.scalar()}")
            print(f"   Total Votes: {vote_count.scalar()}")
            
            # Check for missing indexes
            print("\n📊 Test 5: Index Analysis")
            index_result = await db.execute(text("PRAGMA index_list('jams')"))
            jam_indexes = index_result.fetchall()
            print(f"   Jam table indexes: {len(jam_indexes)}")
            
            index_result = await db.execute(text("PRAGMA index_list('songs')"))
            song_indexes = index_result.fetchall()
            print(f"   Song table indexes: {len(song_indexes)}")
            
            index_result = await db.execute(text("PRAGMA index_list('votes')"))
            vote_indexes = index_result.fetchall()
            print(f"   Vote table indexes: {len(vote_indexes)}")

async def main():
    """Main function to run performance analysis."""
    try:
        await analyze_query_performance()
        print("\n✅ Performance analysis complete!")
        print("\n🎯 Key Optimization Opportunities:")
        print("   1. N+1 Query Problem in get_all_jams()")
        print("   2. N+1 Query Problem in get_jam_by_slug()")
        print("   3. Missing database indexes")
        print("   4. No caching for frequently accessed data")
        print("   5. No query result pagination")
        
    except Exception as e:
        print(f"❌ Error during performance analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())

