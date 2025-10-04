from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from core.database import get_database
from models.database import JamChordSheet, Jam, Song, Attendee
from models.database import JamChordSheetCreate, JamChordSheetUpdate, JamChordSheetInDB
from services.ultimate_guitar_service import ultimate_guitar_service
# Connection manager will be imported at runtime to avoid circular imports
import re
from datetime import datetime

router = APIRouter()

async def validate_url_async(url: str) -> bool:
    """Validate a URL asynchronously"""
    try:
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False
        
        # Try to fetch the URL to check accessibility
        import requests
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
        
    except Exception:
        return False

async def save_validation_result(db: AsyncSession, jam_id: str, song_id: str, url: str, is_valid: bool):
    """Save URL validation result to the appropriate database record"""
    try:
        # First, try to find an existing jam-specific chord sheet
        result = await db.execute(
            select(JamChordSheet)
            .where(and_(JamChordSheet.jam_id == jam_id, JamChordSheet.song_id == song_id))
        )
        jam_chord_sheet = result.scalar_one_or_none()
        
        if jam_chord_sheet:
            # Update existing jam-specific chord sheet
            jam_chord_sheet.chord_sheet_is_valid = is_valid
            jam_chord_sheet.chord_sheet_validated_at = datetime.now()
            print(f"🔍 Updated jam chord sheet validation: {url} -> {is_valid}")
        else:
            # Check if this URL matches the song's default chord sheet
            song_result = await db.execute(select(Song).where(Song.id == song_id))
            song = song_result.scalar_one_or_none()
            
            if song and song.chord_sheet_url == url:
                # Update the song's default chord sheet validation
                song.chord_sheet_is_valid = is_valid
                song.chord_sheet_validated_at = datetime.now()
                print(f"🔍 Updated song default chord sheet validation: {url} -> {is_valid}")
        
        await db.commit()
        
    except Exception as e:
        print(f"🔍 Error saving validation result: {e}")
        await db.rollback()

