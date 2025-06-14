"""
Configuration management for Agentic SRE backend.
Handles all environment variables and application settings using Pydantic
for robust validation and type-checking.
"""

import secrets
from functools import lru_cache
from typing import List, Any

# Pydantic v2 moved BaseSettings to a separate package.
# Attempt to import from the new location first for forward compatibility.
# Fallback to pydantic import for older (<2.0) versions to keep backward compatibility.
try:
    from pydantic_settings import BaseSettings  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from pydantic import BaseSettings  # type: ignore

from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    # --- Core Application Settings ---
    APP_NAME: str = Field(default="Agentic SRE", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(
        default="development",
        env="ENVIRONMENT",
        description="Must be 'development', 'staging', or 'production'",
    )

    # --- API & Security Settings ---
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32), env="SECRET_KEY")

    # --- CORS (Cross-Origin Resource Sharing) Settings ---
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173", env="CORS_ORIGINS"
    )

    # --- Gemini AI Settings ---
    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY", description="Your Google Gemini API Key is required.")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash", env="GEMINI_MODEL")

    # --- Data Collector Service Settings ---
    DATA_COLLECTOR_URL: str = Field(
        ..., env="DATA_COLLECTOR_URL", description="URL for the internal Data Collector service."
    )

    TOOL_EXECUTOR_URL: str = Field(
        ..., env="TOOL_EXECUTOR_URL", description="URL for the internal Tool Executor service."
    )

    # --- Logging Settings ---
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # --- Validator Methods ---
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:  # noqa: N805
        """Ensure log level is a valid choice."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        level = v.upper()
        if level not in valid_levels:
            raise ValueError(f"Invalid log level: '{v}'. Must be one of {valid_levels}")
        return level

    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:  # noqa: N805
        """Ensure environment is a valid choice."""
        valid_envs = ["development", "staging", "production"]
        env = v.lower()
        if env not in valid_envs:
            raise ValueError(f"Invalid environment: '{v}'. Must be one of {valid_envs}")
        return env

    # --- Configuration Class ---
    class Config:  # noqa: D106
        """Pydantic settings configuration."""

        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()


# A single, cached instance of the settings to be imported across the application
settings = get_settings()
