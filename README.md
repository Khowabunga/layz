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

### Google Cloud Setup

Before running the app, you need to set up Google Cloud:

1. **Create a Google Cloud Project** (or use an existing one)
   ```bash
   gcloud projects create YOUR_PROJECT_ID
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Enable the Firestore API**

   Visit: https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=YOUR_PROJECT_ID

3. **Create a Firestore Database**
   ```bash
   gcloud firestore databases create --location=nam5 --type=firestore-native
   ```
   Or via console: https://console.cloud.google.com/datastore/setup?project=YOUR_PROJECT_ID

   - Choose **Native mode** (not Datastore mode)
   - Pick a region (e.g., `nam5` for US multi-region)

4. **Authenticate with Application Default Credentials**
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```

### Setup

```bash
# Clone the repo
git clone https://github.com/Khowabunga/layz.git
cd layz

# Install dependencies
pip install -e .

# Run setup wizard (creates .env file)
python setup.py

# Seed Firestore with default configs
python scripts/seed_firestore.py
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
