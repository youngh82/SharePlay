"""Playback control endpoints (host only)"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import QueueItem, User
from app.database import get_db_session
from app.auth import get_current_user, require_host
from app.websocket import get_websocket_manager
from datetime import datetime


router = APIRouter()


@router.post("/skip/{room_code}")
async def skip_song(
    room_code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Skip the currently playing song"""
    # Get the first item in queue (currently playing)
    current_song = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.played_at == None)
        .order_by(QueueItem.position)
    ).first()
    
    if not current_song:
        raise HTTPException(status_code=404, detail="No song currently playing")
    
    # Mark as played
    current_song.played_at = datetime.utcnow()
    
    # Get all remaining queue items
    remaining_items = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.played_at == None)
        .where(QueueItem.id != current_song.id)
        .order_by(QueueItem.vote_count.desc(), QueueItem.created_at)
    ).all()
    
    # Reorder positions: first song gets position 0 (now playing), rest start from 1
    for idx, item in enumerate(remaining_items):
        item.position = idx
    
    session.commit()
    
    # Get next song
    next_song = remaining_items[0] if remaining_items else None
    
    # Broadcast to room
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(room_code, {
        "type": "song_changed",
        "next_song_id": next_song.id if next_song else None
    })
    
    return {
        "message": "Song skipped",
        "next_song_id": next_song.id if next_song else None
    }


@router.post("/play")
async def play_song(
    current_user: User = Depends(require_host),
    session: Session = Depends(get_db_session)
):
    """Resume playback (host only)"""
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(current_user.room.code, {
        "type": "playback_play"
    })
    
    return {"message": "Playback resumed"}


@router.post("/pause")
async def pause_song(
    current_user: User = Depends(require_host),
    session: Session = Depends(get_db_session)
):
    """Pause playback (host only)"""
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(current_user.room.code, {
        "type": "playback_pause"
    })
    
    return {"message": "Playback paused"}
