"""
Main application entry point.
Initializes the FastAPI server and mounts the API routes.
"""
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.routes import router
from app.core.logger import get_logger

logger = get_logger(__name__)

# Initialized FastAPI
app = FastAPI(
    title="Autonomous RAG Debugger SaaS API >.<",
    description="SaaS Backend for detection hallucination at sistem LLM and RAG yall ^^",
    version="0.0.1:beta"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def serve_homepage(request: Request):
    """Serves a simple homepage for testing."""
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/health")
def health_check():
    """Endpoint to ensure whether server on or off"""
    return {
        "status": "Activate",
        "message": "RAG Debugger Engine is Running. open endpoints /docs for try API >.<",
    }

if __name__ == "__main__":
    logger.info("Running FastAPI Server...")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)