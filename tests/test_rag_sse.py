"""
Integration Tests for RAG Core & SSE Streaming (Week 6).
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(workspace_dir, "backend")
ai_dir = os.path.join(workspace_dir, "ai")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from app.main import app
from citation_validator import CitationValidator
from prompts.masterpro_rag_prompt import build_rag_prompt


class TestRAGStreamAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_sse_stream_post(self):
        """Kiểm tra POST /api/chat/stream trả về Server-Sent Events đúng chuẩn."""
        response = self.client.post("/api/chat/stream", json={"message": "cách khóa sổ kết số"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])

        content = response.text
        self.assertIn("data:", content)
        self.assertIn("[DONE]", content)
        self.assertIn("metadata", content)
        self.assertIn("token", content)

    def test_sse_stream_get(self):
        """Kiểm tra GET /api/chat/stream cho EventSource browser compatibility."""
        response = self.client.get("/api/chat/stream?q=máy in hóa đơn")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/event-stream", response.headers["content-type"])
        self.assertIn("[DONE]", response.text)

    def test_citation_validator_groundedness(self):
        """Kiểm tra CitationValidator nhận diện chính xác trích dẫn hợp lệ."""
        sample_context = [
            {"document_id": "doc_hdsd_002", "page": 5, "title": "Cấu hình kết số và khóa sổ"}
        ]
        grounded_answer = "Vào mục Thiết lập cửa hàng -> Hệ thống -> chọn Khóa số [cite: doc_hdsd_002, trang 5]."
        res = CitationValidator.validate(grounded_answer, sample_context)

        self.assertTrue(res["is_grounded"])
        self.assertEqual(res["valid_citations"], 1)
        self.assertEqual(res["invalid_citations"], 0)
        self.assertEqual(res["groundedness_score"], 1.0)

    def test_citation_validator_hallucination_detection(self):
        """Kiểm tra CitationValidator phát hiện trích dẫn bịa đặt ngoài context."""
        sample_context = [
            {"document_id": "doc_hdsd_002", "page": 5, "title": "Cấu hình kết số"}
        ]
        hallucinated_answer = "Cứ rút dây nguồn ra là được [cite: doc_fake_999, trang 99]."
        res = CitationValidator.validate(hallucinated_answer, sample_context)

        self.assertFalse(res["is_grounded"])
        self.assertEqual(res["valid_citations"], 0)
        self.assertEqual(res["invalid_citations"], 1)
        self.assertEqual(res["groundedness_score"], 0.0)

    def test_prompt_builder(self):
        """Kiểm tra Prompt Builder đóng gói ngữ cảnh chuẩn xác."""
        chunks = [
            {"document_id": "DOC_01", "page": 10, "heading_path": "Hệ thống > In", "content": "Nội dung mẫu"}
        ]
        prompt = build_rag_prompt("Kiểm tra máy in", chunks)
        self.assertIn("DOC_01", prompt)
        self.assertIn("Trang: 10", prompt)
        self.assertIn("CÂU HỎI CỦA NGƯỜI DÙNG:", prompt)


if __name__ == "__main__":
    unittest.main()
