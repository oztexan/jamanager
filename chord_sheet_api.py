from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from ultimate_guitar_service import ultimate_guitar_service

router = APIRouter()

class ChordSheetSearchRequest(BaseModel):
    song_name: str
    artist_name: str

class ChordSheetSearchResponse(BaseModel):
    song_name: str
    artist_name: str
    chord_sheets: List[Dict[str, Any]]
    best_url: Optional[str] = None
    message: str

class ChordSheetInfoRequest(BaseModel):
    url: str

class ChordSheetInfoResponse(BaseModel):
    title: str
    artist: str
    chords: str
    url: str

@router.post("/api/search-chord-sheets", response_model=ChordSheetSearchResponse)
async def search_chord_sheets(request: ChordSheetSearchRequest):
    """
    Search for chord sheets on Ultimate Guitar for a given song and artist.
    """
    print(f"🎵 Searching for chord sheets: {request.song_name} by {request.artist_name}")
    
    try:
        chord_sheets = await ultimate_guitar_service.search_chord_sheets(
            request.song_name, 
            request.artist_name
        )
        
        best_url = None
        if chord_sheets:
            best_url = chord_sheets[0]['url']
        
        return ChordSheetSearchResponse(
            song_name=request.song_name,
            artist_name=request.artist_name,
            chord_sheets=chord_sheets,
            best_url=best_url,
            message=f"Found {len(chord_sheets)} chord sheet(s)" if chord_sheets else "No chord sheets found"
        )
        
    except Exception as e:
        print(f"❌ Error in search_chord_sheets: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching for chord sheets: {str(e)}")

@router.post("/api/get-best-chord-sheet", response_model=Dict[str, Any])
async def get_best_chord_sheet(request: ChordSheetSearchRequest):
    """
    Get the best (highest rated) chord sheet URL for a song.
    """
    print(f"🎸 Getting best chord sheet: {request.song_name} by {request.artist_name}")
    
    try:
        best_url = await ultimate_guitar_service.get_best_chord_sheet(
            request.song_name, 
            request.artist_name
        )
        
        return {
            "song_name": request.song_name,
            "artist_name": request.artist_name,
            "chord_sheet_url": best_url,
            "message": "Best chord sheet found" if best_url else "No chord sheets found"
        }
        
    except Exception as e:
        print(f"❌ Error in get_best_chord_sheet: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting best chord sheet: {str(e)}")

@router.post("/api/get-chord-sheet-info", response_model=ChordSheetInfoResponse)
async def get_chord_sheet_info(request: ChordSheetInfoRequest):
    """
    Get detailed information about a specific chord sheet.
    """
    print(f"📄 Getting chord sheet info for: {request.url}")
    
    try:
        info = await ultimate_guitar_service.get_chord_sheet_info(request.url)
        
        if not info:
            raise HTTPException(status_code=404, detail="Chord sheet not found or could not be parsed")
        
        return ChordSheetInfoResponse(**info)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_chord_sheet_info: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting chord sheet info: {str(e)}")

@router.get("/api/test-chord-search")
async def test_chord_search():
    """
    Test endpoint to verify the chord sheet service is working.
    """
    test_song = "Wonderwall"
    test_artist = "Oasis"
    
    try:
        results = await ultimate_guitar_service.search_chord_sheets(test_song, test_artist)
        return {
            "status": "success",
            "test_song": test_song,
            "test_artist": test_artist,
            "results_count": len(results),
            "sample_results": results[:3] if results else []
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }