#!/usr/bin/env python3
"""
Fix the songs table schema in backend/jamanager.db by recreating it with proper validation columns.
"""

import sqlite3
import os
import shutil
from datetime import datetime

def fix_songs_table():
    """Fix the songs table by recreating it with proper validation columns."""
    
    db_path = "backend/jamanager.db"
    backup_path = f"backend/jamanager_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        # Create backup
        shutil.copy2(db_path, backup_path)
        print(f"✓ Created backup: {backup_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Fixing songs table schema in backend/jamanager.db...")
        
        # Get all data from songs table
        cursor.execute("SELECT * FROM songs")
        songs_data = cursor.fetchall()
        
        # Get column names
        cursor.execute("PRAGMA table_info(songs)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        print(f"Found {len(songs_data)} songs to migrate")
        
        # Drop the existing songs table
        cursor.execute("DROP TABLE songs")
        print("✓ Dropped existing songs table")
        
        # Create new songs table with proper schema
        cursor.execute("""
            CREATE TABLE songs (
                id VARCHAR PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                artist VARCHAR(255) NOT NULL,
                chord_sheet_url VARCHAR(500),
                chord_sheet_is_valid BOOLEAN,
                chord_sheet_validated_at DATETIME,
                vote_count INTEGER DEFAULT 0,
                times_played INTEGER DEFAULT 0,
                last_played DATETIME,
                play_history JSON DEFAULT '[]',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created new songs table with proper schema")
        
        # Recreate the trigger
        cursor.execute("""
            CREATE TRIGGER update_songs_updated_at 
            AFTER UPDATE ON songs 
            BEGIN 
                UPDATE songs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
            END
        """)
        print("✓ Recreated update trigger")
        
        # Migrate data back
        if songs_data:
            # Map old columns to new columns
            id_idx = column_names.index('id')
            title_idx = column_names.index('title')
            artist_idx = column_names.index('artist')
            chord_sheet_url_idx = column_names.index('chord_sheet_url') if 'chord_sheet_url' in column_names else None
            vote_count_idx = column_names.index('vote_count') if 'vote_count' in column_names else None
            times_played_idx = column_names.index('times_played') if 'times_played' in column_names else None
            last_played_idx = column_names.index('last_played') if 'last_played' in column_names else None
            play_history_idx = column_names.index('play_history') if 'play_history' in column_names else None
            created_at_idx = column_names.index('created_at') if 'created_at' in column_names else None
            updated_at_idx = column_names.index('updated_at') if 'updated_at' in column_names else None
            
            for song in songs_data:
                cursor.execute("""
                    INSERT INTO songs (
                        id, title, artist, chord_sheet_url, chord_sheet_is_valid, chord_sheet_validated_at,
                        vote_count, times_played, last_played, play_history, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    song[id_idx],
                    song[title_idx],
                    song[artist_idx],
                    song[chord_sheet_url_idx] if chord_sheet_url_idx is not None else None,
                    None,  # chord_sheet_is_valid - will be validated later
                    None,  # chord_sheet_validated_at - will be set when validated
                    song[vote_count_idx] if vote_count_idx is not None else 0,
                    song[times_played_idx] if times_played_idx is not None else 0,
                    song[last_played_idx] if last_played_idx is not None else None,
                    song[play_history_idx] if play_history_idx is not None else '[]',
                    song[created_at_idx] if created_at_idx is not None else None,
                    song[updated_at_idx] if updated_at_idx is not None else None
                ))
            
            print(f"✓ Migrated {len(songs_data)} songs to new table")
        
        # Commit changes
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
    success = fix_songs_table()
    if success:
        print("\n🎉 Backend songs table fixed successfully!")
        print("The songs table now has proper validation columns.")
    else:
        print("\n💥 Backend songs table fix failed!")
        exit(1)
