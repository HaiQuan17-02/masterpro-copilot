"""
Hybrid Provider Manager and Circuit Breaker (Week 10).
Seamlessly routes queries between Cloud LLM and Local Deterministic Synthesizer.
"""

import time
from typing import AsyncGenerator, Dict, Any, List, Optional, Tuple
from ai.providers.base_provider import BaseLLMProvider, ProviderUnavailableError
from ai.providers.online_provider import OnlineLLMProvider
from ai.providers.offline_provider import OfflineFallbackProvider


class HybridProviderManager:
    """
    Manages active LLM providers and circuit breaker transitions.
    Supported modes: 'auto', 'online_preferred', 'offline_only'.
    """
    _instance: Optional["HybridProviderManager"] = None

    def __init__(self, mode: str = "auto"):
        self.mode = mode  # 'auto', 'online_preferred', 'offline_only'
        self.online_provider = OnlineLLMProvider()
        self.offline_provider = OfflineFallbackProvider()

        # Telemetry & Circuit Breaker State
        self.consecutive_failures = 0
        self.total_requests = 0
        self.fallback_requests = 0
        self.last_failure_reason: Optional[str] = None
        self.last_switch_time = time.time()

    @classmethod
    def get_instance(cls) -> "HybridProviderManager":
        if cls._instance is None:
            cls._instance = HybridProviderManager()
        return cls._instance

    def set_mode(self, mode: str):
        if mode not in ["auto", "online_preferred", "offline_only"]:
            raise ValueError("Mode must be 'auto', 'online_preferred', or 'offline_only'")
        self.mode = mode
        self.last_switch_time = time.time()

    def get_status(self) -> Dict[str, Any]:
        has_api_key = bool(self.online_provider.api_key and self.online_provider.api_key.strip())
        is_healthy = has_api_key and self.consecutive_failures < 3 and not self.online_provider._simulate_failure

        current_active = "offline_fallback"
        if self.mode != "offline_only" and is_healthy:
            current_active = self.online_provider.name

        return {
            "mode": self.mode,
            "current_active_provider": current_active,
            "is_online_available": is_healthy,
            "has_api_key": has_api_key,
            "simulated_failure": self.online_provider._simulate_failure,
            "consecutive_failures": self.consecutive_failures,
            "total_requests": self.total_requests,
            "fallback_requests": self.fallback_requests,
            "fallback_rate_percent": round(
                (self.fallback_requests / self.total_requests * 100), 1
            ) if self.total_requests > 0 else 0.0,
            "last_failure_reason": self.last_failure_reason
        }

    async def generate_stream(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[Tuple[str, str, bool], None]:
        """
        Yields (token, provider_name, is_fallback).
        """
        self.total_requests += 1

        # Case 1: Explicit offline_only
        if self.mode == "offline_only":
            self.fallback_requests += 1
            async for token in self.offline_provider.generate_stream(query, context_chunks, system_prompt):
                yield token, self.offline_provider.name, True
            return

        # Case 2: Attempt online provider
        try:
            tokens_generated = 0
            async for token in self.online_provider.generate_stream(query, context_chunks, system_prompt):
                tokens_generated += 1
                yield token, self.online_provider.name, False

            # Reset circuit breaker on success
            if tokens_generated > 0:
                self.consecutive_failures = 0
                self.last_failure_reason = None
                return

        except ProviderUnavailableError as e:
            # External provider failed -> Seamless fallback to local synthesizer
            self.consecutive_failures += 1
            self.fallback_requests += 1
            self.last_failure_reason = str(e)

            # Fallback stream
            async for token in self.offline_provider.generate_stream(query, context_chunks, system_prompt):
                yield token, self.offline_provider.name, True

        except Exception as general_err:
            self.consecutive_failures += 1
            self.fallback_requests += 1
            self.last_failure_reason = f"Unexpected: {str(general_err)}"
            async for token in self.offline_provider.generate_stream(query, context_chunks, system_prompt):
                yield token, self.offline_provider.name, True
