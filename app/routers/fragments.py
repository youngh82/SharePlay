"""HTMX fragment endpoints for dynamic UI updates"""
from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.models import QueueItem, User, Song
from app.database import get_db_session
from app.auth import get_current_user
from typing import Optional
from pathlib import Path


router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/queue/{room_code}")
async def get_queue_fragment(
    room_code: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get the full queue as HTML fragment (excluding currently playing song)"""
    queue_items = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.played_at == None)
        .where(QueueItem.position > 0)  # Exclude currently playing (position 0)
        .order_by(QueueItem.position)
    ).all()
    
    return templates.TemplateResponse(
        "fragments/queue_list.html",
        {
            "request": request,
            "queue_items": queue_items,
            "current_user": current_user
        }
    )


@router.get("/now-playing/{room_code}")
async def get_now_playing_fragment(
    room_code: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get the currently playing song as HTML fragment"""
    now_playing = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.played_at == None)
        .order_by(QueueItem.position)
    ).first()
    
    # Manually load relationships if needed
    added_by_name = "Unknown"
    if now_playing:
        # Refresh to load relationships
        session.refresh(now_playing)
        now_playing.song = session.get(Song, now_playing.song_id)
        now_playing.added_by = session.get(User, now_playing.added_by_id)
        added_by_name = now_playing.added_by.name if now_playing.added_by else "Unknown"
    
    return templates.TemplateResponse(
        "fragments/now_playing.html",
        {
            "request": request,
            "now_playing": now_playing,
            "added_by_name": added_by_name,
            "current_user": current_user
        }
    )


@router.get("/users/{room_code}")
async def get_users_fragment(
    room_code: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get the user list as HTML fragment"""
    users = session.exec(
        select(User).where(User.room_id == current_user.room_id)
    ).all()
    
    return templates.TemplateResponse(
        "fragments/user_list.html",
        {
            "request": request,
            "users": users,
            "current_user": current_user
        }
    )


@router.get("/search-results")
async def get_search_results_fragment(
    request: Request,
    query: str,
    current_user: User = Depends(get_current_user)
):
    """Get search results as HTML fragment"""
    from app.spotify import get_spotify_client
    
    if not query or len(query) < 1:
        return templates.TemplateResponse(
            "fragments/search_results.html",
            {"request": request, "results": []}
        )
    
    spotify = get_spotify_client()
    results = await spotify.search_tracks(query, limit=10)
    
    return templates.TemplateResponse(
        "fragments/search_results.html",
        {
            "request": request,
            "results": results,
            "current_user": current_user
        }
    )
