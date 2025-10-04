"""
Static file serving endpoints for the Jamanager application.
"""
import os
import logging
from fastapi import APIRouter
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def read_index():
    """Serve the main HTML file"""
    index_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "index.html")
    logger.info(f"Root route called - looking for index.html at: {index_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Index file exists: {os.path.exists(index_path)}")
    if not os.path.exists(index_path):
        logger.error(f"Index file not found at {index_path}")
    return FileResponse(index_path)

@router.get("/test-chords")
async def test_chords_page():
    """Test page for chord sheet functionality."""
    return FileResponse("test_chord_frontend.html")

@router.get("/jam/{slug}")
async def jam_page(slug: str):
    """Serve the jam page"""
    jam_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "jam.html")
    return FileResponse(jam_path)

@router.get("/songs")
async def songs_page():
    """Serve the songs page"""
    songs_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "songs.html")
    return FileResponse(songs_path)

@router.get("/jams")
async def jams_page():
    """Serve the jams page"""
    jams_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "jams.html")
    return FileResponse(jams_path)

@router.get("/jam-manager")
async def jam_manager_page():
    """Serve the jam manager page"""
    admin_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "admin.html")
    logger.info(f"Jam-manager route called - looking for admin.html at: {admin_path}")
    logger.info(f"Admin file exists: {os.path.exists(admin_path)}")
    if not os.path.exists(admin_path):
        logger.error(f"Admin file not found at {admin_path}")
    return FileResponse(admin_path)

@router.get("/jam-manager/feature-flags")
async def jam_manager_feature_flags():
    """Feature flag management interface"""
    flags_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "feature-flags.html")
    return FileResponse(flags_path)

@router.get("/jam-manager/venues")
async def venue_management_page():
    """Venue management interface"""
    venue_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "venue-management.html")
    return FileResponse(venue_path)

@router.get("/favicon.ico")
async def favicon():
    """Serve the favicon"""
    favicon_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "favicon.ico")
    return FileResponse(favicon_path)
