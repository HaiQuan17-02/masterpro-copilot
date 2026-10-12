"""
Offline Deterministic Fallback Provider for MasterPro Copilot (Week 10).
Runs 100% locally with zero external network dependencies, zero API costs,
and zero hallucinations.
"""

import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from ai.providers.base_provider import BaseLLMProvider


class OfflineFallbackProvider(BaseLLMProvider):
    """
    Deterministic Local Rule-Based Synthesizer.
    Guarantees reliable operation on POS cash registers even when WAN/Internet is disconnected.
    """
    def __init__(self, delay_per_token: float = 0.015):
        self.delay_per_token = delay_per_token

    @property
    def name(self) -> str:
        return "offline_rule_synthesizer"

    @property
    def is_online(self) -> bool:
        return False

    async def generate_stream(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        if not context_chunks:
            refusal = (
                f"Tài liệu vận hành MasterPro hiện tại chưa ghi nhận thông tin cụ thể về câu hỏi: *\"{query}\"*.\n\n"
                "Bạn vui lòng kiểm tra lại từ khóa hoặc tạo ticket gửi **Hỗ trợ Kỹ thuật L2** để được trợ giúp."
            )
            for word in refusal.split(" "):
                yield word + " "
                if self.delay_per_token > 0:
                    await asyncio.sleep(self.delay_per_token)
            return

        top = context_chunks[0]
        title = top.get("title") or "Quy trình vận hành"
        module = top.get("module") or "Hệ thống"
        doc_id = top.get("document_id") or "doc"
        page = top.get("page") or 1
        content = (top.get("content") or "").strip()

        # Step 1: Lead header
        lead = f"Theo tài liệu nghiệp vụ MasterPro phân hệ **{module}** (*{title}*):\n\n"
        
        # Step 2: Clean content body
        body = content
        # Remove top heading if content starts with # to avoid heading duplicate
        if body.startswith("#"):
            lines = body.split("\n")
            body = "\n".join(lines[1:]).strip()

        # Step 3: Attach primary citation anchor
        citation = f" [cite: {doc_id}, trang {page}]"
        synthesized_text = lead + body + citation

        # Step 4: If there is a complementary second chunk, add guidance
        if len(context_chunks) > 1 and context_chunks[1].get("score", 0) >= 0.40:
            c2 = context_chunks[1]
            c2_content = (c2.get("content") or "").strip()
            if c2_content.startswith("#"):
                c2_content = "\n".join(c2_content.split("\n")[1:]).strip()
            synthesized_text += (
                f"\n\n**Lưu ý bổ sung:** {c2_content}"
                f" [cite: {c2.get('document_id', 'doc')}, trang {c2.get('page', 1)}]"
            )

        # Stream out words
        for token in synthesized_text.split(" "):
            yield token + " "
            if self.delay_per_token > 0:
                await asyncio.sleep(self.delay_per_token)
