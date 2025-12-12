"""Spotify API client"""
import os
from typing import List, Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyClient:
    """Client for interacting with Spotify Web API"""
    
    def __init__(self):
        """Initialize Spotify client with credentials"""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in environment variables")
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self.client = spotipy.Spotify(auth_manager=auth_manager)
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for tracks on Spotify.
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 10, max: 50)
            
        Returns:
            List of track dictionaries with normalized data
        """
        if limit > 50:
            limit = 50
        
        try:
            results = self.client.search(q=query, type='track', limit=limit)
            
            tracks = []
            for track in results['tracks']['items']:
                tracks.append({
                    'spotify_id': track['id'],
                    'title': track['name'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                    'duration_ms': track['duration_ms'],
                    'album_cover_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                    'preview_url': track['preview_url']
                })
            
            return tracks
        except Exception as e:
            print(f"Spotify API error: {e}")
            return []
    
    async def get_track(self, spotify_id: str) -> Optional[Dict]:
        """
        Get track details by Spotify ID.
        
        Args:
            spotify_id: Spotify track ID
            
        Returns:
            Track dictionary or None if not found
        """
        try:
            track = self.client.track(spotify_id)
            
            return {
                'spotify_id': track['id'],
                'title': track['name'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Unknown Artist',
                'duration_ms': track['duration_ms'],
                'album_cover_url': track['album']['images'][0]['url'] if track['album']['images'] else '',
                'preview_url': track['preview_url']
            }
        except Exception as e:
            print(f"Error fetching track {spotify_id}: {e}")
            return None


# Global Spotify client instance
spotify_client: Optional[SpotifyClient] = None


def get_spotify_client() -> SpotifyClient:
    """Get or create Spotify client instance"""
    global spotify_client
    if spotify_client is None:
        spotify_client = SpotifyClient()
    return spotify_client
