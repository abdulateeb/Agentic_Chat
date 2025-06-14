"""In-memory state store for agentic workflows.

This module provides a simple, non-persistent, in-memory key-value store
for managing the state of active workflows. It is thread-safe, making it
suitable for an asynchronous application.

For production environments with multiple server instances, this should be
replaced with a distributed store like Redis.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from app.models.workflow import Workflow
from app.utils.logging import get_logger

logger = get_logger(__name__)


class MemoryStore:
    """A thread-safe, in-memory dictionary to store workflow states."""

    def __init__(self) -> None:
        self._data: Dict[str, Workflow] = {}
        self._lock = threading.Lock()
        logger.info("In-memory state store initialized.")

    def get(self, key: str) -> Optional[Workflow]:
        """Retrieve a workflow from the store by its key."""

        with self._lock:
            return self._data.get(key)

    def set(self, key: str, value: Workflow) -> None:
        """Save or update a workflow in the store."""

        with self._lock:
            self._data[key] = value
        logger.debug("Workflow state saved for key: %s", key)

    def delete(self, key: str) -> bool:
        """Delete a workflow from the store, returning True if deleted."""

        with self._lock:
            if key in self._data:
                del self._data[key]
                logger.info("Workflow state deleted for key: %s", key)
                return True
            return False

    def exists(self, key: str) -> bool:
        """Check if a workflow exists in the store."""

        with self._lock:
            return key in self._data


# Global singleton instance
memory_store = MemoryStore()
