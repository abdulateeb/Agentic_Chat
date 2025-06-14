"""
Pydantic models for WebSocket events.
Defines the precise structure of messages sent from the backend to the frontend
to ensure type-safe, real-time communication.
"""
from typing import Literal, Union

from pydantic import BaseModel, Field

from app.models.agent_node import AgentNode


class NodeEvent(BaseModel):
    """Represents a node update/creation event."""

    type: Literal["node"] = "node"
    payload: AgentNode = Field(
        ..., description="The full state of the node that was created or updated."
    )


class CommentaryEvent(BaseModel):
    """Represents a new commentary entry event."""

    type: Literal["commentary"] = "commentary"
    payload: dict  # Placeholder for a future CommentaryEntry model


class ErrorEvent(BaseModel):
    """Represents an error event sent to the frontend."""

    type: Literal["error"] = "error"
    payload: dict = Field(..., description="A dictionary containing error details.")


# Union type for any websocket event
WebSocketEvent = Union[NodeEvent, CommentaryEvent, ErrorEvent]
