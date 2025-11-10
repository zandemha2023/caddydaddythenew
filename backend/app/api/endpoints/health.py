"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.base import get_db
from app.services.queue.redis_service import redis_service

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Basic health check."""
    return {"status": "healthy", "service": "theo-cad"}


@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)) -> dict:
    """Detailed health check with database and Redis status."""
    health_status = {
        "status": "healthy",
        "components": {}
    }

    # Check database
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        if await redis_service.exists("health_check"):
            health_status["components"]["redis"] = "healthy"
        else:
            await redis_service.set("health_check", "ok", expire=60)
            health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["components"]["redis"] = f"unhealthy: {str(e)}"

    return health_status
