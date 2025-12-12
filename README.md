# SharePlay - Democratic Music Control System

**SharePlay** is a democratic music control system designed for shared spaces like dorm lounges. It allows multiple people to collaboratively control what music plays next through a voting system, eliminating the "speaker monopoly" problem.

## 🎯 Features

- **No Account Required**: Join with just a display name
- **QR Code Access**: Scan and join instantly
- **Democratic Voting**: Upvote/downvote songs to determine play order
- **Real-time Sync**: WebSocket-powered live updates for all participants
- **Spotify Integration**: Full track playback with Spotify Web Playback SDK
- **Host Premium**: Spotify Premium required for host only
- **Host Controls**: Room creator has playback controls (play/pause/skip)

## 🛠 Tech Stack

### Backend
- **FastAPI 0.104.1**: Modern async web framework
- **SQLModel 0.0.14**: Type-safe ORM with Pydantic validation
- **SQLite**: Lightweight database with auto-creation
- **Uvicorn**: ASGI server
- **Spotipy 2.23.0**: Spotify API client
- **OAuth 2.0 (PKCE)**: Secure authentication without client secret

### Frontend
- **HTMX 1.9.10**: Dynamic HTML interactions without heavy JavaScript
- **Tailwind CSS**: Utility-first CSS framework with glass-morphism effects
- **Vanilla JavaScript**: WebSocket client and Spotify SDK integration
- **Jinja2**: Server-side templating

### Real-time Communication
- **WebSocket**: Bi-directional real-time updates for queue, playback state, and user presence
- **Custom WebSocket Manager**: Handles room-based broadcasting

### External APIs
- **Spotify Web API**: Music search and metadata
- **Spotify Web Playback SDK**: Browser-based music playback
- **QR Code Generation**: segno library for easy room joining

## 📋 Prerequisites

- **Python 3.9+** (tested with Python 3.13)
- **Spotify Developer Account** (free at https://developer.spotify.com/dashboard)
- **Spotify Premium Account** (required for host playback only)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### 1. Setup

```bash
# Clone and enter directory
cd share_play

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Spotify credentials
```

### 2. Spotify Developer Setup

1. Go to https://developer.spotify.com/dashboard
2. Create an app
3. Add redirect URI: `http://127.0.0.1:8000/api/auth/callback`
4. Copy **Client ID** and **Client Secret** to `.env`

### 3. Run Server

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Virtual environment setup
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Detailed architecture

## 🎮 Usage

### For Hosts (Room Creator)

1. Click "Create Room" and enter your name
2. Click "Connect Spotify" (requires Premium)
3. Authorize the app in Spotify
4. Share the room code or QR code with friends
5. Use play/pause/skip controls

### For Guests

1. Enter room code or scan QR code
2. Enter your name and join
3. Search songs from Spotify
4. Add songs to queue
5. Vote on songs (↑ upvote, ↓ downvote)

### Key Features

- **Search**: Find any song from Spotify's 100M+ track library
- **Add to Queue**: Songs appear in vote-based order
- **Vote**: Upvote/downvote to reorder queue democratically
- **Real-time**: All updates sync instantly via WebSocket
- **Auto-Play**: Songs automatically play when reaching position 0

## 🏗️ Architecture

### Project Structure

```
share_play/
├── app/                        # Backend application
│   ├── main.py                 # FastAPI app entry point
│   ├── auth.py                 # Authentication logic
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLModel database models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── spotify.py              # Spotify API client wrapper
│   ├── websocket.py            # WebSocket manager
│   ├── routers/                # API endpoint modules
│   │   ├── auth.py             # Spotify OAuth flow
│   │   ├── rooms.py            # Room management
│   │   ├── queue.py            # Queue & voting system
│   │   ├── playback.py         # Playback controls
│   │   ├── search.py           # Spotify search
│   │   └── fragments.py        # HTMX partial updates
│   └── utils/                  # Helper functions
│       ├── code_generator.py   # Random room code generator
│       └── qr_generator.py     # QR code image generator
├── static/
│   ├── css/
│   │   └── styles.css          # Tailwind CSS styles
│   ├── js/
│   │   ├── audio.js            # Spotify Web Playback SDK wrapper
│   │   └── websocket.js        # WebSocket client
│   └── images/
│       └── logo.png            # Application logo
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Base layout with navbar
│   ├── landing.html            # Home page (create/join)
│   ├── room.html               # Room interface
│   ├── join.html               # Join room page
│   ├── error.html              # Error page
│   └── fragments/              # HTMX partial templates
│       ├── now_playing.html    # Current song display
│       ├── queue_list.html     # Queue with voting buttons
│       ├── search_results.html # Search results list
│       └── user_list.html      # Connected users
├── tests/                      # Test suite
│   ├── test_rooms.py           # Room creation/joining tests
│   └── test_voting.py          # Voting system tests
├── docs/                       # Documentation
│   └── PROJECT_STRUCTURE.md    # Detailed architecture guide
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

### Key Technologies Used

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.104.1 | Async REST API + WebSocket |
| ORM | SQLModel | 0.0.14 | Type-safe database models |
| Database | SQLite | Built-in | Lightweight data storage |
| Server | Uvicorn | 0.24.0 | ASGI server with auto-reload |
| Spotify Client | Spotipy | 2.23.0 | Python Spotify API wrapper |
| Frontend | HTMX | 1.9.10 | Dynamic HTML without heavy JS |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| Templates | Jinja2 | 3.1.x | Server-side rendering |
| QR Codes | segno | 1.6.1 | QR code generation |
| Testing | pytest | 7.4.x | Test framework |

### Data Flow

1. **User Authentication**: OAuth 2.0 PKCE flow with Spotify (host only)
2. **Room Creation**: Generate 6-character code + QR code
3. **WebSocket Connection**: Real-time updates for all room participants
4. **Search**: Query Spotify API, return results via HTMX
5. **Queue Management**: Position-based system (0=playing, 1+=waiting)
6. **Voting**: Recalculate positions based on vote counts
7. **Playback**: Spotify Web Playback SDK in host's browser

## 🧪 Testing

```bash
# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_rooms.py

# Run with coverage
pytest --cov=app

# Verbose output
pytest -v
```

## 🔒 Security

- **Session Tokens**: Cryptographically secure random tokens (64 chars)
- **OAuth 2.0 (PKCE)**: Industry-standard Spotify authentication
- **Input Validation**: Pydantic schemas validate all requests
- **SQL Injection Protection**: SQLModel ORM with parameterized queries
- **No Permanent Storage**: User sessions expire after 24 hours
- **CORS**: Configured for localhost development

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti :8000 | xargs kill -9
```

### Spotify Login Fails

- Verify redirect URI exactly matches: `http://127.0.0.1:8000/api/auth/callback`
- Check `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in `.env`
- Ensure Spotify Premium account for host

### Music Won't Play

- Host must click "Connect Spotify" button first
- Spotify Premium account required for playback
- Check browser console (F12) for Spotify SDK errors
- Verify browser allows audio autoplay

### WebSocket Connection Failed

- Ensure server is running on port 8000
- Check browser console for WebSocket errors
- Verify no firewall blocking WebSocket connections

### Database Errors

- Delete `shareplay.db` and restart (tables will auto-create)
- Check file permissions on database directory

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

**Young Hur**
- UMass Amherst - CS 326 Web Programming
- GitHub: [@youngh82](https://github.com/youngh82)

## 🙏 Acknowledgments

- Built for CS 326 Final Project
- Inspired by the need for democratic music control in shared spaces
- Thanks to the international student community at UMass for testing!

---

**Built with ❤️ for democratic music control**
