# Layz - Fitness Accountability Agent

**Repository:** https://github.com/Khowabunga/layz

## Project Overview

Personal fitness accountability agent that communicates via SMS and voice calls, tracks workouts and nutrition, and proactively keeps you accountable.

## Tech Stack

- Python 3.11+, FastAPI, uvicorn
- OpenAI Agents SDK (gpt-4o)
- Twilio (SMS + Voice)
- Firebase Admin SDK (Firestore)
- Mem0 (semantic memory)
- Docker, Cloud Run, Cloud Scheduler

## Key Commands

```bash
# Run locally
uvicorn src.main:app --reload

# Run tests
pytest

# Deploy to Cloud Run
./scripts/deploy.sh
```

## Project Structure

- `src/agent/` - Agent definition and tools
- `src/webhooks/` - Twilio SMS and voice handlers
- `src/scheduler/` - Cron endpoints for check-ins
- `src/storage/` - Firestore and Mem0 clients
- `src/config/` - Configuration loader
- `configs/defaults.json` - Default personality and schedule config
