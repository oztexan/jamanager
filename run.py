#!/usr/bin/env python3
"""
JaManager Application Entry Point

This script starts the JaManager FastAPI application.
"""

import uvicorn
from jamanger.main import app

if __name__ == "__main__":
    uvicorn.run(
        "jamanger.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
