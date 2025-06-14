"""
Custom exceptions for the Agentic SRE backend.
Provides a structured hierarchy for error handling across the application,
allowing for precise error identification and appropriate HTTP responses.
"""

from typing import Optional, Dict, Any


class AgenticSREException(Exception):
    """Base exception for all custom errors in this application."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class LLMException(AgenticSREException):
    """Base exception for errors related to the LLM service."""

    def __init__(self, message: str, status_code: int = 500, **kwargs):
        super().__init__(message, status_code=status_code, **kwargs)


class LLMConnectionError(LLMException):
    """Raised when the application cannot connect to the LLM service."""

    def __init__(self, service: str, reason: str):
        message = f"Failed to connect to LLM service '{service}': {reason}"
        super().__init__(message, status_code=503, error_code="LLM_CONNECTION_ERROR")  # 503 Service Unavailable


class LLMResponseError(LLMException):
    """Raised when the LLM returns an invalid or unparsable response."""

    def __init__(self, reason: str):
        message = f"Invalid response from LLM: {reason}"
        super().__init__(message, status_code=502, error_code="LLM_RESPONSE_ERROR")  # 502 Bad Gateway


class ToolException(AgenticSREException):
    """Base exception for errors related to tool execution."""

    def __init__(self, message: str, status_code: int = 500, **kwargs):
        super().__init__(message, status_code=status_code, **kwargs)


class ToolExecutionError(ToolException):
    """Raised when a tool fails during execution."""

    def __init__(self, tool_name: str, reason: str):
        message = f"Execution of tool '{tool_name}' failed: {reason}"
        super().__init__(
            message,
            error_code="TOOL_EXECUTION_ERROR",
            details={"tool_name": tool_name},
        )


class ConfigurationError(AgenticSREException):
    """Raised for application configuration errors."""

    def __init__(self, message: str):
        super().__init__(message, status_code=500, error_code="CONFIGURATION_ERROR")


class WorkflowNotFoundError(AgenticSREException):
    """Raised when a specific workflow cannot be found."""

    def __init__(self, workflow_id: str):
        message = f"Workflow with ID '{workflow_id}' not found."
        super().__init__(message, status_code=404, error_code="WORKFLOW_NOT_FOUND")


class WorkflowAlreadyExistsError(AgenticSREException):
    """Raised when trying to create a workflow that already exists."""

    def __init__(self, workflow_id: str):
        message = f"Workflow with ID '{workflow_id}' already exists."
        super().__init__(
            message, status_code=409, error_code="WORKFLOW_ALREADY_EXISTS"
        )  # 409 Conflict
