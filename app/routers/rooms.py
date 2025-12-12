"""Room management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import Room, User, QueueItem
from app.schemas import RoomCreate, RoomResponse, RoomJoin, RoomJoinResponse, RoomStatusResponse, UserResponse, QueueItemResponse, SongResponse
from app.database import get_db_session
from app.auth import generate_session_token, get_current_user
from app.utils.code_generator import generate_room_code
from app.utils.qr_generator import generate_qr_code
import os


router = APIRouter()


@router.post("/create", response_model=RoomResponse)
async def create_room(
    room_data: RoomCreate,
    session: Session = Depends(get_db_session)
):
    """Create a new room with a host"""
    # Generate unique room code
    code = generate_room_code()
    while session.exec(select(Room).where(Room.code == code)).first():
        code = generate_room_code()
    
    # Create room (will create without host_id first)
    room = Room(code=code, host_id=0)  # Temporary host_id
    session.add(room)
    session.flush()  # Get room.id
    
    # Create host user
    token = generate_session_token()
    host = User(
        name=room_data.host_name,
        room_id=room.id,
        role="host",
        session_token=token
    )
    session.add(host)
    session.flush()
    
    # Update room with real host_id
    room.host_id = host.id
    session.commit()
    session.refresh(room)
    
    # Generate QR code
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    room_url = f"{base_url}/join/{code}"
    qr_code_url = generate_qr_code(room_url)
    
    return RoomResponse(
        room_code=code,
        host_token=token,
        qr_code_url=qr_code_url
    )


@router.post("/join", response_model=RoomJoinResponse)
async def join_room(
    join_data: RoomJoin,
    session: Session = Depends(get_db_session)
):
    """Join an existing room as a guest"""
    from app.websocket import get_websocket_manager
    
    # Find room
    room = session.exec(
        select(Room).where(Room.code == join_data.room_code.upper())
    ).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not room.is_active:
        raise HTTPException(status_code=403, detail="Room is no longer active")
    
    # Create guest user
    token = generate_session_token()
    guest = User(
        name=join_data.guest_name,
        room_id=room.id,
        role="guest",
        session_token=token
    )
    session.add(guest)
    session.commit()
    session.refresh(guest)
    
    # Broadcast user_joined event to all room members
    ws_manager = get_websocket_manager()
    await ws_manager.broadcast(room.code, {
        "type": "user_joined",
        "user_id": guest.id,
        "user_name": guest.name
    })
    
    return RoomJoinResponse(
        guest_token=token,
        room_code=room.code
    )


@router.get("/{code}/qr-code")
async def get_room_qr_code(
    code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get QR code for room"""
    room = session.exec(
        select(Room).where(Room.code == code.upper())
    ).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    room_url = f"{base_url}/join/{code}"
    qr_code_url = generate_qr_code(room_url)
    
    return {"qr_code_url": qr_code_url}


@router.get("/{code}/status", response_model=RoomStatusResponse)
async def get_room_status(
    code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Get current room status including users and queue"""
    room = session.exec(select(Room).where(Room.code == code.upper())).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is in this room
    if current_user.room_id != room.id:
        raise HTTPException(status_code=403, detail="Not a member of this room")
    
    # Get host
    host = session.get(User, room.host_id)
    
    # Get all users
    users = [
        UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            joined_at=user.joined_at
        )
        for user in room.users
    ]
    
    # Get queue items (not played yet)
    queue_items = session.exec(
        select(QueueItem)
        .where(QueueItem.room_id == room.id)
        .where(QueueItem.played_at == None)
        .order_by(QueueItem.position)
    ).all()
    
    queue = []
    now_playing = None
    
    for idx, item in enumerate(queue_items):
        queue_response = QueueItemResponse(
            id=item.id,
            song=SongResponse(
                id=item.song.id,
                spotify_id=item.song.spotify_id,
                title=item.song.title,
                artist=item.song.artist,
                duration_ms=item.song.duration_ms,
                album_cover_url=item.song.album_cover_url,
                preview_url=item.song.preview_url
            ),
            added_by_name=item.added_by.name,
            position=item.position,
            vote_count=item.vote_count,
            created_at=item.created_at
        )
        
        if idx == 0:
            now_playing = queue_response
        else:
            queue.append(queue_response)
    
    return RoomStatusResponse(
        room_code=room.code,
        host_name=host.name if host else "Unknown",
        is_active=room.is_active,
        users=users,
        queue=queue,
        now_playing=now_playing
    )


@router.delete("/{code}")
async def close_room(
    code: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db_session)
):
    """Close a room (host only)"""
    room = session.exec(select(Room).where(Room.code == code.upper())).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if current_user.id != room.host_id:
        raise HTTPException(status_code=403, detail="Only the host can close the room")
    
    room.is_active = False
    session.commit()
    
    return {"message": "Room closed successfully"}
