#!/usr/bin/env python3
"""
Reset test data script for Jamanager
This script deletes all existing jams and creates new test data with mandatory fields.
"""

import asyncio
import os
import sys
from datetime import date, datetime
from sqlalchemy import delete, text, select

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_database
from models.database import Jam, Song, JamSong, Attendee, Vote, PerformanceRegistration

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
                    chord_sheet_url="https://www.ultimate-guitar.com/tab/oasis/wonderwall-crd-257797"
                ),
                Song(
                    title="Hotel California",
                    artist="Eagles",
                    chord_sheet_url="https://www.ultimate-guitar.com/tab/eagles/hotel-california-crd-257797"
                ),
                Song(
                    title="Sweet Child O' Mine",
                    artist="Guns N' Roses",
                    chord_sheet_url="https://www.ultimate-guitar.com/tab/guns-n-roses/sweet-child-o-mine-crd-257797"
                ),
                Song(
                    title="Bohemian Rhapsody",
                    artist="Queen",
                    chord_sheet_url="https://www.ultimate-guitar.com/tab/queen/bohemian-rhapsody-crd-257797"
                ),
                Song(
                    title="Stairway to Heaven",
                    artist="Led Zeppelin",
                    chord_sheet_url="https://www.ultimate-guitar.com/tab/led-zeppelin/stairway-to-heaven-crd-257797"
                )
            ]
            
            for song in test_songs:
                db.add(song)
            
            await db.commit()
            print("   - Created 5 test songs")
            
            # Create test venues first
            from models.database import Venue
            test_venues = [
                Venue(
                    name="Main Stage",
                    address="123 Music Street, City, State 12345",
                    description="Large performance venue with professional sound system"
                ),
                Venue(
                    name="Coffee House",
                    address="456 Acoustic Ave, City, State 12345", 
                    description="Intimate coffee shop perfect for acoustic performances"
                ),
                Venue(
                    name="Studio A",
                    address="789 Recording Blvd, City, State 12345",
                    description="Professional recording studio with practice space"
                )
            ]
            
            for venue in test_venues:
                db.add(venue)
            
            await db.commit()
            print("   - Created 3 test venues")
            
            # Get venue IDs for jam creation
            venue_result = await db.execute(select(Venue))
            venues = venue_result.scalars().all()
            main_stage_id = venues[0].id
            coffee_house_id = venues[1].id
            studio_a_id = venues[2].id
            
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
                    venue_id=main_stage_id,
                    jam_date=today,
                    status="waiting"
                ),
                Jam(
                    name="Acoustic Evening",
                    slug="acoustic-evening-coffee-house-2025-10-02",
                    description="Intimate acoustic performance night",
                    venue_id=coffee_house_id,
                    jam_date=today,
                    status="waiting"
                ),
                Jam(
                    name="Rock Workshop",
                    slug="rock-workshop-studio-a-2025-10-03",
                    description="Learn rock techniques and jam together",
                    venue_id=studio_a_id,
                    jam_date=tomorrow,
                    status="waiting"
                ),
                Jam(
                    name="Jazz Night",
                    slug="jazz-night-club-2025-10-01",
                    description="Smooth jazz and improvisation",
                    venue_id=main_stage_id,
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
            
        except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
            print(f"❌ Error resetting test data: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()

if __name__ == "__main__":
    asyncio.run(reset_test_data())
