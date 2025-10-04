# 🎸 Ultimate Guitar Chord Sheet Integration

## Overview

Successfully integrated Ultimate Guitar chord sheet lookup functionality into JaManager using the `ultimate-api` approach. This provides real-time access to chord sheets from Ultimate Guitar without requiring an official API.

## ✅ What's Working

### 1. **Ultimate Guitar Service** (`ultimate_guitar_service.py`)
- ✅ Searches Ultimate Guitar for chord sheets by song and artist
- ✅ Parses JSON data embedded in Ultimate Guitar's HTML response
- ✅ Filters results to show only chord sheets (not tabs)
- ✅ Sorts results by rating (highest first)
- ✅ Returns structured data with URLs, ratings, votes, and difficulty

### 2. **FastAPI Endpoints** (`chord_sheet_api.py`)
- ✅ `POST /api/search-chord-sheets` - Search for all chord sheets
- ✅ `POST /api/get-best-chord-sheet` - Get the highest-rated chord sheet
- ✅ `POST /api/get-chord-sheet-info` - Get detailed chord sheet information
- ✅ `GET /api/test-chord-search` - Test endpoint for verification

### 3. **Web Interface** (`test_chord_frontend.html`)
- ✅ User-friendly web interface at `/test-chords`
- ✅ Search for chord sheets by song and artist
- ✅ Display results with ratings and direct links
- ✅ Test API functionality

### 4. **Integration Examples**
- ✅ `integrate_chord_sheets.py` - Shows how to use the service in other applications
- ✅ `test_chord_sheets.py` - Command-line testing script

## 🎯 Test Results

Successfully tested with popular songs:

| Song | Artist | Chord Sheets Found | Best Rating | Best URL |
|------|--------|-------------------|-------------|----------|
| Wonderwall | Oasis | 15 | 4.87 | [View](https://tabs.ultimate-guitar.com/tab/oasis/wonderwall-chords-1064463) |
| Hotel California | Eagles | 8 | 4.86 | [View](https://tabs.ultimate-guitar.com/tab/eagles/hotel-california-chords-688698) |
| Sweet Child O' Mine | Guns N' Roses | 8 | 4.85 | [View](https://tabs.ultimate-guitar.com/tab/guns-n-roses/sweet-child-o-mine-chords-1719104) |
| Black | Pearl Jam | 14 | 4.88 | [View](https://tabs.ultimate-guitar.com/tab/pearl-jam/black-chords-1115192) |
| Passionfruit | Drake | 9 | 4.86 | [View](https://tabs.ultimate-guitar.com/tab/drake/passionfruit-chords-1972279) |

## 🚀 How to Use

### 1. **Start the Server**
```bash
cd /Users/chrisrobertson/dev/jamanager
pyenv activate jv3.11.11
python run.py
```

### 2. **Test the Web Interface**
Visit: http://localhost:8000/test-chords

### 3. **Use the API**
```bash
# Get best chord sheet
curl -X POST "http://localhost:8000/api/get-best-chord-sheet" \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Wonderwall", "artist_name": "Oasis"}'

# Search all chord sheets
curl -X POST "http://localhost:8000/api/search-chord-sheets" \
  -H "Content-Type: application/json" \
  -d '{"song_name": "Wonderwall", "artist_name": "Oasis"}'
```

### 4. **Integrate in Your Code**
```python
import requests

# Get best chord sheet
response = requests.post(
    "http://localhost:8000/api/get-best-chord-sheet",
    json={"song_name": "Wonderwall", "artist_name": "Oasis"}
)
data = response.json()
print(f"Best chord sheet: {data['chord_sheet_url']}")
```

## 🔧 Technical Details

### **How It Works**
1. **Search Request**: Sends search query to Ultimate Guitar's search endpoint
2. **HTML Response**: Receives HTML with embedded JSON data in `data-content` attribute
3. **JSON Parsing**: Extracts and parses the search results from the JSON
4. **Filtering**: Filters results to show only chord sheets (type: "Chords")
5. **Sorting**: Sorts by rating (highest first)
6. **Response**: Returns structured data with URLs and metadata

### **Key Files**
- `ultimate_guitar_service.py` - Core scraping and parsing logic
- `chord_sheet_api.py` - FastAPI endpoints
- `test_chord_frontend.html` - Web interface
- `integrate_chord_sheets.py` - Integration examples
- `test_chord_sheets.py` - Testing script

### **Dependencies**
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `fastapi` - API framework
- `pydantic` - Data validation

## 🎵 Next Steps

### **Integration with JaManager**
1. **Add to Song Model**: Add `chord_sheet_url` field to songs
2. **Auto-fetch on Creation**: Automatically fetch chord sheets when songs are created
3. **UI Integration**: Add "View Chord Sheet" buttons to song displays
4. **Caching**: Cache chord sheet URLs to avoid repeated API calls

### **Example Integration**
```python
# In song creation
async def create_song(song_data):
    # Create song
    song = Song(**song_data)
    
    # Fetch chord sheet
    chord_service = UltimateGuitarService()
    chord_url = await chord_service.get_best_chord_sheet(
        song.title, song.artist
    )
    
    if chord_url:
        song.chord_sheet_url = chord_url
    
    return song
```

## ⚠️ Important Notes

- **Rate Limiting**: Ultimate Guitar may have rate limits - consider caching
- **Terms of Service**: This uses web scraping - ensure compliance with UG's ToS
- **Reliability**: Web scraping can break if Ultimate Guitar changes their HTML structure
- **Fallback**: Always have a fallback when chord sheets aren't available

## 🎉 Success!

The Ultimate Guitar chord sheet integration is now fully functional and ready for use in JaManager. Users can now easily find and access chord sheets for any song in the system!
