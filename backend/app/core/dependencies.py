"""
FastAPI dependencies for the Agentic SRE backend.
This module provides reusable functions for dependency injection,
such as getting settings, which helps in decoupling components and improving testability.
"""

from app.core.config import Settings, get_settings


# For now, this file is simple. It just re-exports the get_settings function
# so all dependencies can be imported from a single, consistent location.
# As we add more complex dependencies like database sessions or security principals,
# they will be defined here.

def get_app_settings() -> Settings:
    """Return cached application settings (FastAPI dependency)."""
    return get_settings()
