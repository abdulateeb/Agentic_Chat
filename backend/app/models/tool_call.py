"""
Pydantic models related to tool calls made by an agent.
Defines the request to call a tool and the structure of the result.
"""
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


class ToolCallRequest(BaseModel):
    """Represents the agent's request to execute a specific tool with given parameters."""

    tool_name: str = Field(..., description="The name of the tool to be executed.")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="The parameters to pass to the tool."
    )


class ToolCallResult(BaseModel):
    """Represents the result returned after a tool has been executed."""

    status: str = Field(
        ..., description="Outcome of the tool execution (e.g., 'success', 'failure')."
    )
    output: Any = Field(..., description="The data returned by the tool.")
    error: Optional[str] = Field(None, description="An error message if the execution failed.")
