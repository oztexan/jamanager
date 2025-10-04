#!/usr/bin/env python3
"""
Test script for the Ultimate Guitar chord sheet service.
"""
import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ultimate_guitar_service import ultimate_guitar_service

async def test_chord_search():
    """Test the chord sheet search functionality."""
    print("🎸 Testing Ultimate Guitar Chord Sheet Service")
    print("=" * 50)
    
    test_cases = [
        ("Wonderwall", "Oasis"),
        ("Hotel California", "Eagles"),
        ("Sweet Child O' Mine", "Guns N' Roses"),
        ("Black", "Pearl Jam"),
        ("Passionfruit", "Drake")
    ]
    
    for song, artist in test_cases:
        print(f"\n🔍 Testing: {song} by {artist}")
        print("-" * 30)
        
        try:
            # Test search
            results = await ultimate_guitar_service.search_chord_sheets(song, artist)
            print(f"   Found {len(results)} chord sheet(s)")
            
            if results:
                for i, result in enumerate(results[:3]):  # Show top 3
                    print(f"   {i+1}. {result['title']} (rating: {result['rating']})")
                    print(f"      URL: {result['url']}")
                
                # Test getting best result
                best_url = await ultimate_guitar_service.get_best_chord_sheet(song, artist)
                print(f"   🏆 Best URL: {best_url}")
            else:
                print("   ❌ No chord sheets found")
                
        except (ValueError, TypeError) as e:
        logger.error(f"Unexpected error: {e}")
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_chord_search())