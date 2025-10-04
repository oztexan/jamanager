#!/usr/bin/env python3
"""
Simple test to verify web scraping functionality
"""

import requests
from bs4 import BeautifulSoup
import re

def test_ultimate_guitar_search():
    """Test searching Ultimate Guitar directly"""
    print("🎸 Testing Ultimate Guitar Web Scraping")
    print("=" * 50)
    
    # Test search URL
    search_query = "drake passionfruit"
    url = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"
    
    print(f"Searching: {url}")
    
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Successfully got response")
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for various possible result containers
            print("\n🔍 Looking for search results...")
            
            # Try different selectors
            selectors_to_try = [
                'div[class*="result"]',
                'tr[class*="result"]',
                'div[class*="search"]',
                'div[class*="tab"]',
                'a[href*="/tab/"]',
                'a[href*="/chords/"]'
            ]
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                print(f"   Selector '{selector}': {len(elements)} elements found")
                
                if elements:
                    print(f"   First element text: {elements[0].get_text()[:100]}...")
                    if len(elements) > 1:
                        print(f"   Second element text: {elements[1].get_text()[:100]}...")
            
            # Look for any links that might be tabs
            all_links = soup.find_all('a', href=True)
            tab_links = [link for link in all_links if '/tab/' in link.get('href', '') or '/chords/' in link.get('href', '')]
            
            print(f"\n🎵 Found {len(tab_links)} potential tab/chord links:")
            for i, link in enumerate(tab_links[:5]):  # Show first 5
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"   {i+1}. {text} -> {href}")
            
            # Look for rating information
            print(f"\n⭐ Looking for ratings...")
            rating_elements = soup.find_all(text=re.compile(r'\d+\.?\d*\s*/\s*5'))
            print(f"   Found {len(rating_elements)} potential rating elements")
            for i, rating in enumerate(rating_elements[:3]):
                print(f"   {i+1}. {rating}")
            
            # Save the HTML for inspection
            with open('ultimate_guitar_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"\n💾 Saved response HTML to 'ultimate_guitar_response.html'")
            
        else:
            print(f"❌ Failed to get response: {response.status_code}")
            print(f"Response text: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_different_songs():
    """Test with different songs that are more likely to have results"""
    print("\n🎵 Testing with different songs")
    print("=" * 30)
    
    test_songs = [
        ("Wonderwall", "Oasis"),
        ("Hotel California", "Eagles"),
        ("Sweet Child O' Mine", "Guns N' Roses"),
        ("Black", "Pearl Jam")
    ]
    
    for song, artist in test_songs:
        print(f"\n🔍 Testing: {song} by {artist}")
        search_query = f"{artist} {song}"
        url = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                tab_links = soup.find_all('a', href=True)
                tab_links = [link for link in tab_links if '/tab/' in link.get('href', '') or '/chords/' in link.get('href', '')]
                print(f"   Found {len(tab_links)} tab/chord links")
                
                if tab_links:
                    print(f"   First link: {tab_links[0].get_text(strip=True)}")
            else:
                print(f"   Failed: {response.status_code}")
                
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_ultimate_guitar_search()
    test_different_songs()
