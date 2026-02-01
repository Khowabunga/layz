# Fitness Accountability Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a personal fitness accountability agent that communicates via SMS and voice calls, tracks workouts and nutrition, and proactively keeps you accountable.

**Architecture:** FastAPI backend on Cloud Run receiving Twilio webhooks, orchestrating an OpenAI Agent with function tools for fitness tracking. Firestore stores structured data (workouts, meals, configs), Mem0 handles semantic memory. Cloud Scheduler triggers proactive outreach.

**Tech Stack:** Python 3.11+, FastAPI, OpenAI Agents SDK, OpenAI Realtime API, Twilio, Firebase Admin SDK (Firestore), Mem0, Docker, Cloud Run, Cloud Scheduler

---

## Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `src/main.py`
- Create: `.env.example`
- Create: `Dockerfile`
- Create: `.gitignore`

**Step 1: Create pyproject.toml with dependencies**

```toml
[project]
name = "layz"
version = "0.1.0"
description = "Personal fitness accountability agent"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "openai-agents>=0.0.7",
    "openai>=1.12.0",
    "twilio>=9.0.0",
    "firebase-admin>=6.4.0",
    "mem0ai>=0.1.0",
    "python-dotenv>=1.0.0",
    "websockets>=12.0",
    "httpx>=0.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 2: Create src/__init__.py**

```python
"""Layz - Personal fitness accountability agent."""
```

**Step 3: Create minimal src/main.py**

```python
"""FastAPI application entrypoint."""
from fastapi import FastAPI

app = FastAPI(title="Layz", description="Personal fitness accountability agent")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Step 4: Create .env.example**

```bash
# OpenAI
OPENAI_API_KEY=

# Twilio
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Firebase
GOOGLE_CLOUD_PROJECT=
FIREBASE_SERVICE_ACCOUNT=

# Mem0
MEM0_API_KEY=

# App
USER_PHONE_NUMBER=
USER_NAME=
USER_TIMEZONE=America/Los_Angeles
```

**Step 5: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ src/
COPY configs/ configs/

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Step 6: Create .gitignore**

```
__pycache__/
*.py[cod]
.env
.venv/
venv/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
*.log
```

**Step 7: Commit**

```bash
git add pyproject.toml src/__init__.py src/main.py .env.example Dockerfile .gitignore
git commit -m "feat: project scaffolding with FastAPI and dependencies"
```

---

## Task 2: Firestore Storage Layer

**Files:**
- Create: `src/storage/__init__.py`
- Create: `src/storage/firestore.py`
- Create: `tests/test_firestore.py`

**Step 1: Create src/storage/__init__.py**

```python
"""Storage layer for Firestore."""
from src.storage.firestore import FirestoreClient

__all__ = ["FirestoreClient"]
```

**Step 2: Write failing test for FirestoreClient**

```python
# tests/test_firestore.py
import pytest
from unittest.mock import MagicMock, patch


def test_firestore_client_initialization():
    """Test that FirestoreClient initializes with Firebase."""
    with patch("src.storage.firestore.firebase_admin") as mock_firebase:
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_firestore.client.return_value = MagicMock()

            from src.storage.firestore import FirestoreClient
            client = FirestoreClient()

            assert client.db is not None


def test_log_workout():
    """Test logging a workout to Firestore."""
    with patch("src.storage.firestore.firebase_admin"):
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db
            mock_collection = MagicMock()
            mock_db.collection.return_value = mock_collection

            from src.storage.firestore import FirestoreClient
            client = FirestoreClient()

            result = client.log_workout(
                workout_type="push",
                duration_mins=45,
                exercises=[{"name": "bench press", "sets": 3, "reps": 5}],
                notes="felt strong",
                raw_input="Did push day"
            )

            mock_collection.add.assert_called_once()
            assert result is not None


def test_log_meal():
    """Test logging a meal to Firestore."""
    with patch("src.storage.firestore.firebase_admin"):
        with patch("src.storage.firestore.firestore") as mock_firestore:
            mock_db = MagicMock()
            mock_firestore.client.return_value = mock_db
            mock_collection = MagicMock()
            mock_db.collection.return_value = mock_collection

            from src.storage.firestore import FirestoreClient
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

            mock_collection.add.assert_called_once()
            assert result is not None
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_firestore.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.storage'"

**Step 4: Implement FirestoreClient**

```python
# src/storage/firestore.py
"""Firestore client for structured data storage."""
import os
from datetime import datetime, timedelta
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore


