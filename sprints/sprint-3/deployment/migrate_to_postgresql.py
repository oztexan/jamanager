#!/usr/bin/env python3
"""
Database Migration Script: SQLite to PostgreSQL
Sprint 3 Deployment - Australia Optimized

This script migrates the SQLite database to PostgreSQL for production deployment.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Change to project root directory
os.chdir(project_root)

# Set environment variables for the migration
os.environ.setdefault('DATABASE_URL', 'sqlite:///data/development/jamanager.db')

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import sqlite3

# Import our models
from models.database import Base, Jam, Song, Venue, JamSong, Vote, Attendee, PerformanceRegistration, JamChordSheet

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    def __init__(self, sqlite_path: str, postgres_url: str):
        self.sqlite_path = sqlite_path
        self.postgres_url = postgres_url
        self.sqlite_engine = create_engine(f"sqlite:///{sqlite_path}")
        self.postgres_engine = create_async_engine(postgres_url)
        self.postgres_session = async_sessionmaker(self.postgres_engine, class_=AsyncSession)

    async def migrate(self):
        """Perform the complete migration from SQLite to PostgreSQL"""
        logger.info("🚀 Starting database migration: SQLite → PostgreSQL")
        
        try:
            # Step 1: Create PostgreSQL tables
            await self.create_postgres_tables()
            
            # Step 2: Migrate data
            await self.migrate_data()
            
            # Step 3: Verify migration
            await self.verify_migration()
            
            logger.info("✅ Database migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise
        finally:
            await self.postgres_engine.dispose()

    async def create_postgres_tables(self):
        """Create all tables in PostgreSQL"""
        logger.info("📋 Creating PostgreSQL tables...")
        
        async with self.postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ PostgreSQL tables created")

    async def migrate_data(self):
        """Migrate data from SQLite to PostgreSQL"""
        logger.info("📦 Migrating data from SQLite to PostgreSQL...")
        
        # Get SQLite connection
        sqlite_conn = sqlite3.connect(self.sqlite_path)
        sqlite_conn.row_factory = sqlite3.Row
        
        try:
            # Migrate in order (respecting foreign key constraints)
            await self.migrate_table(sqlite_conn, "venues", Venue)
            await self.migrate_table(sqlite_conn, "songs", Song)
            await self.migrate_table(sqlite_conn, "jams", Jam)
            await self.migrate_table(sqlite_conn, "attendees", Attendee)
            await self.migrate_table(sqlite_conn, "jam_songs", JamSong)
            await self.migrate_table(sqlite_conn, "votes", Vote)
            await self.migrate_table(sqlite_conn, "performance_registrations", PerformanceRegistration)
            await self.migrate_table(sqlite_conn, "jam_chord_sheets", JamChordSheet)
            
        finally:
            sqlite_conn.close()

    async def migrate_table(self, sqlite_conn, table_name: str, model_class):
        """Migrate a specific table"""
        logger.info(f"  📄 Migrating {table_name}...")
        
        # Get all rows from SQLite
        cursor = sqlite_conn.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            logger.info(f"    ⏭️  {table_name} is empty, skipping")
            return
        
        # Convert to dictionaries
        data = [dict(row) for row in rows]
        
        # Insert into PostgreSQL
        async with self.postgres_session() as session:
            for row_data in data:
                # Create model instance
                instance = model_class(**row_data)
                session.add(instance)
            
            await session.commit()
        
        logger.info(f"    ✅ Migrated {len(data)} rows from {table_name}")

    async def verify_migration(self):
        """Verify the migration was successful"""
        logger.info("🔍 Verifying migration...")
        
        # Check table counts
        tables_to_check = [
            ("venues", Venue),
            ("songs", Song),
            ("jams", Jam),
            ("attendees", Attendee),
            ("jam_songs", JamSong),
            ("votes", Vote),
            ("performance_registrations", PerformanceRegistration),
            ("jam_chord_sheets", JamChordSheet)
        ]
        
        async with self.postgres_session() as session:
            for table_name, model_class in tables_to_check:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                logger.info(f"  📊 {table_name}: {count} rows")
        
        logger.info("✅ Migration verification completed")

def get_postgres_url():
    """Get PostgreSQL URL from environment variables"""
    # Railway provides DATABASE_URL automatically
    postgres_url = os.getenv("DATABASE_URL")
    
    if not postgres_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Convert to async URL if needed
    if postgres_url.startswith("postgres://"):
        postgres_url = postgres_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif not postgres_url.startswith("postgresql+asyncpg://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return postgres_url

async def main():
    """Main migration function"""
    # Get paths
    sqlite_path = os.getenv("SQLITE_PATH", "data/development/jamanager.db")
    postgres_url = get_postgres_url()
    
    logger.info(f"📂 SQLite source: {sqlite_path}")
    logger.info(f"🐘 PostgreSQL target: {postgres_url.split('@')[1] if '@' in postgres_url else 'configured'}")
    
    # Check if SQLite file exists
    if not os.path.exists(sqlite_path):
        logger.error(f"❌ SQLite file not found: {sqlite_path}")
        sys.exit(1)
    
    # Perform migration
    migrator = DatabaseMigrator(sqlite_path, postgres_url)
    await migrator.migrate()

if __name__ == "__main__":
    asyncio.run(main())
