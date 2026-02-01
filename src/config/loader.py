"""Configuration loader from Firestore."""
import json
import os
from pathlib import Path
from typing import Any

from src.storage.firestore import FirestoreClient


class ConfigLoader:
    """Load and manage configuration from Firestore."""

    def __init__(self):
        self.fs = FirestoreClient()
        self._cache: dict[str, Any] = {}

    def _get_config(self, config_name: str) -> dict:
        """Get a config document, with caching."""
        if config_name in self._cache:
            return self._cache[config_name]

        doc = self.fs.db.collection("config").document(config_name).get()
        if doc.exists:
            self._cache[config_name] = doc.to_dict()
            return self._cache[config_name]

        # Fall back to defaults
        return self._load_default(config_name)

    def _load_default(self, config_name: str) -> dict:
        """Load default config from JSON file."""
        defaults_path = Path(__file__).parent.parent.parent / "configs" / "defaults.json"
        if defaults_path.exists():
            with open(defaults_path) as f:
                defaults = json.load(f)
                return defaults.get(config_name, {})
        return {}

    def get_personality(self) -> dict:
        """Get the active personality config."""
        config = self._get_config("personality")
        active = config.get("active", "sarcastic-drill-sergeant")
        presets = config.get("presets", {})
        return presets.get(active, {})

    def get_schedule(self) -> dict:
        """Get schedule config."""
        return self._get_config("schedule")

    def get_triggers(self) -> dict:
        """Get trigger rules config."""
        return self._get_config("triggers")

    def get_user(self) -> dict:
        """Get user config."""
        config = self._get_config("user")
        # Allow env var overrides
        return {
            "phone": os.getenv("USER_PHONE_NUMBER") or config.get("phone", ""),
            "name": os.getenv("USER_NAME") or config.get("name", ""),
            "timezone": os.getenv("USER_TIMEZONE") or config.get("timezone", "America/Los_Angeles"),
        }

    def clear_cache(self):
        """Clear the config cache."""
        self._cache = {}
