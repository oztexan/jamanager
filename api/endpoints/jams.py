"""
Jam-related API endpoints for the Jamanager application.
"""
import logging
import qrcode
import io
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func

from core.database import get_database
from core.slug_utils import generate_jam_slug, make_slug_unique
from core.image_utils import ImageUploader
from core.auth_middleware import can_vote, can_register_to_perform, can_play_songs
from models.database import (
    Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration, Venue,
    SongInDB, JamInDB, SongUpdate, VenueInDB, VenueCreate, VenueUpdate, JamInDBWithVenue
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jams", tags=["jams"])

@router.post("")
async def create_jam(
    name: str = Form(...),
    description: str = Form(""),
    venue_id: str = Form(...),
    jam_date: str = Form(...),
    background_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_database)
):
    """Create a new jam with enhanced fields"""
    try:
        if not name:
            raise HTTPException(status_code=400, detail="Jam name is required")
        
        if not venue_id:
            raise HTTPException(status_code=400, detail="Venue is required")
        
        if not jam_date:
            raise HTTPException(status_code=400, detail="Date is required")
        
        # Parse jam_date
        try:
            parsed_date = date.fromisoformat(jam_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Handle background image upload
        background_image_path = None
        if background_image and background_image.filename:
            # Validate image
            is_valid, error_msg = ImageUploader.validate_image(background_image)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Get venue information for slug generation
        venue_result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = venue_result.scalar_one_or_none()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        # Generate user-friendly slug using venue name
        slug = generate_jam_slug(name, venue.name, parsed_date)
        
        # Ensure slug is unique
        existing_slugs = []
        result = await db.execute(select(Jam.slug))
        existing_slugs = [row[0] for row in result.fetchall()]
        slug = make_slug_unique(slug, existing_slugs)
        
        # Create new jam
        new_jam = Jam(
            name=name,
            slug=slug,
            description=description,
            venue_id=venue_id,
            jam_date=parsed_date,
            status="waiting"
        )
        
        db.add(new_jam)
        await db.commit()
        await db.refresh(new_jam)
        
        # Save background image after jam is created (so we have the jam_id)
        if background_image and background_image.filename:
            try:
                background_image_path = ImageUploader.save_image(background_image, str(new_jam.id))
                # Update jam with image path
                new_jam.background_image = background_image_path
                await db.commit()
                await db.refresh(new_jam)
            except Exception as e:
                # If image save fails, log the error but don't fail the jam creation
                logger.error(f"Failed to save background image for jam {new_jam.id}: {e}")
                # Set background_image to None so no broken reference is stored
                new_jam.background_image = None
                await db.commit()
                await db.refresh(new_jam)
        
        return {
            "id": str(new_jam.id),
            "name": new_jam.name,
            "slug": new_jam.slug,
            "description": new_jam.description,
            "venue_id": str(new_jam.venue_id),
            "venue_name": venue.name,
            "jam_date": new_jam.jam_date.isoformat() if new_jam.jam_date else None,
            "background_image": new_jam.background_image,
            "status": new_jam.status,
            "songs": [],
            "created_at": new_jam.created_at,
            "updated_at": new_jam.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("")
async def get_all_jams(db: AsyncSession = Depends(get_database)):
    """Get all jams"""
    try:
        result = await db.execute(select(Jam).order_by(Jam.created_at.desc()))
        jams = result.scalars().all()
        
        jam_list = []
        for jam in jams:
            # Get song count for each jam
            song_count_result = await db.execute(
                select(func.count(JamSong.id)).where(JamSong.jam_id == jam.id)
            )
            song_count = song_count_result.scalar()
            
            # Get venue information
            venue_result = await db.execute(select(Venue).where(Venue.id == jam.venue_id))
            venue = venue_result.scalar_one_or_none()
            
            jam_list.append({
                "id": str(jam.id),
                "name": jam.name,
                "slug": jam.slug,
                "description": jam.description,
                "venue_id": str(jam.venue_id),
                "venue_name": venue.name if venue else "Unknown Venue",
                "jam_date": jam.jam_date.isoformat() if jam.jam_date else None,
                "background_image": jam.background_image,
                "status": jam.status,
                "song_count": song_count,
                "created_at": jam.created_at,
                "updated_at": jam.updated_at
            })
        
        return jam_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/by-slug/{slug}", response_model=JamInDBWithVenue)
async def get_jam_by_slug(slug: str, db: AsyncSession = Depends(get_database)):
    """Get jam by slug with all songs"""
    # Get jam with venue information
    result = await db.execute(
        select(Jam, Venue)
        .join(Venue, Jam.venue_id == Venue.id)
        .where(Jam.slug == slug)
    )
    jam_data = result.first()
    
    if not jam_data:
        raise HTTPException(status_code=404, detail="Jam not found")
    
    jam, venue = jam_data
    
    # Get jam songs with song details
    jam_songs_result = await db.execute(
        select(JamSong, Song)
        .join(Song, JamSong.song_id == Song.id)
        .where(JamSong.jam_id == jam.id)
    )
    jam_songs_data = jam_songs_result.all()
    
    # Build the songs list with vote counts and other jam-specific data
    songs = []
    for jam_song, song in jam_songs_data:
        # Get vote count for this song in this jam
        vote_count_result = await db.execute(
            select(func.count(Vote.id))
            .where(Vote.jam_id == jam.id, Vote.song_id == song.id)
        )
        vote_count = vote_count_result.scalar() or 0
        
        # Create the nested structure that the client expects
        jam_song_dict = {
            "id": jam_song.id,
            "jam_id": jam_song.jam_id,
            "song_id": jam_song.song_id,
            "captains": jam_song.captains,
            "played": jam_song.played,
            "played_at": jam_song.played_at,
            "created_at": jam_song.created_at,
            "updated_at": jam_song.updated_at,
            "song": {
                "id": song.id,
                "title": song.title,
                "artist": song.artist,
                "chord_sheet_url": song.chord_sheet_url,
                "vote_count": vote_count,
                "times_played": song.times_played,
                "last_played": song.last_played,
                "created_at": song.created_at,
                "updated_at": song.updated_at
            }
        }
        songs.append(jam_song_dict)
    
    # Sort songs by vote count (highest first)
    songs.sort(key=lambda x: x["song"]["vote_count"], reverse=True)
    
    # Create the response
    jam_in_db = JamInDBWithVenue.from_orm(jam)
    jam_in_db.venue = venue
    jam_in_db.songs = songs
    
    return jam_in_db

@router.get("/{jam_id}/qr")
async def get_jam_qr_code(jam_id: str, db: AsyncSession = Depends(get_database)):
    """Generate QR code for jam access"""
    try:
        # Get jam details
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Generate QR code URL
        jam_url = f"http://localhost:8000/jam/{jam.slug}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(jam_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {e}")

@router.put("/{jam_id}/songs/{song_id}")
async def update_jam_song(
    jam_id: str, 
    song_id: str, 
    updated_song: SongUpdate, 
    db: AsyncSession = Depends(get_database)
):
    """Update a song within a jam"""
    try:
        # Update the song
        update_data = updated_song.dict(exclude_unset=True)
        if update_data:
            await db.execute(
                update(Song)
                .where(Song.id == song_id)
                .values(**update_data)
            )
        
        # Update the jam's updated_at timestamp
        await db.execute(
            update(Jam)
            .where(Jam.id == jam_id)
            .values(updated_at=func.now())
        )
        
        await db.commit()
        
        # Get the updated song
        result = await db.execute(select(Song).where(Song.id == song_id))
        updated_song_obj = result.scalar_one()
        
        return {"message": "Song updated successfully", "song": updated_song_obj}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.put("/{jam_id}/songs/{song_id}/chord-sheet")
async def update_song_chord_sheet(
    jam_id: str,
    song_id: str,
    chord_sheet_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Update the chord sheet URL for a song in a jam"""
    try:
        chord_sheet_url = chord_sheet_data.get("chord_sheet_url")
        
        if not chord_sheet_url:
            raise HTTPException(status_code=400, detail="Chord sheet URL is required")
        
        # Check if song exists in this jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=404, detail="Song not found in this jam")
        
        # Update the song's chord sheet URL
        await db.execute(
            update(Song)
            .where(Song.id == song_id)
            .values(chord_sheet_url=chord_sheet_url)
        )
        
        await db.commit()
        
        return {
            "message": "Chord sheet URL updated successfully",
            "songId": str(song_id),
            "chordSheetUrl": chord_sheet_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/songs/{song_id}/vote")
async def vote_for_song(
    jam_id: str,
    song_id: str,
    vote_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Vote for a song in a jam"""
    try:
        attendee_id = vote_data.get("attendee_id")
        session_id = vote_data.get("session_id")
        
        if not attendee_id and not session_id:
            raise HTTPException(status_code=400, detail="Either attendee_id or session_id is required")
        
        # Check if jam and song exist
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Check if already voted
        existing_vote_query = select(Vote).where(
            (Vote.jam_id == jam_id) &
            (Vote.song_id == song_id) &
            (
                (Vote.attendee_id == attendee_id) if attendee_id else (Vote.session_id == session_id)
            )
        )
        existing_vote = await db.execute(existing_vote_query)
        if existing_vote.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already voted for this song")
        
        # Create vote
        vote = Vote(
            jam_id=jam_id,
            song_id=song_id,
            attendee_id=attendee_id,
            session_id=session_id
        )
        db.add(vote)
        
        # Ensure JamSong entry exists
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            # Create JamSong entry if it doesn't exist
            jam_song = JamSong(
                jam_id=jam_id,
                song_id=song_id
            )
            db.add(jam_song)
        
        await db.commit()
        
        return {"message": "Vote recorded successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/songs/{song_id}/play")
@can_play_songs
async def mark_song_played(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Mark a song as played in a jam"""
    try:
        # Check if jam and song exist
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Update song as played
        await db.execute(
            update(Song)
            .where(Song.id == song_id)
            .values(times_played=Song.times_played + 1)
        )
        
        # Update JamSong as played
        await db.execute(
            update(JamSong)
            .where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
            .values(played=True)
        )
        
        await db.commit()
        
        return {"message": "Song marked as played"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/songs")
async def add_song_to_jam(
    jam_id: str,
    song_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Add a song to a jam"""
    try:
        song_id = song_data.get("song_id")
        
        if not song_id:
            raise HTTPException(status_code=400, detail="Song ID is required")
        
        # Check if jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Check if song exists
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Check if song is already in jam
        existing_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Song already in jam")
        
        # Add song to jam
        jam_song = JamSong(
            jam_id=jam_id,
            song_id=song_id,
            captains=[],
            played=False
        )
        
        db.add(jam_song)
        await db.commit()
        
        return {"message": "Song added to jam successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/attendees")
async def register_attendee(
    jam_id: str,
    attendee_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Register an attendee for a jam"""
    try:
        name = attendee_data.get("name", "").strip()
        session_id = attendee_data.get("session_id", "")
        
        logger.info(f"Registering attendee: name='{name}', session_id='{session_id}', jam_id='{jam_id}'")
        
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Check if jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Check if attendee already exists for this jam and name
        existing_attendee = await db.execute(
            select(Attendee).where(
                (Attendee.jam_id == jam_id) & 
                (Attendee.name == name)
            )
        )
        existing_attendee = existing_attendee.scalar_one_or_none()
        
        logger.info(f"Existing attendee found: {existing_attendee is not None}")
        
        if existing_attendee:
            # Update existing attendee's session_id
            existing_attendee.session_id = session_id
            await db.commit()
            return {"message": "Attendee updated", "attendee_id": str(existing_attendee.id)}
        else:
            # Create new attendee
            attendee = Attendee(
                jam_id=jam_id,
                name=name,
                session_id=session_id
            )
            db.add(attendee)
            await db.commit()
            await db.refresh(attendee)
            return {"message": "Attendee registered", "attendee_id": str(attendee.id)}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/attendees")
async def get_attendees(
    jam_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Get all attendees for a jam, optionally filtered by session_id"""
    try:
        session_id = request.query_params.get("session_id")
        
        # Build query
        query = select(Attendee).where(Attendee.jam_id == jam_id)
        
        if session_id:
            query = query.where(Attendee.session_id == session_id)
        
        result = await db.execute(query.order_by(Attendee.registered_at))
        attendees = result.scalars().all()
        return [{"id": str(a.id), "name": a.name, "registered_at": a.registered_at} for a in attendees]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/songs/{song_id}/register")
@can_register_to_perform
async def register_to_perform(
    jam_id: str,
    song_id: str,
    registration_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Register to perform a song in a jam"""
    try:
        attendee_id = registration_data.get("attendee_id")
        instrument = registration_data.get("instrument", "").strip()
        
        if not attendee_id:
            raise HTTPException(status_code=400, detail="Attendee ID is required")
        
        if not instrument:
            raise HTTPException(status_code=400, detail="Instrument is required")
        
        # Check if already registered
        existing_registration = await db.execute(
            select(PerformanceRegistration).where(
                (PerformanceRegistration.jam_id == jam_id) &
                (PerformanceRegistration.song_id == song_id) &
                (PerformanceRegistration.attendee_id == attendee_id)
            )
        )
        if existing_registration.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Already registered to perform this song")
        
        # Create registration
        registration = PerformanceRegistration(
            jam_id=jam_id,
            song_id=song_id,
            attendee_id=attendee_id,
            instrument=instrument
        )
        db.add(registration)
        await db.commit()
        
        return {"message": "Registered to perform successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{jam_id}/songs/{song_id}/register")
@can_register_to_perform
async def unregister_from_perform(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Unregister from performing a song in a jam"""
    try:
        attendee_id = request.query_params.get("attendee_id")
        
        if not attendee_id:
            raise HTTPException(status_code=400, detail="Attendee ID is required")
        
        # Find and delete registration
        registration_result = await db.execute(
            select(PerformanceRegistration).where(
                (PerformanceRegistration.jam_id == jam_id) &
                (PerformanceRegistration.song_id == song_id) &
                (PerformanceRegistration.attendee_id == attendee_id)
            )
        )
        registration = registration_result.scalar_one_or_none()
        
        if not registration:
            raise HTTPException(status_code=404, detail="Registration not found")
        
        await db.delete(registration)
        await db.commit()
        
        return {"message": "Unregistered from performing successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/songs/{song_id}/performers")
async def get_song_performers(
    jam_id: str,
    song_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get all performers registered for a song in a jam"""
    try:
        result = await db.execute(
            select(Attendee, PerformanceRegistration)
            .join(PerformanceRegistration, Attendee.id == PerformanceRegistration.attendee_id)
            .where(
                (PerformanceRegistration.jam_id == jam_id) &
                (PerformanceRegistration.song_id == song_id)
            )
            .order_by(PerformanceRegistration.registered_at)
        )
        performers = result.all()
        
        return [
            {
                "attendee_id": str(attendee.id),
                "name": attendee.name,
                "instrument": registration.instrument,
                "registered_at": registration.registered_at
            }
            for attendee, registration in performers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/performers")
async def get_jam_performers(
    jam_id: str,
    attendee_id: str = None,
    db: AsyncSession = Depends(get_database)
):
    """Get all performance registrations for a jam, optionally filtered by attendee"""
    try:
        query = select(PerformanceRegistration).where(PerformanceRegistration.jam_id == jam_id)
        
        if attendee_id:
            query = query.where(PerformanceRegistration.attendee_id == attendee_id)
        
        result = await db.execute(query.order_by(PerformanceRegistration.registered_at))
        registrations = result.scalars().all()
        
        return [
            {
                "id": reg.id,
                "jam_id": reg.jam_id,
                "song_id": reg.song_id,
                "attendee_id": reg.attendee_id,
                "instrument": reg.instrument,
                "registered_at": reg.registered_at
            }
            for reg in registrations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/songs/{song_id}/heart")
@can_vote
async def toggle_heart_vote(
    jam_id: str,
    song_id: str,
    vote_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Toggle heart vote for a song in a jam"""
    try:
        attendee_id = vote_data.get("attendee_id")
        session_id = vote_data.get("session_id")
        
        if not attendee_id and not session_id:
            raise HTTPException(status_code=400, detail="Either attendee_id or session_id is required")
        
        # Check if already voted
        existing_vote_query = select(Vote).where(
            (Vote.jam_id == jam_id) &
            (Vote.song_id == song_id) &
            (
                (Vote.attendee_id == attendee_id) if attendee_id else (Vote.session_id == session_id)
            )
        )
        existing_vote = await db.execute(existing_vote_query)
        existing_vote = existing_vote.scalar_one_or_none()
        
        if existing_vote:
            # Remove vote
            await db.delete(existing_vote)
            vote_count_change = -1
        else:
            # Add vote
            vote = Vote(
                jam_id=jam_id,
                song_id=song_id,
                attendee_id=attendee_id,
                session_id=session_id
            )
            db.add(vote)
            vote_count_change = 1
        
        # Ensure JamSong entry exists
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            # Create JamSong entry if it doesn't exist
            jam_song = JamSong(
                jam_id=jam_id,
                song_id=song_id
            )
            db.add(jam_song)
        
        await db.commit()
        
        # Calculate current vote count
        vote_count_result = await db.execute(
            select(func.count(Vote.id))
            .where(Vote.jam_id == jam_id, Vote.song_id == song_id)
        )
        vote_count = vote_count_result.scalar() or 0
        
        return {
            "message": "Vote toggled successfully",
            "voted": vote_count_change > 0,
            "vote_count": vote_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/songs/{song_id}/vote-status")
async def get_vote_status(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Get vote status for a song in a jam"""
    try:
        attendee_id = request.query_params.get("attendee_id")
        session_id = request.query_params.get("session_id")
        
        if not attendee_id and not session_id:
            raise HTTPException(status_code=400, detail="Either attendee_id or session_id is required")
        
        # Check if voted
        vote_query = select(Vote).where(
            (Vote.jam_id == jam_id) &
            (Vote.song_id == song_id) &
            (
                (Vote.attendee_id == attendee_id) if attendee_id else (Vote.session_id == session_id)
            )
        )
        vote_result = await db.execute(vote_query)
        has_voted = vote_result.scalar_one_or_none() is not None
        
        # Get vote count
        vote_count_result = await db.execute(
            select(func.count(Vote.id))
            .where(Vote.jam_id == jam_id, Vote.song_id == song_id)
        )
        vote_count = vote_count_result.scalar() or 0
        
        return {
            "has_voted": has_voted,
            "vote_count": vote_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/votes")
async def get_jam_votes(
    jam_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Get all votes for a jam, optionally filtered by attendee_id"""
    try:
        attendee_id = request.query_params.get("attendee_id")
        
        # Build query
        vote_query = select(Vote).where(Vote.jam_id == jam_id)
        
        if attendee_id:
            vote_query = vote_query.where(Vote.attendee_id == attendee_id)
        
        # Execute query
        votes_result = await db.execute(vote_query)
        votes = votes_result.scalars().all()
        
        # Convert to list of dictionaries
        votes_list = []
        for vote in votes:
            votes_list.append({
                "id": vote.id,
                "song_id": vote.song_id,
                "attendee_id": vote.attendee_id,
                "session_id": vote.session_id,
                "voted_at": vote.voted_at.isoformat() if vote.voted_at else None
            })
        
        return votes_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/vote")
async def vote_for_song_simple(
    jam_id: str,
    vote_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Simple vote endpoint for the new jam page"""
    try:
        song_id = vote_data.get("song_id")
        attendee_id = vote_data.get("attendee_id")
        
        if not song_id or not attendee_id:
            raise HTTPException(status_code=400, detail="song_id and attendee_id are required")
        
        # Check if jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Check if attendee exists
        attendee_result = await db.execute(select(Attendee).where(Attendee.id == attendee_id))
        attendee = attendee_result.scalar_one_or_none()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        
        # Check if song exists
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Check if song is in jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=400, detail="Song not in jam")
        
        # Check if already voted
        existing_vote = await db.execute(
            select(Vote).where(
                Vote.jam_id == jam_id,
                Vote.song_id == song_id,
                Vote.attendee_id == attendee_id
            )
        )
        existing_vote = existing_vote.scalar_one_or_none()
        
        if existing_vote:
            # Remove existing vote
            await db.delete(existing_vote)
            await db.commit()
            
            # Broadcast vote update via WebSocket
            from api.endpoints.websocket import connection_manager
            print(f"🔴 Broadcasting vote removal for song {song_id} in jam {jam_id}")
            await connection_manager.broadcast_to_jam(jam_id, "vote_update", {
                "type": "vote_update", 
                "song_id": song_id, 
                "voted": False,
                "attendee_id": attendee_id
            })
            
            return {"message": "Vote removed", "voted": False}
        else:
            # Add new vote
            vote = Vote(
                jam_id=jam_id,
                song_id=song_id,
                attendee_id=attendee_id
            )
            db.add(vote)
            await db.commit()
            
            # Broadcast vote update via WebSocket
            from api.endpoints.websocket import connection_manager
            print(f"🟢 Broadcasting vote addition for song {song_id} in jam {jam_id}")
            await connection_manager.broadcast_to_jam(jam_id, "vote_update", {
                "type": "vote_update", 
                "song_id": song_id, 
                "voted": True,
                "attendee_id": attendee_id
            })
            
            return {"message": "Vote added", "voted": True}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/perform")
async def register_to_perform_simple(
    jam_id: str,
    perform_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Simple performance registration endpoint for the new jam page"""
    try:
        song_id = perform_data.get("song_id")
        attendee_id = perform_data.get("attendee_id")
        instrument = perform_data.get("instrument", "Unknown")
        
        if not song_id or not attendee_id:
            raise HTTPException(status_code=400, detail="song_id and attendee_id are required")
        
        # Check if jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Check if attendee exists
        attendee_result = await db.execute(select(Attendee).where(Attendee.id == attendee_id))
        attendee = attendee_result.scalar_one_or_none()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")
        
        # Check if song exists
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Check if song is in jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=400, detail="Song not in jam")
        
        # Check if already registered
        existing_registration = await db.execute(
            select(PerformanceRegistration).where(
                PerformanceRegistration.jam_id == jam_id,
                PerformanceRegistration.song_id == song_id,
                PerformanceRegistration.attendee_id == attendee_id
            )
        )
        existing_registration = existing_registration.scalar_one_or_none()
        
        if existing_registration:
            raise HTTPException(status_code=400, detail="Already registered to perform this song")
        
        # Create performance registration
        registration = PerformanceRegistration(
            jam_id=jam_id,
            song_id=song_id,
            attendee_id=attendee_id,
            instrument=instrument
        )
        db.add(registration)
        await db.commit()
        
        return {"message": "Registered to perform successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
@router.delete("/{jam_id}/perform")
async def unregister_from_perform(
    jam_id: str,
    perform_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Unregister from performance endpoint for the new jam page"""
    try:
        song_id = perform_data.get("song_id")
        attendee_id = perform_data.get("attendee_id")
        
        if not song_id or not attendee_id:
            raise HTTPException(status_code=400, detail="song_id and attendee_id are required")
        
        # Find existing registration
        existing_registration = await db.execute(
            select(PerformanceRegistration).where(
                PerformanceRegistration.jam_id == jam_id,
                PerformanceRegistration.song_id == song_id,
                PerformanceRegistration.attendee_id == attendee_id
            )
        )
        existing_registration = existing_registration.scalar_one_or_none()
        
        if not existing_registration:
            raise HTTPException(status_code=404, detail="Performance registration not found")
        
        # Delete the registration
        await db.delete(existing_registration)
        await db.commit()
        
        return {"message": "Unregistered from performance successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
