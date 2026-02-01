# tests/test_config.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_config_loader_get_personality():
    """Test loading active personality from config."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                "active": "sarcastic-drill-sergeant",
                "presets": {
                    "sarcastic-drill-sergeant": {
                        "prompt": "You are a sarcastic drill sergeant...",
                        "voice_id": "ash"
                    }
                }
            }
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            # Reset singleton before import
            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.config.loader import ConfigLoader
            loader = ConfigLoader()

            personality = loader.get_personality()

            assert personality["prompt"] == "You are a sarcastic drill sergeant..."
            assert personality["voice_id"] == "ash"


def test_config_loader_get_schedule():
    """Test loading schedule config."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {
                "timezone": "America/Los_Angeles",
                "daily_checkins": ["07:00", "20:00"]
            }
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            # Reset singleton before import
            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.config.loader import ConfigLoader
            loader = ConfigLoader()

            schedule = loader.get_schedule()

            assert schedule["timezone"] == "America/Los_Angeles"
            assert "07:00" in schedule["daily_checkins"]