class FirestoreClient:
    """Client for Firestore operations."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not FirestoreClient._initialized:
            self._initialize_firebase()
            FirestoreClient._initialized = True

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use Application Default Credentials
                firebase_admin.initialize_app()

        self.db = firestore.client()

    def log_workout(
        self,
        workout_type: str,
        duration_mins: int,
        exercises: list[dict] | None = None,
        notes: str | None = None,
        raw_input: str | None = None,
    ) -> str:
        """Log a workout to Firestore."""
        doc_ref = self.db.collection("logs").document("workouts").collection("entries").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "type": workout_type,
            "duration_mins": duration_mins,
            "exercises": exercises or [],
            "notes": notes,
            "raw_input": raw_input,
        })
        return doc_ref[1].id

    def log_meal(
        self,
        meal_type: str,
        calories: int,
        protein: int,
        carbs: int,
        fat: int,
        description: str,
        raw_input: str | None = None,
    ) -> str:
        """Log a meal to Firestore."""
        doc_ref = self.db.collection("logs").document("nutrition").collection("entries").add({
            "timestamp": firestore.SERVER_TIMESTAMP,
            "meal_type": meal_type,
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat,
            "description": description,
            "raw_input": raw_input,
        })
        return doc_ref[1].id

    def get_workouts(self, days: int = 7) -> list[dict]:
        """Get workouts from the past N days."""
        cutoff = datetime.now() - timedelta(days=days)
        query = (
            self.db.collection("logs")
            .document("workouts")
            .collection("entries")
            .where("timestamp", ">=", cutoff)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

    def get_meals(self, days: int = 1) -> list[dict]:
        """Get meals from the past N days."""
        cutoff = datetime.now() - timedelta(days=days)
        query = (
            self.db.collection("logs")
            .document("nutrition")
            .collection("entries")
            .where("timestamp", ">=", cutoff)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        return [{"id": doc.id, **doc.to_dict()} for doc in query.stream()]

    def get_last_workout_date(self) -> datetime | None:
        """Get the date of the most recent workout."""
        query = (
            self.db.collection("logs")
            .document("workouts")
            .collection("entries")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        docs = list(query.stream())
        if docs:
            return docs[0].to_dict().get("timestamp")
        return None
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_firestore.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/storage/ tests/test_firestore.py
git commit -m "feat: add Firestore storage layer for workouts and meals"
```

---

## Task 3: Config Loader

**Files:**
- Create: `src/config/__init__.py`
- Create: `src/config/loader.py`
- Create: `configs/defaults.json`
- Create: `tests/test_config.py`

**Step 1: Write failing test for ConfigLoader**

```python
# tests/test_config.py
import pytest
from unittest.mock import MagicMock, patch


def test_config_loader_get_personality():
    """Test loading active personality from config."""
    with patch("src.config.loader.FirestoreClient") as mock_fs:
        mock_db = MagicMock()
        mock_fs.return_value.db = mock_db

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

        from src.config.loader import ConfigLoader
        loader = ConfigLoader()

        personality = loader.get_personality()

        assert personality["prompt"] == "You are a sarcastic drill sergeant..."
        assert personality["voice_id"] == "ash"


def test_config_loader_get_schedule():
    """Test loading schedule config."""
    with patch("src.config.loader.FirestoreClient") as mock_fs:
        mock_db = MagicMock()
        mock_fs.return_value.db = mock_db

        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "timezone": "America/Los_Angeles",
            "daily_checkins": ["07:00", "20:00"]
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        from src.config.loader import ConfigLoader
        loader = ConfigLoader()

        schedule = loader.get_schedule()

        assert schedule["timezone"] == "America/Los_Angeles"
        assert "07:00" in schedule["daily_checkins"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.config'"

**Step 3: Create configs/defaults.json**

```json
{
  "personality": {
    "active": "sarcastic-drill-sergeant",
    "presets": {
      "sarcastic-drill-sergeant": {
        "prompt": "You are a sarcastic drill sergeant fitness coach. You're tough but effective. You use dry wit and sarcasm to motivate. You don't accept excuses. You celebrate wins but always push for more. Keep responses concise and punchy. Examples: 'Oh, you're tired? Cool story. The gym doesn't care.' or 'Three days without a workout? And here I thought we were making progress.'",
        "voice_id": "ash"
      },
      "supportive-friend": {
        "prompt": "You are a supportive and encouraging fitness coach. You celebrate every win, big or small. You're empathetic when things get hard. You focus on progress, not perfection. You help find solutions rather than dwelling on setbacks.",
        "voice_id": "coral"
      }
    }
  },
  "schedule": {
    "timezone": "America/Los_Angeles",
    "daily_checkins": ["07:00", "20:00"]
  },
  "triggers": {
    "rules": [
      {"event": "no_workout", "days": 2, "action": "sms"},
      {"event": "no_workout", "days": 4, "action": "call"},
      {"event": "calorie_deficit", "threshold": 500, "action": "sms"}
    ]
  },
  "user": {
    "phone": "",
    "name": ""
  }
}
```

**Step 4: Implement ConfigLoader**

```python
# src/config/loader.py
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
```

**Step 5: Create src/config/__init__.py**

```python
"""Configuration management."""
from src.config.loader import ConfigLoader

__all__ = ["ConfigLoader"]
```

**Step 6: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/config/ configs/defaults.json tests/test_config.py
git commit -m "feat: add config loader with Firestore and defaults fallback"
```

---

## Task 4: Mem0 Memory Wrapper

**Files:**
- Create: `src/storage/memory.py`
- Modify: `src/storage/__init__.py`
- Create: `tests/test_memory.py`

**Step 1: Write failing test for MemoryClient**

```python
# tests/test_memory.py
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


def test_memory_search():
    """Test searching memories."""
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
    with patch("src.storage.memory.MemoryClient") as mock_mem0:
        mock_client = MagicMock()
        mock_mem0.return_value = mock_client

        from src.storage.memory import MemoryWrapper
        wrapper = MemoryWrapper(user_id="keith")

        wrapper.add("User said they hate burpees")

        mock_client.add.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'src.storage.memory'"

**Step 3: Implement MemoryWrapper**

```python
# src/storage/memory.py
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
```

**Step 4: Update src/storage/__init__.py**

```python
"""Storage layer for Firestore and Mem0."""
from src.storage.firestore import FirestoreClient
from src.storage.memory import MemoryWrapper

__all__ = ["FirestoreClient", "MemoryWrapper"]
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_memory.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/storage/memory.py src/storage/__init__.py tests/test_memory.py
git commit -m "feat: add Mem0 memory wrapper for semantic memory"
```

---

## Task 5: Agent Tools

**Files:**
- Create: `src/agent/__init__.py`
- Create: `src/agent/tools/__init__.py`
- Create: `src/agent/tools/fitness.py`
- Create: `src/agent/tools/nutrition.py`
- Create: `src/agent/tools/comms.py`
- Create: `tests/test_tools.py`

**Step 1: Write failing test for fitness tools**

```python
# tests/test_tools.py
import pytest
from unittest.mock import MagicMock, patch


def test_log_workout_tool():
    """Test the log_workout function tool."""
    with patch("src.agent.tools.fitness.FirestoreClient") as mock_fs:
        mock_client = MagicMock()
        mock_fs.return_value = mock_client
        mock_client.log_workout.return_value = "doc123"

        from src.agent.tools.fitness import log_workout

        # The tool should parse natural language and log structured data
        result = log_workout("Did push day - bench 185x5x3, felt strong")

        assert "logged" in result.lower() or "recorded" in result.lower()


def test_get_fitness_summary_tool():
    """Test the get_fitness_summary function tool."""
    with patch("src.agent.tools.fitness.FirestoreClient") as mock_fs:
        mock_client = MagicMock()
        mock_fs.return_value = mock_client
        mock_client.get_workouts.return_value = [
            {"type": "push", "duration_mins": 45, "timestamp": "2024-01-15"},
            {"type": "pull", "duration_mins": 50, "timestamp": "2024-01-14"},
        ]

        from src.agent.tools.fitness import get_fitness_summary

        result = get_fitness_summary(days=7)

        assert "push" in result.lower() or "workout" in result.lower()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_tools.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement fitness tools**

```python
# src/agent/tools/fitness.py
"""Fitness tracking tools for the agent."""
from agents import function_tool

from src.storage.firestore import FirestoreClient


@function_tool
def log_workout(description: str) -> str:
    """Log a workout from a natural language description.

    Parse the description to extract workout type, duration, exercises,
    and any notes. Store in Firestore.

    Args:
        description: Natural language workout description, e.g.,
            "Did push day - bench 185x5x3, incline dumbbell, triceps. 45 mins, felt strong"
    """
    fs = FirestoreClient()

    # Store with raw input - the LLM calling this tool should have already
    # extracted what it can, but we preserve the original
    doc_id = fs.log_workout(
        workout_type="general",  # Could be enhanced with NLP extraction
        duration_mins=0,
        exercises=[],
        notes=description,
        raw_input=description,
    )

    return f"Workout logged successfully (ID: {doc_id}). Keep pushing!"


@function_tool
def get_fitness_summary(days: int = 7) -> str:
    """Get a summary of workouts from the past N days.

    Args:
        days: Number of days to look back (default: 7)
    """
    fs = FirestoreClient()
    workouts = fs.get_workouts(days=days)

    if not workouts:
        return f"No workouts logged in the past {days} days."

    summary_lines = [f"Workouts in the past {days} days ({len(workouts)} total):"]
    for w in workouts:
        workout_type = w.get("type", "workout")
        duration = w.get("duration_mins", "?")
        notes = w.get("notes", "")
        timestamp = w.get("timestamp", "")
        if timestamp:
            date_str = timestamp.strftime("%a %m/%d") if hasattr(timestamp, 'strftime') else str(timestamp)[:10]
        else:
            date_str = "?"
        summary_lines.append(f"- {date_str}: {workout_type} ({duration} min) - {notes[:50]}")

    return "\n".join(summary_lines)


@function_tool
def get_last_workout() -> str:
    """Get information about the most recent workout."""
    fs = FirestoreClient()
    last_date = fs.get_last_workout_date()

    if not last_date:
        return "No workouts logged yet."

    from datetime import datetime
    if hasattr(last_date, 'timestamp'):
        days_ago = (datetime.now() - datetime.fromtimestamp(last_date.timestamp())).days
    else:
        days_ago = "?"

    return f"Last workout was {days_ago} days ago."
```

**Step 4: Implement nutrition tools**

```python
# src/agent/tools/nutrition.py
"""Nutrition tracking tools for the agent."""
from agents import function_tool

from src.storage.firestore import FirestoreClient


@function_tool
def log_meal(description: str, meal_type: str = "meal") -> str:
    """Log a meal from a natural language description.

    Parse the description to estimate calories and macros. Store in Firestore.

    Args:
        description: Natural language meal description, e.g.,
            "Chipotle bowl with chicken, rice, beans, and guac"
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
    """
    fs = FirestoreClient()

    # Store with placeholder values - in production, could use an API
    # or have the LLM estimate before calling this tool
    doc_id = fs.log_meal(
        meal_type=meal_type,
        calories=0,  # Placeholder - LLM should estimate
        protein=0,
        carbs=0,
        fat=0,
        description=description,
        raw_input=description,
    )

    return f"Meal logged successfully (ID: {doc_id}). I'll track your nutrition!"


@function_tool
def get_nutrition_summary(days: int = 1) -> str:
    """Get a summary of nutrition from the past N days.

    Args:
        days: Number of days to look back (default: 1 for today)
    """
    fs = FirestoreClient()
    meals = fs.get_meals(days=days)

    if not meals:
        return f"No meals logged in the past {days} day(s)."

    total_calories = sum(m.get("calories", 0) for m in meals)
    total_protein = sum(m.get("protein", 0) for m in meals)
    total_carbs = sum(m.get("carbs", 0) for m in meals)
    total_fat = sum(m.get("fat", 0) for m in meals)

    summary_lines = [
        f"Nutrition summary for past {days} day(s):",
        f"- Meals logged: {len(meals)}",
        f"- Total calories: {total_calories}",
        f"- Protein: {total_protein}g",
        f"- Carbs: {total_carbs}g",
        f"- Fat: {total_fat}g",
        "",
        "Recent meals:"
    ]

    for m in meals[:5]:
        desc = m.get("description", "Unknown")[:40]
        cals = m.get("calories", "?")
        summary_lines.append(f"- {desc} ({cals} cal)")

    return "\n".join(summary_lines)
```

**Step 5: Implement comms tools**

```python
# src/agent/tools/comms.py
"""Communication tools for the agent."""
import os

from agents import function_tool
from twilio.rest import Client


def _get_twilio_client() -> Client:
    """Get configured Twilio client."""
    return Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
    )


@function_tool
def send_sms(message: str) -> str:
    """Send an SMS message to the user.

    Args:
        message: The message to send
    """
    client = _get_twilio_client()

    msg = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=os.getenv("USER_PHONE_NUMBER"),
    )

    return f"SMS sent successfully (SID: {msg.sid})"


@function_tool
def initiate_call(reason: str) -> str:
    """Initiate a voice call to the user.

    Args:
        reason: The reason for calling (used in the call setup)
    """
    client = _get_twilio_client()

    # The webhook URL will handle the actual voice conversation
    base_url = os.getenv("BASE_URL", "https://your-domain.com")

    call = client.calls.create(
        to=os.getenv("USER_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        url=f"{base_url}/webhook/voice/outbound?reason={reason}",
    )

    return f"Call initiated (SID: {call.sid})"
```

**Step 6: Create __init__.py files**

```python
# src/agent/__init__.py
"""Agent module."""
```

```python
# src/agent/tools/__init__.py
"""Agent tools."""
from src.agent.tools.fitness import log_workout, get_fitness_summary, get_last_workout
from src.agent.tools.nutrition import log_meal, get_nutrition_summary
from src.agent.tools.comms import send_sms, initiate_call

__all__ = [
    "log_workout",
    "get_fitness_summary",
    "get_last_workout",
    "log_meal",
    "get_nutrition_summary",
    "send_sms",
    "initiate_call",
]
```

**Step 7: Run test to verify it passes**

Run: `pytest tests/test_tools.py -v`
Expected: PASS

**Step 8: Commit**

```bash
git add src/agent/ tests/test_tools.py
git commit -m "feat: add agent tools for fitness, nutrition, and comms"
```

---

## Task 6: Core Agent Definition

**Files:**
- Create: `src/agent/coach.py`
- Create: `tests/test_agent.py`

**Step 1: Write failing test for FitnessCoach agent**

```python
# tests/test_agent.py
import pytest
from unittest.mock import MagicMock, patch


def test_fitness_coach_creation():
    """Test that FitnessCoach agent can be created."""
    with patch("src.agent.coach.ConfigLoader") as mock_config:
        mock_config.return_value.get_personality.return_value = {
            "prompt": "You are a sarcastic drill sergeant...",
            "voice_id": "ash"
        }

        from src.agent.coach import create_fitness_coach

        agent = create_fitness_coach()

        assert agent.name == "FitnessCoach"
        assert len(agent.tools) > 0


def test_chat_with_memory():
    """Test chat function integrates memory."""
    with patch("src.agent.coach.ConfigLoader") as mock_config:
        with patch("src.agent.coach.MemoryWrapper") as mock_memory:
            with patch("src.agent.coach.Runner") as mock_runner:
                mock_config.return_value.get_personality.return_value = {
                    "prompt": "You are a coach",
                    "voice_id": "ash"
                }
                mock_config.return_value.get_user.return_value = {"name": "Keith"}
                mock_memory.return_value.search.return_value = ["User likes morning workouts"]
                mock_runner.run_sync.return_value.final_output = "Time to work out!"

                from src.agent.coach import chat

                response = chat("How am I doing?", user_id="keith")

                assert response is not None
                mock_memory.return_value.search.assert_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_agent.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement FitnessCoach agent**

```python
# src/agent/coach.py
"""Fitness coach agent definition."""
from agents import Agent, Runner

from src.agent.tools import (
    log_workout,
    get_fitness_summary,
    get_last_workout,
    log_meal,
    get_nutrition_summary,
    send_sms,
    initiate_call,
)
from src.config.loader import ConfigLoader
from src.storage.memory import MemoryWrapper


def create_fitness_coach() -> Agent:
    """Create the fitness coach agent with current personality."""
    config = ConfigLoader()
    personality = config.get_personality()
    user = config.get_user()

    base_prompt = personality.get("prompt", "You are a helpful fitness coach.")

    instructions = f"""
{base_prompt}

