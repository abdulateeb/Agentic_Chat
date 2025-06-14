"""Gemini API client for the Agentic SRE backend.
This module encapsulates all interactions with the Google Gemini LLM,
providing a clean, error-handled interface for the rest of the application.
"""

from __future__ import annotations

import json
from typing import Any, Dict

import google.generativeai as genai

from app.core.config import Settings
from app.core.exceptions import LLMConnectionError, LLMResponseError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Client for interacting with the Google Gemini API."""

    def __init__(self, settings: Settings):
        """Initialize the Gemini client with application settings."""

        self.settings = settings
        try:
            genai.configure(api_key=self.settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(model_name=self.settings.GEMINI_MODEL)
            logger.info(
                "Gemini client initialized successfully for model: %s",
                self.settings.GEMINI_MODEL,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to configure Gemini client: %s", exc, exc_info=True)
            raise LLMConnectionError(service="Gemini", reason=str(exc)) from exc

    async def generate_plan(self, prompt: str) -> Dict[str, Any]:
        """Generate an execution plan using the provided prompt."""

        logger.info("Generating execution plan from LLM…")
        try:
            response = await self.model.generate_content_async(contents=prompt)

            # The response may include markdown fences; strip them before parsing.
            raw_text = response.text.strip()
            json_text = raw_text.replace("```json", "").replace("```", "").strip()

            if not json_text:
                raise LLMResponseError("LLM returned an empty response for the plan.")

            plan: Dict[str, Any] = json.loads(json_text)
            logger.info(
                "Successfully generated and parsed execution plan with %d nodes.",
                len(plan.get("nodes", [])),
            )
            return plan

        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to decode JSON from LLM response. Raw text: '%s'", raw_text, exc_info=True
            )
            raise LLMResponseError(f"LLM response was not valid JSON: {exc}") from exc
        except LLMResponseError:
            raise  # Re-raise custom errors unchanged
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "An unexpected error occurred during plan generation: %s", exc, exc_info=True
            )
            raise LLMConnectionError(service="Gemini", reason=str(exc)) from exc
