"""FastAPI application entrypoint."""
from fastapi import FastAPI

app = FastAPI(title="Layz", description="Personal fitness accountability agent")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
