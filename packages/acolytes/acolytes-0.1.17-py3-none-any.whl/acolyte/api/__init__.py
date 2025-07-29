"""
ACOLYTE API Module
Basic FastAPI application for the ACOLYTE backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import routers from submodules
from acolyte.api.index import router as index_router
from acolyte.api.openai import router as openai_router
from acolyte.api.dream import router as dream_router
from acolyte.api.health import router as health_router
from acolyte.api.websockets.progress import router as ws_progress_router

# Core imports for lifespan
from acolyte.core.logging import logger

__all__ = ["app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("ACOLYTE API starting up")
    yield
    # Shutdown
    logger.info("ACOLYTE API shutting down")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ACOLYTE API",
    description="Local AI Programming Assistant API",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Solo localhost en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ACOLYTE API is running"}


# Include all routers
app.include_router(openai_router, prefix="/v1", tags=["OpenAI"])
app.include_router(index_router, prefix="/api/index", tags=["Indexing"])
app.include_router(dream_router, prefix="/api/dream", tags=["Dream"])
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(ws_progress_router, prefix="/api/ws", tags=["WebSocket"])
