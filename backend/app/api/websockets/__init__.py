"""WebSocket endpoints."""
from app.api.websockets.agent_ws import router as ws_router

__all__ = ["ws_router"]
