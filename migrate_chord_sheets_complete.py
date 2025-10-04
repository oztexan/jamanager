#!/usr/bin/env python3
"""
Complete migration script to create jam_chord_sheets table with validation fields.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database() -> None:
    """Create jam_chord_sheets table with all fields including validation."""
    
    db_path = "jamanager.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting complete jam_chord_sheets migration...")
        
        # Create jam_chord_sheets table with all fields
        print("Creating jam_chord_sheets table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jam_chord_sheets (
                id TEXT PRIMARY KEY,
                jam_id TEXT NOT NULL,
                song_id TEXT NOT NULL,
                chord_sheet_url TEXT NOT NULL,
                chord_sheet_is_valid BOOLEAN,
                chord_sheet_validated_at DATETIME,
                title TEXT,
                rating TEXT,
                created_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (jam_id) REFERENCES jams (id),
                FOREIGN KEY (song_id) REFERENCES songs (id),
                FOREIGN KEY (created_by) REFERENCES attendees (id),
                UNIQUE (jam_id, song_id)
            )
        """)
        print("✓ Created jam_chord_sheets table with validation fields")
        
        # Commit the changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("The jam_chord_sheets table has been created with validation fields.")
    else:
        print("\n💥 Database migration failed!")
        exit(1)
