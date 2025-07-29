"""Class to access LLMs via the TogetherAI API."""

from typing import Any

import together

from llm_cgr.llm.clients.base import Base_LLM


class TogetherAI_LLM(Base_LLM):
    """Class to access LLMs via the TogetherAI API."""

    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialise the TogetherAI client.

        Requires the TOGETHER_API_KEY environment variable to be set.
        """
        super().__init__(
            model=model,
            system=system,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        self._client = together.Together()

    def _build_message(
        self,
        role: str,
        content: str,
    ) -> dict[str, str]:
        """Build a TogetherAI model message."""
        return {"role": role, "content": content}

    def _build_input(
        self,
        user: str,
        system: str | None = None,
    ) -> list[dict[str, Any]]:
        """Build the full TogetherAI model input."""
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
        """Generate a model response from the TogetherAI API."""
        response = self._client.chat.completions.create(
            model=model,
            messages=input,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