You are coaching {user.get('name', 'the user')}.

You have access to tools to:
- Log workouts and meals they tell you about
- Check their workout and nutrition history
- Send them SMS messages
- Call them if needed

When they tell you about a workout or meal, log it. When they ask about their progress, check their history.
Be concise in your responses - this is SMS, not email.
"""

    return Agent(
        name="FitnessCoach",
        instructions=instructions,
        tools=[
            log_workout,
            get_fitness_summary,
            get_last_workout,
            log_meal,
            get_nutrition_summary,
            send_sms,
            initiate_call,
        ],
        model="gpt-4o",
    )


def chat(user_message: str, user_id: str = "default") -> str:
    """Handle a chat message with memory integration."""
    config = ConfigLoader()
    memory = MemoryWrapper(user_id=user_id)

    # Search for relevant memories
    relevant_memories = memory.search(user_message, limit=10)

    # Create agent with memory context
    agent = create_fitness_coach()

    # Inject memories into the conversation context
    memory_context = memory.format_memories(relevant_memories)
    augmented_message = f"""
[Context from past conversations:]
{memory_context}

[User message:]
{user_message}
"""

    # Run the agent
    result = Runner.run_sync(agent, augmented_message)

    # Store this conversation in memory
    memory.add_conversation([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": result.final_output},
    ])

    return result.final_output


async def chat_async(user_message: str, user_id: str = "default") -> str:
    """Async version of chat."""
    config = ConfigLoader()
    memory = MemoryWrapper(user_id=user_id)

    relevant_memories = memory.search(user_message, limit=10)
    agent = create_fitness_coach()

    memory_context = memory.format_memories(relevant_memories)
    augmented_message = f"""
