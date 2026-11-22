"""
OmniMind AI – Multimodal Intelligence Assistant Backend.
FastAPI Application Entry Point.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import db
from .routers.chat import router as chat_router
from .routers.conversations import router as conversations_router
from .routers.documents import router as documents_router
from .routers.providers import router as providers_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("omnimind.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initializes database and resources on startup."""
    logger.info("Initializing OmniMind AI Backend...")
    try:
        db.init_db()
    except Exception as e:
        logger.error("Database initialization error during startup: %s", e)
    yield
    logger.info("OmniMind AI Backend shutdown complete.")


app = FastAPI(
    title="OmniMind AI – Multimodal Intelligence Assistant",
    description="Multimodal AI Assistant supporting Text, Vision, Audio, PDF/DOCX processing and RAG across Gemini, OpenAI, and Hugging Face.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(providers_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(conversations_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to OmniMind AI – Multimodal Intelligence Assistant API",
        "documentation": "/docs",
        "health": "/api/health",
        "providers": "/api/providers"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.BACKEND_PORT, reload=True)
