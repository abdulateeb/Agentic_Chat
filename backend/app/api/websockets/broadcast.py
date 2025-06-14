"""
Broadcasting service for sending structured WebSocket events.
"""
from app.api.websockets.connection_manager import connection_manager
from app.models.agent_node import AgentNode
from app.models.events import NodeEvent, CommentaryEvent, ErrorEvent
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def broadcast_node_update(workflow_id: str, node: AgentNode):
    event = NodeEvent(payload=node)
    await connection_manager.broadcast_to_workflow(workflow_id, event.dict())


async def broadcast_commentary(workflow_id: str, commentary: dict):
    event = CommentaryEvent(payload=commentary)
    await connection_manager.broadcast_to_workflow(workflow_id, event.dict())


async def broadcast_error(workflow_id: str, error_details: dict):
    event = ErrorEvent(payload=error_details)
    await connection_manager.broadcast_to_workflow(workflow_id, event.dict())
