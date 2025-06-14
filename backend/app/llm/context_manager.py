"""Context management for LLM interactions.

This module is a placeholder for a future, more advanced implementation.
A full context manager would be responsible for:
- Building the conversational history (user, model, tool turns).
- Truncating or summarizing the history to fit within the LLM's token limit.
- Managing the context window to ensure the LLM has the right information
  for each step of a long-running workflow.
"""
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ContextManager:
    """Placeholder class for managing LLM conversational context."""

    def __init__(self) -> None:
        logger.info("ContextManager initialized (placeholder implementation).")
        self.history: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history (placeholder)."""

        # A real implementation would append and manage token limits here.
        self.history.append({"role": role, "content": content})

    def get_context(self) -> list[dict[str, str]]:
        """Retrieve the current context (placeholder)."""

        return self.history.copy()
