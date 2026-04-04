"""
Main application entry point.
Initializes the FastAPI server and mounts the API routes.
"""
import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from app.core.logger import get_logger

logger = get_logger(__name__)

# Initialized FastAPI
app = FastAPI(
    title="Autonomous RAG Debugger SaaS API >.<",
    description="SaaS Backend for detection hallucination at sistem LLM and RAG yall ^^",
    version="0.0.1:beta"
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    """Endpoint to ensure whether server on or off"""
    return {
        "status": "Activate",
        "message": "RAG Debugger Engine is Running. open endpoints /docs for try API >.<",
    }

if __name__ == "__main__":
    logger.info("Running FastAPI Server...")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)