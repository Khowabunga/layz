"""FastAPI application entrypoint."""
from fastapi import FastAPI

from src.webhooks.sms import router as sms_router
from src.webhooks.voice import router as voice_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)
app.include_router(voice_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
