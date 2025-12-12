# SharePlay - Clean Setup Guide

## Fresh Installation Steps

If you've previously installed packages outside of venv, follow these steps for a clean setup:

### 1. Remove old virtual environment

```bash
cd share_play
rm -rf venv/
```

### 2. Create new virtual environment

```bash
python3 -m venv venv
```

### 3. Activate virtual environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Verify installation

```bash
pip list
```

You should see all packages from requirements.txt installed.

### 6. Run the application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Important Notes

- **Always activate venv before running commands**: `source venv/bin/activate`
- **Database auto-creates**: No migration tools needed, tables create on first run
- **Spotify credentials required**: Set up `.env` file (see QUICKSTART.md)

---

For detailed setup, see [QUICKSTART.md](QUICKSTART.md)
