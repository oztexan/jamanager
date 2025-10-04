"""
Song-related API endpoints for the Jamanager application.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_database
from models.database import Song, SongInDB, SongCreate, SongUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/songs", tags=["songs"])

@router.post("", response_model=SongInDB)
async def create_song(
    song_data: SongCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new song"""
    try:
        song = Song(**song_data.dict())
        db.add(song)
        await db.commit()
        await db.refresh(song)
        return song
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating song: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("", response_model=list[SongInDB])
async def get_all_songs(db: AsyncSession = Depends(get_database)):
    """Get all songs"""
    result = await db.execute(select(Song).order_by(Song.title))
    songs = result.scalars().all()
    return songs

@router.get("/{song_id}", response_model=SongInDB)
async def get_song(song_id: str, db: AsyncSession = Depends(get_database)):
    """Get a single song by ID"""
    result = await db.execute(select(Song).where(Song.id == song_id))
    song = result.scalars().first()
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.put("/{song_id}", response_model=SongInDB)
async def update_song(
    song_id: str,
    song_update: SongUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an existing song"""
    try:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalars().first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")

        update_data = song_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(song, key, value)
        
        song.updated_at = func.now()
        await db.commit()
        await db.refresh(song)
        return song
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating song: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{song_id}")
async def delete_song(song_id: str, db: AsyncSession = Depends(get_database)):
    """Delete a song"""
    try:
        result = await db.execute(select(Song).where(Song.id == song_id))
        song = result.scalars().first()
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        await db.delete(song)
        await db.commit()
        return {"message": "Song deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting song: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
