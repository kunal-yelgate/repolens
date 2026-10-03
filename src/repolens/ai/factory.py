"""Ollama, OpenAI, Anthropic, Gemini, Groq LLM providers and provider factory."""

import os
from typing import Optional
import httpx

from repolens.ai.base import BaseLLMProvider, LLMResponse
from repolens.config.models import AIConfig


class NullLLMProvider(BaseLLMProvider):
    """Fallback provider when no AI is configured (--no-ai mode)."""

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        return LLMResponse(
            content="[AI reasoning disabled: running in deterministic static analysis mode]",
            provider="none",
            model="none",
        )

    def is_available(self) -> bool:
        return True


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider using HTTP API."""

    def __init__(self, model: Optional[str] = None, base_url: Optional[str] = None, timeout: float = 180.0, **kwargs) -> None:
        super().__init__(
            model=model or "mistral",
            base_url=base_url or "http://localhost:11434",
        )
        self.timeout = timeout

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        url = f"{self.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
            "stream": False,
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                return LLMResponse(
                    content=data.get("response", ""),
                    provider="ollama",
                    model=self.model or "mistral",
                )
        except Exception as e:
            return LLMResponse(
                content=f"[Local Ollama error: {e}]",
                provider="ollama",
                model=self.model or "mistral",
            )


    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url.rstrip('/')}/api/tags")
                return res.status_code == 200
        except Exception:
            return False


class OpenAIProvider(BaseLLMProvider):
    """OpenAI and OpenAI-compatible API provider (Groq, Together, DeepSeek, vLLM, etc.)."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs) -> None:
        super().__init__(
            model=model or "gpt-4o-mini",
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or "https://api.openai.com/v1",
        )

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content="[OpenAI API key missing. Set REPOLENS_API_KEY or OPENAI_API_KEY]",
                provider="openai",
                model=self.model or "gpt-4o-mini",
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            url = f"{self.base_url.rstrip('/')}/chat/completions"
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(
                    content=content,
                    provider="openai",
                    model=self.model or "gpt-4o-mini",
                )
        except Exception as e:
            return LLMResponse(
                content=f"[OpenAI API error: {e}]",
                provider="openai",
                model=self.model or "gpt-4o-mini",
            )

    def is_available(self) -> bool:
        return bool(self.api_key)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs) -> None:
        super().__init__(
            model=model or "claude-3-5-sonnet-20241022",
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url="https://api.anthropic.com/v1",
        )

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content="[Anthropic API key missing. Set ANTHROPIC_API_KEY]",
                provider="anthropic",
                model=self.model or "claude-3-5-sonnet",
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            url = f"{self.base_url}/messages"
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                text = "".join(b.get("text", "") for b in data.get("content", []))
                return LLMResponse(
                    content=text,
                    provider="anthropic",
                    model=self.model or "claude-3-5-sonnet",
                )
        except Exception as e:
            return LLMResponse(
                content=f"[Anthropic API error: {e}]",
                provider="anthropic",
                model=self.model or "claude-3-5-sonnet",
            )

    def is_available(self) -> bool:
        return bool(self.api_key)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs) -> None:
        super().__init__(
            model=model or "gemini-2.0-flash",
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta",
        )

    def complete(self, prompt: str, system_prompt: Optional[str] = None) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content="[Gemini API key missing. Set GEMINI_API_KEY]",
                provider="gemini",
                model=self.model or "gemini-2.0-flash",
            )

        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        parts = []
        if system_prompt:
            parts.append({"text": f"SYSTEM: {system_prompt}\n\n"})
        parts.append({"text": prompt})

        payload = {
            "contents": [{"parts": parts}]
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return LLMResponse(
                    content=text,
                    provider="gemini",
                    model=self.model or "gemini-2.0-flash",
                )
        except Exception as e:
            return LLMResponse(
                content=f"[Gemini API error: {e}]",
                provider="gemini",
                model=self.model or "gemini-2.0-flash",
            )

    def is_available(self) -> bool:
        return bool(self.api_key)


class GroqProvider(OpenAIProvider):
    """Groq fast inference provider (OpenAI compatible)."""

    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None, **kwargs) -> None:
        super().__init__(
            model=model or "llama-3.3-70b-versatile",
            api_key=api_key or os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )


def get_llm_provider(config: AIConfig) -> BaseLLMProvider:
    """Create appropriate LLMProvider instance based on configuration."""
    provider_name = (config.provider or "none").lower()

    if provider_name == "ollama":
        return OllamaProvider(model=config.model, base_url=config.base_url)
    elif provider_name == "openai":
        return OpenAIProvider(model=config.model, api_key=config.api_key, base_url=config.base_url)
    elif provider_name == "anthropic":
        return AnthropicProvider(model=config.model, api_key=config.api_key)
    elif provider_name == "gemini":
        return GeminiProvider(model=config.model, api_key=config.api_key)
    elif provider_name == "groq":
        return GroqProvider(model=config.model, api_key=config.api_key)
    else:
        return NullLLMProvider()
