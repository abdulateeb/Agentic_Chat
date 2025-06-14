"""Tool Executor Service for Agentic SRE.

This service receives a tool name and parameters, and executes the
corresponding logic via the Data Collector or other subsystems.
"""
from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Cortex Tool Executor",
    description="Executes tool calls requested by the agent.",
    version="1.0.0",
)

# Environment-configurable endpoint for Data Collector
DATA_COLLECTOR_URL = os.getenv("DATA_COLLECTOR_URL", "http://data-collector:8000")


class ToolCallRequest(BaseModel):
    tool_name: str
    parameters: dict[str, object]


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------
async def execute_metrics_tool(params: dict[str, object], client: httpx.AsyncClient):
    """Handler to fetch metrics via Data Collector."""

    response = await client.post(f"{DATA_COLLECTOR_URL}/metrics", json=params)
    response.raise_for_status()
    return response.json()


async def execute_logs_tool(params: dict[str, object], client: httpx.AsyncClient):
    """Handler to fetch logs via Data Collector."""

    response = await client.post(f"{DATA_COLLECTOR_URL}/logs", json=params)
    response.raise_for_status()
    return response.json()


# Registry mapping tool names to handler coroutines
TOOL_REGISTRY = {
    "metrics_tool": execute_metrics_tool,
    "logs_tool": execute_logs_tool,
    # Future tools can be added here
}


@app.get("/health")
def health_check() -> dict[str, str]:  # noqa: D401
    """Liveness probe."""

    return {"service": "Tool Executor", "status": "healthy"}


@app.post("/execute")
async def execute_tool(request: ToolCallRequest):  # noqa: D401, ANN201
    """Endpoint to execute a requested tool."""

    tool_name = request.tool_name
    print("Received request to execute tool:", tool_name, "with params:", request.parameters)

    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found.")

    handler = TOOL_REGISTRY[tool_name]

    try:
        async with httpx.AsyncClient() as client:
            result = await handler(request.parameters, client)

        print("Execution successful for tool:", tool_name)
        return {"status": "success", "output": result}
    except httpx.RequestError as exc:
        print(
            f"Execution failed for tool: {tool_name}. Error connecting to data-collector: {exc}"
        )
        raise HTTPException(
            status_code=503, detail=f"Could not connect to data-collector: {exc}"
        ) from exc
    except Exception as exc:  # noqa: BLE001
        print(f"Execution failed for tool: {tool_name}. Error: {exc}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {exc}") from exc
