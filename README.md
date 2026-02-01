# Layz - Personal Fitness Accountability Agent

A personal fitness accountability agent that keeps you on track with your health goals through SMS and voice calls.

## Features

- **SMS Communication** - Text your coach about workouts and meals
- **Voice Calls** - Get calls (or make them) for real-time coaching
- **Memory** - Remembers your preferences and history
- **Proactive Check-ins** - Daily messages to keep you accountable
- **Smart Triggers** - Calls you if you've been slacking
- **Configurable Personality** - Sarcastic drill sergeant or supportive friend

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
+-------------------+
|   Your Phone      |
+---------+---------+
          |
          v
+-------------------+
|     Twilio        |
+---------+---------+
          |
          v
+---------------------------------+
|      Cloud Run (FastAPI)        |
|  +---------------------------+  |
|  |   OpenAI Agents SDK       |  |
|  |   + Function Tools        |  |
|  +---------------------------+  |
+-------+----------+------+-------+
        |          |      |
        v          v      v
      Mem0    Firestore  OpenAI
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/webhook/sms` | POST | Twilio SMS webhook |
| `/webhook/voice/incoming` | POST | Twilio voice webhook |
| `/webhook/voice/outbound` | POST | Outbound call setup |
| `/cron/daily-checkin` | POST | Daily check-in trigger |
| `/cron/check-triggers` | POST | Event trigger checker |

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src
```

## License

MIT
