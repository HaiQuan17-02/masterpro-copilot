"""
Online External LLM Provider for MasterPro Copilot (Week 10).
Connects to external Cloud LLM (OpenAI / Azure / Gemini) with strict timeouts.
Raises ProviderUnavailableError when API key is missing or network fails.
"""

import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from ai.providers.base_provider import BaseLLMProvider, ProviderUnavailableError


class OnlineLLMProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 4.0
    ):
        self.api_key = api_key or os.getenv("AI_API_KEY", "")
        self.model = model or os.getenv("AI_MODEL", "gpt-4o-mini")
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds
        # Flag for testing resilience during UAT
        self._simulate_failure: bool = False

    @property
    def name(self) -> str:
        return f"online_cloud_llm_{self.model}"

    @property
    def is_online(self) -> bool:
        return True

    def set_simulate_failure(self, fail: bool):
        self._simulate_failure = fail

    async def generate_stream(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        # 1. Validation check
        if self._simulate_failure:
            raise ProviderUnavailableError("Simulated external cloud network error / 503 Service Unavailable")

        if not self.api_key or not self.api_key.strip():
            raise ProviderUnavailableError("Missing AI_API_KEY. External Cloud Provider cannot be reached.")

        # 2. Attempt HTTP Stream call with timeout
        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            # Pack prompt with context
            context_str = "\n\n".join([
                f"[{c.get('document_id')}] (Trang {c.get('page', 1)}): {c.get('content')}"
                for c in context_chunks
            ])
            messages = [
                {"role": "system", "content": system_prompt or "Bạn là MasterPro Copilot trợ lý ERP."},
                {"role": "user", "content": f"Ngữ cảnh:\n{context_str}\n\nCâu hỏi: {query}"}
            ]

            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.1
                    }
                ) as response:
                    if response.status_code != 200:
                        raise ProviderUnavailableError(f"Cloud API returned HTTP status {response.status_code}")

                    async for line in response.aiter_lines():
                        line = line.strip()
                        if line.startswith("data: ") and line != "data: [DONE]":
                            try:
                                chunk = json.loads(line[6:])
                                delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if delta:
                                    yield delta
                            except Exception:
                                continue

        except Exception as e:
            if isinstance(e, ProviderUnavailableError):
                raise e
            raise ProviderUnavailableError(f"External Cloud LLM call failed: {str(e)}")
