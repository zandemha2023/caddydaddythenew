"""WebSocket manager for real-time agent streaming."""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Any, Optional
import json
import asyncio
import structlog
from datetime import datetime

from app.services.queue.redis_service import redis_service

logger = structlog.get_logger()


class AgentStreamManager:
    """Manager for streaming agent thinking and progress to frontend."""

    def __init__(self) -> None:
        """Initialize agent stream manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.job_status: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, job_id: str) -> None:
        """
        Connect a WebSocket client to an agent stream.

        Args:
            websocket: WebSocket connection
            job_id: Job ID to subscribe to
        """
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        logger.info("agent_stream_connected", job_id=job_id, total_connections=len(self.active_connections[job_id]))

        # Send initial status
        await self.send_message(websocket, {
            "type": "connected",
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Connected to agent stream"
        })

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
        logger.info("agent_stream_disconnected", job_id=job_id)

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """
        Send message to a specific WebSocket.

        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("websocket_send_failed", error=str(e))

    async def broadcast_to_job(self, job_id: str, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all connections for a job.

        Args:
            job_id: Job ID
            message: Message to broadcast
        """
        if job_id not in self.active_connections:
            return

        # Add timestamp
        message["timestamp"] = datetime.utcnow().isoformat()

        # Cache in Redis for late joiners
        cache_key = f"job:{job_id}:stream"
        await redis_service.set_json(cache_key, message, expire=3600)

        # Broadcast to all connected clients
        disconnected = set()
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("broadcast_send_failed", job_id=job_id, error=str(e))
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.active_connections[job_id].discard(connection)

    async def stream_agent_thinking(
        self,
        job_id: str,
        agent_type: str,
        thinking: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stream agent thinking/reasoning to connected clients.

        Args:
            job_id: Job ID
            agent_type: Type of agent (requirements, cad, validation, export)
            thinking: Agent's thinking/reasoning text
            metadata: Additional metadata
        """
        message = {
            "type": "agent_thinking",
            "job_id": job_id,
            "agent": agent_type,
            "thinking": thinking,
            "metadata": metadata or {}
        }
        await self.broadcast_to_job(job_id, message)

    async def stream_tool_use(
        self,
        job_id: str,
        agent_type: str,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_result: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stream tool use to connected clients.

        Args:
            job_id: Job ID
            agent_type: Agent using the tool
            tool_name: Name of tool being used
            tool_input: Tool input parameters
            tool_result: Optional tool result
        """
        message = {
            "type": "tool_use",
            "job_id": job_id,
            "agent": agent_type,
            "tool": tool_name,
            "input": tool_input,
            "result": tool_result
        }
        await self.broadcast_to_job(job_id, message)

    async def stream_progress(
        self,
        job_id: str,
        progress: int,
        stage: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Stream progress update to connected clients.

        Args:
            job_id: Job ID
            progress: Progress percentage (0-100)
            stage: Current stage name
            message: Progress message
            metadata: Additional metadata
        """
        update = {
            "type": "progress",
            "job_id": job_id,
            "progress": progress,
            "stage": stage,
            "message": message,
            "metadata": metadata or {}
        }
        await self.broadcast_to_job(job_id, update)

    async def stream_code_generation(
        self,
        job_id: str,
        code_type: str,
        code: str,
        line_count: int
    ) -> None:
        """
        Stream code generation to connected clients.

        Args:
            job_id: Job ID
            code_type: Type of code (cadquery, openscad, gcode)
            code: Generated code
            line_count: Number of lines
        """
        message = {
            "type": "code_generated",
            "job_id": job_id,
            "code_type": code_type,
            "code": code,
            "line_count": line_count
        }
        await self.broadcast_to_job(job_id, message)

    async def stream_validation_results(
        self,
        job_id: str,
        valid: bool,
        score: int,
        issues: list,
        recommendations: list
    ) -> None:
        """
        Stream validation results to connected clients.

        Args:
            job_id: Job ID
            valid: Whether design is valid
            score: Validation score (0-100)
            issues: List of issues found
            recommendations: List of recommendations
        """
        message = {
            "type": "validation_results",
            "job_id": job_id,
            "valid": valid,
            "score": score,
            "issues": issues,
            "recommendations": recommendations
        }
        await self.broadcast_to_job(job_id, message)

    async def stream_error(
        self,
        job_id: str,
        error: str,
        agent: Optional[str] = None,
        recoverable: bool = True
    ) -> None:
        """
        Stream error to connected clients.

        Args:
            job_id: Job ID
            error: Error message
            agent: Agent that encountered the error
            recoverable: Whether the error is recoverable
        """
        message = {
            "type": "error",
            "job_id": job_id,
            "error": error,
            "agent": agent,
            "recoverable": recoverable
        }
        await self.broadcast_to_job(job_id, message)

    async def stream_completion(
        self,
        job_id: str,
        success: bool,
        result: Dict[str, Any]
    ) -> None:
        """
        Stream job completion to connected clients.

        Args:
            job_id: Job ID
            success: Whether job completed successfully
            result: Final result data
        """
        message = {
            "type": "complete",
            "job_id": job_id,
            "success": success,
            "result": result
        }
        await self.broadcast_to_job(job_id, message)


# Global stream manager instance
agent_stream_manager = AgentStreamManager()
