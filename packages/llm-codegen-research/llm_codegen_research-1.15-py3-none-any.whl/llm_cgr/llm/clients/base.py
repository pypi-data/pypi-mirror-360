from abc import ABC, abstractmethod
from typing import Any


class Base_LLM(ABC):
    """Base class to access LLMs via their APIs."""

    def __init__(
        self,
        model: str | None = None,
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        """
        Initialise the LLM client.
        """
        self._model = model
        self._system = system

        # default parameters
        self._temperature = temperature
        self._top_p = top_p
        self._max_tokens = max_tokens

        self._history: list[dict[str, Any]] | None = None

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
        _model = model or self._model
        if _model is None:
            raise ValueError("Model must be specified for LLM APIs.")

        messages = self._build_input(
            user=user,
            system=system or self._system,
        )

        _generations = []
        for _ in range(samples):
            response = self._get_response(
                input=messages,
                model=_model,
                temperature=temperature or self._temperature,
                top_p=top_p or self._top_p,
                max_tokens=max_tokens or self._max_tokens,
            )
            _generations.append(response)

        return _generations

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
        _model = model or self._model
        if _model is None:
            raise ValueError("Model must be specified for LLM APIs.")

        if self._history is None:
            # initialise the history
            self._history = self._build_input(
                user=user,
                system=system or self._system,
            )
        else:
            # or add the new message
            self._history.append(
                self._build_message(
                    role="user",
                    content=user,
                )
            )

        response = self._get_response(
            input=self._history,
            system=system,
            model=_model,
            temperature=temperature or self._temperature,
            top_p=top_p or self._top_p,
            max_tokens=max_tokens or self._max_tokens,
        )

        # update the history and return
        self._history.append(
            self._build_message(
                role="assistant",
                content=response,
            )
        )
        return response

    @property
    def history(self) -> list[dict[str, Any]]:
        """
        Get the chat history for this session.
        """
        return self._history or []

    @abstractmethod
    def _build_message(
        self,
        role: str,
        content: str,
    ) -> dict[str, Any]:
        """
        Build an LLM input message.
        """

    @abstractmethod
    def _build_input(
        self,
        user: str,
        system: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Build the full LLM input, with system and user messages if needed.
        """

    @abstractmethod
    def _get_response(
        self,
        model: str,
        input: list[dict[str, Any]],
        system: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a model response from the LLM API.

        Returns the text response to the prompt.
        """