[Context from past conversations:]
{memory_context}

[User message:]
{user_message}
"""

    result = await Runner.run(agent, augmented_message)

    memory.add_conversation([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": result.final_output},
    ])

    return result.final_output
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_agent.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/agent/coach.py tests/test_agent.py
git commit -m "feat: add FitnessCoach agent with memory integration"
```

---

## Task 7: SMS Webhook Handler

**Files:**
- Create: `src/webhooks/__init__.py`
- Create: `src/webhooks/sms.py`
- Modify: `src/main.py`
- Create: `tests/test_webhooks.py`

**Step 1: Write failing test for SMS webhook**

```python
# tests/test_webhooks.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_sms_webhook():
    """Test SMS webhook receives and processes messages."""
    with patch("src.webhooks.sms.chat_async") as mock_chat:
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
        assert "Get to the gym!" in response.text or "Response" in response.text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_webhooks.py -v`
Expected: FAIL

**Step 3: Implement SMS webhook**

```python
# src/webhooks/sms.py
"""SMS webhook handler for Twilio."""
from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse

from src.agent.coach import chat_async

router = APIRouter()


@router.post("/webhook/sms")
async def handle_sms(Body: str = Form(...), From: str = Form(...)):
    """Handle incoming SMS from Twilio."""
    # Use phone number as user_id for simplicity
    user_id = From.replace("+", "")

    # Get response from agent
    agent_response = await chat_async(Body, user_id=user_id)

    # Format as TwiML response
    response = MessagingResponse()
    response.message(agent_response)

    return str(response)
```

**Step 4: Create src/webhooks/__init__.py**

```python
"""Webhook handlers."""
from src.webhooks.sms import router as sms_router

__all__ = ["sms_router"]
```

**Step 5: Update src/main.py to include router**

```python
"""FastAPI application entrypoint."""
from fastapi import FastAPI

from src.webhooks.sms import router as sms_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Step 6: Run test to verify it passes**

Run: `pytest tests/test_webhooks.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/webhooks/ src/main.py tests/test_webhooks.py
git commit -m "feat: add SMS webhook handler"
```

---

## Task 8: Voice Webhook Handler

**Files:**
- Create: `src/webhooks/voice.py`
- Modify: `src/webhooks/__init__.py`
- Modify: `src/main.py`

**Step 1: Write failing test for voice webhook**

```python
# tests/test_voice.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


def test_voice_incoming_webhook():
    """Test incoming voice call webhook returns TwiML with stream."""
    from src.main import app
    client = TestClient(app)

    response = client.post("/webhook/voice/incoming")

    assert response.status_code == 200
    assert "Stream" in response.text or "Connect" in response.text
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_voice.py -v`
Expected: FAIL

**Step 3: Implement voice webhook**

```python
# src/webhooks/voice.py
"""Voice webhook handlers for Twilio + OpenAI Realtime."""
import asyncio
import base64
import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from twilio.twiml.voice_response import VoiceResponse, Connect

from src.config.loader import ConfigLoader
from src.storage.memory import MemoryWrapper

router = APIRouter()


@router.post("/webhook/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming voice call - connect to media stream."""
    response = VoiceResponse()

    # Add a brief greeting while connecting
    response.say("Connecting you to your coach.", voice="alice")

    # Connect to WebSocket for media streaming
    connect = Connect()
    host = request.headers.get("host", "localhost")
    protocol = "wss" if request.url.scheme == "https" else "ws"
    connect.stream(url=f"{protocol}://{host}/media-stream")
    response.append(connect)

    return str(response)


