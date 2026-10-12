"""
Retrieval Benchmark Runner for MasterPro Copilot (Week 4 - Gate 1).

Executes 30 Ground Truth queries against Qdrant Vector Store,
measures Precision@1, Precision@3, MRR, Latency, and verifies Gate 1 criteria.
"""

import os
import sys
import io
import json
import time

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure paths
ai_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.abspath(os.path.join(ai_dir, ".."))
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from qdrant_manager import QdrantVectorStore

def run_benchmark():
    gt_file = os.path.join(workspace_dir, "docs", "testing", "ground_truth_30_queries.json")
    if not os.path.exists(gt_file):
        raise FileNotFoundError(f"Ground truth file not found: {gt_file}")

    with open(gt_file, "r", encoding="utf-8") as f:
        ground_truth = json.load(f)

    store = QdrantVectorStore()
    total_docs = store.count()
    print("=" * 80)
    print(f"BẮT ĐẦU BENCHMARK RETRIEVAL POC (GATE 1) - QDRANT ({total_docs} Points)")
    print("=" * 80)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    latencies = []

    print(f"\n{'ID':<5} | {'Query':<42} | {'Top-1 Match':<20} | {'Score':<6} | {'Status'}")
    print("-" * 88)

    for item in ground_truth:
        q_id = item["id"]
        query = item["query"]
        expected_doc = item["expected_doc_id"]
        expected_module = item["expected_module"]

        start_t = time.perf_counter()
        hits = store.search(query, limit=3, score_threshold=0.30)
        elapsed_ms = (time.perf_counter() - start_t) * 1000
        latencies.append(elapsed_ms)

        hit_doc_ids = [h.get("document_id") for h in hits]
        hit_modules = [h.get("module") for h in hits]

        # Check Top-1 match (by doc_id or module)
        is_top1 = False
        if hits and (hits[0].get("document_id") == expected_doc or hits[0].get("module") == expected_module):
            is_top1 = True
            top1_correct += 1

        # Check Top-3 match
        rank = 0
        for r, h in enumerate(hits, 1):
            if h.get("document_id") == expected_doc or h.get("module") == expected_module:
                rank = r
                break

        if rank > 0:
            top3_correct += 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        top1_title = hits[0].get("title", "N/A")[:18] if hits else "None"
        top1_score = hits[0].get("score", 0.0) if hits else 0.0
        status = "PASSED" if rank > 0 else "MISSED"

        q_display = query[:38] + ".." if len(query) > 40 else query
        print(f"{q_id:<5} | {q_display:<42} | {top1_title:<20} | {top1_score:<6.2f} | {status}")

    n = len(ground_truth)
    p1 = (top1_correct / n) * 100
    p3 = (top3_correct / n) * 100
    mrr = sum(reciprocal_ranks) / n
    avg_latency = sum(latencies) / n

    print("\n" + "=" * 80)
    print("KẾT QUẢ ĐO LƯỜNG ĐỊNH LƯỢNG GATE 1")
    print("=" * 80)
    print(f"- Tổng số câu hỏi kiểm thử : {n}")
    print(f"- Precision@1 (Top-1)     : {p1:.1f}% ({top1_correct}/{n})")
    print(f"- Precision@3 (Top-3)     : {p3:.1f}% ({top3_correct}/{n})")
    print(f"- Mean Reciprocal Rank MRR: {mrr:.3f}")
    print(f"- Độ trễ trung bình       : {avg_latency:.2f} ms")
    print("-" * 80)

    # Validate against Gate 1 criteria
    gate1_pass = True
    print("\n[ĐÁNH GIÁ TIÊU CHÍ GATE 1]")
    if p3 >= 85.0:
        print(f"  [x] Precision@3 đạt {p3:.1f}% >= 85.0% (ĐẠT)")
    else:
        print(f"  [ ] Precision@3 đạt {p3:.1f}% < 85.0% (KHÔNG ĐẠT)")
        gate1_pass = False

    if avg_latency <= 300.0:
        print(f"  [x] Độ trễ trung bình {avg_latency:.2f} ms <= 300 ms (ĐẠT)")
    else:
        print(f"  [ ] Độ trễ trung bình {avg_latency:.2f} ms > 300 ms (KHÔNG ĐẠT)")
        gate1_pass = False

    if total_docs >= 50:
        print(f"  [x] Quy mô index {total_docs} >= 50 documents (ĐẠT)")
    else:
        print(f"  [ ] Quy mô index {total_docs} < 50 documents (KHÔNG ĐẠT)")
        gate1_pass = False

    print("=" * 80)
    if gate1_pass:
        print("KẾT LUẬN: ĐỦ ĐIỀU KIỆN NGHIỆM THU GATE 1 (RETRIEVAL POC HOÀN TẤT)")
    else:
        print("KẾT LUẬN: CHƯA ĐỦ ĐIỀU KIỆN NGHIỆM THU GATE 1")
    print("=" * 80)

    return {
        "precision_1": p1,
        "precision_3": p3,
        "mrr": mrr,
        "avg_latency_ms": avg_latency,
        "gate1_pass": gate1_pass
    }

if __name__ == "__main__":
    run_benchmark()
