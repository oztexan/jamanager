#!/usr/bin/env python3
"""
Example of how to integrate the Ultimate Guitar chord sheet service
into the main JaManager application.
"""

import asyncio
import requests
from typing import Optional, Dict, Any

class ChordSheetIntegration:
    """
    Example integration class showing how to use the chord sheet service
    in the main application.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def get_chord_sheet_for_song(self, song_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the best chord sheet for a song and return it in a format
        suitable for the main application.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/get-best-chord-sheet",
                json={
                    "song_name": song_name,
                    "artist_name": artist_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "song_name": data["song_name"],
                    "artist_name": data["artist_name"],
                    "chord_sheet_url": data["chord_sheet_url"],
                    "has_chord_sheet": data["chord_sheet_url"] is not None,
                    "message": data["message"]
                }
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
            print(f"❌ Error getting chord sheet: {e}")
            return None
    
    async def search_all_chord_sheets(self, song_name: str, artist_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for all available chord sheets for a song.
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/search-chord-sheets",
                json={
                    "song_name": song_name,
                    "artist_name": artist_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "song_name": data["song_name"],
                    "artist_name": data["artist_name"],
                    "chord_sheets": data["chord_sheets"],
                    "best_url": data["best_url"],
                    "total_found": len(data["chord_sheets"]),
                    "message": data["message"]
                }
            else:
                print(f"❌ API Error: {response.status_code}")
                return None
                
        except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
            print(f"❌ Error searching chord sheets: {e}")
            return None

async def demo_integration():
    """
    Demo showing how to use the chord sheet integration.
    """
    print("🎸 Chord Sheet Integration Demo")
    print("=" * 40)
    
    integration = ChordSheetIntegration()
    
    # Test songs
    test_songs = [
        ("Wonderwall", "Oasis"),
        ("Hotel California", "Eagles"),
        ("Passionfruit", "Drake")
    ]
    
    for song, artist in test_songs:
        print(f"\n🔍 Getting chord sheet for: {song} by {artist}")
        
        # Get best chord sheet
        result = await integration.get_chord_sheet_for_song(song, artist)
        
        if result and result["has_chord_sheet"]:
            print(f"   ✅ Found chord sheet!")
            print(f"   🎵 URL: {result['chord_sheet_url']}")
            print(f"   📝 Message: {result['message']}")
        else:
            print(f"   ❌ No chord sheet found")
            if result:
                print(f"   📝 Message: {result['message']}")
    
    print(f"\n🔍 Searching all chord sheets for: Wonderwall by Oasis")
    all_results = await integration.search_all_chord_sheets("Wonderwall", "Oasis")
    
    if all_results:
        print(f"   📊 Found {all_results['total_found']} chord sheets")
        print(f"   🏆 Best: {all_results['best_url']}")
        print(f"   📝 Message: {all_results['message']}")
        
        # Show top 3
        print(f"   🎵 Top 3 chord sheets:")
        for i, sheet in enumerate(all_results['chord_sheets'][:3], 1):
            print(f"      {i}. {sheet['title']} (rating: {sheet['rating']})")
            print(f"         URL: {sheet['url']}")

if __name__ == "__main__":
    asyncio.run(demo_integration())