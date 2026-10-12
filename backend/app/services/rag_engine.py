import sys
import os
import time
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ai_dir = os.path.join(backend_dir, "..", "ai")
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from app.services.search_service import SearchService
from prompts.masterpro_rag_prompt import MASTERPRO_SYSTEM_PROMPT, build_rag_prompt
from citation_validator import CitationValidator
from providers.hybrid_manager import HybridProviderManager


class RAGEngine:
    """
    RAG Core Engine for MasterPro Copilot (Week 6 & Week 10).
    Handles hybrid retrieval, prompt injection, Hybrid LLM Provider streaming
    with automatic offline fallback, and post-generation citation validation.
    """
    _instance: Optional["RAGEngine"] = None

    def __init__(self, score_threshold: float = 0.30):
        self.search_service = SearchService.get_instance()
        self.provider_manager = HybridProviderManager.get_instance()
        self.score_threshold = score_threshold

    @classmethod
    def get_instance(cls) -> "RAGEngine":
        if cls._instance is None:
            cls._instance = RAGEngine()
        return cls._instance

    async def query_stream(self, query: str, user_role: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Asynchronously streams SSE events for real-time chat with RBAC and Hybrid Provider Fallback.
        Yields lines formatted as `data: {...}\n\n`.
        """
        start_t = time.perf_counter()
        q_clean = query.strip()

        # Step 1: Semantic Retrieval from Qdrant with Role Filtering
        search_res = self.search_service.search(
            query=q_clean,
            limit=3,
            score_threshold=self.score_threshold,
            user_role=user_role
        )
        hits = search_res.get("results", [])

        # Check provider status
        provider_info = self.provider_manager.get_status()

        # Send initial metadata event with citations and provider telemetry
        citations = []
        for h in hits:
            citations.append({
                "title": h.get("title"),
                "document": h.get("source") or "Tài liệu MasterPro",
                "page": h.get("page") or 1,
                "score": h.get("score"),
                "heading_path": h.get("heading_path")
            })

        meta_event = {
            "type": "metadata",
            "query": q_clean,
            "user_role": user_role or "guest",
            "citations": citations,
            "total_retrieved": len(hits),
            "provider": provider_info["current_active_provider"],
            "fallback_mode": not provider_info["is_online_available"]
        }
        yield f"data: {json.dumps(meta_event, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.02)

        # Step 2: Content Generation Stream
        if not hits:
            if user_role and user_role.lower() != "admin":
                refusal_text = (
                    f"⚠️ **Thông báo Phân quyền (RBAC):** Tài khoản vai trò **{user_role.upper()}** "
                    f"không có quyền truy cập thông tin về *\"{q_clean}\"* theo chính sách bảo mật ERP.\n\n"
                    "Vui lòng liên hệ **Quản trị viên (Admin)** để được cấp quyền hoặc chọn câu hỏi thuộc phạm vi công việc của bạn."
                )
            else:
                refusal_text = (
                    f"Tài liệu vận hành MasterPro hiện tại chưa có thông tin chi tiết về câu hỏi: *\"{q_clean}\"*.\n\n"
                    "Bạn vui lòng kiểm tra lại từ khóa hoặc liên hệ **Chuyên viên Hỗ trợ Kỹ thuật cấp 2 (L2 Support)**."
                )
            for word in refusal_text.split(" "):
                token_event = {"type": "token", "token": word + " "}
                yield f"data: {json.dumps(token_event, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.015)
        else:
            # Stream generated tokens via Hybrid Provider Manager
            full_answer = ""
            active_provider_name = "unknown"
            is_fallback = False

            async for token, p_name, fallback_flag in self.provider_manager.generate_stream(
                query=q_clean,
                context_chunks=hits,
                system_prompt=MASTERPRO_SYSTEM_PROMPT
            ):
                full_answer += token
                active_provider_name = p_name
                is_fallback = fallback_flag
                token_event = {"type": "token", "token": token}
                yield f"data: {json.dumps(token_event, ensure_ascii=False)}\n\n"

            # Step 3: Run Citation Validator
            val_res = CitationValidator.validate(full_answer, hits)
            val_event = {
                "type": "validation",
                "groundedness_score": val_res["groundedness_score"],
                "is_grounded": val_res["is_grounded"],
                "total_citations": val_res["total_citations"],
                "provider": active_provider_name,
                "is_fallback": is_fallback
            }
            yield f"data: {json.dumps(val_event, ensure_ascii=False)}\n\n"

        # End of Stream
        done_event = {
            "type": "done",
            "elapsed_ms": round((time.perf_counter() - start_t) * 1000, 2)
        }
        yield f"data: {json.dumps(done_event, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
