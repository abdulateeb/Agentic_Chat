"""High-level service for managing workflow state.

This module provides a clean interface for creating, retrieving, and updating
workflow objects, abstracting away the underlying storage mechanism (currently
an in-memory `MemoryStore`).
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.core.exceptions import WorkflowAlreadyExistsError, WorkflowNotFoundError
from app.models.agent_node import AgentNode
from app.models.workflow import Workflow
from app.state.memory_store import memory_store
from app.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowStateManager:
    """Facade for workflow CRUD operations backed by a state store."""

    def __init__(self, store) -> None:  # noqa: ANN001
        self.store = store

    # ---------------------------------------------------------------------
    # Workflow-level helpers
    # ---------------------------------------------------------------------
    def create_workflow(self, session_id: str, query: str) -> Workflow:
        """Instantiate and persist a new workflow."""

        workflow = Workflow(session_id=session_id, query=query)
        if self.store.exists(workflow.id):
            raise WorkflowAlreadyExistsError(workflow.id)

        self.store.set(workflow.id, workflow)
        logger.info("Created workflow %s for session %s", workflow.id, session_id)
        return workflow

    def get_workflow(self, workflow_id: str) -> Workflow:
        """Retrieve a workflow or raise if not found."""

        workflow = self.store.get(workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(workflow_id)
        return workflow

    def save_workflow(self, workflow: Workflow) -> None:
        """Persist a workflow object (full overwrite)."""

        self.store.set(workflow.id, workflow)
        logger.debug("Saved workflow %s", workflow.id)

    # ---------------------------------------------------------------------
    # Node helpers
    # ---------------------------------------------------------------------
    def add_node_to_workflow(self, workflow_id: str, node: AgentNode) -> None:
        """Add a new node to the workflow's node tree."""

        workflow = self.get_workflow(workflow_id)
        workflow.node_tree[node.id] = node
        self.save_workflow(workflow)
        logger.debug("Added node %s to workflow %s", node.id, workflow_id)

    def update_node_in_workflow(self, workflow_id: str, node: AgentNode) -> None:
        """Alias for add_node_to_workflow (update/insert)."""

        self.add_node_to_workflow(workflow_id, node)
        logger.debug("Updated node %s in workflow %s", node.id, workflow_id)


# Singleton instance used application-wide
workflow_state_manager = WorkflowStateManager(store=memory_store)
