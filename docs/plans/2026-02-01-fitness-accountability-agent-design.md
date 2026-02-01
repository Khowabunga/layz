# Fitness Accountability Agent - Design Document

## Overview

A personal fitness accountability agent that communicates via SMS and voice calls, tracks workouts and nutrition, and proactively keeps you accountable with a configurable personality (starting with sarcastic drill sergeant).

## Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | OpenAI Agents SDK (Python) |
| Voice | OpenAI Realtime API + Twilio |
| SMS | Twilio |
| Memory | Mem0 |
| Storage | Firestore |
| Hosting | Cloud Run (min instances = 1) |
| Scheduling | Cloud Scheduler |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         YOUR PHONE                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TWILIO                                  │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD RUN (Python)                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              OPENAI AGENTS SDK (Core)                     │  │
│  │                                                           │  │
│  │   Agent: "Fitness Coach"                                  │  │
│  │   ├── @tool log_workout()                                 │  │
│  │   ├── @tool log_meal()                                    │  │
│  │   ├── @tool get_fitness_summary()                         │  │
│  │   ├── @tool get_nutrition_summary()                       │  │
│  │   ├── @tool search_recipes()                              │  │
│  │   ├── @tool send_sms()                                    │  │
│  │   └── @tool initiate_call()                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└────┬────────────────┬────────────────┬──────────────────────────┘
     ▼                ▼                ▼
   Mem0          Firestore          OpenAI
```

### Flow

1. You text or call your Twilio number
2. Twilio sends webhook to Cloud Run
3. Agent processes with context from Mem0 + Firestore
4. Agent responds via Twilio (text or voice)
5. Cloud Scheduler triggers proactive outreach

## Firestore Data Model

```
firestore/
│
├── config/                         # All modular settings
│   ├── personality                 # Active personality ID + available presets
│   │   {
│   │     active: "sarcastic-drill-sergeant",
│   │     presets: {
│   │       "sarcastic-drill-sergeant": {
│   │         prompt: "You are a sarcastic drill sergeant...",
│   │         voice_id: "ash"
│   │       },
│   │       "supportive-friend": { ... }
│   │     }
│   │   }
│   │
│   ├── schedule                    # Proactive check-in times
│   │   {
│   │     timezone: "America/Los_Angeles",
│   │     daily_checkins: ["07:00", "20:00"]
│   │   }
│   │
│   ├── triggers                    # Event-based rules
│   │   {
│   │     rules: [
│   │       { event: "no_workout", days: 2, action: "sms" },
│   │       { event: "no_workout", days: 4, action: "call" },
│   │       { event: "calorie_deficit", threshold: 500, action: "sms" }
│   │     ]
│   │   }
│   │
│   └── user                        # Your basic info
│       {
│         phone: "+1234567890",
│         name: "Keith"
│       }
│
├── logs/
│   ├── workouts/                   # Workout entries
│   │   └── {auto-id}
│   │       {
│   │         timestamp: ...,
│   │         type: "push",
│   │         duration_mins: 45,
│   │         exercises: [...],
│   │         notes: "felt strong",
│   │         raw_input: "Did push day, bench 185x5x3..."
│   │       }
│   │
│   └── nutrition/                  # Meal entries
│       └── {auto-id}
│           {
│             timestamp: ...,
│             meal_type: "lunch",
│             calories: 650,
│             protein: 45,
│             carbs: 70,
│             fat: 18,
│             description: "Chipotle bowl",
│             raw_input: "Had a chipotle bowl with..."
│           }
│
└── conversations/                  # Optional: conversation history backup
    └── {date}/
        └── {auto-id}
```

## Agent & Tools

```python
from agents import Agent, function_tool, Runner

@function_tool
def log_workout(description: str) -> str:
    """Parse natural language workout and store in Firestore."""

@function_tool
def log_meal(description: str) -> str:
    """Parse natural language meal and store with macro estimates."""

@function_tool
def get_fitness_summary(days: int = 7) -> str:
    """Get workout summary for past N days from Firestore."""

@function_tool
def get_nutrition_summary(days: int = 1) -> str:
    """Get calorie/macro summary for past N days."""

@function_tool
def search_recipes(criteria: str) -> str:
    """Search for recipes matching criteria using web search."""

@function_tool
def send_sms(message: str) -> str:
    """Send SMS to user via Twilio."""

@function_tool
def initiate_call(reason: str) -> str:
    """Initiate outbound voice call to user."""

fitness_coach = Agent(
    name="FitnessCoach",
    instructions=load_personality_prompt(),
    tools=[log_workout, log_meal, get_fitness_summary,
           get_nutrition_summary, search_recipes, send_sms, initiate_call],
    model="gpt-4o"
)
```

## Mem0 Integration

Both SMS and voice conversations integrate with Mem0:

```python
from mem0 import Memory

memory = Memory()

async def chat(user_message: str) -> str:
    # Retrieve relevant memories
    context = memory.search(user_message, user_id="keith")

    # Run agent with memory context injected
    result = await Runner.run(
        fitness_coach,
        messages=[{"role": "user", "content": user_message}],
        context={"memories": context}
    )

    # Store new memories from conversation
    memory.add(user_message, user_id="keith")
    memory.add(result.output, user_id="keith")

    return result.output
