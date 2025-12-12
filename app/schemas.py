"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Room schemas
class RoomCreate(BaseModel):
    host_name: str = Field(..., max_length=50, min_length=1)


class RoomResponse(BaseModel):
    room_code: str
    host_token: str
    qr_code_url: str


class RoomJoin(BaseModel):
    guest_name: str = Field(..., max_length=50, min_length=1)
    room_code: str = Field(..., max_length=6, min_length=6)


class RoomJoinResponse(BaseModel):
    guest_token: str
    room_code: str


# Song schemas
class SongResponse(BaseModel):
    id: int
    spotify_id: str
    title: str
    artist: str
    duration_ms: int
    album_cover_url: str
    preview_url: Optional[str]


class SongSearchResult(BaseModel):
    """Song result from Spotify search (no database id)"""
    spotify_id: str
    title: str
    artist: str
    duration_ms: int
    album_cover_url: str
    preview_url: Optional[str]


# Queue schemas
class QueueItemAdd(BaseModel):
    spotify_id: str


class QueueItemResponse(BaseModel):
    id: int
    song: SongResponse
    added_by_name: str
    position: int
    vote_count: int
    created_at: datetime


class VoteRequest(BaseModel):
    queue_item_id: int
    vote_type: int = Field(..., ge=-1, le=1)


# User schemas
class UserResponse(BaseModel):
    id: int
    name: str
    role: str
    joined_at: datetime


# Room status schemas
class RoomStatusResponse(BaseModel):
    room_code: str
    host_name: str
    is_active: bool
    users: List[UserResponse]
    queue: List[QueueItemResponse]
    now_playing: Optional[QueueItemResponse]


# Search schemas
class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=50)


class SearchResponse(BaseModel):
    results: List[SongSearchResult]
