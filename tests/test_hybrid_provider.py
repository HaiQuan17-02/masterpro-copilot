"""
Unit and Integration Tests for Hybrid Provider and Fallback Engine (Week 10).
"""

import unittest
import os
import sys
import asyncio

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai"))
for p in [backend_dir, ai_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app
from ai.providers.offline_provider import OfflineFallbackProvider
from ai.providers.online_provider import OnlineLLMProvider
from ai.providers.base_provider import ProviderUnavailableError
from ai.providers.hybrid_manager import HybridProviderManager


class TestHybridProvider(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.manager = HybridProviderManager.get_instance()
        # Reset to auto mode
        self.manager.set_mode("auto")
        self.manager.online_provider.set_simulate_failure(False)

    def test_offline_fallback_provider_generation(self):
        """Kiểm tra Offline Synthesizer tạo văn bản chuẩn tiếng Việt và citation mà không cần mạng."""
        provider = OfflineFallbackProvider()
        chunks = [
            {
                "document_id": "doc_hdsd_004",
                "title": "Cấu hình máy in POS",
                "module": "Hệ thống",
                "page": 2,
                "content": "Kiểm tra dây cáp máy in và chọn đúng Driver K80."
            }
        ]

        async def run_gen():
            tokens = []
            async for t in provider.generate_stream("Cách sửa máy in", chunks):
                tokens.append(t)
            return "".join(tokens)

        text = asyncio.run(run_gen())
        self.assertIn("Hệ thống", text)
        self.assertIn("doc_hdsd_004", text)
        self.assertIn("[cite: doc_hdsd_004, trang 2]", text)

    def test_online_provider_failure_when_no_key(self):
        """Kiểm tra Online Provider báo lỗi ProviderUnavailableError khi không có API key hoặc lỗi mạng."""
        online_p = OnlineLLMProvider(api_key="")
        chunks = [{"document_id": "d1", "content": "test"}]

        async def run_fail():
            async for _ in online_p.generate_stream("test", chunks):
                pass

        with self.assertRaises(ProviderUnavailableError):
            asyncio.run(run_fail())

    def test_hybrid_manager_automatic_fallback(self):
        """Kiểm tra Hybrid Manager tự động fallback sang Offline Synthesizer trong 0ms."""
        # Giả lập lỗi mạng online provider
        self.manager.online_provider.set_simulate_failure(True)

        chunks = [
            {
                "document_id": "doc_test",
                "title": "Chính sách giá",
                "module": "Bán hàng",
                "page": 1,
                "content": "Giá bán niêm yết đã bao gồm thuế VAT."
            }
        ]

        async def run_hybrid():
            tokens = []
            is_fallback_recorded = False
            async for tok, prov_name, is_fb in self.manager.generate_stream("Hỏi giá", chunks):
                tokens.append(tok)
                if is_fb:
                    is_fallback_recorded = True
            return "".join(tokens), is_fallback_recorded

        full_text, was_fallback = asyncio.run(run_hybrid())
        self.assertTrue(was_fallback)
        self.assertIn("Bán hàng", full_text)
        self.assertIn("doc_test", full_text)
        self.assertGreater(self.manager.consecutive_failures, 0)

    def test_api_provider_status_and_mode_switch(self):
        """Kiểm tra API chuyển mode sang offline_only và đọc trạng thái telemetry."""
        # 1. Đọc status
        res = self.client.get("/api/provider/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("mode", data)
        self.assertIn("is_online_available", data)

        # 2. Đổi mode sang offline_only
        mode_res = self.client.post("/api/provider/mode", json={"mode": "offline_only"})
        self.assertEqual(mode_res.status_code, 200)
        self.assertEqual(mode_res.json()["current_mode"], "offline_only")

        # 3. Giả lập bật cờ simulate-failure
        sim_res = self.client.post("/api/provider/simulate-failure", json={"simulate_failure": True})
        self.assertEqual(sim_res.status_code, 200)
        self.assertTrue(sim_res.json()["simulate_failure"])

        # Reset lại
        self.client.post("/api/provider/simulate-failure", json={"simulate_failure": False})
        self.client.post("/api/provider/mode", json={"mode": "auto"})

    def test_chat_stream_includes_provider_metadata(self):
        """Kiểm tra SSE Chat stream gửi metadata chứa thông tin Provider và Fallback."""
        res = self.client.post(
            "/api/chat/stream",
            json={"message": "Cấu hình máy in và thiết lập thông số hệ thống"}
        )
        self.assertEqual(res.status_code, 200)
        content = res.text
        self.assertIn('"type": "metadata"', content)
        self.assertIn('"provider":', content)
        self.assertIn('"fallback_mode":', content)


if __name__ == "__main__":
    unittest.main()
