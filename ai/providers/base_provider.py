"""
Base LLM Provider Interface for MasterPro Copilot (Week 10).
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional


class ProviderUnavailableError(Exception):
    """Raised when an external LLM provider is unreachable, times out, or lacks credentials."""
    pass


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g., 'openai', 'gemini', 'offline_fallback')."""
        pass

    @property
    @abstractmethod
    def is_online(self) -> bool:
        """True if external network dependent, False if runs locally offline."""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generates answer tokens asynchronously.
        Yields token strings.
        """
        pass