@router.post("/webhook/voice/outbound")
async def handle_outbound_call(request: Request):
    """Handle outbound voice call setup."""
    reason = request.query_params.get("reason", "check-in")

    response = VoiceResponse()
    response.say(f"Hey, this is your fitness coach calling about {reason}.", voice="alice")

    # Connect to media stream for conversation
    connect = Connect()
    host = request.headers.get("host", "localhost")
    protocol = "wss" if request.url.scheme == "https" else "ws"
    connect.stream(url=f"{protocol}://{host}/media-stream?reason={reason}")
    response.append(connect)

    return str(response)


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Handle bidirectional audio stream between Twilio and OpenAI Realtime."""
    await websocket.accept()

    config = ConfigLoader()
    personality = config.get_personality()
    user = config.get_user()

    # Load memories for context
    memory = MemoryWrapper(user_id=user.get("phone", "default").replace("+", ""))
    relevant_memories = memory.search("fitness coaching conversation", limit=20)

    instructions = f"""
{personality.get('prompt', 'You are a helpful fitness coach.')}

You are on a voice call with {user.get('name', 'the user')}.

What you remember about them:
{memory.format_memories(relevant_memories)}

Keep responses conversational and concise - this is a phone call.
"""

    transcript_parts = []

    try:
        # In production, this would connect to OpenAI Realtime API
        # For now, we'll handle the Twilio media stream events
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["event"] == "connected":
                print("Twilio media stream connected")

            elif data["event"] == "start":
                print(f"Stream started: {data.get('start', {})}")

            elif data["event"] == "media":
                # Audio data from Twilio (base64 encoded)
                # In production: forward to OpenAI Realtime API
                pass

            elif data["event"] == "stop":
                print("Stream stopped")
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        # Store conversation transcript in memory
        if transcript_parts:
            transcript = "\n".join(transcript_parts)
            memory.add(
                f"Voice conversation:\n{transcript}",
                metadata={"type": "voice_call"}
            )
```

**Step 4: Update src/webhooks/__init__.py**

```python
"""Webhook handlers."""
from src.webhooks.sms import router as sms_router
from src.webhooks.voice import router as voice_router

__all__ = ["sms_router", "voice_router"]
```

**Step 5: Update src/main.py**

```python
"""FastAPI application entrypoint."""
from fastapi import FastAPI

from src.webhooks.sms import router as sms_router
from src.webhooks.voice import router as voice_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)
app.include_router(voice_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Step 6: Run test to verify it passes**

Run: `pytest tests/test_voice.py -v`
Expected: PASS

**Step 7: Commit**

```bash
git add src/webhooks/voice.py src/webhooks/__init__.py src/main.py tests/test_voice.py
git commit -m "feat: add voice webhook handlers for Twilio media streaming"
```

---

## Task 9: Scheduler Endpoints

**Files:**
- Create: `src/scheduler/__init__.py`
- Create: `src/scheduler/checkins.py`
- Create: `src/scheduler/triggers.py`
- Modify: `src/main.py`

**Step 1: Write failing test for scheduler endpoints**

```python
# tests/test_scheduler.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


def test_daily_checkin_endpoint():
    """Test daily check-in cron endpoint."""
    with patch("src.scheduler.checkins.Runner") as mock_runner:
        with patch("src.scheduler.checkins.ConfigLoader") as mock_config:
            with patch("src.scheduler.checkins.MemoryWrapper") as mock_memory:
                with patch("src.scheduler.checkins.FirestoreClient") as mock_fs:
                    mock_config.return_value.get_personality.return_value = {"prompt": "test"}
                    mock_config.return_value.get_user.return_value = {"name": "Keith", "phone": "+1234"}
                    mock_memory.return_value.search.return_value = []
                    mock_fs.return_value.get_workouts.return_value = []
                    mock_fs.return_value.get_meals.return_value = []
                    mock_runner.run_sync.return_value.final_output = "Time to move!"

                    from src.main import app
                    client = TestClient(app)

                    response = client.post("/cron/daily-checkin")

                    assert response.status_code == 200
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scheduler.py -v`
Expected: FAIL

**Step 3: Implement checkins module**

```python
# src/scheduler/checkins.py
"""Daily check-in scheduler."""
from fastapi import APIRouter
from agents import Agent, Runner

from src.agent.tools import send_sms, log_workout, log_meal
from src.config.loader import ConfigLoader
from src.storage.firestore import FirestoreClient
from src.storage.memory import MemoryWrapper

router = APIRouter()


@router.post("/cron/daily-checkin")
async def daily_checkin():
    """Triggered by Cloud Scheduler for daily check-ins."""
    config = ConfigLoader()
    personality = config.get_personality()
    user = config.get_user()

    fs = FirestoreClient()
    memory = MemoryWrapper(user_id=user.get("phone", "default").replace("+", ""))

    # Gather context
    recent_workouts = fs.get_workouts(days=3)
    recent_meals = fs.get_meals(days=1)
    relevant_memories = memory.search("recent activity and mood", limit=10)

    # Format context
    workout_summary = f"{len(recent_workouts)} workouts in last 3 days"
    if recent_workouts:
        workout_summary += f": {', '.join(w.get('type', 'workout') for w in recent_workouts[:3])}"

    meal_summary = f"{len(recent_meals)} meals logged today"

    # Create check-in agent
    agent = Agent(
        name="CheckInAgent",
        instructions=f"""
{personality.get('prompt', 'You are a fitness coach.')}

