from typing import List, Dict, Any, Optional
import os
from app.core.config import settings
from app.services.search_service import SearchService

class BaseAIProvider:
    async def generate_response(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class RAGAIProvider(BaseAIProvider):
    """
    RAG-powered AI Provider for MasterPro Copilot.
    Retrieves grounded context from Qdrant Vector Store and builds structured answers with citations.
    """
    async def generate_response(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        q_clean = question.strip()
        q_lower = q_clean.lower()

        # Handle greetings
        if q_lower in ["chào", "xin chào", "hello", "hi", "alo", "chào bot"]:
            return {
                "answer": "Xin chào! Tôi là **MasterPro Copilot** - trợ lý AI hỗ trợ tra cứu quy trình vận hành và tài liệu kỹ thuật MasterPro ERP/POS.\n\nBạn có thể hỏi tôi về:\n- Quy trình mở ca, kết ca, khóa sổ bán hàng\n- Thao tác lập phiếu nhập kho, xuất bán, đổi trả\n- Xử lý lỗi máy in hóa đơn, máy quét mã vạch\n- Quản lý danh mục hàng hóa, khách hàng và công nợ.",
                "citations": [],
                "provider": "masterpro-rag",
                "model": "qdrant-retrieval-v1"
            }

        # Query Qdrant Vector Store
        try:
            search_service = SearchService.get_instance()
            search_result = search_service.search(query=q_clean, limit=3, score_threshold=0.30)
            hits = search_result.get("results", [])
        except Exception as e:
            hits = []

        if hits:
            top_hit = hits[0]
            # Synthesize answer from top retrieved chunks
            answer_parts = [
                f"Dựa trên tài liệu nghiệp vụ MasterPro về **{top_hit.get('title', 'Quy trình')}**:",
                "",
                top_hit.get("content", "")
            ]

            # If there are additional relevant points from second hit
            if len(hits) > 1 and hits[1].get("score", 0) >= 0.40:
                answer_parts.extend([
                    "",
                    f"**Bổ sung từ {hits[1].get('title')}:**",
                    hits[1].get("content", "")
                ])

            citations = []
            for h in hits:
                citations.append({
                    "title": h.get("title"),
                    "document": h.get("source") or "Tài liệu MasterPro",
                    "page": h.get("page") or 1,
                    "chunk_id": f"chunk_{h.get('document_id')}_{h.get('chunk_index', 1)}",
                    "score": h.get("score"),
                    "heading_path": h.get("heading_path")
                })

            return {
                "answer": "\n".join(answer_parts),
                "citations": citations,
                "provider": "masterpro-rag",
                "model": "qdrant-retrieval-v1"
            }
        else:
            return {
                "answer": f"Không tìm thấy thông tin đủ tin cậy trong tài liệu MasterPro cho câu hỏi: *\"{q_clean}\"*.\n\nVui lòng thử lại với từ khóa cụ thể hơn (ví dụ: *'kết số'*, *'máy in'*, *'phiếu xuất kho'*), hoặc liên hệ chuyên viên hỗ trợ cấp 2.",
                "citations": [],
                "provider": "masterpro-rag",
                "model": "qdrant-retrieval-v1"
            }

def get_ai_provider() -> BaseAIProvider:
    return RAGAIProvider()
