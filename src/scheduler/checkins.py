"""Daily check-in scheduler."""
from fastapi import APIRouter
from agents import Agent, Runner

from src.agent.tools import send_sms
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
