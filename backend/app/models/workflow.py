"""
Pydantic models for managing an entire agentic workflow.
This represents the state of a single user query from start to finish.
"""
from datetime import datetime
import uuid
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.models.agent_node import AgentNode


class WorkflowStatus(str, Enum):
    """Enumeration for the overall status of a workflow."""

    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class Workflow(BaseModel):
    """Represents the complete state of a single agentic workflow session."""

    id: str = Field(
        default_factory=lambda: f"wf-{uuid.uuid4().hex[:12]}",
        description="Unique identifier for the workflow.",
    )
    session_id: str = Field(..., description="The WebSocket session ID this workflow is associated with.")
    query: str = Field(..., description="The initial user query that started this workflow.")
    status: WorkflowStatus = Field(
        default=WorkflowStatus.PLANNING, description="The current status of the workflow."
    )

    # Node tree keyed by node ID for quick access; parent_id builds the hierarchy
    node_tree: Dict[str, AgentNode] = Field(
        default_factory=dict, description="Dictionary of all nodes in the workflow keyed by node ID."
    )

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    error: Optional[str] = Field(None, description="An error message if the entire workflow failed.")

    class Config:  # noqa: D106
        use_enum_values = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}
