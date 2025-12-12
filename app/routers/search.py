"""Search endpoints for Spotify"""
from fastapi import APIRouter, Depends, Query
from app.schemas import SearchResponse, SongSearchResult
from app.spotify import get_spotify_client
from typing import List


router = APIRouter()


@router.get("/songs", response_model=SearchResponse)
async def search_songs(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results")
):
    """Search for songs on Spotify"""
    spotify = get_spotify_client()
    results = await spotify.search_tracks(q, limit)
    
    return SearchResponse(
        results=[SongSearchResult(**track) for track in results]
    )
