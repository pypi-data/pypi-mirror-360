"""Class to access LLMs via the MistralAI API."""

import os
from typing import Any

import mistralai

from llm_cgr.llm.clients.base import Base_LLM


class Mistral_LLM(Base_LLM):
    """Class to access LLMs via the MistralAI API."""

    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialise the Mistral client.

        Requires the MISTRAL_API_KEY environment variable to be set.
        """
        super().__init__(
            model=model,
            system=system,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        self._client = mistralai.Mistral(
            api_key=os.environ["MISTRAL_API_KEY"],
        )

    def _build_message(
        self,
        role: str,
        content: str,
    ) -> dict[str, str | list[dict[str, str]]]:
        """Build a Mistral model message."""
        return {
            "role": role,
            "content": content,
        }

    def _build_input(
        self,
        user: str,
        system: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the full Mistral model input."""
        input = []
        if system:
            input.append(self._build_message(role="system", content=system))
        input.append(self._build_message(role="user", content=user))
        return input

    def _get_response(
        self,
        model: str,
        input: list[dict[str, Any]],
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate a model response from the MistralAI API."""
        response = self._client.chat.complete(
            model=model,
            messages=input,
            temperature=temperature or mistralai.UNSET,
            top_p=top_p,
            max_tokens=max_tokens or mistralai.UNSET,
        )
        return response.choices[0].message.content
