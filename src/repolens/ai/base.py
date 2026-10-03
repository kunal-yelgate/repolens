"""Base LLM Provider interface."""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    content: str
    provider: str
    model: str
    raw_tokens_used: Optional[int] = None


class BaseLLMProvider(ABC):
    """Abstract base LLM provider interface."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        """Execute a text completion request."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass
