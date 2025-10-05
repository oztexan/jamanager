#!/usr/bin/env python3
"""
PostgreSQL JSON Field Fix Script for Jamanager
Fixes JSON field compatibility issues in PostgreSQL
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

async def fix_postgres_json():
    """Fix JSON field compatibility issues in PostgreSQL"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    if "postgresql" not in database_url:
        print("❌ This script is only for PostgreSQL databases")
        return False
    
    print(f"🔗 Connecting to PostgreSQL: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")
    
    try:
        # Create async engine
        engine = create_async_engine(database_url, echo=False)
        
        # Fix JSON fields
        async with engine.begin() as conn:
            # Fix play_history fields that might be stored as strings instead of JSON
            result = await conn.execute(text("""
                UPDATE songs 
                SET play_history = '[]'::json 
                WHERE play_history::text = '"[]"'
            """))
            
            print(f"🔧 Fixed {result.rowcount} JSON field compatibility issues")
            
            if result.rowcount > 0:
                print("✅ JSON fields fixed successfully!")
            else:
                print("ℹ️ No JSON field issues found")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Error fixing JSON fields: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_postgres_json())
    sys.exit(0 if success else 1)