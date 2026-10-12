"""
Integration Tests for Ingestion Pipeline API (Week 5).
"""

import sys
import os
import unittest
import io
from fastapi.testclient import TestClient

workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(workspace_dir, "backend")
ai_dir = os.path.join(workspace_dir, "ai")

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from app.main import app


class TestIngestionAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_get_ingestion_stats(self):
        """Kiểm tra API thống kê Ingestion."""
        response = self.client.get("/api/ingestion/stats")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_vectors", data)
        self.assertIn("collection_name", data)
        self.assertGreaterEqual(data["total_vectors"], 50)
        self.assertIn(".md", data["supported_formats"])

    def test_ingest_text_document(self):
        """Kiểm tra nạp tài liệu text/markdown trực tiếp."""
        payload = {
            "title": "Hướng dẫn bảo dưỡng đầu in mã vạch Zebra",
            "content": "## Quy trình bảo dưỡng định kỳ\n\n1. Tắt nguồn máy in Zebra trước khi vệ sinh.\n2. Dùng cồn Isopropyl 99% thấm bông tăm lau thanh nhiệt.\n3. Đợi 5 phút cho cồn bay hơi hoàn toàn trước khi bật máy.",
            "category": "RUNBOOK_L1",
            "module": "Hardware_POS",
            "chunk_size": 400,
            "chunk_overlap": 60
        }
        response = self.client.post("/api/ingestion/text", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "COMPLETED")
        self.assertGreater(data["chunks_count"], 0)
        self.assertIn("job_id", data)

        # Kiểm tra truy vấn lại theo Job ID
        status_res = self.client.get(f"/api/ingestion/status/{data['job_id']}")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.json()
        self.assertEqual(status_data["status"], "COMPLETED")

    def test_ingest_file_upload_markdown(self):
        """Kiểm tra upload file Markdown phân đoạn nạp vào Qdrant."""
        file_content = b"# Huong Dan Kiem Ke Kho Ban Le\n\nBuoc 1: Quet ma vach kiem ke.\nBuoc 2: Chot so ton kho thuc te."
        files = {
            "file": ("HDSD_KiemKe.md", io.BytesIO(file_content), "text/markdown")
        }
        data = {
            "category": "HDSD",
            "module": "Kho hàng",
            "title": "Hướng dẫn kiểm kê kho bán lẻ"
        }
        response = self.client.post("/api/ingestion/file", files=files, data=data)
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertEqual(res_data["status"], "COMPLETED")
        self.assertGreater(res_data["chunks_count"], 0)

    def test_ingest_file_unsupported_extension(self):
        """Kiểm tra từ chối định dạng file không hợp lệ."""
        files = {
            "file": ("malware.exe", io.BytesIO(b"fake binary"), "application/octet-stream")
        }
        response = self.client.post("/api/ingestion/file", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("không được hỗ trợ", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
