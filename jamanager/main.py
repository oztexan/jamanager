from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
import json
import asyncio
from typing import List, Dict
import os
import qrcode
import io
from datetime import date
from dotenv import load_dotenv
from feature_flags import UserRole, FeatureFlags
from user_roles import UserRoleManager, get_current_user_role
from auth_middleware import (
    FeatureGate, can_vote, can_register_to_perform, can_suggest_songs, 
    can_manage_jam, can_play_songs, get_user_role_dependency, get_user_permissions
)
from feature_flag_config import get_feature_flag_value
from feature_flag_api_simple import router as feature_flag_router
from access_config import AccessConfig, jam_manager_sessions
from jam_config import JamConfig
from slug_utils import generate_jam_slug, make_slug_unique
from image_utils import ImageUploader

# Load environment variables
load_dotenv()

# Import our modules
from jamanager.database import get_database, init_database
from jamanager.models import Song, Jam, JamSong, Attendee, Vote, PerformanceRegistration, Venue, SongInDB, JamInDB, SongCreate, SongUpdate, VenueInDB, VenueCreate, VenueUpdate, JamInDBWithVenue
from connection_manager import ConnectionManager

app = FastAPI(title="Jamanager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include feature flag API router
app.include_router(feature_flag_router)

# Include chord sheet API router
from chord_sheet_api import router as chord_sheet_router
app.include_router(chord_sheet_router)

# Connection manager for WebSocket connections
connection_manager = ConnectionManager()

# Mount static files (for the frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure uploads directory exists
JamConfig.ensure_upload_dir()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()

@app.get("/")
async def read_index():
    """Serve the main HTML file"""
    return FileResponse("static/index.html")

@app.get("/test-chords")
async def test_chords_page():
    """Test page for chord sheet functionality."""
    return FileResponse("test_chord_frontend.html")

@app.get("/jam/{slug}")
async def jam_page(slug: str):
    """Serve the jam page"""
    return FileResponse("static/jam.html")

@app.get("/songs")
async def songs_page():
    """Serve the songs page"""
    return FileResponse("static/songs.html")

@app.get("/jams")
async def jams_page():
    """Serve the jams page"""
    return FileResponse("static/jams.html")

@app.get("/jam-manager")
async def jam_manager_page():
    """Serve the jam manager page"""
    return FileResponse("static/admin.html")

@app.get("/jam-manager/feature-flags")
async def jam_manager_feature_flags():
    """Feature flag management interface"""
    return FileResponse("static/feature-flags.html")

@app.get("/jam-manager/venues")
async def venue_management_page():
    """Venue management interface"""
    return FileResponse("static/venue-management.html")

@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon"""
    return FileResponse("static/favicon.ico")

# WebSocket endpoint
@app.websocket("/ws/{jam_id}")
async def websocket_endpoint(websocket: WebSocket, jam_id: str):
    await connection_manager.connect(websocket, jam_id)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                print(f"Received message: {message}")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, jam_id)
        print(f"WebSocket client disconnected from jam: {jam_id}")

@app.get("/api/jams/by-slug/{slug}", response_model=JamInDBWithVenue)
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
    
    # Get jam songs with song details, ordered by vote count (descending)
    jam_songs_result = await db.execute(
        select(JamSong, Song)
        .join(Song, JamSong.song_id == Song.id)
        .where(JamSong.jam_id == jam.id)
        .order_by(Song.vote_count.desc())
    )
    
    jam_songs = []
    for jam_song, song in jam_songs_result:
        jam_song.song = song
        jam_songs.append(jam_song)
    
    jam.songs = jam_songs
    jam.venue = venue
    
    # Get current song if exists
    if jam.current_song_id:
        current_song_result = await db.execute(
            select(Song).where(Song.id == jam.current_song_id)
        )
        jam.current_song = current_song_result.scalar_one_or_none()
    
    return jam

@app.get("/api/songs", response_model=List[SongInDB])
async def get_all_songs(db: AsyncSession = Depends(get_database)):
    """Get all songs"""
    result = await db.execute(select(Song))
    songs = result.scalars().all()
    return songs

@app.put("/api/jams/{jam_id}/songs/{song_id}")
async def update_jam_song(
    jam_id: str, 
    song_id: str, 
    updated_song: SongUpdate, 
    db: AsyncSession = Depends(get_database)
):
    """Update a song within a jam"""
    try:
        # Convert string IDs to UUID
        
        # Update the song
        update_data = updated_song.model_dump(exclude_unset=True)
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
        
        # Broadcast the update to WebSocket clients
        await connection_manager.broadcast(
            jam_id, 
            "song-edited", 
            {
                "songId": str(song_id), 
                "updatedSong": SongInDB.model_validate(updated_song_obj).model_dump()
            }
        )
        
        return {"message": "Song updated and broadcasted", "song": updated_song_obj}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.put("/api/jams/{jam_id}/songs/{song_id}/chord-sheet")
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
        
        # Get the updated song
        result = await db.execute(select(Song).where(Song.id == song_id))
        updated_song = result.scalar_one()
        
        # Broadcast the update to WebSocket clients
        await connection_manager.broadcast_to_jam(
            jam_id,
            "chord-sheet-updated",
            {
                "songId": str(song_id),
                "chordSheetUrl": chord_sheet_url,
                "songTitle": updated_song.title,
                "songArtist": updated_song.artist
            }
        )
        
        return {
            "message": "Chord sheet URL updated successfully",
            "songId": str(song_id),
            "chordSheetUrl": chord_sheet_url
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/api/jams/{jam_id}/songs/{song_id}/vote")
async def vote_for_song(
    jam_id: str,
    song_id: str,
    vote_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Vote for a song in a jam"""
    try:
        attendee_id = vote_data.get("attendee_id")
        
        if not attendee_id:
            raise HTTPException(status_code=400, detail="Attendee ID is required")
        
        
        # Check if attendee exists and belongs to this jam
        attendee_result = await db.execute(
            select(Attendee).where(Attendee.id == attendee_id, Attendee.jam_id == jam_id)
        )
        attendee = attendee_result.scalar_one_or_none()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found in this jam")
        
        # Check if attendee has already voted for this song
        existing_vote_result = await db.execute(
            select(Vote).where(
                Vote.jam_id == jam_id,
                Vote.song_id == song_id,
                Vote.attendee_id == attendee_id
            )
        )
        existing_vote = existing_vote_result.scalar_one_or_none()
        if existing_vote:
            raise HTTPException(status_code=400, detail="You have already voted for this song")
        
        # Create vote
        vote = Vote(
            jam_id=jam_id,
            song_id=song_id,
            attendee_id=attendee_id
        )
        
        db.add(vote)
        
        # Update song vote count
        await db.execute(
            update(Song)
            .where(Song.id == song_id)
            .values(vote_count=Song.vote_count + 1)
        )
        
        await db.commit()
        
        # Get updated song
        result = await db.execute(select(Song).where(Song.id == song_id))
        updated_song = result.scalar_one()
        
        # Broadcast vote update
        await connection_manager.broadcast_to_jam(
            jam_id,
            "song-voted",
            {
                "songId": str(song_id),
                "voteCount": updated_song.vote_count,
                "attendeeName": attendee.name
            }
        )
        
        return {"message": "Vote recorded", "voteCount": updated_song.vote_count}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/api/jams/{jam_id}/songs/{song_id}/play")
@can_play_songs
async def mark_song_played(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database),
    user_role: UserRole = Depends(get_user_role_dependency)
):
    """Mark a song as played in a jam"""
    try:
        
        # Update jam song as played
        await db.execute(
            update(JamSong)
            .where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
            .values(played=True, played_at=func.now())
        )
        
        # Update song play count
        await db.execute(
            update(Song)
            .where(Song.id == song_id)
            .values(
                times_played=Song.times_played + 1,
                last_played=func.now()
            )
        )
        
        await db.commit()
        
        # Broadcast play update
        await connection_manager.broadcast_to_jam(
            jam_id,
            "song-played",
            {"songId": str(song_id)}
        )
        
        return {"message": "Song marked as played"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/api/jams")
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
            background_image_path = ImageUploader.save_image(background_image, str(new_jam.id))
            # Update jam with image path
            new_jam.background_image = background_image_path
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

@app.get("/api/jams")
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


@app.post("/api/jams/{jam_id}/songs")
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
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/api/jams/{jam_id}/attendees")
async def register_attendee(
    jam_id: str,
    attendee_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Register an attendee for a jam"""
    try:
        name = attendee_data.get("name", "").strip()
        session_id = attendee_data.get("session_id", "")
        
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Check if jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Check if name is already taken in this jam
        existing_result = await db.execute(
            select(Attendee).where(Attendee.jam_id == jam_id, Attendee.name == name)
        )
        existing = existing_result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Name already taken in this jam")
        
        # Create attendee
        attendee = Attendee(
            jam_id=jam_id,
            name=name,
            session_id=session_id
        )
        
        db.add(attendee)
        await db.commit()
        await db.refresh(attendee)
        
        return {
            "id": str(attendee.id),
            "name": attendee.name,
            "jam_id": str(attendee.jam_id),
            "registered_at": attendee.registered_at
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions (like "Name already taken")
        raise
    except Exception as e:
        await db.rollback()
        # Check if it's a unique constraint violation
        if "unique_attendee_name_per_jam" in str(e):
            raise HTTPException(status_code=400, detail="Name already taken in this jam")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/api/jams/{jam_id}/attendees")
async def get_attendees(
    jam_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get all attendees for a jam"""
    try:
        
        result = await db.execute(
            select(Attendee).where(Attendee.jam_id == jam_id).order_by(Attendee.registered_at)
        )
        attendees = result.scalars().all()
        
        return [
            {
                "id": str(attendee.id),
                "name": attendee.name,
                "registered_at": attendee.registered_at
            }
            for attendee in attendees
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/api/jams/{jam_id}/qr")
async def get_jam_qr_code(jam_id: str, db: AsyncSession = Depends(get_database)):
    """Generate QR code for jam access"""
    try:
        
        # Get jam details
        result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Generate QR code URL
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        jam_url = f"{base_url}/jam/{jam.slug}"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(jam_url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Response(content=img_buffer.getvalue(), media_type="image/png")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating QR code: {e}")

@app.post("/api/jams/{jam_id}/songs/{song_id}/register")
@can_register_to_perform
async def register_to_perform(
    jam_id: str,
    song_id: str,
    registration_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_database),
    user_role: UserRole = Depends(get_user_role_dependency)
):
    """Register an attendee to perform on a song"""
    try:
        attendee_id = registration_data.get("attendee_id")
        instrument = registration_data.get("instrument", "")
        
        if not attendee_id:
            raise HTTPException(status_code=400, detail="Attendee ID is required")
        
        
        # Check if attendee exists and belongs to this jam
        attendee_result = await db.execute(
            select(Attendee).where(Attendee.id == attendee_id, Attendee.jam_id == jam_id)
        )
        attendee = attendee_result.scalar_one_or_none()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found in this jam")
        
        # Check if song exists in this jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=404, detail="Song not found in this jam")
        
        # Check if attendee is already registered to perform this song
        existing_registration_result = await db.execute(
            select(PerformanceRegistration).where(
                PerformanceRegistration.jam_id == jam_id,
                PerformanceRegistration.song_id == song_id,
                PerformanceRegistration.attendee_id == attendee_id
            )
        )
        existing_registration = existing_registration_result.scalar_one_or_none()
        if existing_registration:
            raise HTTPException(status_code=400, detail="You are already registered to perform this song")
        
        # Create performance registration
        registration = PerformanceRegistration(
            jam_id=jam_id,
            song_id=song_id,
            attendee_id=attendee_id,
            instrument=instrument
        )
        
        db.add(registration)
        await db.commit()
        
        # Broadcast registration update
        await connection_manager.broadcast_to_jam(
            jam_id,
            "performance-registered",
            {
                "songId": str(song_id),
                "attendeeName": attendee.name,
                "instrument": instrument
            }
        )
        
        return {"message": "Successfully registered to perform", "attendeeName": attendee.name}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.delete("/api/jams/{jam_id}/songs/{song_id}/register")
@can_register_to_perform
async def unregister_from_perform(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database),
    user_role: UserRole = Depends(get_user_role_dependency)
):
    """Unregister an attendee from performing on a song"""
    try:
        
        # Get attendee ID from headers
        attendee_id = request.headers.get('X-Attendee-ID')
        if not attendee_id:
            raise HTTPException(status_code=400, detail="Attendee ID is required")
        
        
        # Check if attendee exists and belongs to this jam
        attendee_result = await db.execute(
            select(Attendee).where(Attendee.id == attendee_id, Attendee.jam_id == jam_id)
        )
        attendee = attendee_result.scalar_one_or_none()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found in this jam")
        
        # Check if song exists in this jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=404, detail="Song not found in this jam")
        
        # Check if attendee is already registered to perform
        existing_registration_result = await db.execute(
            select(PerformanceRegistration).where(
                PerformanceRegistration.jam_id == jam_id,
                PerformanceRegistration.song_id == song_id,
                PerformanceRegistration.attendee_id == attendee_id
            )
        )
        existing_registration = existing_registration_result.scalar_one_or_none()
        if not existing_registration:
            raise HTTPException(status_code=404, detail="Not registered to perform this song")
        
        # Remove the registration
        await db.delete(existing_registration)
        await db.commit()
        
        # Broadcast unregistration update
        await connection_manager.broadcast_to_jam(
            jam_id,
            "performance-unregistered",
            {
                "songId": str(song_id),
                "attendeeName": attendee.name
            }
        )
        
        return {"message": "Successfully unregistered from performing", "attendeeName": attendee.name}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/api/jams/{jam_id}/songs/{song_id}/performers")
async def get_song_performers(
    jam_id: str,
    song_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get all performers registered for a song"""
    try:
        
        result = await db.execute(
            select(PerformanceRegistration, Attendee)
            .join(Attendee, PerformanceRegistration.attendee_id == Attendee.id)
            .where(
                PerformanceRegistration.jam_id == jam_id,
                PerformanceRegistration.song_id == song_id
            )
            .order_by(PerformanceRegistration.registered_at)
        )
        
        performers = result.all()
        
        return [
            {
                "attendee_id": str(perf.attendee_id),
                "attendee_name": attendee.name,
                "instrument": perf.instrument,
                "registered_at": perf.registered_at
            }
            for perf, attendee in performers
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.post("/api/jams/{jam_id}/songs/{song_id}/heart")
@can_vote
async def toggle_heart_vote(
    jam_id: str,
    song_id: str,
    vote_data: dict,
    request: Request,
    db: AsyncSession = Depends(get_database),
    user_role: UserRole = Depends(get_user_role_dependency)
):
    """Toggle heart vote for a song (no registration required)"""
    try:
        session_id = vote_data.get("session_id", "anonymous")
        
        # Check if song exists in this jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=404, detail="Song not found in this jam")
        
        # Check if this session already voted for this song
        existing_vote_result = await db.execute(
            select(Vote).where(
                Vote.jam_id == jam_id,
                Vote.song_id == song_id,
                Vote.session_id == session_id
            )
        )
        existing_vote = existing_vote_result.scalar_one_or_none()
        
        if existing_vote:
            # Remove the vote (unheart)
            await db.delete(existing_vote)
            # Update song vote count
            await db.execute(
                update(Song)
                .where(Song.id == song_id)
                .values(vote_count=Song.vote_count - 1)
            )
            action = "removed"
        else:
            # Add the vote (heart)
            new_vote = Vote(
                jam_id=jam_id,
                song_id=song_id,
                attendee_id=None,  # Anonymous vote
                session_id=session_id,
                voted_at=func.now()
            )
            db.add(new_vote)
            # Update song vote count
            await db.execute(
                update(Song)
                .where(Song.id == song_id)
                .values(vote_count=Song.vote_count + 1)
            )
            action = "added"
        
        await db.commit()
        
        # Get updated song with vote count
        song_result = await db.execute(select(Song).where(Song.id == song_id))
        updated_song = song_result.scalar_one()
        vote_count = updated_song.vote_count
        
        # Broadcast vote update
        await connection_manager.broadcast_to_jam(
            jam_id,
            "heart-toggled",
            {
                "songId": str(song_id),
                "voteCount": vote_count,
                "action": action,
                "sessionId": session_id
            }
        )
        
        return {
            "message": f"Vote {action}",
            "voteCount": vote_count,
            "action": action
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/api/jams/{jam_id}/songs/{song_id}/vote-status")
async def get_vote_status(
    jam_id: str,
    song_id: str,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Check if current session has voted for a song"""
    try:
        session_id = request.headers.get('X-Session-ID', 'anonymous')
        
        # Check if song exists in this jam
        jam_song_result = await db.execute(
            select(JamSong).where(JamSong.jam_id == jam_id, JamSong.song_id == song_id)
        )
        jam_song = jam_song_result.scalar_one_or_none()
        if not jam_song:
            raise HTTPException(status_code=404, detail="Song not found in this jam")
        
        # Check if this session has voted for this song
        vote_result = await db.execute(
            select(Vote).where(
                Vote.jam_id == jam_id,
                Vote.song_id == song_id,
                Vote.session_id == session_id
            )
        )
        has_voted = vote_result.scalar_one_or_none() is not None
        
        return {
            "hasVoted": has_voted,
            "sessionId": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/api/user/permissions")
async def get_user_permissions_endpoint(
    request: Request,
    user_role: UserRole = Depends(get_user_role_dependency),
    permissions: dict = Depends(get_user_permissions)
):
    """Get current user's permissions and available features"""
    # Get user_id and jam_id for feature flag resolution
    user_id = request.headers.get("X-Attendee-ID")
    jam_id = request.path_params.get('jam_id') if hasattr(request, 'path_params') else None
    
    # Get effective feature flags using the configuration system
    from feature_flag_config import feature_flag_manager
    effective_flags = feature_flag_manager.get_user_feature_flags(user_role, user_id, jam_id)
    
    return {
        "user_role": user_role.value,
        "role_display_name": UserRoleManager.get_role_display_name(user_role),
        "role_description": UserRoleManager.get_role_description(user_role),
        "permissions": permissions,
        "enabled_features": [name for name, enabled in effective_flags.items() if enabled],
        "effective_feature_flags": effective_flags,
        "user_id": user_id,
        "jam_id": jam_id
    }

@app.get("/api/feature-flags")
async def get_feature_flags():
    """Get all available feature flags (for admin/debug purposes)"""
    return {
        "features": {
            name: {
                "name": feature.name,
                "description": feature.description,
                "enabled_for": [role.value for role in feature.enabled_for],
                "default_enabled": feature.default_enabled
            }
            for name, feature in FeatureFlags.get_all_features().items()
        },
        "user_roles": {
            role.value: {
                "display_name": UserRoleManager.get_role_display_name(role),
                "description": UserRoleManager.get_role_description(role),
                "enabled_features": FeatureFlags.get_enabled_features(role)
            }
            for role in UserRole
        }
    }

@app.post("/api/access-code/verify")
async def verify_access_code(
    request: Request,
    access_data: dict
):
    """Verify access code and grant jam manager privileges"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    provided_code = access_data.get("access_code", "").strip()
    
    if not AccessConfig.validate_access_code(provided_code):
        raise HTTPException(status_code=401, detail="Invalid access code")
    
    # Grant jam manager access
    success = jam_manager_sessions.grant_jam_manager_access(session_id)
    
    if success:
        return {
            "success": True,
            "message": "Access granted",
            "role": "jam_manager",
            "session_id": session_id
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to grant access")

@app.post("/api/access-code/logout")
async def logout_jam_manager(
    request: Request
):
    """Logout from jam manager session"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    success = jam_manager_sessions.revoke_jam_manager_access(session_id)
    
    if success:
        return {
            "success": True,
            "message": "Logged out successfully",
            "role": "anonymous"
        }
    else:
        return {
            "success": False,
            "message": "No active session found"
        }

@app.get("/api/access-code/status")
async def get_access_status(
    request: Request
):
    """Get current access status"""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return {
            "has_access": False,
            "role": "anonymous",
            "session_id": None
        }
    
    has_access = jam_manager_sessions.has_jam_manager_access(session_id)
    session_info = jam_manager_sessions.get_session_info(session_id)
    
    return {
        "has_access": has_access,
        "role": "jam_manager" if has_access else "anonymous",
        "session_id": session_id,
        "session_info": session_info
    }

# Venue Management API Endpoints
@app.get("/api/venues")
async def get_all_venues(db: AsyncSession = Depends(get_database)):
    """Get all venues"""
    result = await db.execute(select(Venue).order_by(Venue.name))
    venues = result.scalars().all()
    return venues

@app.post("/api/venues", response_model=VenueInDB)
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new venue"""
    venue = Venue(**venue_data.dict())
    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    return venue

@app.get("/api/venues/{venue_id}", response_model=VenueInDB)
async def get_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get a specific venue by ID"""
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@app.put("/api/venues/{venue_id}", response_model=VenueInDB)
async def update_venue(
    venue_id: str,
    venue_data: VenueUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update a venue"""
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Update only provided fields
    update_data = venue_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(venue, field, value)
    
    await db.commit()
    await db.refresh(venue)
    return venue

@app.delete("/api/venues/{venue_id}")
async def delete_venue(
    venue_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete a venue"""
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalar_one_or_none()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    
    # Check if venue is being used by any jams
    jam_result = await db.execute(select(Jam).where(Jam.venue_id == venue_id))
    jams_using_venue = jam_result.scalars().all()
    if jams_using_venue:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete venue. It is being used by {len(jams_using_venue)} jam(s)."
        )
    
    await db.delete(venue)
    await db.commit()
    return {"message": "Venue deleted successfully"}

# Song Management API Endpoints
@app.post("/api/songs", response_model=SongInDB)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new song"""
    song = Song(**song_data.dict())
    db.add(song)
    await db.commit()
    await db.refresh(song)
    return song

@app.get("/api/songs")
async def get_all_songs(db: AsyncSession = Depends(get_database)):
    """Get all songs"""
    result = await db.execute(select(Song).order_by(Song.title))
    songs = result.scalars().all()
    return songs

@app.get("/api/songs/{song_id}", response_model=SongInDB)
async def get_song(song_id: str, db: AsyncSession = Depends(get_database)):
    """Get a specific song by ID"""
    try:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        return song
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid song ID format")

@app.put("/api/songs/{song_id}", response_model=SongInDB)
async def update_song(
    song_id: str,
    song_data: SongUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update a song"""
    try:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Update song fields
        for field, value in song_data.dict(exclude_unset=True).items():
            setattr(song, field, value)
        
        await db.commit()
        await db.refresh(song)
        return song
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid song ID format")

@app.delete("/api/songs/{song_id}")
async def delete_song(song_id: str, db: AsyncSession = Depends(get_database)):
    """Delete a song"""
    try:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        await db.delete(song)
        await db.commit()
        return {"message": "Song deleted successfully"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid song ID format")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)