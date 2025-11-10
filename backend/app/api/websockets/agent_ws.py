"""WebSocket endpoint for real-time agent communication."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import structlog
from datetime import datetime

from app.services.queue.redis_service import redis_service

router = APIRouter()
logger = structlog.get_logger()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self) -> None:
        """Initialize connection manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str) -> None:
        """
        Connect a WebSocket client.

        Args:
            websocket: WebSocket connection
            job_id: Job ID to subscribe to
        """
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        logger.info("websocket_connected", job_id=job_id)

    def disconnect(self, websocket: WebSocket, job_id: str) -> None:
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
            job_id: Job ID
        """
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.info("websocket_disconnected", job_id=job_id)

    async def send_to_job(self, job_id: str, message: dict) -> None:
        """
        Send message to all connections for a job.

        Args:
            job_id: Job ID
            message: Message to send
        """
        if job_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error("websocket_send_failed", job_id=job_id, error=str(e))
                    disconnected.add(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[job_id].discard(connection)


manager = ConnectionManager()


@router.websocket("/agent/{job_id}")
async def agent_websocket(websocket: WebSocket, job_id: str) -> None:
    """
    WebSocket endpoint for real-time agent updates.

    Args:
        websocket: WebSocket connection
        job_id: Job ID to track
    """
    await manager.connect(websocket, job_id)

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to agent updates"
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                message_type = message.get("type")

                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message_type == "status_request":
                    # Get job status from Redis cache
                    status_key = f"job:{job_id}:status"
                    status = await redis_service.get_json(status_key)

                    await websocket.send_json({
                        "type": "status",
                        "job_id": job_id,
                        "data": status or {"status": "unknown"},
                        "timestamp": datetime.utcnow().isoformat()
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                    "timestamp": datetime.utcnow().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
        logger.info("websocket_client_disconnected", job_id=job_id)
    except Exception as e:
        logger.error("websocket_error", job_id=job_id, error=str(e))
        manager.disconnect(websocket, job_id)


async def broadcast_agent_update(job_id: str, update: dict) -> None:
    """
    Broadcast an agent update to all connected clients.

    Args:
        job_id: Job ID
        update: Update data to broadcast
    """
    message = {
        "type": "agent_update",
        "job_id": job_id,
        "data": update,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Cache update in Redis
    cache_key = f"job:{job_id}:status"
    await redis_service.set_json(cache_key, update, expire=3600)

    # Broadcast to WebSocket clients
    await manager.send_to_job(job_id, message)
