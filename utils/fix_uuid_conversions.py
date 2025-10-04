#!/usr/bin/env python3
"""
Script to fix UUID conversions in main.py for SQLite compatibility
"""

import re

def fix_uuid_conversions():
    """Remove UUID conversions from main.py"""
    
    with open('jamanager/main.py', 'r') as f:
        content = f.read()
    
    # Remove UUID imports and conversions
    # Remove uuid import if it's only used for UUID conversions
    content = re.sub(r'import uuid\n', '', content)
    
    # Remove UUID conversion lines
    content = re.sub(r'        \w+_uuid = uuid\.UUID\(\w+\)\n', '', content)
    
    # Replace UUID variables with string variables
    replacements = [
        ('jam_uuid', 'jam_id'),
        ('song_uuid', 'song_id'),
        ('attendee_uuid', 'attendee_id'),
        ('venue_uuid', 'venue_id'),
    ]
    
    for old_var, new_var in replacements:
        content = content.replace(old_var, new_var)
    
    # Remove ValueError handling for UUID conversion
    content = re.sub(r'    except ValueError as e:\n        raise HTTPException\(status_code=400, detail=f"Invalid UUID: \{e\}"\)\n', '', content)
    
    with open('jamanager/main.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed UUID conversions in main.py")

if __name__ == "__main__":
    fix_uuid_conversions()
