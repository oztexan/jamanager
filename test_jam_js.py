#!/usr/bin/env python3
"""
Test JavaScript execution for jam page
"""

import requests
import re
import json

def extract_js_from_html() -> None:
    """Extract JavaScript from the jam page HTML"""
    print("🔍 Extracting JavaScript from jam page...")
    
    jam_slug = "friday-night-jam-main-stage-2025-10-04"
    url = f"http://localhost:8000/jam/{jam_slug}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"   Error: {response.status_code}")
            return None
            
        html = response.text
        
        # Extract script src attributes
        script_srcs = re.findall(r'<script src="([^"]+)"', html)
        print(f"   Found {len(script_srcs)} script tags")
        
        for src in script_srcs:
            print(f"   - {src}")
            
        return script_srcs
        
    except Exception as e:
        print(f"   Error: {e}")
        return None

def test_js_files() -> None:
    """Test individual JavaScript files for syntax errors"""
    print("\n🔍 Testing JavaScript files...")
    
    js_files = [
        "/static/js/jam-core.js",
        "/static/js/jam-main.js", 
        "/static/js/jam-songs.js",
        "/static/js/jam-attendee.js"
    ]
    
    for js_file in js_files:
        try:
            response = requests.get(f"http://localhost:8000{js_file}")
            if response.status_code == 200:
                content = response.text
                print(f"   {js_file}: OK ({len(content)} chars)")
                
                # Check for basic syntax issues
                if 'console.log' in content:
                    log_count = content.count('console.log')
                    print(f"      - Contains {log_count} console.log statements")
                
                # Check for class definitions
                if 'class ' in content:
                    classes = re.findall(r'class (\w+)', content)
                    print(f"      - Classes: {classes}")
                    
            else:
                print(f"   {js_file}: Error {response.status_code}")
                
        except Exception as e:
            print(f"   {js_file}: Error - {e}")

def simulate_js_execution() -> None:
    """Simulate what should happen when JavaScript runs"""
    print("\n🔍 Simulating JavaScript execution...")
    
    # Get jam data
    jam_slug = "friday-night-jam-main-stage-2025-10-04"
    api_url = f"http://localhost:8000/api/jams/by-slug/{jam_slug}"
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            jam_data = response.json()
            print(f"   Jam data loaded: {jam_data['name']}")
            print(f"   Songs count: {len(jam_data.get('songs', []))}")
            
            # Simulate what the JavaScript should do
            songs = jam_data.get('songs', [])
            if songs:
                print(f"   Songs that should be displayed:")
                for i, jam_song in enumerate(songs[:3]):  # Show first 3
                    song = jam_song.get('song', {})
                    print(f"      {i+1}. {song.get('title', 'Unknown')} - {song.get('artist', 'Unknown')}")
                    
                print(f"   ... and {len(songs) - 3} more songs")
            else:
                print("   ❌ No songs found in jam data!")
                
        else:
            print(f"   API Error: {response.status_code}")
            
    except Exception as e:
        print(f"   Error: {e}")

def main() -> None:
    print("🚀 Starting JavaScript debug test...")
    
    # Extract JS files from HTML
    script_srcs = extract_js_from_html()
    
    # Test individual JS files
    test_js_files()
    
    # Simulate JS execution
    simulate_js_execution()
    
    print("\n✅ JavaScript debug test complete!")
    print("\n💡 Next steps:")
    print("   1. Check browser console for JavaScript errors")
    print("   2. Verify that jam-core.js is calling loadJamData()")
    print("   3. Check that jam-songs.js is receiving the jam data")
    print("   4. Verify that displaySongs() is being called")

if __name__ == "__main__":
    main()
