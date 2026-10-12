"""
Unit & Integration Tests for MasterPro Search API (Week 4 - Retrieval PoC).
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure backend and ai modules are on path
workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(workspace_dir, "backend")
ai_dir = os.path.join(workspace_dir, "ai")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from app.main import app


class TestSearchAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_search_filters(self):
        """Kiểm tra API lấy danh sách bộ lọc Category và Module."""
        response = self.client.get("/api/search/filters")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertIn("modules", data)
        self.assertIn("HDSD", data["categories"])
        self.assertIn("Kho hàng", data["modules"])

    def test_semantic_search_basic(self):
        """Kiểm tra tìm kiếm ngữ nghĩa cơ bản qua Qdrant."""
        payload = {
            "query": "cách phân quyền người dùng theo kho",
            "limit": 3,
            "score_threshold": 0.30
        }
        response = self.client.post("/api/search", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["query"], payload["query"])
        self.assertGreater(data["total"], 0)
        self.assertIsInstance(data["results"], list)
        self.assertGreater(len(data["results"]), 0)
        self.assertIn("latency_ms", data)
        self.assertLess(data["latency_ms"], 300.0)

        # Kiểm tra cấu trúc item kết quả
        top_hit = data["results"][0]
        self.assertIn("score", top_hit)
        self.assertIn("title", top_hit)
        self.assertIn("content", top_hit)
        self.assertIn("heading_path", top_hit)
        self.assertGreater(top_hit["score"], 0.30)

    def test_search_with_module_filter(self):
        """Kiểm tra tìm kiếm kết hợp bộ lọc Module."""
        payload = {
            "query": "quản lý kho hàng",
            "limit": 3,
            "module": "Kho hàng",
            "score_threshold": 0.20
        }
        response = self.client.post("/api/search", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        for hit in data["results"]:
            self.assertEqual(hit["module"], "Kho hàng")

    def test_search_empty_query_validation(self):
        """Kiểm tra validation khi query rỗng (phải trả về 422)."""
        response = self.client.post("/api/search", json={"query": ""})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
