"""Authentication and authorization"""
from fastapi import Header, HTTPException, Depends
from sqlmodel import Session, select
from app.models import User
from app.database import get_db_session
import secrets
from typing import Optional


def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(48)


async def get_current_user(
    authorization: str = Header(...),
    session: Session = Depends(get_db_session)
) -> User:
    """Validate session token and return user"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    user = session.exec(select(User).where(User.session_token == token)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Check if room is still active
    if not user.room.is_active:
        raise HTTPException(status_code=403, detail="Room is no longer active")
    
    return user


async def require_host(
    user: User = Depends(get_current_user),
) -> User:
    """Ensure user is a room host"""
    if user.role != "host":
        raise HTTPException(status_code=403, detail="Host privileges required")
    return user

