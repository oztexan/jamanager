"""
Main FastAPI application for Jamanager.
This file handles app initialization and includes all the modular routers.
"""
import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import core modules
from core.database import init_database
from core.jam_config import JamConfig
from core.feature_flag_api_simple import router as feature_flag_router
from services.chord_sheet_api import router as chord_sheet_router
from services.connection_manager import ConnectionManager

# Import endpoint routers
from api.endpoints import static, songs, venues, jams, websocket, auth, jam_chord_sheets

# Create FastAPI app
app = FastAPI(title="Jamanager API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(feature_flag_router)
app.include_router(chord_sheet_router)
app.include_router(static.router)
app.include_router(songs.router)
app.include_router(venues.router)
app.include_router(jams.router)
app.include_router(jam_chord_sheets.router, prefix="/api/jams", tags=["jam-chord-sheets"])
app.include_router(websocket.router)
app.include_router(auth.router)

# Connection manager for WebSocket connections
connection_manager = ConnectionManager()

# Set the connection manager in the websocket module
websocket.set_connection_manager(connection_manager)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
logger.info(f"Mounting static files from directory: {static_dir}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Static directory exists: {os.path.exists(static_dir)}")
if os.path.exists(static_dir):
    logger.info(f"Static directory contents: {os.listdir(static_dir)}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Ensure uploads directory exists
JamConfig.ensure_upload_dir()

@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup"""
    await init_database()