```

Voice conversations load memories before the session and store the transcript after:

```python
@app.websocket("/media-stream")
async def media_stream(websocket):
    # Load memories BEFORE starting session
    relevant_memories = memory.search(
        "fitness coaching conversation",
        user_id="keith",
        limit=20
    )

    # Inject memories into system prompt
    personality = load_personality_prompt()
    instructions = f"""
    {personality}

    ## What you remember about this user:
    {format_memories(relevant_memories)}
    """

    async with openai_realtime_session(
        model="gpt-4o-realtime-preview",
        voice=load_voice_from_config(),
        instructions=instructions,
        tools=[log_workout, log_meal, get_fitness_summary, ...]
    ) as session:
        transcript = await bridge_audio_streams(websocket, session)

        # Store memories AFTER call ends
        memory.add(
            f"Voice conversation:\n{transcript}",
            user_id="keith",
            metadata={"type": "voice_call", "timestamp": now()}
        )
```

## Webhooks & Voice

### SMS Handling

```python
@app.post("/webhook/sms")
async def handle_sms(request: Request):
    form = await request.form()
    user_message = form.get("Body")
    response = await chat(user_message)
    return TwiMLResponse(response)
```

### Voice Handling

```python
@app.post("/webhook/voice/incoming")
async def handle_incoming_call(request: Request):
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"wss://{YOUR_DOMAIN}/media-stream")
    response.append(connect)
    return str(response)

@app.websocket("/media-stream")
async def media_stream(websocket):
    # Bridge Twilio audio <-> OpenAI Realtime (with Mem0)
    ...

def initiate_outbound_call(reason: str):
    client = TwilioClient()
    client.calls.create(
        to=USER_PHONE,
        from_=TWILIO_NUMBER,
        url=f"https://{YOUR_DOMAIN}/webhook/voice/outbound?reason={reason}"
    )
```

## Proactive Outreach

### Cloud Scheduler Jobs

```yaml
jobs:
  - name: morning-checkin
    schedule: "0 7 * * *"
    uri: /cron/daily-checkin

  - name: evening-checkin
    schedule: "0 20 * * *"
    uri: /cron/daily-checkin

  - name: trigger-check
    schedule: "0 * * * *"
    uri: /cron/check-triggers
```

### Daily Check-in

```python
@app.post("/cron/daily-checkin")
async def daily_checkin():
    memories = memory.search("recent activity and mood", user_id="keith", limit=10)
    nutrition = get_nutrition_summary(days=1)
    workouts = get_fitness_summary(days=3)

    prompt = f"""
    Time for a scheduled check-in.

    Recent nutrition: {nutrition}
    Recent workouts: {workouts}
    Memories: {format_memories(memories)}

    Send an appropriate check-in SMS. Be the sarcastic drill sergeant.
    """

    result = await Runner.run(fitness_coach, messages=[{"role": "system", "content": prompt}])
```

### Event-Based Triggers

```python
@app.post("/cron/check-triggers")
async def check_triggers():
    triggers = load_trigger_config()

    for rule in triggers["rules"]:
        if rule["event"] == "no_workout":
            last_workout = get_last_workout_date()
            days_since = (now() - last_workout).days

            if days_since >= rule["days"]:
                await execute_trigger_action(rule, days_since)
```

## Project Structure

```
layz/
├── README.md
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── setup.py                      # CLI wizard for first-time setup
│
├── src/
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entrypoint
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── coach.py              # Agent definition
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── fitness.py        # log_workout, get_fitness_summary
│   │   │   ├── nutrition.py      # log_meal, get_nutrition_summary
│   │   │   ├── recipes.py        # search_recipes
│   │   │   └── comms.py          # send_sms, initiate_call
│   │   └── prompts/
│   │       └── personalities.py  # Load/format personality prompts
│   │
│   ├── webhooks/
│   │   ├── __init__.py
│   │   ├── sms.py                # SMS webhook handler
│   │   └── voice.py              # Voice + WebSocket handlers
│   │
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── checkins.py           # Daily check-in logic
│   │   └── triggers.py           # Event-based trigger evaluation
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── firestore.py          # Firestore client + helpers
│   │   └── memory.py             # Mem0 wrapper
│   │
│   └── config/
│       ├── __init__.py
│       └── loader.py             # Load configs from Firestore
│
├── configs/
│   └── defaults.json             # Default configs seeded on first run
│
├── scripts/
│   ├── deploy.sh                 # Deploy to Cloud Run
│   └── seed_firestore.py         # Initialize Firestore with defaults
│
└── tests/
    └── ...
```

## Environment Variables

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
```

## Setup Flow

```bash
git clone https://github.com/youruser/layz.git
cd layz
pip install -r requirements.txt
python setup.py  # Interactive wizard
```

The setup wizard walks through:
1. OpenAI API key
2. Twilio credentials and phone number
3. Firebase/GCP project setup
4. Mem0 API key
5. User info (phone, name, timezone)

## Key Design Principles

1. **Modularity** - Personality, schedule, triggers, and voice all configurable in Firestore without code changes
2. **Single interface** - One phone number for text + calls (bidirectional)
3. **Natural language** - Log workouts and meals conversationally, agent extracts structured data
4. **Proactive + reactive** - Scheduled check-ins plus event-based triggers that escalate to calls
5. **Memory across channels** - Mem0 integrates with both SMS and voice, memories flow between them
6. **Open-source friendly** - Setup wizard, clear docs, env-based config
