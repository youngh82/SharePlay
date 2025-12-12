"""Database models using SQLModel"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Room(SQLModel, table=True):
    """Room where music is played and voted on"""
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(max_length=6, unique=True, index=True)
    host_id: int = Field(foreign_key="user.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=24))
    
    # Relationships - specify foreign_keys to avoid ambiguity
    users: List["User"] = Relationship(
        back_populates="room",
        sa_relationship_kwargs={"foreign_keys": "[User.room_id]"}
    )
    queue_items: List["QueueItem"] = Relationship(back_populates="room")


class User(SQLModel, table=True):
    """User participating in a room (no permanent accounts)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    room_id: int = Field(foreign_key="room.id")
    role: str = Field(default="guest")  # "host" or "guest"
    session_token: str = Field(max_length=64, unique=True, index=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Spotify Auth (Host only)
    spotify_access_token: Optional[str] = Field(default=None)
    spotify_refresh_token: Optional[str] = Field(default=None)
    spotify_token_expires_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    room: "Room" = Relationship(
        back_populates="users",
        sa_relationship_kwargs={"foreign_keys": "[User.room_id]"}
    )
    queue_items: List["QueueItem"] = Relationship(back_populates="added_by")
    votes: List["Vote"] = Relationship(back_populates="user")


class Song(SQLModel, table=True):
    """Song metadata cached from Spotify"""
    id: Optional[int] = Field(default=None, primary_key=True)
    spotify_id: str = Field(max_length=22, unique=True, index=True)
    title: str = Field(max_length=200)
    artist: str = Field(max_length=200)
    duration_ms: int
    album_cover_url: str = Field(max_length=500)
    preview_url: Optional[str] = Field(max_length=500, default=None)
    
    # Relationships
    queue_items: List["QueueItem"] = Relationship(back_populates="song")


class QueueItem(SQLModel, table=True):
    """Song in a room's queue"""
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.id")
    song_id: int = Field(foreign_key="song.id")
    added_by_id: int = Field(foreign_key="user.id")
    position: int = Field(ge=1)
    vote_count: int = Field(default=0)  # Denormalized for performance
    created_at: datetime = Field(default_factory=datetime.utcnow)
    played_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    room: "Room" = Relationship(back_populates="queue_items")
    song: "Song" = Relationship(back_populates="queue_items")
    added_by: "User" = Relationship(back_populates="queue_items")
    votes: List["Vote"] = Relationship(back_populates="queue_item")


class Vote(SQLModel, table=True):
    """User vote on a queue item"""
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    queue_item_id: int = Field(foreign_key="queueitem.id")
    vote_type: int = Field(ge=-1, le=1)  # 1 = upvote, -1 = downvote
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: "User" = Relationship(back_populates="votes")
    queue_item: "QueueItem" = Relationship(back_populates="votes")
    
    class Config:
        # Unique constraint: one vote per user per queue item
        table_args = {"sqlite_autoincrement": True}
