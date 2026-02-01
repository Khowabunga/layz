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
