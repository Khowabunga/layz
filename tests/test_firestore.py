# tests/test_firestore.py
import pytest
from unittest.mock import MagicMock, patch
import importlib


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    # Reset after each test
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_firestore_client_initialization():
    """Test that FirestoreClient initializes with Firebase."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_firestore.client.return_value = MagicMock()

            from src.storage.firestore import FirestoreClient
            # Reset singleton for this test
            FirestoreClient._instance = None
            FirestoreClient._initialized = False

            client = FirestoreClient()

            assert client.db is not None


def test_log_workout():
    """Test logging a workout to Firestore."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Set up the chained call: collection().document().collection().add()
            mock_entries_collection = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "doc123"
            mock_entries_collection.add.return_value = (None, mock_doc_ref)

            mock_workouts_doc = MagicMock()
            mock_workouts_doc.collection.return_value = mock_entries_collection

            mock_logs_collection = MagicMock()
            mock_logs_collection.document.return_value = mock_workouts_doc

            mock_db.collection.return_value = mock_logs_collection

            from src.storage.firestore import FirestoreClient
            # Reset singleton for this test
            FirestoreClient._instance = None
            FirestoreClient._initialized = False

            client = FirestoreClient()

            result = client.log_workout(
                workout_type="push",
                duration_mins=45,
                exercises=[{"name": "bench press", "sets": 3, "reps": 5}],
                notes="felt strong",
                raw_input="Did push day"
            )

            mock_entries_collection.add.assert_called_once()
            assert result == "doc123"


def test_log_meal():
    """Test logging a meal to Firestore."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Set up the chained call: collection().document().collection().add()
            mock_entries_collection = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "meal456"
            mock_entries_collection.add.return_value = (None, mock_doc_ref)

            mock_nutrition_doc = MagicMock()
            mock_nutrition_doc.collection.return_value = mock_entries_collection

            mock_logs_collection = MagicMock()
            mock_logs_collection.document.return_value = mock_nutrition_doc

            mock_db.collection.return_value = mock_logs_collection

            from src.storage.firestore import FirestoreClient
            # Reset singleton for this test
            FirestoreClient._instance = None
            FirestoreClient._initialized = False

            client = FirestoreClient()

            result = client.log_meal(
                meal_type="lunch",
                calories=650,
                protein=45,
                carbs=70,
                fat=18,
                description="Chipotle bowl",
                raw_input="Had a chipotle bowl"
            )

            mock_entries_collection.add.assert_called_once()
            assert result == "meal456"
