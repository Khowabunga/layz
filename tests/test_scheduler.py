# tests/test_scheduler.py
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


def test_daily_checkin_endpoint():
    """Test daily check-in cron endpoint."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            with patch("src.scheduler.checkins.Runner") as mock_runner:
                mock_firebase._apps = []
                mock_db = MagicMock()
                mock_firestore.client.return_value = mock_db

                # Mock config
                mock_doc = MagicMock()
                mock_doc.exists = True
                mock_doc.to_dict.return_value = {
                    "active": "test",
                    "presets": {"test": {"prompt": "You are a coach", "voice_id": "ash"}}
                }
                mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

                # Mock workout/meal queries
                mock_query = MagicMock()
                mock_query.stream.return_value = []
                mock_db.collection.return_value.document.return_value.collection.return_value.where.return_value.order_by.return_value = mock_query

                # Mock runner
                mock_result = MagicMock()
                mock_result.final_output = "Time to move!"
                mock_runner.run_sync.return_value = mock_result

                import src.storage.firestore as fs_module
                fs_module.FirestoreClient._instance = None
                fs_module.FirestoreClient._initialized = False

                from src.main import app
                client = TestClient(app)

                response = client.post("/cron/daily-checkin")

                assert response.status_code == 200
                assert response.json()["status"] == "ok"


def test_check_triggers_endpoint():
    """Test trigger check cron endpoint."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Mock config
            mock_doc = MagicMock()
            mock_doc.exists = True
            mock_doc.to_dict.return_value = {"rules": []}
            mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.main import app
            client = TestClient(app)

            response = client.post("/cron/check-triggers")

            assert response.status_code == 200
            assert response.json()["status"] == "ok"
