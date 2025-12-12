"""FastAPI main application"""
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from app.database import init_db, get_db_session
from app.routers import rooms, search, queue, fragments, playback, auth
from app.websocket import get_websocket_manager
from app.models import Room
from app.utils.qr_generator import generate_qr_code
import os
from pathlib import Path


# Create FastAPI app
app = FastAPI(
    title="SharePlay",
    description="Democratic Music Control System for Shared Spaces",
    version="1.0.0"
)

# Get base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include routers
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(queue.router, prefix="/api/queue", tags=["queue"])
app.include_router(fragments.router, prefix="/fragments", tags=["fragments"])
app.include_router(playback.router, prefix="/api/playback", tags=["playback"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Landing page"""
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/room/{code}", response_class=HTMLResponse)
async def room_page(
    code: str,
    request: Request,
    session: Session = Depends(get_db_session)
):
    """Room page"""
    room = session.exec(select(Room).where(Room.code == code.upper())).first()
    
    if not room:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Room not found"},
            status_code=404
        )
    
    # Generate QR code for this room
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    room_url = f"{base_url}/join/{code.upper()}"
    qr_code_url = generate_qr_code(room_url)
    
    return templates.TemplateResponse(
        "room.html",
        {
            "request": request, 
            "room": room,
            "qr_code_url": qr_code_url
        }
    )


@app.get("/join/{code}", response_class=HTMLResponse)
async def join_page(
    code: str,
    request: Request,
    session: Session = Depends(get_db_session)
):
    """Join page - QR code lands here"""
    room = session.exec(select(Room).where(Room.code == code.upper())).first()
    
    if not room:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Room not found"},
            status_code=404
        )
    
    if not room.is_active:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Room is no longer active"},
            status_code=403
        )
    
    return templates.TemplateResponse(
        "join.html",
        {"request": request, "room": room}
    )


@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """WebSocket endpoint for real-time updates"""
    manager = get_websocket_manager()
    await manager.connect(websocket, room_code.upper())
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code.upper())
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, room_code.upper())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
