"""Main Agent Orchestrator for the Agentic SRE system.

Drives a workflow through planning, execution, and synthesis stages using
Gemini LLM and tool execution services.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

from app.agents.node_manager import NodeManager
from app.core.config import get_settings
from app.core.exceptions import LLMResponseError
from app.llm.gemini_client import GeminiClient
from app.llm.prompt_templates import get_planner_prompt, get_synthesizer_prompt
from app.models.agent_node import NodeStatus, NodeType
from app.state.workflow_state import workflow_state_manager
from app.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ToolExecutorClient:  # noqa: D101
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]):  # noqa: D401
        logger.info("MOCK EXECUTING tool '%s' with params: %s", tool_name, parameters)
        await asyncio.sleep(2)
        return {"status": "success", "output": f"Mock result for {tool_name}"}


class AgentOrchestrator:  # noqa: D101
    def __init__(self, workflow_id: str) -> None:  # noqa: D401
        self.workflow_id = workflow_id
        self.workflow = workflow_state_manager.get_workflow(workflow_id)
        self.node_manager = NodeManager(workflow_id)
        self.llm_client = GeminiClient(settings)
        self.tool_executor = ToolExecutorClient()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def run(self) -> None:  # noqa: D401
        try:
            plan = await self._planning_phase()
            if plan and plan.get("nodes"):
                await self._execution_phase(plan)
            else:
                await self.node_manager.add_commentary(
                    title="Planning Skipped",
                    content="No actionable plan was generated. Attempting direct answer.",
                    severity="warn",
                )
            await self._synthesis_phase()
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Workflow %s failed with unhandled exception: %s", self.workflow_id, exc, exc_info=True
            )
            await self.node_manager.add_commentary(
                title="Workflow Failed",
                content=f"An unexpected error occurred: {exc}",
                severity="error",
            )

    # ------------------------------------------------------------------
    # Internal phases
    # ------------------------------------------------------------------
    async def _planning_phase(self) -> dict:
        """
        Handles the planning stage. It can now result in a direct answer or a plan.
        """
        await self.node_manager.add_commentary(
            title="Planning Started",
            content="Generating an execution plan or a direct answer."
        )
        planner_node = await self.node_manager.create_node(
            label="Planning",
            node_type=NodeType.ORCHESTRATOR,
            description="Contacting LLM to analyze query.",
            parent_id=None
        )
        await self.node_manager.update_node_status(planner_node, NodeStatus.PROCESSING)

        try:
            prompt = get_planner_prompt(self.workflow.query)
            response_json = await self.llm_client.generate_plan(prompt) # This function name is now more generic

            # --- THIS IS THE NEW LOGIC ---
            if "direct_answer" in response_json:
                # The LLM chose to answer directly.
                answer = response_json["direct_answer"]
                await self.node_manager.update_node_status(planner_node, NodeStatus.COMPLETED)
                await self.node_manager.add_commentary(
                    title="Direct Answer Provided",
                    content=answer,
                    severity="success"
                )
                # By returning None, we signal that there is no execution plan to run.
                return None 
            
            # If we are here, the LLM returned a plan.
            await self.node_manager.update_node_status(planner_node, NodeStatus.COMPLETED)
            await self.node_manager.add_commentary(
                title="Planning Complete",
                content=f"Generated a plan with {len(response_json.get('nodes', []))} steps."
            )
            return response_json

        except (LLMResponseError, json.JSONDecodeError) as e:
            error_message = f"Failed to generate or parse a valid response from the LLM: {e}"
            logger.error(f"Workflow {self.workflow_id}: {error_message}")
            await self.node_manager.update_node_status(planner_node, NodeStatus.FAILED, error=error_message)
            return None

    async def _execution_phase(self, plan: dict[str, Any]) -> None:
        await self.node_manager.add_commentary(
            title="Execution Started", content="Beginning execution of planned steps."
        )

        # Pre-create nodes in WAITING state
        tool_nodes: dict[str, Any] = {}
        for node_data in plan.get("nodes", []):
            node = await self.node_manager.create_node(
                label=node_data.get("label", "Step"),
                node_type=NodeType.TOOL,
                parent_id=None,
                data=node_data.get("data", {}),
            )
            tool_nodes[node_data["id"]] = node

        # Execute sequentially
        for node_id in sorted(tool_nodes):
            node = tool_nodes[node_id]
            await self.node_manager.update_node_status(node, NodeStatus.PROCESSING)
            tool_name = node.data.description.get("tool_name")
            parameters = node.data.description.get("parameters")
            if not tool_name:
                await self.node_manager.update_node_status(
                    node, NodeStatus.FAILED, error="Tool name missing in plan."
                )
                continue

            result = await self.tool_executor.execute_tool(tool_name, parameters)
            node.data.output = result
            if result.get("status") == "success":
                await self.node_manager.update_node_status(node, NodeStatus.COMPLETED)
            else:
                await self.node_manager.update_node_status(
                    node, NodeStatus.FAILED, error=str(result.get("output"))
                )

    async def _synthesis_phase(self):
        """
        Gathers all tool results, sends them to the LLM for a final answer,
        and broadcasts the result.
        """
        synthesis_node = await self.node_manager.create_node(
            label="Synthesize Final Answer",
            node_type=NodeType.SYNTHESIS,
            description="Combining all collected data into a final response."
        )
        await self.node_manager.update_node_status(synthesis_node, NodeStatus.PROCESSING)

        try:
            # Gather all the outputs from the completed tool nodes
            workflow_state = workflow_state_manager.get_workflow(self.workflow_id)
            collected_data: list[dict[str, Any]] = []
            for node in workflow_state.node_tree.values():
                if node.type == NodeType.TOOL and node.status == NodeStatus.COMPLETED:
                    collected_data.append({
                        "step": node.label,
                        "result": node.data.output
                    })

            # If no data was collected, create a default response
            if not collected_data:
                final_answer = "I was unable to gather any data to answer the query."
            else:
                # Create the prompt for the synthesizer
                prompt = get_synthesizer_prompt(self.workflow.query, collected_data)

                # Make the LLM call to get the final answer
                final_answer = await self.llm_client.generate_synthesis(prompt)

            # Update the synthesis node and broadcast the final answer
            synthesis_node.data.output = {"final_answer": final_answer}
            await self.node_manager.update_node_status(synthesis_node, NodeStatus.COMPLETED)

            await self.node_manager.add_commentary(
                title="Final Answer Generated",
                content=final_answer,
                severity="success"
            )
            logger.info(f"Workflow {self.workflow_id} completed successfully.")

        except Exception as e:  # noqa: BLE001
            error_message = f"Failed during synthesis phase: {e}"
            logger.error(error_message, exc_info=True)
            await self.node_manager.update_node_status(synthesis_node, NodeStatus.FAILED, error=error_message)
