"""Authentication endpoints for Spotify"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database import get_db_session
from app.auth import get_current_user
from app.models import User
import os
import hashlib
import base64
import secrets
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta

router = APIRouter()

# In-memory storage for code verifiers (production should use Redis/DB)
_verifier_store = {}

# Spotify API constants
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:8000/api/auth/callback"
SPOTIFY_SCOPES = "streaming user-read-email user-read-private user-modify-playback-state"

def generate_code_verifier() -> str:
    """Generate PKCE code verifier"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier: str) -> str:
    """Generate PKCE code challenge from verifier"""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

@router.get("/login")
async def login_spotify(
    room_code: str,
    token: str,
    session: Session = Depends(get_db_session)
):
    """Redirect to Spotify login with PKCE"""
    user = session.exec(select(User).where(User.session_token == token)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
        
    if user.role != "host":
        raise HTTPException(status_code=403, detail="Only host can connect Spotify")
    
    # Generate PKCE verifier and challenge
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    state = f"{room_code}:{user.id}"
    _verifier_store[state] = verifier
    
    # Build authorization URL
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'scope': SPOTIFY_SCOPES,
        'code_challenge_method': 'S256',
        'code_challenge': challenge,
        'state': state
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get("/callback")
async def spotify_callback(
    code: str,
    state: str,
    session: Session = Depends(get_db_session)
):
    """Handle Spotify callback with PKCE"""
    try:
        room_code, user_id = state.split(":")
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Retrieve and remove code verifier
    verifier = _verifier_store.pop(state, None)
    if not verifier:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    
    # Exchange code for access token
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'code_verifier': verifier
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {response.text}")
    
    token_info = response.json()
    
    # Update user with tokens
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.spotify_access_token = token_info['access_token']
    user.spotify_refresh_token = token_info.get('refresh_token')
    expires_in = token_info.get('expires_in', 3600)
    user.spotify_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    session.add(user)
    session.commit()
    
    return RedirectResponse(url=f"/room/{room_code}")

@router.get("/token")
async def get_token(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get current access token (refresh if needed)"""
    if current_user.role != "host":
        raise HTTPException(status_code=403, detail="Only host has Spotify token")
        
    if not current_user.spotify_access_token:
        raise HTTPException(status_code=404, detail="No Spotify token found")
        
    # Check if token expired (with 5 min buffer)
    if current_user.spotify_token_expires_at and \
       datetime.utcnow() > current_user.spotify_token_expires_at - timedelta(minutes=5):
        # Refresh token
        response = requests.post(
            'https://accounts.spotify.com/api/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': current_user.spotify_refresh_token,
                'client_id': SPOTIFY_CLIENT_ID
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            token_info = response.json()
            current_user.spotify_access_token = token_info['access_token']
            if 'refresh_token' in token_info:
                current_user.spotify_refresh_token = token_info['refresh_token']
            
            expires_in = token_info.get('expires_in', 3600)
            current_user.spotify_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            session.add(current_user)
            session.commit()
        
    return {"access_token": current_user.spotify_access_token}
