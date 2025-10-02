#!/usr/bin/env python3
"""
Reset database script - drops and recreates the database with clean schema
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def reset_database():
    """Reset database by dropping and recreating it"""
    
    # Database connection (to postgres database to drop/recreate jamanager)
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:jamanager123@localhost:5432/jamanager")
    
    # Extract connection details
    if "postgresql://" in DATABASE_URL:
        # Parse the URL to get connection details
        url_parts = DATABASE_URL.replace("postgresql://", "").split("/")
        auth_host = url_parts[0]
        db_name = url_parts[1] if len(url_parts) > 1 else "jamanager"
        
        if "@" in auth_host:
            auth, host = auth_host.split("@")
            if ":" in auth:
                user, password = auth.split(":")
            else:
                user, password = auth, ""
        else:
            user, password, host = "postgres", "", auth_host
        
        if ":" in host:
            host, port = host.split(":")
        else:
            port = "5432"
    else:
        # Fallback values
        user, password, host, port, db_name = "postgres", "jamanager123", "localhost", "5432", "jamanager"
    
    # Connect to postgres database to drop/recreate jamanager
    postgres_url = f"postgresql://{user}:{password}@{host}:{port}/postgres"
    
    try:
        conn = await asyncpg.connect(postgres_url)
        print("✅ Connected to postgres database")
        
        # Drop database if it exists
        await conn.execute(f"DROP DATABASE IF EXISTS {db_name}")
        print(f"✅ Dropped database {db_name}")
        
        # Create database
        await conn.execute(f"CREATE DATABASE {db_name}")
        print(f"✅ Created database {db_name}")
        
        await conn.close()
        
        # Now connect to the new database and run schema
        print("✅ Running database initialization...")
        from init_database import init_database
        await init_database()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(reset_database())
