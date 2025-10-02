#!/usr/bin/env python3
"""
Reset test data script for Jamanager
This script deletes all existing jams and creates new test data with mandatory fields.
"""

import asyncio
import os
from datetime import date, datetime
from sqlalchemy import delete, text
from database import get_database
from models import Jam, Song, JamSong, Attendee, Vote, PerformanceRegistration

async def reset_test_data():
    """Delete all existing data and create new test data"""
    print("🗑️  Resetting test data...")
    
    # Get database session
    async for db in get_database():
        try:
            # Delete all data in correct order (respecting foreign key constraints)
            print("   - Deleting votes...")
            await db.execute(delete(Vote))
            
            print("   - Deleting performance registrations...")
            await db.execute(delete(PerformanceRegistration))
            
            print("   - Deleting attendees...")
            await db.execute(delete(Attendee))
            
            print("   - Deleting jam songs...")
            await db.execute(delete(JamSong))
            
            print("   - Deleting jams...")
            await db.execute(delete(Jam))
            
            print("   - Deleting songs...")
            await db.execute(delete(Song))
            
            # Commit deletions
            await db.commit()
            print("✅ All existing data deleted")
            
            # Create new test data
            print("📝 Creating new test data...")
            
            # Create test songs
            test_songs = [
                Song(
                    title="Wonderwall",
                    artist="Oasis",
                    type="rock",
                    tags=["rock", "classic", "acoustic"]
                ),
                Song(
                    title="Hotel California",
                    artist="Eagles",
                    type="rock",
                    tags=["rock", "classic", "guitar"]
                ),
                Song(
                    title="Sweet Child O' Mine",
                    artist="Guns N' Roses",
                    type="rock",
                    tags=["rock", "guitar", "classic"]
                ),
                Song(
                    title="Bohemian Rhapsody",
                    artist="Queen",
                    type="rock",
                    tags=["rock", "classic", "opera"]
                ),
                Song(
                    title="Stairway to Heaven",
                    artist="Led Zeppelin",
                    type="rock",
                    tags=["rock", "classic", "guitar"]
                )
            ]
            
            for song in test_songs:
                db.add(song)
            
            await db.commit()
            print("   - Created 5 test songs")
            
            # Create test jams with mandatory fields
            today = date(2025, 10, 2)  # Use 2025-10-02 for testing (current year)
            tomorrow = date(2025, 10, 3)
            yesterday = date(2025, 10, 1)
            
            # For testing empty state, only create jams for tomorrow
            test_today = tomorrow  # Use tomorrow as "today" to test empty state
            
            test_jams = [
                Jam(
                    name="Friday Night Jam",
                    slug="friday-night-jam-main-stage-2025-10-02",
                    description="Weekly community jam session",
                    location="Main Stage",
                    jam_date=today,
                    status="waiting"
                ),
                Jam(
                    name="Acoustic Evening",
                    slug="acoustic-evening-coffee-house-2025-10-02",
                    description="Intimate acoustic performance night",
                    location="Coffee House",
                    jam_date=today,
                    status="waiting"
                ),
                Jam(
                    name="Rock Workshop",
                    slug="rock-workshop-studio-a-2025-10-03",
                    description="Learn rock techniques and jam together",
                    location="Studio A",
                    jam_date=tomorrow,
                    status="waiting"
                ),
                Jam(
                    name="Jazz Night",
                    slug="jazz-night-club-2025-10-01",
                    description="Smooth jazz and improvisation",
                    location="Jazz Club",
                    jam_date=yesterday,
                    status="ended"
                )
            ]
            
            for jam in test_jams:
                db.add(jam)
            
            await db.commit()
            print("   - Created 4 test jams")
            
            # Add some songs to today's jams
            friday_jam = test_jams[0]
            acoustic_jam = test_jams[1]
            
            # Add songs to Friday Night Jam
            jam_songs_friday = [
                JamSong(jam_id=friday_jam.id, song_id=test_songs[0].id),
                JamSong(jam_id=friday_jam.id, song_id=test_songs[1].id),
                JamSong(jam_id=friday_jam.id, song_id=test_songs[2].id)
            ]
            
            # Add songs to Acoustic Evening
            jam_songs_acoustic = [
                JamSong(jam_id=acoustic_jam.id, song_id=test_songs[0].id),
                JamSong(jam_id=acoustic_jam.id, song_id=test_songs[3].id)
            ]
            
            for jam_song in jam_songs_friday + jam_songs_acoustic:
                db.add(jam_song)
            
            await db.commit()
            print("   - Added songs to jams")
            
            # Create some test attendees
            test_attendees = [
                Attendee(
                    name="Alice",
                    jam_id=friday_jam.id
                ),
                Attendee(
                    name="Bob",
                    jam_id=friday_jam.id
                ),
                Attendee(
                    name="Charlie",
                    jam_id=acoustic_jam.id
                )
            ]
            
            for attendee in test_attendees:
                db.add(attendee)
            
            await db.commit()
            print("   - Created 3 test attendees")
            
            # Create some test votes
            test_votes = [
                Vote(
                    jam_id=friday_jam.id,
                    song_id=test_songs[0].id,
                    attendee_id=test_attendees[0].id
                ),
                Vote(
                    jam_id=friday_jam.id,
                    song_id=test_songs[0].id,
                    attendee_id=test_attendees[1].id
                ),
                Vote(
                    jam_id=friday_jam.id,
                    song_id=test_songs[1].id,
                    attendee_id=test_attendees[0].id
                )
            ]
            
            for vote in test_votes:
                db.add(vote)
            
            await db.commit()
            print("   - Created test votes")
            
            print("✅ Test data reset complete!")
            print(f"   - {len(test_songs)} songs created")
            print(f"   - {len(test_jams)} jams created")
            print(f"   - {len(test_attendees)} attendees created")
            print(f"   - {len(test_votes)} votes created")
            print(f"   - Today's jams: {len([j for j in test_jams if j.jam_date == today])} (should be 2 for today's jams)")
            
        except Exception as e:
            print(f"❌ Error resetting test data: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(reset_test_data())
