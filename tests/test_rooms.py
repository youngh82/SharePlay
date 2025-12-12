"""Test suite for room management"""
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
    """Create a test client with database session override"""
    def get_session_override():
        return session
    
    app.dependency_overrides[get_db_session] = get_session_override
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()


def test_create_room(client: TestClient):
    """Test room creation"""
    response = client.post(
        "/api/rooms/create",
        json={"host_name": "Test Host"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "room_code" in data
    assert "host_token" in data
    assert "qr_code_url" in data
    assert len(data["room_code"]) == 6


def test_join_room(client: TestClient):
    """Test joining an existing room"""
    # First create a room
    create_response = client.post(
        "/api/rooms/create",
        json={"host_name": "Host"}
    )
    room_code = create_response.json()["room_code"]
    
    # Join the room
    join_response = client.post(
        "/api/rooms/join",
        json={"guest_name": "Guest", "room_code": room_code}
    )
    
    assert join_response.status_code == 200
    data = join_response.json()
    
    assert "guest_token" in data
    assert data["room_code"] == room_code


def test_join_nonexistent_room(client: TestClient):
    """Test joining a room that doesn't exist"""
    response = client.post(
        "/api/rooms/join",
        json={"guest_name": "Guest", "room_code": "FAKE12"}
    )
    
    assert response.status_code == 404


def test_get_room_status(client: TestClient):
    """Test getting room status"""
    # Create room
    create_response = client.post(
        "/api/rooms/create",
        json={"host_name": "Host"}
    )
    room_code = create_response.json()["room_code"]
    host_token = create_response.json()["host_token"]
    
    # Get status
    status_response = client.get(
        f"/api/rooms/{room_code}/status",
        headers={"Authorization": f"Bearer {host_token}"}
    )
    
    assert status_response.status_code == 200
    data = status_response.json()
    
    assert data["room_code"] == room_code
    assert data["is_active"] == True
    assert len(data["users"]) == 1
    assert data["users"][0]["name"] == "Host"
    assert data["users"][0]["role"] == "host"


def test_room_code_uniqueness(client: TestClient):
    """Test that room codes are unique"""
    # Create multiple rooms
    codes = set()
    for i in range(5):
        response = client.post(
            "/api/rooms/create",
            json={"host_name": f"Host {i}"}
        )
        codes.add(response.json()["room_code"])
    
    # All codes should be unique
    assert len(codes) == 5
