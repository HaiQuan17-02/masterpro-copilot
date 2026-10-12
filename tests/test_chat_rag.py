"""
Integration Tests for RAG Chat API (Week 5).
Verifies that chat returns grounded answers with real Qdrant citations.
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


class TestChatRAGAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_chat_greeting(self):
        """Kiểm tra bot phản hồi câu chào mừng thân thiện."""
        response = self.client.post("/api/chat", json={"message": "Xin chào"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("MasterPro Copilot", data["answer"])

    def test_chat_grounded_rag_retrieval(self):
        """Kiểm tra câu hỏi nghiệp vụ trả về câu trả lời kèm citation từ Qdrant."""
        response = self.client.post("/api/chat", json={"message": "Cách cấu hình kết số và khóa sổ"})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("answer", data)
        self.assertIn("citations", data)
        self.assertGreater(len(data["citations"]), 0)

        top_citation = data["citations"][0]
        self.assertIn("title", top_citation)
        self.assertIn("score", top_citation)
        self.assertGreater(top_citation["score"], 0.30)


if __name__ == "__main__":
    unittest.main()
