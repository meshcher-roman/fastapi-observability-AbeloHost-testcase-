from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

patch("app.main.init_db_and_seed", new_callable=AsyncMock).start()

from app.db.database import get_db
from app.db.models import Message
from app.main import app

client = TestClient(app)


def test_health_check():
    """/health endpoint test"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_process_data():
    """Heavy endpoint test /process"""
    payload = {"data": "test string"}
    response = client.post("/process", json=payload)

    assert response.status_code == 200
    assert response.json() == {"echo": "test string"}


async def override_get_db_success():
    """We create a fake DB session that returns a message"""
    mock_session = AsyncMock()
    mock_msg = Message(id=1, text="This is test message number 1 for API testing")

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = mock_msg
    mock_result.scalars.return_value = mock_scalars

    mock_session.execute.return_value = mock_result
    yield mock_session


async def override_get_db_not_found():
    """Create a fake DB session that finds nothing"""
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_result.scalars.return_value = mock_scalars

    mock_session.execute.return_value = mock_result
    yield mock_session


def test_get_existing_message():
    """Message retrieval test (simulation of a successful database search)"""
    app.dependency_overrides[get_db] = override_get_db_success

    response = client.get("/message/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1

    app.dependency_overrides.clear()


def test_get_nonexistent_message():
    """Error 404 test (simulating absence in the database)"""
    app.dependency_overrides[get_db] = override_get_db_not_found

    response = client.get("/message/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Message is not found"}

    app.dependency_overrides.clear()
