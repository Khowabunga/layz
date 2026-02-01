# tests/test_webhooks.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_sms_webhook():
    """Test SMS webhook receives and processes messages."""
    with patch("src.webhooks.sms.chat_async", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Get to the gym!"

        from src.main import app
        client = TestClient(app)

        response = client.post(
            "/webhook/sms",
            data={
                "Body": "I just did a workout",
                "From": "+15551234567",
            }
        )

        assert response.status_code == 200
        assert "Get to the gym!" in response.text
        mock_chat.assert_called_once()


def test_health_endpoint():
    """Test health check endpoint."""
    from src.main import app
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
