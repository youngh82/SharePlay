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

- **FastAPI**: Modern async web framework
- **SQLModel**: Type-safe ORM with Pydantic validation
- **SQLite**: Lightweight database
- **WebSocket**: Real-time communication
- **OAuth 2.0 (PKCE)**: Secure Spotify authentication

### Frontend

- **HTMX**: Dynamic HTML interactions without heavy JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Vanilla JavaScript**: WebSocket client and Spotify SDK integration

### External Services

- **Spotify Web API**: Music search and metadata
- **Spotify Web Playback SDK**: In-browser music playback
- **QR Code Generation**: Easy room joining

## 📋 Prerequisites

- Python 3.9+
- Spotify Developer Account (for API credentials)
- Spotify Premium Account (for host playback)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### 1. Setup

```bash
# Clone and enter directory
cd share_play

# Create virtual environment
python -m venv venv
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
4. Copy Client ID and Client Secret to `.env`

### 3. Run Server

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000`

## 📚 Documentation

- **[Project Structure](docs/PROJECT_STRUCTURE.md)** - Detailed architecture guide
- **[Quick Start](QUICKSTART.md)** - Setup instructions

# Or let FastAPI create tables on startup (development)

# Tables will auto-create when you run the app

````

### 8. Run the application

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
````

Visit http://localhost:8000 in your browser!

## 📖 Usage

## 🎮 Usage

### For Hosts (Room Creator)

1. Create a room
2. Click "Connect Spotify" (requires Premium)
3. Authorize the app
4. Share room code or QR code
5. Use play/pause/skip controls

### For Guests

1. Join via room code or QR scan
2. Search and add songs
3. Vote on songs in the queue
4. Enjoy collaborative music!

### Key Features

- **Search**: Find songs from Spotify's library
- **Add to Queue**: Songs appear in voting order
- **Vote**: ↑ upvote, ↓ downvote to reorder queue
- **Real-time**: All updates sync instantly via WebSocket

## 🏗️ Architecture

See [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) for complete architecture details.

### Key Components

- **FastAPI Backend**: REST API + WebSocket
- **SQLite Database**: Lightweight data storage
- **Spotify Integration**: OAuth + Web Playback SDK
- **HTMX Frontend**: Dynamic updates without heavy JS
- **WebSocket**: Real-time synchronization
  │ ├── websocket.py # WebSocket manager
  │ ├── routers/ # API endpoints
  │ └── utils/ # Helper functions
  ├── static/
  │ ├── css/ # Stylesheets
  │ └── js/ # JavaScript
  ├── templates/ # Jinja2 templates
  │ ├── base.html
  │ ├── landing.html
  │ ├── room.html

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_rooms.py

# Run with coverage
pytest --cov=app
```

## 🔒 Security

- **Session Tokens**: Secure random tokens for authentication
- **OAuth 2.0 (PKCE)**: Industry-standard Spotify auth
- **Input Validation**: Pydantic schemas on all endpoints
- **SQL Injection Protection**: SQLModel ORM
- **Temporary Sessions**: No permanent user data storage

## 🐛 Troubleshooting

### Spotify Login Fails

- Verify redirect URI: `http://127.0.0.1:8000/api/auth/callback`
- Check credentials in `.env`
- Ensure Spotify Premium for host

### Music Won't Play

- Host must click "Connect Spotify" first
- Spotify Premium required
- Check browser console for SDK errors

### WebSocket Issues

- Ensure port 8000 is accessible
- Check browser console for connection errors

## 📝 License

MIT License - see LICENSE file for details

## 👤 Author

Young Hur - CS 326 Final Project

---

**Built with ❤️ for democratic music control**

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables
4. Deploy!

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Heroku

```bash
# Install Heroku CLI
heroku login
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SPOTIFY_CLIENT_ID=your_id
heroku config:set SPOTIFY_CLIENT_SECRET=your_secret

# Deploy
git push heroku main
```

## 🤝 Contributing

This is a CS 326 final project. Contributions are welcome after the course ends!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👤 Author

**Young Hur**

- UMass Amherst CS 326
- Final Project: SharePlay

## 🙏 Acknowledgments

- Inspired by the need for democratic music control in James Hall lounge
- Built for CS 326: Web Programming
- Thanks to all the international students who shared their music preferences!

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Made with ❤️ for shared spaces everywhere**
