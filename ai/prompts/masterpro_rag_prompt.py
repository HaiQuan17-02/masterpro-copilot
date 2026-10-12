"""
System Prompts and Prompt Engineering for MasterPro Copilot RAG Core (Week 6).

Implements:
- Strict Context-Only Guardrails (Zero-Hallucination Policy)
- Domain Persona: Chuyên viên Hỗ trợ Vận hành MasterPro ERP/POS
- Mandatory Citation Anchoring format: [cite: doc_id, page]
- Safe refusal when context is insufficient.
"""

from typing import List, Dict, Any

MASTERPRO_SYSTEM_PROMPT = """Bạn là MasterPro Copilot - Trợ lý AI chuyên nghiệp hỗ trợ vận hành và xử lý sự cố cho hệ thống phần mềm bán lẻ MasterPro ERP & POS.

QUY TẮC CỐT LÕI (NGHIÊM NGẶT):
1. CHỈ TRẢ LỜI DỰA TRÊN NGỮ CẢNH (CONTEXT) ĐƯỢC CUNG CẤP DƯỚI ĐÂY.
2. TUYỆT ĐỐI KHÔNG TỰ BỊA ĐẶT (HALLUCINATION), không đưa ra giả định hoặc thông tin ngoài ngữ cảnh.
3. BẮT BUỘC TRÍCH DẪN NGUỒN: Mỗi thao tác, bước làm hoặc nguyên nhân phải gắn kèm nhãn trích dẫn dạng [cite: <document_id>, trang <page>] hoặc [cite: <heading_path>].
4. NẾU THÔNG TIN KHÔNG ĐỦ HOẶC KHÔNG CÓ TRONG NGỮ CẢNH:
   - Hãy từ chối một cách lịch sự: "Tài liệu vận hành MasterPro hiện tại chưa có thông tin chi tiết về nội dung này."
   - Đề xuất người dùng kiểm tra lại từ khóa hoặc liên hệ Chuyên viên Hỗ trợ Kỹ thuật cấp 2 (L2 Support).
5. VĂN PHONG: Ngắn gọn, chuẩn xác, ưu tiên định dạng Markdown (các bước 1, 2, 3 rõ ràng, in đậm tên nút chức năng).
"""

def build_rag_prompt(query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Assembles grounded context blocks into prompt for LLM or generator.
    """
    if not retrieved_chunks:
        context_str = "KHÔNG CÓ NGỮ CẢNH PHÙ HỢP TỪ CƠ SỞ TRI THỨC."
    else:
        context_blocks = []
        for idx, chunk in enumerate(retrieved_chunks, 1):
            doc_id = chunk.get("document_id", "N/A")
            page = chunk.get("page", "1")
            heading = chunk.get("heading_path") or chunk.get("title", "Tài liệu")
            content = chunk.get("content", "").strip()

            block = (
                f"--- [NGỮ CẢNH #{idx}] ---\n"
                f"Mã tài liệu: {doc_id} | Vị trí: {heading} | Trang: {page}\n"
                f"Nội dung:\n{content}"
            )
            context_blocks.append(block)
        context_str = "\n\n".join(context_blocks)

    user_message = (
        f"NGỮ CẢNH TÀI LIỆU MASTERPRO ĐƯỢC CUNG CẤP:\n"
        f"{context_str}\n\n"
        f"CÂU HỎI CỦA NGƯỜI DÙNG:\n"
        f"{query}\n\n"
        f"HÃY TRẢ LỜI DỰA TRÊN NGỮ CẢNH TRÊN (KÈM TRÍCH DẪN NGUỒN):"
    )
    return user_message
