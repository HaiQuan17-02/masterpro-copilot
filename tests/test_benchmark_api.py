"""
Unit & Integration Tests for Stress Benchmark API (Week 11 - Gate 3 Milestone).
"""

import unittest
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai"))
for p in [backend_dir, ai_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi.testclient import TestClient
from app.main import app


class TestBenchmarkAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_benchmark_metrics(self):
        """Kiểm tra API trả về dữ liệu hiệu năng Gate 3 hợp lệ."""
        res = self.client.get("/api/benchmark/metrics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "PASSED")
        self.assertGreaterEqual(data["groundedness_score_percent"], 90.0)
        self.assertLess(data["p95_latency_ms"], 2000.0)
        self.assertEqual(data["error_rate_percent"], 0.0)

    def test_run_quick_test(self):
        """Kiểm tra API chạy benchmark nhanh 5 câu hỏi nghiệp vụ và đo độ trễ."""
        res = self.client.post("/api/benchmark/quick-test")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["queries_tested"], 5)
        self.assertGreater(data["total_duration_ms"], 0)
        self.assertLess(data["avg_latency_ms"], 500.0)
        self.assertEqual(len(data["details"]), 5)


if __name__ == "__main__":
    unittest.main()
