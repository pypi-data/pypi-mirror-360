"""Protocol for the completion API of an LLM service."""

from typing import Any, Protocol


class GenerationProtocol(Protocol):
    """
    Protocol that describes how to access the generation API of an LLM service.
    """

    def generate(
        self,
        user: str,
        system: str | None = None,
        model: str | None = None,
        samples: int = 1,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> list[str]:
        """
        Generate model responses from the LLMs API.
        """

    def chat(
        self,
        user: str,
        system: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a model response from the LLMs API, in the ongoing chat.
        """

    @property
    def history(self) -> list[dict[str, Any]]:
        """
        Get the chat history for this session.
        """
