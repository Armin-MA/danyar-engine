from dataclasses import dataclass


@dataclass(frozen=True)
class LLMConfig:
    """Configuration data structure for Frontier and SLM LLM models."""

    frontier_model: str = "gemini-1.5-pro"
    slm_model: str = "gemini-1.5-flash"
    api_key: str = ""
