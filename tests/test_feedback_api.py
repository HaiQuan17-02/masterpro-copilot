import unittest
import os
import sys

# Ensure backend directory is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.feedback_service import get_feedback_service


class TestFeedbackEscalationAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.service = get_feedback_service()

    def test_submit_positive_feedback(self):
        """Kiểm tra gửi đánh giá tích cực (Like) kèm doc_id."""
        payload = {
            "message_id": "msg_001",
            "rating": "like",
            "comment": "Rất rõ ràng, làm đúng các bước là in hóa đơn được ngay",
            "cited_doc_ids": ["doc_hdsd_001"],
            "query": "Làm thế nào để in lại hóa đơn?"
        }
        res = self.client.post("/api/feedback", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("feedback_id", data)

    def test_submit_negative_feedback_with_reason(self):
        """Kiểm tra gửi đánh giá tiêu cực (Dislike) kèm lý do nghiệp vụ."""
        payload = {
            "message_id": "msg_002",
            "rating": "dislike",
            "reason": "incorrect_step",
            "comment": "Bước 3 trong giao diện MasterPro v4 nằm ở góc trên bên phải chứ không phải menu trái",
            "cited_doc_ids": ["doc_hdsd_002"],
            "query": "Cách hủy phiếu tạm tính"
        }
        res = self.client.post("/api/feedback", json=payload)
        self.assertEqual(res.status_code, 200)

        # Kiểm tra stats
        stats_res = self.client.get("/api/feedback/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertGreaterEqual(stats["total"], 1)
        self.assertGreaterEqual(stats["dislikes"], 1)
        self.assertIn("incorrect_step", stats["reason_breakdown"])

    def test_create_and_manage_escalation_ticket(self):
        """Kiểm tra tạo ticket L2 khi Copilot không giải quyết được và cập nhật trạng thái."""
        ticket_payload = {
            "query": "Lỗi lệch tiền ca giao nhận giữa tiền mặt thực tế và số liệu trên máy POS",
            "bot_response": "Kiểm tra lại kết ca và liên hệ quản trị.",
            "conversation_id": "conv_999",
            "user_note": "Đã đếm lại két 3 lần, lệch 150.000đ nhưng không thấy giao dịch bị hủy",
            "priority": "high",
            "user_role": "cashier",
            "retrieved_chunks": [
                {"document_id": "doc_hdsd_002", "title": "Cấu hình kết số"}
            ]
        }
        res = self.client.post("/api/escalation", json=ticket_payload)
        self.assertEqual(res.status_code, 200)
        ticket = res.json()
        ticket_id = ticket["ticket_id"]
        self.assertTrue(ticket_id.startswith("ESC-"))
        self.assertEqual(ticket["priority"], "high")
        self.assertEqual(ticket["status"], "pending")

        # Lấy danh sách ticket pending
        list_res = self.client.get("/api/escalation/tickets?status=pending")
        self.assertEqual(list_res.status_code, 200)
        tickets = list_res.json()
        self.assertTrue(any(t["ticket_id"] == ticket_id for t in tickets))

        # Update trạng thái lên in_progress
        patch_res = self.client.patch(f"/api/escalation/tickets/{ticket_id}?status=in_progress")
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["status"], "in_progress")


if __name__ == "__main__":
    unittest.main()
