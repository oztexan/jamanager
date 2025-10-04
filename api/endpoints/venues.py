"""
Venue-related API endpoints for the Jamanager application.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from core.database import get_database
from models.database import Venue, VenueInDB, VenueCreate, VenueUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/venues", tags=["venues"])

@router.get("", response_model=list[VenueInDB])
async def get_all_venues(db: AsyncSession = Depends(get_database)):
    """Get all venues"""
    result = await db.execute(select(Venue).order_by(Venue.name))
    venues = result.scalars().all()
    return venues

@router.post("", response_model=VenueInDB)
async def create_venue(
    venue_data: VenueCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new venue"""
    try:
        venue = Venue(**venue_data.dict())
        db.add(venue)
        await db.commit()
        await db.refresh(venue)
        return venue
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        await db.rollback()
        logger.error(f"Error creating venue: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.get("/{venue_id}", response_model=VenueInDB)
async def get_venue(venue_id: str, db: AsyncSession = Depends(get_database)):
    """Get a single venue by ID"""
    result = await db.execute(select(Venue).where(Venue.id == venue_id))
    venue = result.scalars().first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@router.put("/{venue_id}", response_model=VenueInDB)
async def update_venue(
    venue_id: str,
    venue_update: VenueUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update an existing venue"""
    try:
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = result.scalars().first()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")

        update_data = venue_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venue, key, value)
        
        venue.updated_at = func.now()
        await db.commit()
        await db.refresh(venue)
        return venue
    except HTTPException:
        raise
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        await db.rollback()
        logger.error(f"Error updating venue: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.delete("/{venue_id}")
async def delete_venue(venue_id: str, db: AsyncSession = Depends(get_database)):
    """Delete a venue"""
    try:
        result = await db.execute(select(Venue).where(Venue.id == venue_id))
        venue = result.scalars().first()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        
        await db.delete(venue)
        await db.commit()
        return {"message": "Venue deleted successfully"}
    except HTTPException:
        raise
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        await db.rollback()
        logger.error(f"Error deleting venue: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
