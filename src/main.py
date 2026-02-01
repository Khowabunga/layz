"""FastAPI application entrypoint."""
from fastapi import FastAPI

from src.webhooks.sms import router as sms_router

app = FastAPI(title="Layz", description="Personal fitness accountability agent")

# Include routers
app.include_router(sms_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
