"""Test suite for voting functionality"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_db_session


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="room_with_songs")
def room_with_songs_fixture(client: TestClient):
    """Create a room with songs in queue"""
    # Create room
    create_response = client.post(
        "/api/rooms/create",
        json={"host_name": "Host"}
    )
    room_code = create_response.json()["room_code"]
    host_token = create_response.json()["host_token"]
    
    # Note: In a real test, you'd mock the Spotify API
    # For now, this is a placeholder structure
    
    return {
        "room_code": room_code,
        "host_token": host_token
    }


def test_vote_on_song(client: TestClient, room_with_songs):
    """Test voting on a song"""
    # This test would require mocking Spotify API
    # and adding songs to the queue first
    pass


def test_vote_changes_queue_order(client: TestClient):
    """Test that votes change queue order"""
    # This test would verify the queue reordering logic
    pass


def test_user_can_change_vote(client: TestClient):
    """Test that a user can change their vote"""
    pass


def test_user_cannot_vote_twice_same_type(client: TestClient):
    """Test that clicking same vote type removes the vote"""
    pass
