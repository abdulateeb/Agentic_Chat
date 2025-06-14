"""Manages tool definitions for Gemini's function calling feature.

This module will define the schema of the tools that the LLM can request to use.
For now, it's a placeholder, as our current planning prompt asks the LLM to generate
the tool name and parameters directly in the JSON plan.

In a more advanced implementation, we would define the function schemas here and
pass them to the Gemini API's `tools` parameter. This enables more reliable and
structured tool use by the LLM.
"""
from typing import Any, Dict, List


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Return tool definitions list (placeholder)."""

    # Future example:
    # metrics_tool = {
    #     "name": "metrics_tool",
    #     "description": "Query time-series metrics",
    #     "parameters": {"type": "object", "properties": {...}},
    # }
    # logs_tool = {...}
    # return [{"function_declarations": [metrics_tool, logs_tool]}]

    return []
