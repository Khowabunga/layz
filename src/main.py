"""FastAPI application entrypoint."""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from src.webhooks.sms import router as sms_router
from src.webhooks.voice import router as voice_router
from src.scheduler.checkins import router as checkins_router
from src.scheduler.triggers import router as triggers_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)
app.include_router(voice_router)
app.include_router(checkins_router)
app.include_router(triggers_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
