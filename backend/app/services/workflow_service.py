"""Workflow Service for the Agentic SRE backend.

Encapsulates the business logic for managing the lifecycle of agentic
workflows. Responsible for creating a new workflow, persisting its initial
state, and launching the `AgentOrchestrator` in the background so that API
routes can return immediately while the agent continues processing.
"""
from __future__ import annotations

import asyncio

from app.agents.orchestrator import AgentOrchestrator
from app.state.workflow_state import workflow_state_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowService:  # noqa: D101
    async def start_workflow(self, session_id: str, query: str) -> str:  # noqa: D401
        """Create and launch a new workflow.

        Args:
            session_id: WebSocket session ID for live updates.
            query: The user's natural-language query.

        Returns:
            The unique workflow ID.
        """

        # 1. Persist initial workflow state
        workflow = workflow_state_manager.create_workflow(session_id=session_id, query=query)
        logger.info("Workflow %s created for query: '%s'", workflow.id, query)

        # 2. Instantiate orchestrator
        orchestrator = AgentOrchestrator(workflow_id=workflow.id)

        # 3. Schedule asynchronous execution
        asyncio.create_task(orchestrator.run())
        logger.info("Scheduled background execution for workflow %s", workflow.id)

        return workflow.id


# Singleton instance used by API routes
workflow_service = WorkflowService()
