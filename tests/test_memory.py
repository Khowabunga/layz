# tests/test_memory.py
import pytest
from unittest.mock import MagicMock, patch
import os


def test_memory_search():
    """Test searching memories."""
    with patch.dict(os.environ, {"MEM0_API_KEY": "test-key"}):
        with patch("src.storage.memory.MemoryClient") as mock_mem0:
            mock_client = MagicMock()
            mock_mem0.return_value = mock_client
            mock_client.search.return_value = {
                "results": [
                    {"memory": "User prefers morning workouts"},
                    {"memory": "User is training for a marathon"}
                ]
            }

            from src.storage.memory import MemoryWrapper
            wrapper = MemoryWrapper(user_id="keith")

            results = wrapper.search("workout preferences")

            assert len(results) == 2
            assert "morning workouts" in results[0]


def test_memory_add():
    """Test adding memories."""
    with patch.dict(os.environ, {"MEM0_API_KEY": "test-key"}):
        with patch("src.storage.memory.MemoryClient") as mock_mem0:
            mock_client = MagicMock()
            mock_mem0.return_value = mock_client

            from src.storage.memory import MemoryWrapper
            wrapper = MemoryWrapper(user_id="keith")

            wrapper.add("User said they hate burpees")

            mock_client.add.assert_called_once()


def test_memory_format():
    """Test formatting memories for prompts."""
    with patch("src.storage.memory.MemoryClient") as mock_mem0:
        mock_mem0.return_value = MagicMock()

        from src.storage.memory import MemoryWrapper
        wrapper = MemoryWrapper(user_id="keith")

        formatted = wrapper.format_memories(["Likes morning workouts", "Hates burpees"])

        assert "- Likes morning workouts" in formatted
        assert "- Hates burpees" in formatted


def test_memory_format_empty():
    """Test formatting empty memories."""
    with patch("src.storage.memory.MemoryClient") as mock_mem0:
        mock_mem0.return_value = MagicMock()

        from src.storage.memory import MemoryWrapper
        wrapper = MemoryWrapper(user_id="keith")

        formatted = wrapper.format_memories([])

        assert "No relevant memories" in formatted


def test_memory_no_api_key():
    """Test that MemoryWrapper works without API key (returns empty)."""
    with patch.dict(os.environ, {}, clear=True):
        # Ensure MEM0_API_KEY is not set
        if "MEM0_API_KEY" in os.environ:
            del os.environ["MEM0_API_KEY"]

        from src.storage.memory import MemoryWrapper
        wrapper = MemoryWrapper(user_id="keith")

        results = wrapper.search("anything")
        assert results == []

        # Should not raise
        wrapper.add("test")
