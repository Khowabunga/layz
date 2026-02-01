"""Voice webhook handlers for Twilio + OpenAI Realtime."""
import asyncio
import base64
import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request
from twilio.twiml.voice_response import VoiceResponse, Connect

from src.config.loader import ConfigLoader
from src.storage.memory import MemoryWrapper

router = APIRouter()


@router.post("/webhook/voice/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming voice call - connect to media stream."""
    response = VoiceResponse()

    # Add a brief greeting while connecting
    response.say("Connecting you to your coach.", voice="alice")

    # Connect to WebSocket for media streaming
    connect = Connect()
    host = request.headers.get("host", "localhost")
    protocol = "wss" if request.url.scheme == "https" else "ws"
    connect.stream(url=f"{protocol}://{host}/media-stream")
    response.append(connect)

    return str(response)


@router.post("/webhook/voice/outbound")
async def handle_outbound_call(request: Request):
    """Handle outbound voice call setup."""
    reason = request.query_params.get("reason", "check-in")

    response = VoiceResponse()
    response.say(f"Hey, this is your fitness coach calling about {reason}.", voice="alice")

    # Connect to media stream for conversation
    connect = Connect()
    host = request.headers.get("host", "localhost")
    protocol = "wss" if request.url.scheme == "https" else "ws"
    connect.stream(url=f"{protocol}://{host}/media-stream?reason={reason}")
    response.append(connect)

    return str(response)


@router.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    """Handle bidirectional audio stream between Twilio and OpenAI Realtime."""
    await websocket.accept()

    config = ConfigLoader()
    personality = config.get_personality()
    user = config.get_user()

    # Load memories for context
    memory = MemoryWrapper(user_id=user.get("phone", "default").replace("+", ""))
    relevant_memories = memory.search("fitness coaching conversation", limit=20)

    instructions = f"""
{personality.get('prompt', 'You are a helpful fitness coach.')}

You are on a voice call with {user.get('name', 'the user')}.

What you remember about them:
{memory.format_memories(relevant_memories)}

Keep responses conversational and concise - this is a phone call.
"""

    transcript_parts = []

    try:
        # In production, this would connect to OpenAI Realtime API
        # For now, we'll handle the Twilio media stream events
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            if data["event"] == "connected":
                print("Twilio media stream connected")

            elif data["event"] == "start":
                print(f"Stream started: {data.get('start', {})}")

            elif data["event"] == "media":
                # Audio data from Twilio (base64 encoded)
                # In production: forward to OpenAI Realtime API
                pass

            elif data["event"] == "stop":
                print("Stream stopped")
                break

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        # Store conversation transcript in memory
        if transcript_parts:
            transcript = "\n".join(transcript_parts)
            memory.add(
                f"Voice conversation:\n{transcript}",
                metadata={"type": "voice_call"}
            )
