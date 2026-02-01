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
