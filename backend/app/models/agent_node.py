"""
Pydantic models for an Agent Node in the execution graph.
Defines the structure, states, and metadata associated with each step of a workflow.
"""

from datetime import datetime
import uuid
from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """Enumeration for the different types of nodes in the agent graph."""

    QUERY = "query"
    ORCHESTRATOR = "orchestrator"
    ANALYZER = "analyzer"
    TOOL = "tool"
    RESULT = "result"
    DECISION = "decision"
    SYNTHESIS = "synthesis"


class NodeStatus(str, Enum):
    """Enumeration for the execution status of a node."""

    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NodeData(BaseModel):
    """Represents the data payload of a node, including its inputs, outputs, and metadata."""

    description: Dict[str, Any] = Field(
        default_factory=dict,
        description="A dictionary describing the node's purpose and tool metadata.",
    )
    input: Dict[str, Any] = Field(
        default_factory=dict, description="The input data for this node's execution."
    )
    output: Dict[str, Any] = Field(
        default_factory=dict, description="The result or output of this node's execution."
    )
    error: Optional[str] = Field(None, description="Error message if the node failed.")

    class Config:  # noqa: D106
        extra = "allow"  # Allows for additional, ad-hoc data fields.


class AgentNode(BaseModel):
    """The core model for a node in the agent's execution graph."""

    id: str = Field(
        default_factory=lambda: f"node-{uuid.uuid4().hex[:8]}",
        description="Unique identifier for the node.",
    )
    label: str = Field(..., description="A short, display-friendly label for the UI.")
    type: NodeType = Field(..., description="The functional type of the node.")
    status: NodeStatus = Field(
        default=NodeStatus.WAITING, description="The current execution status of the node."
    )

    # Graph structure
    parent_id: Optional[str] = Field(
        None, description="The ID of the parent node in the graph."
    )

    # Timestamps for performance tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Data payload
    data: NodeData = Field(default_factory=NodeData)

    class Config:  # noqa: D106
        use_enum_values = True  # Ensures enum members are stored as their string values.
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