@router.get("/{jam_id}/chord-sheets")
async def get_jam_chord_sheets(
    jam_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get all chord sheets for a jam"""
    try:
        result = await db.execute(
            select(JamChordSheet)
            .where(JamChordSheet.jam_id == jam_id)
            .order_by(JamChordSheet.created_at)
        )
        chord_sheets = result.scalars().all()
        return [JamChordSheetInDB.from_orm(cs) for cs in chord_sheets]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{jam_id}/chord-sheets/{song_id}")
async def get_jam_song_chord_sheet(
    jam_id: str,
    song_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get chord sheet for a specific song in a jam"""
    try:
        result = await db.execute(
            select(JamChordSheet)
            .where(and_(JamChordSheet.jam_id == jam_id, JamChordSheet.song_id == song_id))
        )
        chord_sheet = result.scalar_one_or_none()
        
        if not chord_sheet:
            # Return the song's default chord sheet if no jam-specific one exists
            song_result = await db.execute(select(Song).where(Song.id == song_id))
            song = song_result.scalar_one_or_none()
            
            if song and song.chord_sheet_url:
                return {
                    "id": None,
                    "jam_id": jam_id,
                    "song_id": song_id,
                    "chord_sheet_url": song.chord_sheet_url,
                    "title": f"{song.title} - {song.artist}",
                    "rating": None,
                    "created_by": None,
                    "created_at": None,
                    "updated_at": None,
                    "is_default": True
                }
            
            return None
        
        return JamChordSheetInDB.from_orm(chord_sheet)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/chord-sheets")
async def create_jam_chord_sheet(
    jam_id: str,
    chord_sheet_data: JamChordSheetCreate,
    request: Request,
    db: AsyncSession = Depends(get_database)
):
    """Create or update a chord sheet for a song in a jam"""
    try:
        # Verify jam exists
        jam_result = await db.execute(select(Jam).where(Jam.id == jam_id))
        jam = jam_result.scalar_one_or_none()
        if not jam:
            raise HTTPException(status_code=404, detail="Jam not found")
        
        # Verify song exists
        song_result = await db.execute(select(Song).where(Song.id == chord_sheet_data.song_id))
        song = song_result.scalar_one_or_none()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Get current attendee (if any)
        attendee_id = None
        if hasattr(request, 'state') and hasattr(request.state, 'attendee_id'):
            attendee_id = request.state.attendee_id
        
        # Check if chord sheet already exists
        existing_result = await db.execute(
            select(JamChordSheet)
            .where(and_(JamChordSheet.jam_id == jam_id, JamChordSheet.song_id == chord_sheet_data.song_id))
        )
        existing = existing_result.scalar_one_or_none()
        
        # Validate the URL and save the validation result
        is_valid = await validate_url_async(chord_sheet_data.chord_sheet_url)
        await save_validation_result(db, jam_id, chord_sheet_data.song_id, chord_sheet_data.chord_sheet_url, is_valid)
        
        if existing:
            # Update existing chord sheet
            existing.chord_sheet_url = chord_sheet_data.chord_sheet_url
            existing.title = chord_sheet_data.title
            existing.rating = chord_sheet_data.rating
            if attendee_id:
                existing.created_by = attendee_id
            
            await db.commit()
            await db.refresh(existing)
            
            # Broadcast chord sheet update via WebSocket (outside transaction)
            try:
                from main import connection_manager
                print(f"🎵 Broadcasting chord sheet update for song {chord_sheet_data.song_id} in jam {jam_id}")
                print(f"🎵 Active connections: {connection_manager.active_connections}")
                await connection_manager.broadcast_to_jam(jam_id, "chord_sheet_update", {
                    "type": "chord_sheet_update", 
                    "song_id": chord_sheet_data.song_id,
                    "action": "update",
                    "chord_sheet_url": chord_sheet_data.chord_sheet_url,
                    "is_valid": is_valid
                })
            except Exception as e:
                print(f"⚠️ WebSocket broadcast failed (non-critical): {e}")
            
            return JamChordSheetInDB.from_orm(existing)
        else:
            # Create new chord sheet
            chord_sheet = JamChordSheet(
                jam_id=jam_id,
                song_id=chord_sheet_data.song_id,
                chord_sheet_url=chord_sheet_data.chord_sheet_url,
                title=chord_sheet_data.title,
                rating=chord_sheet_data.rating,
                created_by=attendee_id
            )
            
            db.add(chord_sheet)
            await db.commit()
            await db.refresh(chord_sheet)
            
            # Broadcast chord sheet creation via WebSocket (outside transaction)
            try:
                from main import connection_manager
                print(f"🎵 Broadcasting chord sheet creation for song {chord_sheet_data.song_id} in jam {jam_id}")
                await connection_manager.broadcast_to_jam(jam_id, "chord_sheet_update", {
                    "type": "chord_sheet_update", 
                    "song_id": chord_sheet_data.song_id,
                    "action": "create",
                    "chord_sheet_url": chord_sheet_data.chord_sheet_url,
                    "is_valid": is_valid
                })
            except Exception as e:
                print(f"⚠️ WebSocket broadcast failed (non-critical): {e}")
            
            return JamChordSheetInDB.from_orm(chord_sheet)
            
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{jam_id}/chord-sheets/{song_id}")
async def delete_jam_chord_sheet(
    jam_id: str,
    song_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete a chord sheet for a song in a jam"""
    try:
        result = await db.execute(
            select(JamChordSheet)
            .where(and_(JamChordSheet.jam_id == jam_id, JamChordSheet.song_id == song_id))
        )
        chord_sheet = result.scalar_one_or_none()
        
        if not chord_sheet:
            raise HTTPException(status_code=404, detail="Chord sheet not found")
        
        await db.delete(chord_sheet)
        await db.commit()
        
        # Broadcast chord sheet deletion via WebSocket (outside transaction)
        try:
            from main import connection_manager
            print(f"🎵 Broadcasting chord sheet deletion for song {song_id} in jam {jam_id}")
            await connection_manager.broadcast_to_jam(jam_id, "chord_sheet_update", {
                "type": "chord_sheet_update", 
                "song_id": song_id,
                "action": "delete",
                "chord_sheet_url": None,
                "is_valid": False
            })
        except Exception as e:
            print(f"⚠️ WebSocket broadcast failed (non-critical): {e}")
        
        return {"message": "Chord sheet deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/{jam_id}/chord-sheets/search")
async def search_chord_sheets(
    jam_id: str,
    search_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Search for chord sheets using Ultimate Guitar service"""
    try:
        song_title = search_data.get("song_title", "").strip()
        artist_name = search_data.get("artist_name", "").strip()
        
        if not song_title or not artist_name:
            raise HTTPException(status_code=400, detail="Both song title and artist name are required")
        
        # Search for chord sheets
        results = await ultimate_guitar_service.search_chord_sheets(song_title, artist_name)
        
        # Limit to top 5 results as per requirements
        top_results = results[:5]
        
        return {
            "song_title": song_title,
            "artist_name": artist_name,
            "results": top_results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {e}")

@router.post("/{jam_id}/chord-sheets/validate-url")
async def validate_chord_sheet_url(
    jam_id: str,
    url_data: dict,
    db: AsyncSession = Depends(get_database)
):
    """Validate a chord sheet URL for accessibility and optionally save the result"""
    try:
        url = url_data.get("url", "").strip()
        song_id = url_data.get("song_id")  # Optional: if provided, save validation result
        print(f"🔍 Validating URL: {url}")
        
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            result = {
                "valid": False,
                "error": "Invalid URL format"
            }
        else:
            # Try to fetch the URL to check accessibility
            try:
                import requests
                response = requests.head(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    result = {
                        "valid": True,
                        "status_code": response.status_code,
                        "final_url": response.url
                    }
                else:
                    result = {
                        "valid": False,
                        "error": f"URL returned status code {response.status_code}"
                    }
            except requests.exceptions.RequestException as e:
                result = {
                    "valid": False,
                    "error": f"URL is not accessible: {str(e)}"
                }
        
        # If song_id is provided, save the validation result to the database
        if song_id and result["valid"] is not None:
            await save_validation_result(db, jam_id, song_id, url, result["valid"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {e}")
