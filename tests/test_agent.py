# tests/test_agent.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def reset_firestore_singleton():
    """Reset the FirestoreClient singleton between tests."""
    yield
    import src.storage.firestore as fs_module
    fs_module.FirestoreClient._instance = None
    fs_module.FirestoreClient._initialized = False


def test_fitness_coach_creation():
    """Test that FitnessCoach agent can be created."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firebase._apps = []
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db

            # Mock config document
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

            import src.storage.firestore as fs_module
            fs_module.FirestoreClient._instance = None
            fs_module.FirestoreClient._initialized = False

            from src.agent.coach import create_fitness_coach

            agent = create_fitness_coach()

            assert agent.name == "FitnessCoach"
            assert len(agent.tools) > 0


def test_chat_with_memory():
    """Test chat function integrates memory."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            with patch("src.storage.memory.MemoryClient") as mock_mem0:
                with patch("src.agent.coach.Runner") as mock_runner:
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

                    # Mock memory
                    mock_mem_client = MagicMock()
                    mock_mem0.return_value = mock_mem_client
                    mock_mem_client.search.return_value = {
                        "results": [{"memory": "User likes morning workouts"}]
                    }

                    # Mock runner
                    mock_result = MagicMock()
                    mock_result.final_output = "Time to work out!"
                    mock_runner.run_sync.return_value = mock_result

                    import src.storage.firestore as fs_module
                    fs_module.FirestoreClient._instance = None
                    fs_module.FirestoreClient._initialized = False

                    # Set MEM0_API_KEY for memory to work
                    import os
                    with patch.dict(os.environ, {"MEM0_API_KEY": "test-key"}):
                        from src.agent.coach import chat

                        response = chat("How am I doing?", user_id="keith")

                        assert response == "Time to work out!"
                        mock_runner.run_sync.assert_called_once()
