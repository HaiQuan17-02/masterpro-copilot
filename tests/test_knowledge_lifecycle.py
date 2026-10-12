"""
Unit and Integration Tests for Knowledge Lifecycle and Document Versioning (Week 9).
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.lifecycle_service import get_lifecycle_service
from app.services.search_service import SearchService


class TestKnowledgeLifecycleAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.lifecycle_service = get_lifecycle_service()
        self.search_service = SearchService.get_instance()

    def test_create_and_submit_lifecycle_document(self):
        """Kiểm tra tạo tài liệu ở trạng thái Draft và gửi sang Under Review."""
        payload = {
            "title": "Quy trình đối soát mã coupon khuyến mãi dịp Tết",
            "content": "# Đối soát coupon Tết\n\n## Hướng dẫn thu ngân\n- Quét mã vạch trên ứng dụng di động.\n- Áp dụng giảm tối đa 20% tổng hóa đơn.",
            "category": "HDSD",
            "module": "Bán hàng",
            "version_id": "v1.0"
        }
        res = self.client.post("/api/lifecycle/documents", json=payload)
        self.assertEqual(res.status_code, 200)
        doc = res.json()
        doc_id = doc["document_id"]
        self.assertEqual(doc["status"], "draft")

        # Gửi duyệt
        submit_res = self.client.post(f"/api/lifecycle/documents/{doc_id}/submit")
        self.assertEqual(submit_res.status_code, 200)
        self.assertEqual(submit_res.json()["current_status"], "under_review")

    def test_approve_and_index_document(self):
        """Kiểm tra phê duyệt tài liệu và xác nhận lập chỉ mục vào Qdrant."""
        payload = {
            "title": "Chính sách đổi trả hàng hóa trong 7 ngày",
            "content": "# Chính sách đổi trả\n\n## Điều kiện áp dụng\n- Hàng hóa còn nguyên tem mác.\n- Có hóa đơn mua hàng MasterPro hợp lệ.",
            "category": "HDSD",
            "module": "Bán hàng",
            "version_id": "v1.0"
        }
        create_res = self.client.post("/api/lifecycle/documents", json=payload)
        doc_id = create_res.json()["document_id"]

        approve_res = self.client.post(f"/api/lifecycle/documents/{doc_id}/approve?approver=TesterAdmin")
        self.assertEqual(approve_res.status_code, 200)
        data = approve_res.json()
        self.assertEqual(data["current_status"], "approved")
        self.assertGreater(data["chunks_indexed"], 0)

    def test_supersede_old_version(self):
        """Kiểm tra thay thế tài liệu cũ (Superseded) và cô lập khỏi retrieval."""
        # Bước 1: Tạo và duyệt phiên bản v1
        v1_payload = {
            "title": "Quy định chiết khấu đại lý v1 cũ",
            "content": "# Chiết khấu cũ\n\nĐại lý cấp 1 được chiết khấu cố định 10% trên giá bán buôn.",
            "category": "HDSD",
            "module": "Bán hàng",
            "version_id": "v1.0"
        }
        v1_doc = self.client.post("/api/lifecycle/documents", json=v1_payload).json()
        v1_id = v1_doc["document_id"]
        self.client.post(f"/api/lifecycle/documents/{v1_id}/approve")

        # Bước 2: Tạo phiên bản v2 thay thế v1
        v2_payload = {
            "title": "Quy định chiết khấu đại lý v2 mới 2026",
            "content": "# Chiết khấu mới 2026\n\nĐại lý cấp 1 được chiết khấu linh hoạt 15% theo doanh số tháng.",
            "category": "HDSD",
            "module": "Bán hàng",
            "version_id": "v2.0",
            "supersedes_doc_id": v1_id
        }
        v2_doc = self.client.post("/api/lifecycle/documents", json=v2_payload).json()
        v2_id = v2_doc["document_id"]

        # Duyệt v2
        approve_v2_res = self.client.post(f"/api/lifecycle/documents/{v2_id}/approve")
        self.assertEqual(approve_v2_res.status_code, 200)

        # Bước 3: Xác nhận v1 chuyển sang trạng thái superseded
        get_v1_res = self.client.get(f"/api/lifecycle/documents/{v1_id}")
        self.assertEqual(get_v1_res.status_code, 200)
        v1_data = get_v1_res.json()
        self.assertEqual(v1_data["status"], "superseded")
        self.assertEqual(v1_data["superseded_by"], v2_id)

    def test_reindex_all_active_documents(self):
        """Kiểm tra API Reindex toàn bộ tài liệu Approved."""
        res = self.client.post("/api/lifecycle/reindex")
        self.assertEqual(res.status_code, 200)
        report = res.json()
        self.assertGreater(report["approved_documents"], 0)
        self.assertGreater(report["total_chunks_indexed"], 0)


if __name__ == "__main__":
    unittest.main()
