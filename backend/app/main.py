"""Main FastAPI application."""
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import engine
from app.services.queue.redis_service import redis_service
from app.api.endpoints import health, cad, projects, designs, jobs, printer_profiles, print_jobs, design
from app.api.websockets import ws_router

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    setup_logging()
    logger.info("application_starting", environment=settings.ENVIRONMENT)

    # Connect to Redis
    await redis_service.connect()

    # Create database tables (in production, use Alembic migrations)
    # Uncomment the following for development only:
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    logger.info("application_ready", port=settings.PORT)

    yield

    # Shutdown
    logger.info("application_shutting_down")
    await redis_service.disconnect()
    await engine.dispose()
    logger.info("application_stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade agentic CAD platform for natural language to 3D model conversion",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(cad.router, prefix="/api/v1/cad", tags=["CAD"])
app.include_router(design.router, prefix="/api/v1/design", tags=["Design Workflow"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(designs.router, prefix="/api/v1/designs", tags=["Designs"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(printer_profiles.router, prefix="/api/v1/printer-profiles", tags=["Printer Profiles"])
app.include_router(print_jobs.router, prefix="/api/v1/print-jobs", tags=["Print Jobs"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "description": "Theo - Agentic CAD Platform",
        "status": "online"
    }
