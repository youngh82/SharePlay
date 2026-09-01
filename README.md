# SharePlay

A real-time collaborative music queue system for shared spaces. Multiple users join a room, add songs from Spotify, and vote to decide what plays next -- eliminating the "one person controls the speaker" problem.

## Demo

[![Demo Video](https://drive.google.com/thumbnail?id=18nHK0dbMt-ka2O0C5yVKYLcQyXVM4pRy&sz=w1280)](https://drive.google.com/file/d/18nHK0dbMt-ka2O0C5yVKYLcQyXVM4pRy/view?usp=drive_link)

> Click the image above to watch the full demo video.

## Features

- **No account required** -- guests join with just a display name
- **Spotify integration** -- search and play from Spotify's full catalog (host needs Premium)
- **Vote-based queue** -- upvote/downvote songs to reorder the queue democratically
- **Real-time sync** -- WebSocket-powered live updates for all participants
- **QR code access** -- scan to join a room instantly
- **Host controls** -- room creator manages playback (play, pause, skip)

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI 0.104 | Async REST API + WebSocket support |
| ORM | SQLModel 0.0.14 | Type-safe models with Pydantic validation |
| Database | SQLite | Lightweight storage with auto-creation |
| Auth | OAuth 2.0 (PKCE) | Spotify authentication without client secret |
| Music API | Spotipy 2.23 | Spotify Web API client for search and metadata |
| Playback | Spotify Web Playback SDK | Browser-based music playback |
| Frontend | HTMX 1.9 | SPA-like interactions without a JS framework |
| Styling | Tailwind CSS | Utility-first CSS with glass-morphism effects |
| Real-time | WebSocket | Bi-directional updates for queue, playback, presence |
| QR Code | segno | Room sharing via generated QR codes |
| Testing | pytest | Unit tests for rooms and voting logic |

## Architecture

### Request Flow

| Action | Method | Endpoint | Response |
|--------|--------|----------|----------|
| Create room | POST | `/api/rooms/create` | Room page with generated 6-char code |
| Join room | POST | `/api/rooms/{code}/join` | Room page for guest |
| Spotify auth | GET | `/api/auth/callback` | OAuth 2.0 PKCE redirect |
| Search songs | GET | `/api/search` | Spotify search results (HTML fragment) |
| Add to queue | POST | `/api/queue/add` | Updated queue list (HTML fragment) |
| Vote | POST | `/api/queue/vote` | Reordered queue item (HTML fragment) |
| Playback control | POST | `/api/playback/{action}` | Updated now-playing card |
| WebSocket | WS | `/ws/{room_code}` | Real-time queue, playback, user events |

All non-WebSocket responses are server-rendered HTML fragments. HTMX swaps them into the DOM without full page reloads.

### Data Flow

1. **Auth** -- Host authenticates via OAuth 2.0 PKCE with Spotify
2. **Room** -- Server generates a 6-character code and QR code
3. **Connect** -- All participants establish WebSocket connections
4. **Search** -- Queries Spotify API, returns results via HTMX fragments
5. **Queue** -- Position-based system (0 = now playing, 1+ = waiting)
6. **Vote** -- Server recalculates queue positions based on vote counts
7. **Playback** -- Spotify Web Playback SDK streams audio in host's browser

### Project Structure

```
share_play/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── auth.py              # Session token management
│   ├── database.py          # SQLite configuration
│   ├── models.py            # SQLModel schemas (Room, QueueItem, Vote, User)
│   ├── schemas.py           # Pydantic request/response models
│   ├── spotify.py           # Spotify API client wrapper
│   ├── websocket.py         # Room-based WebSocket manager
│   ├── routers/
│   │   ├── auth.py          # Spotify OAuth flow
│   │   ├── rooms.py         # Room CRUD
│   │   ├── queue.py         # Queue and voting endpoints
│   │   ├── playback.py      # Play, pause, skip controls
│   │   ├── search.py        # Spotify search proxy
│   │   └── fragments.py     # HTMX partial HTML responses
│   └── utils/
│       ├── code_generator.py
│       └── qr_generator.py
├── static/
│   ├── css/styles.css
│   └── js/
│       ├── audio.js         # Spotify Web Playback SDK wrapper
│       └── websocket.js     # WebSocket client
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── room.html
│   └── fragments/           # HTMX partial templates
├── tests/
│   ├── test_rooms.py
│   └── test_voting.py
├── requirements.txt
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.9+
- Spotify Developer account ([developer.spotify.com/dashboard](https://developer.spotify.com/dashboard))
- Spotify Premium (host only)

### Setup

```bash
git clone https://github.com/youngh82/SharePlay.git
cd SharePlay

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
# Add your Spotify Client ID and Client Secret to .env
```

### Spotify Configuration

1. Create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Add redirect URI: `http://127.0.0.1:8000/api/auth/callback`
3. Copy Client ID and Client Secret into `.env`

### Run

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

## Testing

```bash
pytest                        # run all tests
pytest tests/test_rooms.py    # room creation and joining
pytest tests/test_voting.py   # voting logic
pytest --cov=app              # with coverage
```

## Security

- **Session tokens**: cryptographically secure, 64-character random strings
- **OAuth 2.0 PKCE**: no client secret stored on the client
- **Input validation**: Pydantic schemas on all endpoints
- **SQL injection protection**: parameterized queries via SQLModel ORM
- **Session expiry**: user sessions auto-expire after 24 hours

## License

MIT

## Author

**Young Hur** -- University of Massachusetts Amherst

GitHub: [@youngh82](https://github.com/youngh82)
