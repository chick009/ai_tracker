from __future__ import annotations

from abc import ABC, abstractmethod


class LLMError(RuntimeError):
    """Raised when a runner cannot produce a usable completion."""


class LLMRunner(ABC):
    """Pluggable completion backend. Implementations must be side-effect free besides I/O."""

    name: str = "base"

    @abstractmethod
    def complete(self, prompt: str, *, max_turns: int = 4, label: str = "") -> str:
        """Return the assistant's final text for `prompt`."""
