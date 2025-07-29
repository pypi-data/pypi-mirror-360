"""Module for LLM client initialisation."""

from llm_cgr.llm.clients.anthropic import Anthropic_LLM
from llm_cgr.llm.clients.base import Base_LLM
from llm_cgr.llm.clients.deepseek import DeepSeek_LLM
from llm_cgr.llm.clients.mistral import Mistral_LLM
from llm_cgr.llm.clients.openai import OpenAI_LLM
from llm_cgr.llm.clients.protocol import GenerationProtocol
from llm_cgr.llm.clients.together import TogetherAI_LLM


def get_llm(
    model: str,
    system: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    max_tokens: int | None = None,
) -> GenerationProtocol:
    """
    Initialise the correct LLM client for the given model.
    """
    llm_class: type[Base_LLM]
    if "claude" in model:
        llm_class = Anthropic_LLM
    elif "gpt" in model or model.startswith("o"):
        llm_class = OpenAI_LLM
    elif "tral" in model:
        llm_class = Mistral_LLM
    elif "deepseek" in model:
        llm_class = DeepSeek_LLM
    else:
        llm_class = TogetherAI_LLM

    return llm_class(
        model=model,
        system=system,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )


__all__ = [
    "Anthropic_LLM",
    "Base_LLM",
    "DeepSeek_LLM",
    "GenerationProtocol",
    "OpenAI_LLM",
    "TogetherAI_LLM",
    "Mistral_LLM",
    "get_llm",
]
