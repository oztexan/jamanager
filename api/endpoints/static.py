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
    # Use absolute path to static directory
    static_dir = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    index_path = os.path.join(static_dir, "index.html")
    index_path = os.path.abspath(index_path)
    
    logger.info(f"Root route called - looking for index.html at: {index_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Static directory: {static_dir}")
    logger.info(f"Index file exists: {os.path.exists(index_path)}")
    
    if not os.path.exists(index_path):
        logger.error(f"Index file not found at {index_path}")
        # Try alternative path
        alt_path = os.path.join(os.getcwd(), "static", "index.html")
        logger.info(f"Trying alternative path: {alt_path}")
        if os.path.exists(alt_path):
            index_path = alt_path
        else:
            logger.error(f"Alternative path also not found: {alt_path}")
    
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

@router.get("/song-details")
async def song_details_page():
    """Serve the song details page"""
    song_details_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "song-details.html")
    return FileResponse(song_details_path)

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
    favicon_path = os.path.abspath(favicon_path)
    
    if not os.path.exists(favicon_path):
        # Try alternative path
        alt_path = os.path.join(os.getcwd(), "static", "favicon.ico")
        if os.path.exists(alt_path):
            favicon_path = alt_path
    
    return FileResponse(favicon_path)
