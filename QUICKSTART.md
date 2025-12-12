# SharePlay - Quick Start Guide

## Quick Start

### 1. Create and activate virtual environment

```bash
cd share_play
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit the `.env` file and set the following values:

```env
# PostgreSQL database (or start with SQLite)
DATABASE_URL=sqlite:///./shareplay.db

# Spotify API credentials
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Base URL
BASE_URL=http://localhost:8000
```

### 4. Get Spotify API keys

1. Visit https://developer.spotify.com/dashboard
2. Log in or create an account
3. Click "Create an App"
4. Enter app name and description
5. Copy Client ID and Client Secret to `.env` file

### 5. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Note: Database tables will be created automatically when the app starts.

### 6. Open in browser

http://localhost:8000

## Testing Key Features

### Create Room

1. Enter name on homepage
2. Click "Create Room"
3. 6-character Room Code and QR code generated

### Join Room

1. Enter name and Room Code on homepage
2. Click "Join Room"
3. Or scan QR code

### Add Music and Vote

1. Search for songs in search bar
2. Click "Add" button to add to queue
3. Click ↑ to upvote, ↓ to downvote
4. Queue order updates in real-time

## Troubleshooting

### Spotify API Errors

- Verify Client ID and Client Secret are correct
- Check app status at https://developer.spotify.com/dashboard

### Database Connection Errors

- Verify DATABASE_URL is correct
- Check if PostgreSQL is running: `pg_isready`
- Or use SQLite for development: `DATABASE_URL=sqlite:///./shareplay.db`

### WebSocket Connection Failed

- Check firewall is not blocking port 8000
- Check browser console for error messages

## Production Deployment

See README.md for detailed deployment guide.

### Quick Checklist:

- [ ] Set up PostgreSQL production database
- [ ] Configure environment variables (Spotify API keys, etc.)
- [ ] Set up HTTPS (required for WebSocket)
- [ ] Run uvicorn with `--workers` option
- [ ] Configure static file serving

## Development Tips

### Auto-restart on code changes

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest
pytest --cov=app  # with coverage
```

## Additional Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- SQLModel docs: https://sqlmodel.tiangolo.com/
- HTMX docs: https://htmx.org/docs/
- Spotify Web API: https://developer.spotify.com/documentation/web-api/

---

For questions or bugs, please report to GitHub Issues!
