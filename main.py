"""
Main FastAPI application for Jamanager.

This module serves as the entry point for the Jamanager application, handling:
- FastAPI app initialization and configuration
- CORS middleware setup
- Router registration for all API endpoints
- Static file serving
- WebSocket connection management
- Database initialization

The application provides a real-time jam session management system with:
- Song queue management and voting
- WebSocket-based real-time updates
- User authentication and authorization
- Chord sheet integration with Ultimate Guitar
- Venue and jam session management

Author: Jamanager Development Team
Version: 1.0.0
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def is_development_environment() -> bool:
    """
    Determine if the application is running in development mode.
    
    Returns:
        bool: True if in development mode, False otherwise
    """
    # Check environment variables
    debug_mode = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    show_dev_indicator = os.getenv("SHOW_DEV_INDICATOR", "True").lower() in ("true", "1", "yes")
    
    # Check if running on development port
    port = os.getenv("PORT", "3000")
    dev_ports = ["3000", "8000", "5000", "3001", "8001"]
    is_dev_port = port in dev_ports
    
    # Check if running locally (not in production)
    is_local = os.getenv("ENVIRONMENT", "").lower() not in ("production", "prod")
    
    return debug_mode or show_dev_indicator or is_dev_port or is_local

# Import core modules
from core.database import init_database
from core.jam_config import JamConfig
from core.feature_flag_api_simple import router as feature_flag_router
from services.chord_sheet_api import router as chord_sheet_router
from services.connection_manager import ConnectionManager

# Sprint 3 Architecture Improvements
from core.config import get_config
from core.connection_pool import initialize_connection_pool
from core.background_jobs import start_background_jobs, shutdown_background_jobs
from core.event_system import event_handler, EventTypes

# Import endpoint routers
from api.endpoints import static, songs, venues, jams, websocket, auth, jam_chord_sheets, system

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

# Add development environment middleware
@app.middleware("http")
async def add_dev_environment_middleware(request: Request, call_next):
    """
    Middleware to inject development environment meta tag into HTML responses.
    """
    response = await call_next(request)
    
    # Only modify HTML responses
    if (response.headers.get("content-type", "").startswith("text/html") and 
        is_development_environment()):
        
        # Read the response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # Convert to string and inject dev environment meta tag
        html_content = body.decode("utf-8")
        
        # Replace the meta tag if it exists, or add it if it doesn't
        if '<meta name="dev-environment"' in html_content:
            # Update existing meta tag
            html_content = html_content.replace(
                '<meta name="dev-environment" content="true">',
                '<meta name="dev-environment" content="true">'
            )
        else:
            # Add meta tag after viewport meta tag
            html_content = html_content.replace(
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
                '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta name="dev-environment" content="true">'
            )
        
        # Create new response with modified content
        response = HTMLResponse(
            content=html_content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    
    return response

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
app.include_router(system.router)  # Sprint 3: System management endpoints

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
async def startup_event():
    """
    Initialize application on startup.
    
    This function is called when the FastAPI application starts up and handles:
    - Database initialization and schema creation
    - Logging configuration
    - Application health checks
    
    Raises:
        Exception: If database initialization fails
    """
    try:
        logger.info("Starting Jamanager application...")
        
        # Sprint 3: Initialize configuration and connection pool
        logger.info("Initializing Sprint 3 architecture components...")
        initialize_connection_pool()
        logger.info("Connection pool initialized")
        
        # Initialize database
        logger.info("Initializing database...")
        await init_database()
        logger.info("Database initialization completed successfully")
        
        # Sprint 3: Start background jobs
        logger.info("Starting background job system...")
        await start_background_jobs()
        logger.info("Background job system started")
        
        # Sprint 3: Emit system startup event
        await event_handler.emit(
            EventTypes.SYSTEM_STARTUP,
            {"message": "Jamanager application started successfully"},
            source="main_app"
        )
        
        logger.info("Jamanager application started successfully")
    except Exception as e:
        logger.error(f"Failed to start Jamanager application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup application on shutdown.
    
    This function is called when the FastAPI application shuts down and handles:
    - Background job system shutdown
    - Connection pool cleanup
    - Event system cleanup
    """
    try:
        logger.info("Shutting down Jamanager application...")
        
        # Sprint 3: Emit system shutdown event
        await event_handler.emit(
            EventTypes.SYSTEM_SHUTDOWN,
            {"message": "Jamanager application shutting down"},
            source="main_app"
        )
        
        # Sprint 3: Shutdown background jobs
        logger.info("Shutting down background job system...")
        await shutdown_background_jobs()
        logger.info("Background job system shutdown completed")
        
        # Sprint 3: Cleanup connection pool
        logger.info("Cleaning up connection pool...")
        from core.connection_pool import cleanup_connection_pool
        await cleanup_connection_pool()
        logger.info("Connection pool cleanup completed")
        
        logger.info("Jamanager application shutdown completed")
    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")