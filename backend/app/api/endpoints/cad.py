"""CAD generation endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.db.base import get_db
from app.schemas.cad import CADGenerationRequest, CADGenerationResponse
from app.services.cad.generation_service import CADGenerationService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/generate", response_model=CADGenerationResponse)
async def generate_cad_model(
    request: CADGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> CADGenerationResponse:
    """
    Generate a 3D CAD model from natural language description.

    Args:
        request: CAD generation request with prompt and parameters
        background_tasks: FastAPI background tasks
        db: Database session

    Returns:
        Job information for tracking generation progress
    """
    try:
        logger.info("cad_generation_requested", prompt=request.prompt[:100])

        service = CADGenerationService(db)
        result = await service.create_generation_job(request)

        logger.info("cad_generation_job_created", job_id=result.job_id)
        return result

    except Exception as e:
        logger.error("cad_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_supported_formats() -> dict:
    """Get list of supported export formats."""
    return {
        "formats": [
            {
                "name": "STL",
                "extension": "stl",
                "description": "Standard Tessellation Language - for 3D printing",
                "binary": True
            },
            {
                "name": "STEP",
                "extension": "step",
                "description": "STEP format - CAD interchange standard",
                "binary": False
            },
            {
                "name": "OBJ",
                "extension": "obj",
                "description": "Wavefront OBJ - general 3D format",
                "binary": False
            },
            {
                "name": "DXF",
                "extension": "dxf",
                "description": "Drawing Exchange Format - 2D/3D CAD",
                "binary": False
            },
            {
                "name": "GCODE",
                "extension": "gcode",
                "description": "G-code - direct printer instructions",
                "binary": False
            },
            {
                "name": "SVG",
                "extension": "svg",
                "description": "Scalable Vector Graphics - 2D profiles",
                "binary": False
            }
        ]
    }
