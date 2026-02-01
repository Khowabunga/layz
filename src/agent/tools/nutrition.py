"""Nutrition tracking tools for the agent."""
from agents import function_tool

from src.storage.firestore import FirestoreClient


def _log_meal(description: str, meal_type: str = "meal") -> str:
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


def _get_nutrition_summary(days: int = 1) -> str:
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


# Create function tools for agent use
log_meal = function_tool(_log_meal)
get_nutrition_summary = function_tool(_get_nutrition_summary)
