#!/usr/bin/env python3
"""
PostgreSQL Connection Test Script for Jamanager
Tests basic connectivity to PostgreSQL database
"""

import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

async def test_postgres_connection():
    """Test PostgreSQL database connection"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    print(f"🔗 Testing PostgreSQL connection: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url, echo=False)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL version: {version}")
            
            # Test basic query
            result = await conn.execute(text("SELECT current_database(), current_user"))
            db_name, user = result.fetchone()
            print(f"🗄️ Database: {db_name}")
            print(f"👤 User: {user}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_postgres_connection())
    sys.exit(0 if success else 1)