"""Class to access LLMs via the OpenAI API."""

import os
from typing import Any

import openai

from llm_cgr.llm.clients.base import Base_LLM


class DeepSeek_LLM(Base_LLM):
    """Class to access LLMs via the DeepSeek API, using the OpenAI interfaces."""

    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialise the DeepSeek client.

        Requires the DEEPSEEK_API_KEY environment variable to be set.
        """
        super().__init__(
            model=model,
            system=system,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        self._client = openai.OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com",
        )

    def _build_message(
        self,
        role: str,
        content: str,
    ) -> dict[str, str]:
        """Build an OpenAI model message."""
        return {"role": role, "content": content}

    def _build_input(
        self,
        user: str,
        system: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the full OpenAI model input."""
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
        """Generate a model response from the OpenAI API."""
        response = self._client.chat.completions.create(
            messages=input,
            model=model,
            temperature=temperature or openai.NOT_GIVEN,
            top_p=top_p or openai.NOT_GIVEN,
            max_completion_tokens=max_tokens or openai.NOT_GIVEN,
        )
        return response.choices[0].message.content
