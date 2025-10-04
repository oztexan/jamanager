#!/usr/bin/env python3
"""
Debug script to test the jam page functionality
"""

import requests
import json
import sys

def test_jam_api():
    """Test the jam API endpoint"""
    print("🔍 Testing jam API...")
    
    # Test the specific jam slug
    jam_slug = "friday-night-jam-main-stage-2025-10-04"
    url = f"http://localhost:8000/api/jams/by-slug/{jam_slug}"
    
    try:
        response = requests.get(url)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Jam ID: {data.get('id')}")
            print(f"   Jam Name: {data.get('name')}")
            print(f"   Songs Count: {len(data.get('songs', []))}")
            print(f"   Songs: {[song.get('song', {}).get('title', 'Unknown') for song in data.get('songs', [])]}")
            return data
        else:
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_static_files():
    """Test if static files are accessible"""
    print("\n🔍 Testing static files...")
    
    static_files = [
        "/static/js/jam-core.js",
        "/static/js/jam-main.js", 
        "/static/js/jam-songs.js",
        "/static/js/jam-attendee.js"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"http://localhost:8000{file_path}")
            print(f"   {file_path}: {response.status_code}")
            if response.status_code != 200:
                print(f"      Error: {response.text[:100]}")
        except Exception as e:
            print(f"   {file_path}: Error - {e}")

def test_jam_page():
    """Test the jam page HTML"""
    print("\n🔍 Testing jam page...")
    
    jam_slug = "friday-night-jam-main-stage-2025-10-04"
    url = f"http://localhost:8000/jam/{jam_slug}"
    
    try:
        response = requests.get(url)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html = response.text
            print(f"   HTML Length: {len(html)}")
            
            # Check for script tags
            script_count = html.count('<script')
            print(f"   Script tags: {script_count}")
            
            # Check for specific elements
            has_songs_list = 'id="songsList"' in html
            has_user_section = 'id="userSection"' in html
            print(f"   Has songsList: {has_songs_list}")
            print(f"   Has userSection: {has_user_section}")
            
            return True
        else:
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

def main():
    print("🚀 Starting jam page debug test...")
    
    # Test API
    jam_data = test_jam_api()
    
    # Test static files
    test_static_files()
    
    # Test jam page
    test_jam_page()
    
    print("\n✅ Debug test complete!")
    
    if jam_data and jam_data.get('songs'):
        print(f"\n📊 Summary:")
        print(f"   - Jam has {len(jam_data['songs'])} songs")
        print(f"   - Songs: {[song.get('song', {}).get('title', 'Unknown') for song in jam_data['songs']]}")
        print(f"   - The issue is likely in the frontend JavaScript not displaying the songs")
    else:
        print(f"\n❌ No songs found in jam data - this is the root cause!")

if __name__ == "__main__":
    main()
