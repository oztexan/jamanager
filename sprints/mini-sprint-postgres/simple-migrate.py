#!/usr/bin/env python3
"""
Simple Migration Script: SQLite to PostgreSQL
Mini-Sprint: PostgreSQL Development Setup

This script migrates data from SQLite to PostgreSQL using direct SQL queries.
"""

import sqlite3
import psycopg2
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    print("🔄 Starting SQLite to PostgreSQL migration...")
    
    # SQLite connection
    sqlite_path = "data/development/jamanager.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at {sqlite_path}")
        return False
    
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
    
    # PostgreSQL connection
    postgres_url = os.getenv("DATABASE_URL")
    if not postgres_url:
        print("❌ DATABASE_URL environment variable not set")
        return False
    
    # Parse PostgreSQL URL
    # postgresql+asyncpg://user:pass@host:port/db
    if postgres_url.startswith("postgresql+asyncpg://"):
        postgres_url = postgres_url.replace("postgresql+asyncpg://", "postgresql://")
    
    try:
        pg_conn = psycopg2.connect(postgres_url)
        pg_cursor = pg_conn.cursor()
        
        print("✅ Connected to both databases")
        
        # Get list of tables
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"📋 Found tables: {', '.join(tables)}")
        
        # Clear PostgreSQL tables first
        print("🧹 Clearing PostgreSQL tables...")
        for table in reversed(tables):  # Reverse order for foreign key constraints
            try:
                pg_cursor.execute(f"DELETE FROM {table}")
                print(f"  ✅ Cleared {table}")
            except Exception as e:
                print(f"  ⚠️ Could not clear {table}: {e}")
        
        pg_conn.commit()
        
        # Migrate data table by table
        for table in tables:
            print(f"📊 Migrating {table}...")
            
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            if not rows:
                print(f"  ⚠️ No data in {table}")
                continue
            
            # Get column names
            columns = [description[0] for description in sqlite_cursor.description]
            
            # Create INSERT statement
            placeholders = ', '.join(['%s'] * len(columns))
            insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert data
            for row in rows:
                try:
                    # Convert row to tuple
                    values = tuple(row)
                    pg_cursor.execute(insert_sql, values)
                except Exception as e:
                    print(f"  ❌ Error inserting row into {table}: {e}")
                    print(f"     Row: {values}")
                    continue
            
            pg_conn.commit()
            print(f"  ✅ Migrated {len(rows)} rows to {table}")
        
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1)
