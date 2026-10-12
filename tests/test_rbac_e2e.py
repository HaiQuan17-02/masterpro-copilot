"""
Unit and E2E RBAC Integration Tests (Week 8 - Gate 2 Milestone).
Validates Role-Based Access Control, JWT authentication, and Qdrant retrieval isolation.
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.services.search_service import SearchService


class TestRBACE2E(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.search_service = SearchService.get_instance()

    def test_login_demo_roles(self):
        """Kiểm tra xác thực đăng nhập cấp JWT Token chuẩn cho các vai trò."""
        roles_to_test = [
            ("cashier1", "123", "cashier"),
            ("inventory1", "123", "inventory"),
            ("accountant1", "123", "accountant"),
            ("admin", "admin123", "admin")
        ]
        for uname, pwd, expected_role in roles_to_test:
            res = self.client.post("/api/auth/login", json={"username": uname, "password": pwd})
            self.assertEqual(res.status_code, 200, f"Đăng nhập thất bại cho {uname}")
            data = res.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["user"]["role"], expected_role)

    def test_login_invalid_credentials(self):
        """Kiểm tra từ chối đăng nhập khi sai mật khẩu."""
        res = self.client.post("/api/auth/login", json={"username": "cashier1", "password": "wrongpassword"})
        self.assertEqual(res.status_code, 401)

    def test_cashier_rbac_allowed_queries(self):
        """Kiểm tra Thu ngân (Cashier) truy vấn thành công tài liệu POS & Hóa đơn."""
        res = self.search_service.search(
            query="Cấu hình máy in và thiết lập thông số hệ thống",
            limit=3,
            user_role="cashier"
        )
        self.assertGreater(res["total"], 0)
        # Kết quả phải thuộc phạm vi cho phép
        allowed_keywords = self.search_service.ROLE_MODULE_MAPPING["cashier"]
        for hit in res["results"]:
            combined_text = f"{hit.get('module', '')} {hit.get('title', '')} {hit.get('heading_path', '')}".lower()
            self.assertTrue(any(kw in combined_text for kw in allowed_keywords))

    def test_cashier_rbac_blocked_finance_query(self):
        """Kiểm tra Thu ngân (Cashier) bị chặn khi cố tra cứu tài liệu Sổ quỹ / Tài chính kế toán."""
        res = self.search_service.search(
            query="Báo cáo thuế giá trị gia tăng và hạch toán sổ quỹ kế toán",
            limit=3,
            user_role="cashier"
        )
        # Vì câu hỏi thuần túy về kế toán, các tài liệu tài chính bị lọc khỏi kết quả của Cashier
        for hit in res["results"]:
            h_mod = (hit.get("module") or "").lower()
            self.assertNotIn("sổ quỹ", h_mod)
            self.assertNotIn("kế toán", h_mod)

    def test_admin_rbac_unrestricted_access(self):
        """Kiểm tra Quản trị viên (Admin) có quyền truy cập toàn bộ tài liệu hệ thống."""
        res = self.search_service.search(
            query="Cấu hình hệ thống và khóa sổ",
            limit=3,
            user_role="admin"
        )
        self.assertGreater(res["total"], 0)

    def test_chat_stream_with_role_header(self):
        """Kiểm tra SSE Stream endpoint nhận biết vai trò qua Header X-User-Role."""
        res = self.client.post(
            "/api/chat/stream",
            json={"message": "Cách in lại hóa đơn cho khách"},
            headers={"X-User-Role": "cashier"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))
        self.assertIn("cashier", res.text)


if __name__ == "__main__":
    unittest.main()
