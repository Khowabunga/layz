# tests/test_voice.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_voice_incoming_webhook():
    """Test incoming voice call webhook returns TwiML with stream."""
    from src.main import app
    client = TestClient(app)

    response = client.post("/webhook/voice/incoming")

    assert response.status_code == 200
    assert "Stream" in response.text or "Connect" in response.text


def test_voice_outbound_webhook():
    """Test outbound voice call webhook."""
    from src.main import app
    client = TestClient(app)

    response = client.post("/webhook/voice/outbound?reason=check-in")

    assert response.status_code == 200
    assert "check-in" in response.text or "coach" in response.text.lower()
