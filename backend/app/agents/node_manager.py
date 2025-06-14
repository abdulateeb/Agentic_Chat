"""Node Manager for the Agentic SRE system.

Centralised helper for creating, updating, and broadcasting `AgentNode` states
within a workflow, keeping the main orchestration code concise.
"""
from __future__ import annotations

from typing import Optional

from app.api.websockets.broadcast import broadcast_commentary, broadcast_node_update
from app.models.agent_node import AgentNode, NodeData, NodeStatus, NodeType
from app.state.workflow_state import workflow_state_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)


class NodeManager:  # noqa: D101
    def __init__(self, workflow_id: str) -> None:  # noqa: D401
        self.workflow_id = workflow_id

    # ------------------------------------------------------------------
    # Creation helpers
    # ------------------------------------------------------------------
    async def create_node(
        self,
        label: str,
        node_type: NodeType,
        parent_id: Optional[str] = None,
        data: Optional[dict[str, object]] = None,
    ) -> AgentNode:
        """Create a new node, persist it, and broadcast its creation."""

        data = data or {}
        node_data = NodeData(
            description=data.get("description"),
            input=data,  # store full original payload
        )
        node = AgentNode(label=label, type=node_type, parent_id=parent_id, data=node_data)

        workflow_state_manager.add_node_to_workflow(self.workflow_id, node)
        await broadcast_node_update(self.workflow_id, node)
        logger.info(
            "Created and broadcasted new node %s ('%s') for workflow %s",
            node.id,
            label,
            self.workflow_id,
        )
        return node

    # ------------------------------------------------------------------
    # Update helpers
    # ------------------------------------------------------------------
    async def update_node_status(
        self, node: AgentNode, status: NodeStatus, error: Optional[str] = None
    ) -> None:
        """Update a node's status, persist, and broadcast."""

        node.status = status
        if error:
            node.data.error = error

        workflow_state_manager.update_node_in_workflow(self.workflow_id, node)
        await broadcast_node_update(self.workflow_id, node)
        logger.info(
            "Updated node %s status to %s for workflow %s", node.id, status.value, self.workflow_id
        )

    # ------------------------------------------------------------------
    # Commentary helpers
    # ------------------------------------------------------------------
    async def add_commentary(
        self, title: str, content: str, severity: str = "info"
    ) -> None:
        """Add arbitrary commentary to workflow and broadcast."""

        commentary = {"title": title, "content": content, "severity": severity}
        await broadcast_commentary(self.workflow_id, commentary)
