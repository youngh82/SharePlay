"""Database connection and session management"""
from sqlmodel import SQLModel, create_engine, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL from environment variable (default to SQLite for development)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./shareplay.db")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    """Create all tables"""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    """Context manager for database sessions"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db_session():
    """Dependency for FastAPI to get database session"""
    with get_session() as session:
        yield session
