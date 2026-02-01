"""Communication tools for the agent."""
import os

from agents import function_tool
from twilio.rest import Client


def _get_twilio_client() -> Client:
    """Get configured Twilio client."""
    return Client(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
    )


def _send_sms(message: str) -> str:
    """Send an SMS message to the user.

    Args:
        message: The message to send
    """
    client = _get_twilio_client()

    msg = client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        to=os.getenv("USER_PHONE_NUMBER"),
    )

    return f"SMS sent successfully (SID: {msg.sid})"


def _initiate_call(reason: str) -> str:
    """Initiate a voice call to the user.

    Args:
        reason: The reason for calling (used in the call setup)
    """
    client = _get_twilio_client()

    # The webhook URL will handle the actual voice conversation
    base_url = os.getenv("BASE_URL", "https://your-domain.com")

    call = client.calls.create(
        to=os.getenv("USER_PHONE_NUMBER"),
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        url=f"{base_url}/webhook/voice/outbound?reason={reason}",
    )

    return f"Call initiated (SID: {call.sid})"


# Create function tools for agent use
send_sms = function_tool(_send_sms)
initiate_call = function_tool(_initiate_call)
