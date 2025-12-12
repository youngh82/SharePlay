"""Queue management and voting endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import QueueItem, Song, Vote, User
from app.schemas import QueueItemAdd, QueueItemResponse, SongResponse, VoteRequest
from app.database import get_db_session
from app.auth import get_current_user, require_host
from app.spotify import get_spotify_client
from app.websocket import get_websocket_manager
from datetime import datetime


router = APIRouter()


async def get_or_create_song(session: Session, spotify_id: str) -> Song:
    """Get song from database or fetch from Spotify and create"""
    song = session.exec(select(Song).where(Song.spotify_id == spotify_id)).first()
    if song:
        return song
    
    # Fetch from Spotify
    spotify = get_spotify_client()
    track_data = await spotify.get_track(spotify_id)
    
    if not track_data:
        raise HTTPException(status_code=404, detail="Track not found on Spotify")
    
    song = Song(
        spotify_id=track_data['spotify_id'],
        title=track_data['title'],
        artist=track_data['artist'],
        duration_ms=track_data['duration_ms'],
        album_cover_url=track_data['album_cover_url'],
        preview_url=track_data['preview_url']
    )
    session.add(song)
    session.flush()
    return song


def reorder_queue(session: Session, room_id: int):
    """Reorder queue based on vote count (position 0 = now playing, 1+ = waiting)"""
    # Get currently playing song (position 0) - should NOT be reordered
    now_playing = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == room_id)
        .where(QueueItem.played_at == None)
        .where(QueueItem.position == 0)
    ).first()
    
    # Get all waiting songs (position > 0) - these will be reordered
    waiting_items = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == room_id)
        .where(QueueItem.played_at == None)
        .where(QueueItem.position > 0)
        .order_by(QueueItem.vote_count.desc(), QueueItem.created_at.asc())
    ).all()
    
    # Reorder only the waiting queue (starting from position 1)
    for idx, item in enumerate(waiting_items, start=1):
        item.position = idx
    
    session.commit()


@router.post("/add", response_model=QueueItemResponse)
async def add_to_queue(
    item_data: QueueItemAdd,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Add a song to the queue"""
    # Get or create song
    song = await get_or_create_song(session, item_data.spotify_id)
    
    # Check if song already in queue
    existing = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.song_id == song.id)
        .where(QueueItem.played_at == None)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Song already in queue")
    
    # Get current queue size for position
    queue_size = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == current_user.room_id)
        .where(QueueItem.played_at == None)
    ).all()
    
    # Create queue item
    queue_item = QueueItem(
        room_id=current_user.room_id,
        song_id=song.id,
        added_by_id=current_user.id,
        position=len(queue_size),  # First song gets position 0, next gets 1, etc.
        vote_count=0
    )
    session.add(queue_item)
    session.commit()
    session.refresh(queue_item)
    
    # Check if this is the first song (should start playing)
    is_first_song = len(queue_size) == 0
    
    # Broadcast to room
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(current_user.room.code, {
        "type": "song_added",
        "queue_item_id": queue_item.id,
        "should_play": is_first_song  # Start playing if first song
    })
    
    return QueueItemResponse(
        id=queue_item.id,
        song=SongResponse(
            id=song.id,
            spotify_id=song.spotify_id,
            title=song.title,
            artist=song.artist,
            duration_ms=song.duration_ms,
            album_cover_url=song.album_cover_url,
            preview_url=song.preview_url
        ),
        added_by_name=current_user.name,
        position=queue_item.position,
        vote_count=queue_item.vote_count,
        created_at=queue_item.created_at
    )


@router.post("/vote")
async def vote_on_song(
    vote_data: VoteRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Vote on a queue item"""
    # Get queue item
    queue_item = session.get(QueueItem, vote_data.queue_item_id)
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    # Check if user is in the same room
    if queue_item.room_id != current_user.room_id:
        raise HTTPException(status_code=403, detail="Not in the same room")
    
    # Check if song already played
    if queue_item.played_at:
        raise HTTPException(status_code=400, detail="Cannot vote on played songs")
    
    # Check if song is currently playing (position 0)
    if queue_item.position == 0:
        raise HTTPException(status_code=400, detail="Cannot vote on currently playing song")
    
    # Check for existing vote
    existing_vote = session.exec(
        select(Vote)
        .where(Vote.user_id == current_user.id)
        .where(Vote.queue_item_id == vote_data.queue_item_id)
    ).first()
    
    if existing_vote:
        # Update vote
        old_vote = existing_vote.vote_type
        queue_item.vote_count -= old_vote
        
        if existing_vote.vote_type == vote_data.vote_type:
            # Remove vote if same type
            session.delete(existing_vote)
        else:
            # Change vote
            existing_vote.vote_type = vote_data.vote_type
            queue_item.vote_count += vote_data.vote_type
    else:
        # New vote
        new_vote = Vote(
            user_id=current_user.id,
            queue_item_id=vote_data.queue_item_id,
            vote_type=vote_data.vote_type
        )
        session.add(new_vote)
        queue_item.vote_count += vote_data.vote_type
    
    session.commit()
    
    # Reorder queue
    reorder_queue(session, queue_item.room_id)
    
    # Broadcast to room
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(queue_item.room.code, {
        "type": "vote_changed",
        "queue_item_id": vote_data.queue_item_id
    })
    
    return {"message": "Vote recorded", "new_vote_count": queue_item.vote_count}


@router.delete("/{queue_item_id}")
async def remove_from_queue(
    queue_item_id: int,
    current_user: User = Depends(require_host),
    session: Session = Depends(get_db_session)
):
    """Remove a song from the queue (host only)"""
    queue_item = session.get(QueueItem, queue_item_id)
    if not queue_item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    
    if queue_item.room_id != current_user.room_id:
        raise HTTPException(status_code=403, detail="Not in the same room")
    
    room_code = queue_item.room.code
    session.delete(queue_item)
    session.commit()
    
    # Reorder remaining items
    reorder_queue(session, current_user.room_id)
    
    # Broadcast to room
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(room_code, {
        "type": "song_removed",
        "queue_item_id": queue_item_id
    })
    
    return {"message": "Song removed from queue"}
