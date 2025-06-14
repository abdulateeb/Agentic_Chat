"""WebSocket Connection Manager for the Agentic SRE backend.

This module provides a thread-safe manager to handle the lifecycle of
WebSocket connections, associating them with specific workflow sessions.
"""
from __future__ import annotations

import asyncio
from typing import Dict

from fastapi import WebSocket

from app.utils.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        # Maps session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Maps session_id -> workflow_id
        self.session_to_workflow: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str, workflow_id: str) -> None:
        """Accept a new WebSocket and register it with the manager."""

        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_to_workflow[session_id] = workflow_id
        logger.info(
            "WebSocket connected: session_id=%s, workflow_id=%s", session_id, workflow_id
        )

    def disconnect(self, session_id: str) -> None:
        """Remove a WebSocket connection from the active pool."""

        if session_id in self.active_connections:
            del self.active_connections[session_id]
            self.session_to_workflow.pop(session_id, None)
            logger.info("WebSocket disconnected: session_id=%s", session_id)

    async def send_personal_message(self, message: dict, session_id: str) -> None:
        """Send a JSON message to a specific WebSocket connection."""

        websocket = self.active_connections.get(session_id)
        if not websocket:
            logger.warning("Attempted to send message to inactive session: %s", session_id)
            return

        try:
            await websocket.send_json(message)
            logger.debug("Sent message to session %s: %s", session_id, message.get("type"))
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to send message to session %s: %s", session_id, exc, exc_info=True
            )
            self.disconnect(session_id)

    async def broadcast_to_workflow(self, workflow_id: str, message: dict) -> None:
        """Broadcast a message to all sessions subscribed to a workflow."""

        session_ids = [
            sid for sid, wid in self.session_to_workflow.items() if wid == workflow_id
        ]
        if not session_ids:
            logger.warning(
                "No active WebSocket sessions found for workflow_id: %s", workflow_id
            )
            return

        await asyncio.gather(
            *(self.send_personal_message(message, sid) for sid in session_ids)
        )
        logger.info(
            "Broadcast message to %d sessions for workflow %s", len(session_ids), workflow_id
        )


# Global singleton instance
connection_manager = ConnectionManager()
