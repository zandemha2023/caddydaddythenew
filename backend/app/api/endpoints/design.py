"""Design workflow endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path
from datetime import datetime
import structlog

from app.db.base import get_db
from app.services.agents.design_orchestrator import DesignOrchestrator
from app.api.websockets.agent_stream import agent_stream_manager

router = APIRouter()
logger = structlog.get_logger()


class DesignStartRequest(BaseModel):
    """Request to start a design session."""
    prompt: str
    project_id: Optional[str] = None


class DesignProcessRequest(BaseModel):
    """Request to process a design message."""
    session_id: str
    message: str


class DesignStartResponse(BaseModel):
    """Response from starting a design session."""
    session_id: str
    status: str
    message: str


class DesignStatusResponse(BaseModel):
    """Design session status response."""
    session_id: str
    status: str
    current_agent: Optional[str] = None
    design_id: Optional[str] = None
    has_requirements: bool


# Global orchestrator instances (in production, use Redis for session storage)
orchestrators: dict[str, DesignOrchestrator] = {}


def get_orchestrator(db: AsyncSession) -> DesignOrchestrator:
    """Get or create orchestrator for this request."""
    # In production, this should be cached/shared properly
    # For now, create a new one each time
    return DesignOrchestrator(db)


@router.post("/start", response_model=DesignStartResponse)
async def start_design(
    request: DesignStartRequest,
    db: AsyncSession = Depends(get_db)
) -> DesignStartResponse:
    """
    Start a new design session.

    Args:
        request: Design start request with prompt
        db: Database session

    Returns:
        Session ID and status
    """
    try:
        logger.info("starting_design", prompt=request.prompt[:100])

        orchestrator = get_orchestrator(db)

        # Save orchestrator reference
        session_id = await orchestrator.start_design_session(
            prompt=request.prompt,
            project_id=request.project_id
        )

        # Store orchestrator (in production, use Redis)
        orchestrators[session_id] = orchestrator

        logger.info("design_started", session_id=session_id)

        return DesignStartResponse(
            session_id=session_id,
            status="started",
            message="Design session created. Connect to WebSocket for real-time updates."
        )

    except Exception as e:
        logger.error("start_design_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_design(
    request: DesignProcessRequest,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Process a design message (initial request or clarification response).

    Args:
        request: Design process request
        db: Database session

    Returns:
        Processing result
    """
    try:
        logger.info("processing_design", session_id=request.session_id, message=request.message[:100])

        # Get orchestrator
        if request.session_id not in orchestrators:
            # Create new orchestrator (shouldn't happen in normal flow)
            orchestrator = get_orchestrator(db)
            orchestrators[request.session_id] = orchestrator
        else:
            orchestrator = orchestrators[request.session_id]

        # Process request
        result = await orchestrator.process_design_request(
            session_id=request.session_id,
            user_message=request.message
        )

        logger.info("design_processed", session_id=request.session_id, status=result.get("status"))

        return result

    except Exception as e:
        logger.error("process_design_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/status", response_model=DesignStatusResponse)
async def get_design_status(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> DesignStatusResponse:
    """
    Get design session status.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        Session status
    """
    try:
        if session_id not in orchestrators:
            raise HTTPException(status_code=404, detail="Session not found")

        orchestrator = orchestrators[session_id]
        status = orchestrator.get_session_status(session_id)

        return DesignStatusResponse(**status)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_status_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/download")
async def download_design(
    session_id: str,
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Download STL file for a completed design.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        STL file
    """
    try:
        if session_id not in orchestrators:
            raise HTTPException(status_code=404, detail="Session not found")

        orchestrator = orchestrators[session_id]
        session = orchestrator.sessions.get(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        if session["status"] != "complete":
            raise HTTPException(status_code=400, detail="Design not complete yet")

        # Get file path from session (stored during CAD generation)
        # In production, query from database using design_id
        from app.models.cad_file import CADFile
        from app.models.design import Design
        from sqlalchemy import select

        # Get design
        design_result = await db.execute(
            select(Design).where(Design.id == session["design_id"])
        )
        design = design_result.scalar_one_or_none()

        if not design:
            raise HTTPException(status_code=404, detail="Design not found")

        # Get latest version's primary CAD file
        file_result = await db.execute(
            select(CADFile)
            .join(CADFile.design_version)
            .where(CADFile.is_primary == True)
            .where(CADFile.design_version.has(design_id=design.id))
            .order_by(CADFile.created_at.desc())
        )
        cad_file = file_result.scalar_one_or_none()

        if not cad_file:
            raise HTTPException(status_code=404, detail="STL file not found")

        file_path = Path(cad_file.file_path)

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="STL file not found on disk")

        logger.info("downloading_design", session_id=session_id, file=str(file_path))

        return FileResponse(
            path=str(file_path),
            media_type="model/stl",
            filename=file_path.name
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("download_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time design updates.

    Args:
        websocket: WebSocket connection
        session_id: Session ID
    """
    await agent_stream_manager.connect(websocket, session_id)

    try:
        # Keep connection alive and handle pings
        while True:
            data = await websocket.receive_text()

            try:
                import json
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": str(datetime.utcnow())
                    })

            except json.JSONDecodeError:
                logger.warning("invalid_websocket_message", data=data)

    except WebSocketDisconnect:
        agent_stream_manager.disconnect(websocket, session_id)
        logger.info("websocket_disconnected", session_id=session_id)
    except Exception as e:
        logger.error("websocket_error", session_id=session_id, error=str(e))
        agent_stream_manager.disconnect(websocket, session_id)
