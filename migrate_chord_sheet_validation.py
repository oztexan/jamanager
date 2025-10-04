#!/usr/bin/env python3
"""
Migration script to add chord sheet validation fields to songs and jam_chord_sheets tables.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add chord sheet validation fields to the database."""
    
    db_path = "jamanager.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting chord sheet validation migration...")
        
        # Add validation fields to songs table
        print("Adding validation fields to songs table...")
        try:
            cursor.execute("""
                ALTER TABLE songs 
                ADD COLUMN chord_sheet_is_valid BOOLEAN
            """)
            print("✓ Added chord_sheet_is_valid to songs table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ chord_sheet_is_valid already exists in songs table")
            else:
                raise
        
        try:
            cursor.execute("""
                ALTER TABLE songs 
                ADD COLUMN chord_sheet_validated_at DATETIME
            """)
            print("✓ Added chord_sheet_validated_at to songs table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ chord_sheet_validated_at already exists in songs table")
            else:
                raise
        
        # Add validation fields to jam_chord_sheets table
        print("Adding validation fields to jam_chord_sheets table...")
        try:
            cursor.execute("""
                ALTER TABLE jam_chord_sheets 
                ADD COLUMN chord_sheet_is_valid BOOLEAN
            """)
            print("✓ Added chord_sheet_is_valid to jam_chord_sheets table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ chord_sheet_is_valid already exists in jam_chord_sheets table")
            else:
                raise
        
        try:
            cursor.execute("""
                ALTER TABLE jam_chord_sheets 
                ADD COLUMN chord_sheet_validated_at DATETIME
            """)
            print("✓ Added chord_sheet_validated_at to jam_chord_sheets table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("✓ chord_sheet_validated_at already exists in jam_chord_sheets table")
            else:
                raise
        
        # Commit the changes
        conn.commit()
        print("✓ Migration completed successfully!")
        
        return True
        
    except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("The chord sheet validation fields have been added to both tables.")
    else:
        print("\n💥 Database migration failed!")
        exit(1)