You are doing a scheduled check-in with {user.get('name', 'the user')}.

Their recent activity:
- Workouts: {workout_summary}
- Nutrition: {meal_summary}

What you remember about them:
{memory.format_memories(relevant_memories)}

Send them a brief, personalized check-in SMS. Be the personality described above.
Use the send_sms tool to send the message.
""",
        tools=[send_sms],
        model="gpt-4o",
    )

    result = Runner.run_sync(agent, "Send the daily check-in message.")

    return {"status": "ok", "result": result.final_output}
```

**Step 4: Implement triggers module**

```python
# src/scheduler/triggers.py
"""Event-based trigger checker."""
from datetime import datetime, timedelta
from fastapi import APIRouter
from agents import Agent, Runner

from src.agent.tools import send_sms, initiate_call
from src.config.loader import ConfigLoader
from src.storage.firestore import FirestoreClient
from src.storage.memory import MemoryWrapper

router = APIRouter()


@router.post("/cron/check-triggers")
async def check_triggers():
    """Check and execute event-based triggers."""
    config = ConfigLoader()
    triggers_config = config.get_triggers()
    personality = config.get_personality()
    user = config.get_user()

    fs = FirestoreClient()
    memory = MemoryWrapper(user_id=user.get("phone", "default").replace("+", ""))

    triggered = []

    for rule in triggers_config.get("rules", []):
        event = rule.get("event")

        if event == "no_workout":
            last_workout = fs.get_last_workout_date()
            if last_workout:
                if hasattr(last_workout, 'timestamp'):
                    last_dt = datetime.fromtimestamp(last_workout.timestamp())
                else:
                    last_dt = last_workout
                days_since = (datetime.now() - last_dt).days
            else:
                days_since = 999  # No workouts ever

            if days_since >= rule.get("days", 2):
                triggered.append({
                    "rule": rule,
                    "context": {"days_since_workout": days_since}
                })

        elif event == "calorie_deficit":
            meals = fs.get_meals(days=1)
            total_cals = sum(m.get("calories", 0) for m in meals)
            target = 2000  # Could be configurable
            deficit = target - total_cals

            if deficit > rule.get("threshold", 500):
                triggered.append({
                    "rule": rule,
                    "context": {"calorie_deficit": deficit, "total_today": total_cals}
                })

    # Execute triggered actions
    for trigger in triggered:
        await execute_trigger(trigger, personality, user, memory)

    return {"status": "ok", "triggers_fired": len(triggered)}


async def execute_trigger(trigger: dict, personality: dict, user: dict, memory: MemoryWrapper):
    """Execute a triggered action."""
    rule = trigger["rule"]
    context = trigger["context"]
    action = rule.get("action", "sms")

    relevant_memories = memory.search(str(context), limit=10)

    tools = [send_sms] if action == "sms" else [initiate_call]

    agent = Agent(
        name="TriggerAgent",
        instructions=f"""
{personality.get('prompt', 'You are a fitness coach.')}

A trigger has been activated for {user.get('name', 'the user')}.

Trigger: {rule.get('event')}
Context: {context}

