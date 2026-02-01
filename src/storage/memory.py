"""Mem0 memory wrapper for semantic memory."""
import os
from typing import Any

from mem0 import MemoryClient


class MemoryWrapper:
    """Wrapper around Mem0 for agent memory."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        api_key = os.getenv("MEM0_API_KEY")
        if api_key:
            self.client = MemoryClient(api_key=api_key)
        else:
            # For testing without API key
            self.client = None

    def search(self, query: str, limit: int = 10) -> list[str]:
        """Search for relevant memories."""
        if not self.client:
            return []

        results = self.client.search(query, user_id=self.user_id, limit=limit)
        if results and results.get("results"):
            return [mem["memory"] for mem in results["results"]]
        return []

    def add(self, content: str, metadata: dict[str, Any] | None = None):
        """Add a memory."""
        if not self.client:
            return

        self.client.add(
            [{"role": "user", "content": content}],
            user_id=self.user_id,
            metadata=metadata,
        )

    def add_conversation(self, messages: list[dict], metadata: dict[str, Any] | None = None):
        """Add a full conversation to memory."""
        if not self.client:
            return

        self.client.add(messages, user_id=self.user_id, metadata=metadata)

    def format_memories(self, memories: list[str]) -> str:
        """Format memories for injection into prompts."""
        if not memories:
            return "No relevant memories."
        return "\n".join(f"- {mem}" for mem in memories)
