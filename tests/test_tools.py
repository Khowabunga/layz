# tests/test_tools.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_log_workout_tool():
    """Test the log_workout function tool."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Set up mock for log_workout
            mock_entries = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "workout123"
            mock_entries.add.return_value = (None, mock_doc_ref)
            mock_db.collection.return_value.document.return_value.collection.return_value = mock_entries

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.agent.tools.fitness import _log_workout

            result = _log_workout("Did push day - bench 185x5x3, felt strong")

            assert "logged" in result.lower() or "workout123" in result.lower()


def test_get_fitness_summary_tool():
    """Test the get_fitness_summary function tool."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Mock the query chain
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_db.collection.return_value.document.return_value.collection.return_value.where.return_value.order_by.return_value = mock_query

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.agent.tools.fitness import _get_fitness_summary

            result = _get_fitness_summary(days=7)

            assert "No workouts" in result or "workout" in result.lower()


def test_log_meal_tool():
    """Test the log_meal function tool."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Set up mock for log_meal
            mock_entries = MagicMock()
            mock_doc_ref = MagicMock()
            mock_doc_ref.id = "meal456"
            mock_entries.add.return_value = (None, mock_doc_ref)
            mock_db.collection.return_value.document.return_value.collection.return_value = mock_entries

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.agent.tools.nutrition import _log_meal

            result = _log_meal("Chipotle bowl with chicken", meal_type="lunch")

            assert "logged" in result.lower() or "meal456" in result.lower()


def test_get_nutrition_summary_tool():
    """Test the get_nutrition_summary function tool."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Mock the query chain
            mock_query = MagicMock()
            mock_query.stream.return_value = []
            mock_db.collection.return_value.document.return_value.collection.return_value.where.return_value.order_by.return_value = mock_query

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.agent.tools.nutrition import _get_nutrition_summary

            result = _get_nutrition_summary(days=1)

            assert "No meals" in result or "meal" in result.lower()


def test_send_sms_tool():
    """Test the send_sms function tool."""
    with patch("src.agent.tools.comms.Client") as mock_twilio:
        with patch.dict("os.environ", {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_PHONE_NUMBER": "+15551234567",
            "USER_PHONE_NUMBER": "+15559876543",
        }):
            mock_client = MagicMock()
            mock_twilio.return_value = mock_client
            mock_msg = MagicMock()
            mock_msg.sid = "SM123"
            mock_client.messages.create.return_value = mock_msg

            from src.agent.tools.comms import _send_sms

            result = _send_sms("Time to work out!")

            mock_client.messages.create.assert_called_once()
            assert "SM123" in result or "sent" in result.lower()


def test_function_tools_are_created():
    """Test that FunctionTool objects are properly created."""
    from agents import FunctionTool
    from src.agent.tools.fitness import log_workout, get_fitness_summary, get_last_workout
    from src.agent.tools.nutrition import log_meal, get_nutrition_summary
    from src.agent.tools.comms import send_sms, initiate_call

    assert isinstance(log_workout, FunctionTool)
    assert isinstance(get_fitness_summary, FunctionTool)
    assert isinstance(get_last_workout, FunctionTool)
    assert isinstance(log_meal, FunctionTool)
    assert isinstance(get_nutrition_summary, FunctionTool)
    assert isinstance(send_sms, FunctionTool)
    assert isinstance(initiate_call, FunctionTool)