What you remember about them:
{memory.format_memories(relevant_memories)}

{"Send them an SMS" if action == "sms" else "Call them"} about this.
Be the personality described above. Be direct but motivating.
""",
        tools=tools,
        model="gpt-4o",
    )

    Runner.run_sync(agent, f"Execute the {action} for this trigger.")
```

**Step 5: Create src/scheduler/__init__.py**

```python
"""Scheduler modules."""
from src.scheduler.checkins import router as checkins_router
from src.scheduler.triggers import router as triggers_router

__all__ = ["checkins_router", "triggers_router"]
```

**Step 6: Update src/main.py**

```python
"""FastAPI application entrypoint."""
from fastapi import FastAPI

from src.webhooks.sms import router as sms_router
from src.webhooks.voice import router as voice_router
from src.scheduler.checkins import router as checkins_router
from src.scheduler.triggers import router as triggers_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)
app.include_router(voice_router)
app.include_router(checkins_router)
app.include_router(triggers_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
```

**Step 7: Run test to verify it passes**

Run: `pytest tests/test_scheduler.py -v`
Expected: PASS

**Step 8: Commit**

```bash
git add src/scheduler/ src/main.py tests/test_scheduler.py
git commit -m "feat: add scheduler endpoints for check-ins and triggers"
```

---

## Task 10: Setup Wizard

**Files:**
- Create: `setup.py`
- Create: `scripts/seed_firestore.py`

**Step 1: Create setup wizard**

```python
# setup.py
"""Interactive setup wizard for Layz."""
import json
import os
import sys
from pathlib import Path


def main():
    print("\n🏋️ Layz - Fitness Accountability Agent Setup\n")

    env_vars = {}

    # Step 1: OpenAI
    print("Step 1/5: OpenAI")
    api_key = input("  Enter your OpenAI API key: ").strip()
    if not api_key.startswith("sk-"):
        print("  ⚠️  Warning: API key doesn't look like an OpenAI key")
    env_vars["OPENAI_API_KEY"] = api_key
    print("  ✓ OpenAI configured\n")

    # Step 2: Twilio
    print("Step 2/5: Twilio")
    env_vars["TWILIO_ACCOUNT_SID"] = input("  Enter Account SID: ").strip()
    env_vars["TWILIO_AUTH_TOKEN"] = input("  Enter Auth Token: ").strip()
    env_vars["TWILIO_PHONE_NUMBER"] = input("  Enter your Twilio phone number (e.g., +1234567890): ").strip()
    print("  ✓ Twilio configured\n")

    # Step 3: Firebase
    print("Step 3/5: Firebase")
    env_vars["GOOGLE_CLOUD_PROJECT"] = input("  Enter GCP Project ID: ").strip()
    cred_path = input("  Path to service account JSON (or press Enter to use ADC): ").strip()
    if cred_path:
        env_vars["FIREBASE_SERVICE_ACCOUNT"] = cred_path
    print("  ✓ Firebase configured\n")

    # Step 4: Mem0
    print("Step 4/5: Mem0")
    mem0_key = input("  Enter Mem0 API key (or press Enter for self-hosted): ").strip()
    if mem0_key:
        env_vars["MEM0_API_KEY"] = mem0_key
    print("  ✓ Mem0 configured\n")

    # Step 5: User Info
    print("Step 5/5: Your Info")
    env_vars["USER_PHONE_NUMBER"] = input("  Your phone number (e.g., +1234567890): ").strip()
    env_vars["USER_NAME"] = input("  Your name: ").strip()
    env_vars["USER_TIMEZONE"] = input("  Timezone (default: America/Los_Angeles): ").strip() or "America/Los_Angeles"
    print("  ✓ User info configured\n")

    # Write .env file
    env_path = Path(".env")
    with open(env_path, "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print(f"✓ Configuration saved to {env_path}")

    # Seed Firestore
    print("\nSeeding Firestore with default configs...")
    try:
        from scripts.seed_firestore import seed_defaults
        seed_defaults()
        print("✓ Firestore seeded with default configs")
    except Exception as e:
        print(f"⚠️  Could not seed Firestore: {e}")
        print("   Run 'python scripts/seed_firestore.py' manually after setting up credentials")

    print("\n" + "="*50)
    print("Setup complete!")
    print("\nNext steps:")
    print("  Run locally:     uvicorn src.main:app --reload")
    print("  Run with Docker: docker-compose up")
    print("  Deploy:          ./scripts/deploy.sh")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
```

**Step 2: Create Firestore seeder**

```python
# scripts/seed_firestore.py
"""Seed Firestore with default configuration."""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def seed_defaults():
    """Seed Firestore with defaults from configs/defaults.json."""
    import firebase_admin
    from firebase_admin import credentials, firestore

    # Initialize Firebase
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()

    db = firestore.client()

    # Load defaults
    defaults_path = Path(__file__).parent.parent / "configs" / "defaults.json"
    with open(defaults_path) as f:
        defaults = json.load(f)

    # Seed each config
    for config_name, config_value in defaults.items():
        doc_ref = db.collection("config").document(config_name)

        # Check if already exists
        if doc_ref.get().exists:
            print(f"  Config '{config_name}' already exists, skipping")
            continue

        doc_ref.set(config_value)
        print(f"  ✓ Seeded '{config_name}'")

    # Update user config with env vars if present
    user_phone = os.getenv("USER_PHONE_NUMBER")
    user_name = os.getenv("USER_NAME")
    if user_phone or user_name:
        db.collection("config").document("user").update({
            **({"phone": user_phone} if user_phone else {}),
            **({"name": user_name} if user_name else {}),
        })
        print("  ✓ Updated user config with env vars")


if __name__ == "__main__":
    print("Seeding Firestore with default configs...")
    seed_defaults()
    print("Done!")
```

**Step 3: Commit**

```bash
git add setup.py scripts/seed_firestore.py
git commit -m "feat: add setup wizard and Firestore seeder"
```

---

## Task 11: Deployment Scripts

**Files:**
- Create: `scripts/deploy.sh`
- Create: `docker-compose.yml`
- Create: `scheduler.yaml`

**Step 1: Create deploy script**

```bash
#!/bin/bash
# scripts/deploy.sh
# Deploy Layz to Cloud Run

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
SERVICE_NAME=${SERVICE_NAME:-layz}

echo "🚀 Deploying Layz to Cloud Run..."
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"

# Build and push container
echo "\n📦 Building container..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "\n🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --min-instances 1 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
echo "\n✅ Deployed to: $SERVICE_URL"

# Deploy Cloud Scheduler jobs
echo "\n⏰ Deploying Cloud Scheduler jobs..."

# Morning check-in
gcloud scheduler jobs create http layz-morning-checkin \
  --location $REGION \
  --schedule "0 7 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-morning-checkin \
  --location $REGION \
  --schedule "0 7 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin"

# Evening check-in
gcloud scheduler jobs create http layz-evening-checkin \
  --location $REGION \
  --schedule "0 20 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-evening-checkin \
  --location $REGION \
  --schedule "0 20 * * *" \
  --uri "$SERVICE_URL/cron/daily-checkin"

# Trigger checker (hourly)
gcloud scheduler jobs create http layz-trigger-check \
  --location $REGION \
  --schedule "0 * * * *" \
  --uri "$SERVICE_URL/cron/check-triggers" \
  --http-method POST \
  --oidc-service-account-email "$PROJECT_ID@appspot.gserviceaccount.com" \
  2>/dev/null || gcloud scheduler jobs update http layz-trigger-check \
  --location $REGION \
  --schedule "0 * * * *" \
  --uri "$SERVICE_URL/cron/check-triggers"

echo "\n✅ Deployment complete!"
echo "\nNext steps:"
echo "  1. Configure Twilio webhook: $SERVICE_URL/webhook/sms"
echo "  2. Configure Twilio voice webhook: $SERVICE_URL/webhook/voice/incoming"
```

**Step 2: Create docker-compose.yml for local dev**

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
    env_file:
      - .env
    environment:
      - GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
    volumes:
      - ./src:/app/src
      - ./configs:/app/configs
    command: uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload
```

**Step 3: Make deploy script executable and commit**

```bash
chmod +x scripts/deploy.sh
git add scripts/deploy.sh docker-compose.yml
git commit -m "feat: add deployment scripts and docker-compose"
```

---

## Task 12: README and Final Polish

**Files:**
- Create: `README.md`

**Step 1: Create comprehensive README**

```markdown
# Layz - Personal Fitness Accountability Agent

A personal fitness accountability agent that keeps you on track with your health goals through SMS and voice calls.

## Features

- 📱 **SMS Communication** - Text your coach about workouts and meals
- 📞 **Voice Calls** - Get calls (or make them) for real-time coaching
- 🧠 **Memory** - Remembers your preferences and history
- ⏰ **Proactive Check-ins** - Daily messages to keep you accountable
- 🚨 **Smart Triggers** - Calls you if you've been slacking
- 🎭 **Configurable Personality** - Sarcastic drill sergeant or supportive friend

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- Twilio account with phone number
- Google Cloud project with Firestore
- Mem0 API key (optional)

### Setup

```bash
# Clone the repo
git clone https://github.com/youruser/layz.git
cd layz

# Install dependencies
pip install -e .

# Run setup wizard
python setup.py
```

### Run Locally

```bash
# With uvicorn
uvicorn src.main:app --reload

# Or with Docker
docker-compose up
```

### Deploy to Cloud Run

```bash
./scripts/deploy.sh
```

## Configuration

All configuration is stored in Firestore and can be modified without code changes:

### Personality

Switch between personalities in Firestore `config/personality`:

```json
{
  "active": "sarcastic-drill-sergeant",
  "presets": {
    "sarcastic-drill-sergeant": {
      "prompt": "You are a sarcastic drill sergeant...",
      "voice_id": "ash"
    }
  }
}
```

### Schedule

Configure check-in times in `config/schedule`:

```json
{
  "timezone": "America/Los_Angeles",
  "daily_checkins": ["07:00", "20:00"]
}
```

### Triggers

Configure event-based triggers in `config/triggers`:

```json
{
  "rules": [
    {"event": "no_workout", "days": 2, "action": "sms"},
    {"event": "no_workout", "days": 4, "action": "call"}
  ]
}
```

## Architecture

```
┌─────────────────┐
│   Your Phone    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Twilio      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│        Cloud Run (FastAPI)      │
│  ┌───────────────────────────┐  │
│  │   OpenAI Agents SDK       │  │
│  │   + Function Tools        │  │
│  └───────────────────────────┘  │
└──────┬─────────┬────────┬───────┘
       │         │        │
       ▼         ▼        ▼
    Mem0    Firestore   OpenAI
```

## License

MIT
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project Scaffolding | pyproject.toml, src/main.py, Dockerfile |
| 2 | Firestore Storage | src/storage/firestore.py |
| 3 | Config Loader | src/config/loader.py, configs/defaults.json |
| 4 | Mem0 Memory | src/storage/memory.py |
| 5 | Agent Tools | src/agent/tools/*.py |
| 6 | Core Agent | src/agent/coach.py |
| 7 | SMS Webhook | src/webhooks/sms.py |
| 8 | Voice Webhook | src/webhooks/voice.py |
| 9 | Scheduler | src/scheduler/*.py |
| 10 | Setup Wizard | setup.py, scripts/seed_firestore.py |
| 11 | Deployment | scripts/deploy.sh, docker-compose.yml |
| 12 | Documentation | README.md |

Total: ~12 tasks, each with clear TDD steps and commits.
