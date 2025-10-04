# Database Setup

This document describes the SQLite database setup for Jamanager.

## Schema Files

- **`schema.sql`** - Consolidated database schema with all tables and indexes
- **`init_sqlite_db.py`** - Initialize SQLite database with schema and sample data
- **`reset_database.py`** - Drop and recreate database from scratch

## Quick Start

### 1. Initialize Database

```bash
# Activate Python environment
pyenv activate jv3.11.11

# Initialize SQLite database with schema and sample data
python init_dev_database.py
```

### 2. Reset Database (if needed)

```bash
# Drop and recreate database from scratch
python reset_database.py
```

## Schema Overview

The database uses a simplified song model with the following tables:

### Core Tables

- **`venues`** - Jam venues
- **`songs`** - Song library (simplified: title, artist, chord_sheet_url only)
- **`jams`** - Jam sessions
- **`jam_songs`** - Songs in each jam
- **`attendees`** - Jam attendees
- **`votes`** - Song votes
- **`performance_registrations`** - Who's performing what

### Key Features

- **Simplified Song Model**: Removed genre, chord_chart, and tags fields
- **UUID Primary Keys**: All tables use UUIDs for better distributed system support
- **JSON Support**: For flexible data like play_history and captains
- **Automatic Timestamps**: created_at and updated_at fields
- **Proper Indexes**: For optimal query performance

## Migration History

All previous development migrations have been consolidated into this single schema:

- ✅ Removed `type` (genre) field from songs
- ✅ Removed `chord_chart` field from songs  
- ✅ Removed `tags` field from songs
- ✅ Added `chord_sheet_url` for Ultimate Guitar integration
- ✅ Added venue management system
- ✅ Added performance registration system
- ✅ Migrated from PostgreSQL to SQLite for easier setup

## Environment Variables

Set these in your `.env` file:

```bash
DATABASE_URL=sqlite+aiosqlite:///./jamanager.db
```

## Development Workflow

1. **Make schema changes**: Edit `schema.sql`
2. **Test changes**: Run `python reset_database.py`
3. **Update models**: Update SQLAlchemy models in `models/database.py`
4. **Test application**: Start server and test functionality

## Production Considerations

For production deployment:

1. **Backup existing data** before running reset scripts
2. **Use proper migrations** (Alembic) for production schema changes
3. **Set secure connection strings**
4. **Configure proper indexes** based on query patterns
5. **Set up monitoring** and backup procedures
6. **Consider PostgreSQL** for high-traffic production environments