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
