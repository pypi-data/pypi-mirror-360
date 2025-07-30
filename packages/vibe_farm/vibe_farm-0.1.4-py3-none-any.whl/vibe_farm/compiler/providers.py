# Copyright (c) 2025 Kris Jordan
# Licensed under the MIT License.
from __future__ import annotations
from vibe_farm.__about__ import __license__, __copyright__

"""LLM provider abstractions used during compilation."""

import os
from typing import Protocol


class LLMProvider(Protocol):
    """Protocol for LLM providers."""

    name: str
    api_key_env: str

    def generate(self, prompt: str) -> str:
        """Return generated code for *prompt*."""
        ...  # pragma: no cover


class OpenAIProvider:
    """OpenAI provider implementation."""

    name = "openai"
    api_key_env = "OPENAI_API_KEY"

    def __init__(self) -> None:
        if self.api_key_env not in os.environ:
            raise EnvironmentError(f"{self.api_key_env} not set")
        self.api_key = os.environ[self.api_key_env]

    def generate(self, prompt: str) -> str:  # pragma: no cover - external service
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}]
        )
        return str(response.choices[0].message.content)


class ClaudeProvider:
    """Anthropic Claude provider implementation."""

    name = "claude"
    api_key_env = "ANTHROPIC_API_KEY"

    def __init__(self) -> None:
        if self.api_key_env not in os.environ:
            raise EnvironmentError(f"{self.api_key_env} not set")
        self.api_key = os.environ[self.api_key_env]

    def generate(self, prompt: str) -> str:  # pragma: no cover - external service
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        return str(response.content[0].text)  # type: ignore[union-attr]


_PROVIDERS: dict[str, type[LLMProvider]] = {
    OpenAIProvider.name: OpenAIProvider,
    ClaudeProvider.name: ClaudeProvider,
}

PROVIDER_NAMES = list(_PROVIDERS.keys())


def provider_from_name(name: str) -> LLMProvider:
    """Return provider instance for *name*."""
    cls = _PROVIDERS.get(name)
    if cls is None:
        raise KeyError(f"Unknown provider: {name}")
    return cls()


def auto_provider() -> LLMProvider | None:
    """Return the first available provider based on environment variables."""
    for cls in _PROVIDERS.values():
        if os.getenv(cls.api_key_env):
            return cls()
    return None


__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "ClaudeProvider",
    "PROVIDER_NAMES",
    "provider_from_name",
    "auto_provider",
]
