# SharePlay Project Structure

## 📁 Directory Structure

```
share_play/
├── app/                          # Backend application
│   ├── routers/                  # API endpoints
│   │   ├── auth.py              # Spotify authentication (PKCE)
│   │   ├── rooms.py             # Room creation/joining
│   │   ├── search.py            # Music search
│   │   ├── queue.py             # Queue management & voting
│   │   ├── playback.py          # Playback control
│   │   └── fragments.py         # HTMX fragments
│   │
│   ├── utils/                    # Utilities
│   │   ├── qr_generator.py      # QR code generation
│   │   └── code_generator.py    # Room code generation
│   │
│   ├── main.py                   # FastAPI app & page routes
│   ├── models.py                 # SQLModel database models
│   ├── schemas.py                # Pydantic validation schemas
│   ├── database.py               # DB connection & session
│   ├── auth.py                   # Authentication middleware
│   ├── spotify.py                # Spotify API client
│   └── websocket.py              # WebSocket manager
│
├── static/                       # Static files
│   ├── css/
│   │   └── styles.css           # Custom styles
│   └── js/
│       ├── audio.js             # Spotify Web Playback SDK
│       └── websocket.js         # WebSocket client
│
├── templates/                    # Jinja2 templates
│   ├── fragments/               # HTMX dynamic fragments
│   │   ├── now_playing.html    # Currently playing
│   │   ├── queue_list.html     # Queue list
│   │   ├── search_results.html # Search results
│   │   └── user_list.html      # User list
│   │
│   ├── base.html                # Base layout
│   ├── landing.html             # Landing page
│   ├── room.html                # Room page (main)
│   ├── join.html                # Join after QR scan
│   └── error.html               # Error page
│
├── tests/                        # Tests
│   ├── test_rooms.py
│   └── test_voting.py
│
├── docs/                         # Documentation
│   └── PROJECT_STRUCTURE.md
│
├── .env                          # Environment variables (secret)
├── .env.example                  # Environment variables template
├── requirements.txt              # Python packages
├── README.md                     # Project README
└── QUICKSTART.md                 # Quick start guide
```

---

## 🔍 Key File Descriptions

### Backend (app/)

#### 1. **routers/** - API Endpoints

- **auth.py**: Spotify OAuth PKCE authentication flow

  - `/api/auth/login` - Start Spotify login
  - `/api/auth/callback` - Spotify callback
  - `/api/auth/token` - Token lookup (auto-refresh)

- **rooms.py**: Room management

  - `POST /api/rooms/create` - Create room (host)
  - `POST /api/rooms/join` - Join room (guest)
  - `GET /api/rooms/{id}/status` - Room status

- **search.py**: Music search

  - `GET /api/search/songs?q=query` - Spotify search

- **queue.py**: Queue & voting

  - `POST /api/queue/add` - Add song
  - `POST /api/queue/vote` - Vote (upvote/downvote)
  - `GET /api/queue/{room_id}` - Queue list

- **playback.py**: Playback control (host only)

  - `POST /api/playback/play` - Play
  - `POST /api/playback/pause` - Pause
  - `POST /api/playback/skip` - Skip

- **fragments.py**: HTMX dynamic updates
  - `GET /api/fragments/now-playing` - Currently playing
  - `GET /api/fragments/queue` - Queue list
  - `GET /api/fragments/users` - User list

#### 2. **utils/** - Utilities

- **qr_generator.py**: Generate QR code as Base64 PNG
- **code_generator.py**: Generate 6-character room code

#### 3. **Core Files**

- **main.py**: FastAPI app initialization, page routes
- **models.py**: Room, User, Song, QueueItem, Vote models
- **schemas.py**: Pydantic request/response validation
- **database.py**: SQLite connection & session
- **auth.py**: JWT token validation middleware
- **spotify.py**: Spotify API client (spotipy)
- **websocket.py**: WebSocket broadcast manager

---

### Frontend (static/ & templates/)

#### 1. **JavaScript (static/js/)**

- **audio.js**: Spotify Web Playback SDK integration
  - Play music in host browser
  - Broadcast playback state via WebSocket
- **websocket.js**: WebSocket client
  - Real-time queue updates
  - Vote reflection
  - Playback state sync

#### 2. **Templates (templates/)**

- **base.html**: Common layout (Tailwind CSS, HTMX)
- **landing.html**: Main page (create/join room)
- **room.html**: Room page (search, queue, playback)
- **fragments/**: HTML fragments for HTMX dynamic updates

---

## 🗄️ Database Structure

### Room

- `code`: 6-character room code
- `host_id`: Host user ID
- `device_id`: Spotify device ID (host)
- `is_active`: Active status

### User

- `name`: User name
- `role`: 'host' | 'guest'
- `session_token`: Authentication token
- `spotify_access_token`: Spotify access token (host only)
- `spotify_refresh_token`: Refresh token
- `spotify_token_expires_at`: Token expiration time

### Song

- `spotify_id`: Spotify track ID
- `title`, `artist`, `duration_ms`, `album_cover_url`

### QueueItem

- `room_id`, `song_id`, `user_id`
- `position`: Queue position (based on vote score)
- `vote_count`: Total vote count
- `played_at`: Playback time

### Vote

- `user_id`, `queue_item_id`
- `vote_type`: 'upvote' | 'downvote'

---

## 🔄 Data Flow

### 1. Create Room

```
User → POST /api/rooms/create
     → Create Room + Host User
     → Issue session_token
     → Redirect to /room/{code}
```

### 2. Spotify Login (Host)

```
Connect Spotify button → GET /api/auth/login
                       → Spotify OAuth (PKCE)
                       → Callback
                       → Save token
                       → Initialize SDK
```

### 3. Search & Add Music

```
Search → GET /api/search/songs
       → POST /api/queue/add
       → WebSocket broadcast
       → All clients update queue
```

### 4. Vote

```
UP/DOWN button → POST /api/queue/vote
               → Create/update Vote
               → Recalculate QueueItem position
               → WebSocket broadcast
```

### 5. Playback

```
Play button → POST /api/playback/play
            → Call Spotify Web API
            → SDK starts playback
            → player_state_changed event
            → WebSocket broadcast
```

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, SQLModel, Uvicorn
- **Frontend**: Jinja2, HTMX, Tailwind CSS
- **Database**: SQLite
- **Real-time**: WebSocket
- **External APIs**: Spotify Web API, Spotify Web Playback SDK
- **Authentication**: OAuth 2.0 (PKCE)
