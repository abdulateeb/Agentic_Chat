"""Main WebSocket event handlers for the Agentic SRE backend.

Defines WebSocket endpoint that manages client connections and echoes/acknowledges
messages. Future enhancements will use this channel for workflow control.
"""
from fastapi import APIRouter, Path, WebSocket, WebSocketDisconnect

from app.api.websockets.connection_manager import connection_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Router dedicated to websocket routes
router = APIRouter()


@router.websocket("/ws/{session_id}/{workflow_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str = Path(..., title="Unique ID for this WebSocket session"),
    workflow_id: str = Path(..., title="ID of the workflow to subscribe to"),
) -> None:  # noqa: D401, ANN001
    """Handle WebSocket lifecycle for a given session and workflow."""

    await connection_manager.connect(websocket, session_id, workflow_id)
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("Received message from session %s: %s", session_id, data)

            # Echo/acknowledge back to client; replace with richer handling later
            await connection_manager.send_personal_message(
                {"status": "acknowledged", "message": data}, session_id
            )

    except WebSocketDisconnect:
        connection_manager.disconnect(session_id)
        logger.info(
            "WebSocket session %s for workflow %s disconnected.", session_id, workflow_id
        )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unexpected error in WebSocket session %s: %s", session_id, exc, exc_info=True
        )
        connection_manager.disconnect(session_id)
