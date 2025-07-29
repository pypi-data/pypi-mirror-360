"""Classes to access LLMs via the Anthropic Claude API."""

from typing import Any

import anthropic

from llm_cgr.defaults import DEFAULT_MAX_TOKENS
from llm_cgr.llm.clients.base import Base_LLM


class Anthropic_LLM(Base_LLM):
    """Class to access LLMs via the Anthropic API."""

    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialise the Anthropic client.

        Requires the ANTHROPIC_API_KEY environment variable to be set.
        """
        super().__init__(
            model=model,
            system=system,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        self._client = anthropic.Anthropic()

    def _build_message(
        self,
        role: str,
        content: str,
    ) -> dict[str, str | list[dict[str, str]]]:
        """Build an Anthropic model message."""
        return {
            "role": role,
            "content": [
                {
                    "type": "text",
                    "text": content,
                }
            ],
        }

    def _build_input(
        self,
        user: str,
        system: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the full Anthropic model input."""
        return [self._build_message(role="user", content=user)]

    def _get_response(
        self,
        model: str,
        input: list[dict[str, Any]],
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a model response from the Anthropic API."""
        response = self._client.messages.create(
            model=model,
            system=system or self._system or anthropic.NOT_GIVEN,
            messages=input,
            temperature=temperature or anthropic.NOT_GIVEN,
            top_p=top_p or anthropic.NOT_GIVEN,
            max_tokens=max_tokens or DEFAULT_MAX_TOKENS,
        )
        return response.content[0].text
