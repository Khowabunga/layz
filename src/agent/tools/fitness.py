"""Fitness tracking tools for the agent."""
from agents import function_tool

from src.storage.firestore import FirestoreClient


def _log_workout(description: str) -> str:
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


def _get_fitness_summary(days: int = 7) -> str:
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


def _get_last_workout() -> str:
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


# Create function tools for agent use
log_workout = function_tool(_log_workout)
get_fitness_summary = function_tool(_get_fitness_summary)
get_last_workout = function_tool(_get_last_workout)
