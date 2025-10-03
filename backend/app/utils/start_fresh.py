#!/usr/bin/env python3
"""
Fresh start script for Jamanager with SQLite
This script ensures a clean setup and starts the server
"""

import os
import sys
import subprocess
import asyncio
import aiosqlite
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_database():
    """Check if the SQLite database exists and has data"""
    db_path = "jamanager.db"
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        # Quick check to see if database has tables
        async def check_db():
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = await cursor.fetchall()
                return len(tables) > 0
        
        has_tables = asyncio.run(check_db())
        if not has_tables:
            print("❌ Database exists but has no tables")
            return False
        
        print("✅ Database exists and has tables")
        return True
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    print("🚀 Starting Jamanager with SQLite...")
    
    # Change to the project directory
    project_dir = "/Users/chrisrobertson/dev/jamanager"
    os.chdir(project_dir)
    print(f"📁 Working directory: {project_dir}")
    
    # Check if database exists and is valid
    if not check_database():
        print("🔧 Initializing database...")
        success, stdout, stderr = run_command("python init_sqlite_db.py")
        if not success:
            print(f"❌ Database initialization failed: {stderr}")
            return False
        print("✅ Database initialized successfully")
    
    # Kill any existing server processes
    print("🛑 Stopping any existing server processes...")
    run_command("pkill -f 'uvicorn.*main:app'")
    
    # Set environment variables
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite+aiosqlite:///./jamanager.db'
    
    print("🌐 Starting server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 Network access: http://192.168.86.31:8000")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the server
    try:
        cmd = ["uvicorn", "jamanager.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
