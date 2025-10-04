import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, List, Dict, Any
import json

class UltimateGuitarService:
    """
    Service to search Ultimate Guitar for chord sheets and tabs.
    Based on the ultimate-api project but integrated for our use case.
    """
    
    BASE_URL = "https://www.ultimate-guitar.com"
    SEARCH_URL = f"{BASE_URL}/search.php"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    async def search_chord_sheets(self, song_name: str, artist_name: str) -> List[Dict[str, Any]]:
        """
        Search for chord sheets on Ultimate Guitar.
        Returns a list of matching chord sheets with URLs and ratings.
        """
        search_query = f'"{artist_name}" "{song_name}"'
        params = {
            'search_type': 'title',
            'value': search_query
        }
        
        try:
            print(f"🔍 Searching Ultimate Guitar for: {search_query}")
            response = self.session.get(self.SEARCH_URL, params=params, timeout=10)
            response.raise_for_status()
            
            # Save response for debugging
            with open("ultimate_guitar_response.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved response HTML to 'ultimate_guitar_response.html'")
            
            # Parse the search results
            results = self._parse_search_results(response.text, song_name, artist_name)
            print(f"✅ Found {len(results)} chord sheet results")
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error searching Ultimate Guitar: {e}")
            return []
    
    def _parse_search_results(self, html_content: str, song_name: str, artist_name: str) -> List[Dict[str, Any]]:
        """
        Parse Ultimate Guitar search results HTML to extract chord sheet information.
        Ultimate Guitar embeds search results as JSON in a data-content attribute.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Look for the div with data-content attribute containing JSON
        store_div = soup.find('div', class_='js-store')
        if not store_div:
            print("❌ No js-store div found")
            return results
        
        try:
            # Extract and parse the JSON data
            data_content = store_div.get('data-content')
            if not data_content:
                print("❌ No data-content found in js-store div")
                return results
            
            # Parse the JSON data
            import json
            data = json.loads(data_content)
            
            # Navigate to the search results
            store = data.get('store', {})
            page = store.get('page', {})
            page_data = page.get('data', {})
            search_results = page_data.get('results', [])
            
            print(f"📊 Found {len(search_results)} total results in JSON data")
            
            # Filter for chord sheets only
            chord_results = []
            for result in search_results:
                if result.get('type') == 'Chords':
                    chord_results.append({
                        'title': f"{result.get('song_name', 'Unknown')} by {result.get('artist_name', 'Unknown')}",
                        'url': result.get('tab_url', ''),
                        'rating': result.get('rating', 0),
                        'votes': result.get('votes', 0),
                        'difficulty': result.get('difficulty', 'unknown'),
                        'type': 'chords',
                        'artist_name': result.get('artist_name', ''),
                        'song_name': result.get('song_name', '')
                    })
            
            print(f"🎸 Found {len(chord_results)} chord sheet results")
            
            # Sort by exact match first, then by votes
            def sort_key(x):
                # Check for exact artist match
                artist_match = x['artist_name'].lower() == artist_name.lower()
                song_match = x['song_name'].lower() == song_name.lower()
                
                # Priority: exact artist + song match, then exact artist match, then by votes
                if artist_match and song_match:
                    return (0, -x['votes'])  # Highest priority, then by votes
                elif artist_match:
                    return (1, -x['votes'])  # Second priority, then by votes
                else:
                    return (2, -x['votes'])  # Third priority, then by votes
            
            chord_results.sort(key=sort_key)
            
            return chord_results
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON data: {e}")
            return results
        except Exception as e:
            print(f"❌ Error extracting search results: {e}")
            return results
    
    async def get_best_chord_sheet(self, song_name: str, artist_name: str) -> Optional[str]:
        """
        Get the best (highest rated) chord sheet URL for a song.
        """
        results = await self.search_chord_sheets(song_name, artist_name)
        
        if not results:
            return None
        
        # Return the URL of the highest rated chord sheet
        best_result = results[0]
        print(f"🎸 Best chord sheet: {best_result['title']} (rating: {best_result['rating']})")
        return best_result['url']
    
    async def get_chord_sheet_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific chord sheet.
        This would use the tab_parser from the ultimate-api project.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the chord sheet content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract song information
            title_elem = soup.find('h1', class_='js-tab-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            artist_elem = soup.find('h2', class_='js-tab-artist')
            artist = artist_elem.get_text(strip=True) if artist_elem else "Unknown"
            
            # Extract chord content
            chord_content = soup.find('div', class_='js-tab-content')
            chords = chord_content.get_text(strip=True) if chord_content else ""
            
            return {
                'title': title,
                'artist': artist,
                'chords': chords,
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching chord sheet info: {e}")
            return None

# Global instance
ultimate_guitar_service = UltimateGuitarService()