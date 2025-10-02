#!/usr/bin/env python3
"""
Simple test for the chord sheet API endpoints
"""

import asyncio
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from chord_sheet_api import router
import uvicorn

# Create a simple test app
app = FastAPI(title="Chord Sheet API Test", version="1.0.0")
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Chord Sheet API Test Server", "endpoints": [
        "/api/chord-sheets/search?song_title=Song&artist=Artist",
        "/api/chord-sheets/best?song_title=Song&artist=Artist",
        "/api/chord-sheets/health",
        "/api/chord-sheets/test"
    ]}

if __name__ == "__main__":
    print("🎸 Starting Chord Sheet API Test Server")
    print("=" * 50)
    print("Available endpoints:")
    print("  GET  /api/chord-sheets/search?song_title=Song&artist=Artist")
    print("  GET  /api/chord-sheets/best?song_title=Song&artist=Artist")
    print("  GET  /api/chord-sheets/health")
    print("  GET  /api/chord-sheets/test")
    print("  GET  /docs - Swagger UI")
    print("=" * 50)
    print("Starting server on http://localhost:8001")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
