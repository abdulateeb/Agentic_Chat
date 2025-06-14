"""API routes for chat and workflow initiation for the Agentic SRE backend.

Defines the HTTP endpoint that the frontend calls to start a new agentic
workflow based on a user's query.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.dependencies import get_app_settings
from app.core.config import Settings
from app.services.workflow_service import workflow_service
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):  # noqa: D101
    query: str = Field(..., description="User query to the SRE agent.", min_length=1, max_length=2000)
    session_id: str = Field(..., description="Unique WebSocket session ID from the frontend.")


class ChatResponse(BaseModel):  # noqa: D101
    workflow_id: str = Field(..., description="Unique ID of the created workflow.")


@router.post(
    "/initiate",
    response_model=ChatResponse,
    summary="Initiate a new Agentic SRE Chat Workflow",
    description=(
        "Start a new agentic workflow. Accepts a user query and session ID, "
        "creates workflow state, launches orchestration in the background, and "
        "immediately returns a unique workflow ID."
    ),
)
async def initiate_chat_workflow(
    request: ChatRequest,
    settings: Settings = Depends(get_app_settings),  # noqa: ARG001  # settings can be used later
):
    """HTTP handler that kicks off a workflow."""

    logger.info(
        "Chat initiation request received for session %s", request.session_id, extra={"query": request.query}
    )

    workflow_id = await workflow_service.start_workflow(
        session_id=request.session_id, query=request.query
    )
    return ChatResponse(workflow_id=workflow_id)
