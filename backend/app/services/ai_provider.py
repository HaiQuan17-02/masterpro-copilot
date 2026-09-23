from typing import List, Dict, Any, Optional
import os
from app.core.config import settings

class BaseAIProvider:
    async def generate_response(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        raise NotImplementedError

class MockAIProvider(BaseAIProvider):
    """
    Mock AI Provider for development and testing without requiring external API keys.
    Simulates retrieval-augmented answers with realistic citations.
    """
    async def generate_response(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        q_lower = question.lower()

        if "máy in" in q_lower or "printer" in q_lower or "in" in q_lower:
            return {
                "answer": "Để xử lý sự cố máy in không nhận lệnh hoặc không in được, bạn có thể thực hiện theo các bước sau:\n1. **Kiểm tra nguồn điện**: Đảm bảo dây nguồn cắm chặt và đèn nguồn máy in sáng xanh.\n2. **Kiểm tra kết nối cáp / mạng**: Rút và cắm lại cáp USB hoặc kiểm tra địa chỉ IP máy in trong mạng LAN nội bộ.\n3. **Kiểm tra khay giấy và mực in**: Xác nhận khay nạp còn giấy chuẩn khổ và hộp mực không bị kẹt.\n4. **Khởi động lại dịch vụ Print Spooler** trên máy tính hoặc restart máy in để xóa hàng đợi lệnh in cũ.",
                "citations": [
                    {
                        "title": "Hướng dẫn xử lý lỗi thiết bị bán hàng & Máy in",
                        "document": "HDSD_ThietBi_MasterPro_v1.2.pdf",
                        "page": 15,
                        "chunk_id": "chunk_doc_001_p15",
                        "score": 0.94
                    },
                    {
                        "title": "Cấu hình cổng COM/USB máy in hóa đơn bill",
                        "document": "CauHinh_PhanCung_v2.0.pdf",
                        "page": 7,
                        "chunk_id": "chunk_doc_003_p7",
                        "score": 0.88
                    }
                ],
                "provider": "mock",
                "model": "mock-rag-v1"
            }
        elif "chào" in q_lower or "hello" in q_lower or "hi" in q_lower:
            return {
                "answer": "Xin chào! Tôi là **MasterPro Copilot** - trợ lý AI hỗ trợ tra cứu tài liệu vận hành và kỹ thuật của hệ thống MasterPro. Tôi có thể giúp gì cho bạn hôm nay?",
                "citations": [],
                "provider": "mock",
                "model": "mock-rag-v1"
            }
        else:
            return {
                "answer": f"Hệ thống đã tiếp nhận câu hỏi của bạn: \"{question}\". Dựa trên cơ sở tri thức hiện tại của MasterPro Copilot, tính năng và quy trình liên quan đã sẵn sàng.",
                "citations": [
                    {
                        "title": "Tài liệu tổng quan hệ thống MasterPro Copilot",
                        "document": "TongQuan_MasterPro_2026.pdf",
                        "page": 1,
                        "chunk_id": "chunk_overview_01",
                        "score": 0.82
                    }
                ],
                "provider": "mock",
                "model": "mock-rag-v1"
            }

def get_ai_provider() -> BaseAIProvider:
    if settings.AI_PROVIDER.lower() == "mock":
        return MockAIProvider()
    # Placeholder for OpenAI or Gemini when API key is provided
    return MockAIProvider()
