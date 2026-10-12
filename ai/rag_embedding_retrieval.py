import sys
import os
import io
import re
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure backend and ai modules are accessible
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.core.database import SessionLocal
from app.models.document import Document
from benchmark_chunking import chunk_strategy_d_structure_aware

# =============================================================================
# 1. EMBEDDING PROVIDER & VECTOR STORE
# =============================================================================
class VietnameseEmbeddingRetriever:
    """
    RAG Retrieval Engine for Vietnamese Enterprise ERP/POS documents.
    Combines Word N-gram and Character N-gram TF-IDF vectors
    to capture both exact technical keywords and Vietnamese morphological roots.
    Supports OpenAI Embedding API when configured.
    """

    def __init__(self, provider: str = "hybrid_vietnamese", model_name: str = "text-embedding-3-small"):
        self.provider = os.getenv("EMBEDDING_PROVIDER", provider)
        self.model_name = os.getenv("EMBEDDING_MODEL", model_name)
        self.api_key = os.getenv("AI_API_KEY", "")
        self.chunks = []
        self.vectorizer = None
        self.chunk_vectors = None

    def fit_and_embed(self, chunks: List[Dict[str, Any]]):
        """Builds vector representation for all chunks."""
        self.chunks = chunks
        corpus = [c["content"] for c in chunks]

        # Dual word & sub-character n-gram vectorizer optimized for Vietnamese
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            analyzer="word",
            lowercase=True,
            sublinear_tf=True
        )
        self.chunk_vectors = self.vectorizer.fit_transform(corpus)
        print(f"[{self.provider}] Successfully embedded {len(chunks)} chunks into vector space of {self.chunk_vectors.shape[1]} dimensions.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Performs cosine similarity search over chunk vectors."""
        if self.vectorizer is None or self.chunk_vectors is None:
            raise ValueError("Retriever has not been fitted with chunks yet.")

        query_vec = self.vectorizer.transform([query])
        sim_scores = cosine_similarity(query_vec, self.chunk_vectors)[0]

        top_indices = np.argsort(sim_scores)[::-1][:top_k]

        results = []
        for rank, idx in enumerate(top_indices, 1):
            chunk = self.chunks[idx]
            results.append({
                "rank": rank,
                "document_id": chunk["document_id"],
                "category": chunk["category"],
                "module": chunk["module"],
                "title": chunk["title"],
                "source": chunk["source"],
                "page": chunk.get("page"),
                "score": float(sim_scores[idx]),
                "snippet": chunk["content"][:150] + "..."
            })
        return results

    def save_index(self, filepath: str):
        """Persists the vector index metadata to disk."""
        data = {
            "provider": self.provider,
            "model_name": self.model_name,
            "total_chunks": len(self.chunks),
            "chunks": self.chunks
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Vector index metadata saved to: {filepath}")

# =============================================================================
# 2. 30 TEST QUERIES BENCHMARK SUITE
# =============================================================================
TEST_QUERIES = [
    # --- 10 HDSD QUERIES ---
    {
        "id": 1,
        "category": "HDSD",
        "query": "Làm sao để đăng nhập vào phần mềm MasterPro?",
        "expected_id": 1,
        "expected_title": "Đăng nhập vào hệ thống"
    },
    {
        "id": 2,
        "category": "HDSD",
        "query": "Cách cấu hình kết số và khóa sổ dữ liệu kế toán?",
        "expected_id": 2,
        "expected_title": "Cấu hình kết số và khóa sổ"
    },
    {
        "id": 3,
        "category": "HDSD",
        "query": "Quy trình thêm mới một danh mục kho hàng?",
        "expected_id": 5,
        "expected_title": "Thêm mới danh mục kho hàng"
    },
    {
        "id": 4,
        "category": "HDSD",
        "query": "Cách tạo phương thức giảm quỹ hoặc chi khác?",
        "expected_id": 9,
        "expected_title": "Tạo phương thức giảm quỹ (Chi khác)"
    },
    {
        "id": 5,
        "category": "HDSD",
        "query": "Làm thế nào để thêm mới tài khoản ngân hàng hoặc thẻ?",
        "expected_id": 11,
        "expected_title": "Thêm mới tài khoản ngân hàng / thẻ"
    },
    {
        "id": 6,
        "category": "HDSD",
        "query": "Làm sao để import danh sách sản phẩm hàng loạt từ Excel?",
        "expected_id": 23,
        "expected_title": "Nhập danh sách sản phẩm hàng loạt từ Excel"
    },
    {
        "id": 7,
        "category": "HDSD",
        "query": "Cách cập nhật giá bán danh mục từ file Excel?",
        "expected_id": 24,
        "expected_title": "Cập nhật giá bán danh mục từ Excel"
    },
    {
        "id": 8,
        "category": "HDSD",
        "query": "Cách tạo phiếu bán lẻ tại quầy thu ngân POS?",
        "expected_id": 39,
        "expected_title": "Tạo phiếu bán lẻ tại quầy"
    },
    {
        "id": 9,
        "category": "HDSD",
        "query": "Cài đặt chương trình khuyến mãi mua hàng này tặng hàng khác KM 03?",
        "expected_id": 46,
        "expected_title": "Cài đặt KM 03: Mua hàng này tặng hàng khác"
    },
    {
        "id": 10,
        "category": "HDSD",
        "query": "Quy trình xuất nhập điều chỉnh kho thủ công?",
        "expected_id": 50,
        "expected_title": "Xuất/Nhập điều chỉnh kho thủ công"
    },

    # --- 10 FAQ QUERIES ---
    {
        "id": 11,
        "category": "FAQ",
        "query": "Tôi có thể đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc không?",
        "expected_id": 51,
        "expected_title": "Tôi có thể đăng nhập một tài khoản ở nhiều chi nhánh cùng lúc không?"
    },
    {
        "id": 12,
        "category": "FAQ",
        "query": "Mã kho phải đặt như thế nào?",
        "expected_id": 52,
        "expected_title": "Quy tắc đặt Mã kho hàng mới trên phần mềm như thế nào?"
    },
    {
        "id": 13,
        "category": "FAQ",
        "query": "Kho hàng đã phát sinh hóa đơn bán hoặc nhập có xóa được không?",
        "expected_id": 53,
        "expected_title": "Kho hàng đã phát sinh hóa đơn bán hoặc nhập có xóa được không?"
    },
    {
        "id": 14,
        "category": "FAQ",
        "query": "Chỉ số Đầu kỳ trong khai báo Tài khoản ngân hàng có ý nghĩa gì?",
        "expected_id": 56,
        "expected_title": "Chỉ số Đầu kỳ trong khai báo Tài khoản ngân hàng có ý nghĩa gì?"
    },
    {
        "id": 15,
        "category": "FAQ",
        "query": "Điều kiện để xóa vĩnh viễn một sản phẩm khỏi danh mục là gì?",
        "expected_id": 57,
        "expected_title": "Điều kiện để xóa vĩnh viễn một sản phẩm khỏi danh mục là gì?"
    },
    {
        "id": 16,
        "category": "FAQ",
        "query": "Khi import sản phẩm từ Excel, các cột màu nào là bắt buộc?",
        "expected_id": 58,
        "expected_title": "Khi import sản phẩm từ Excel, các cột màu nào là bắt buộc?"
    },
    {
        "id": 17,
        "category": "FAQ",
        "query": "Tại sao không import được định mức thành phẩm từ Excel?",
        "expected_id": 60,
        "expected_title": "Tại sao không import được định mức thành phẩm từ Excel?"
    },
    {
        "id": 18,
        "category": "FAQ",
        "query": "Đơn đặt hàng có làm tăng tồn kho ngay không?",
        "expected_id": 63,
        "expected_title": "Đơn đặt hàng nhà cung cấp (PO) có làm tăng tồn kho ngay không?"
    },
    {
        "id": 19,
        "category": "FAQ",
        "query": "Khách hàng đặt cọc khi đặt mua hàng được ghi nhận vào đâu?",
        "expected_id": 66,
        "expected_title": "Khách hàng đặt cọc khi đặt mua hàng được ghi nhận vào đâu?"
    },
    {
        "id": 20,
        "category": "FAQ",
        "query": "Tại sao trên hóa đơn bán không tự động nhảy chương trình khuyến mãi?",
        "expected_id": 73,
        "expected_title": "Tại sao trên hóa đơn bán không tự động nhảy chương trình khuyến mãi?"
    },

    # --- 10 RUNBOOK_L1 QUERIES ---
    {
        "id": 21,
        "category": "RUNBOOK_L1",
        "query": "Tôi không đăng nhập được MasterPro thì phải làm gì?",
        "expected_id": 81,
        "expected_title": "Sự cố không đăng nhập được phần mềm hoặc sai chi nhánh"
    },
    {
        "id": 22,
        "category": "RUNBOOK_L1",
        "query": "Quy trình khởi tạo nhanh một kho hàng mới và cấp quyền sử dụng cho user?",
        "expected_id": 82,
        "expected_title": "Quy trình khởi tạo nhanh một kho hàng mới và cấp quyền sử dụng"
    },
    {
        "id": 23,
        "category": "RUNBOOK_L1",
        "query": "Quy trình import bảng giá mới áp dụng từ đầu tháng?",
        "expected_id": 83,
        "expected_title": "Quy trình import bảng giá mới áp dụng từ đầu tháng"
    },
    {
        "id": 24,
        "category": "RUNBOOK_L1",
        "query": "Làm thế nào xử lý lỗi import Excel?",
        "expected_id": 84,
        "expected_title": "Xử lý lỗi import Excel báo sai định dạng hoặc thiếu cột"
    },
    {
        "id": 25,
        "category": "RUNBOOK_L1",
        "query": "Quy trình khởi tạo dữ liệu công nợ đầu kỳ khi golive phần mềm?",
        "expected_id": 85,
        "expected_title": "Quy trình khởi tạo dữ liệu công nợ đầu kỳ khi golive phần mềm"
    },
    {
        "id": 26,
        "category": "RUNBOOK_L1",
        "query": "Quy trình duyệt đơn đặt hàng nhập và chuyển thành phiếu nhập kho?",
        "expected_id": 86,
        "expected_title": "Quy trình duyệt đơn đặt hàng nhập và chuyển thành phiếu nhập kho"
    },
    {
        "id": 27,
        "category": "RUNBOOK_L1",
        "query": "Quy trình xuất trả hàng cho Nhà cung cấp bị lỗi hỏng?",
        "expected_id": 87,
        "expected_title": "Quy trình xuất trả hàng cho Nhà cung cấp bị lỗi/hỏng"
    },
    {
        "id": 28,
        "category": "RUNBOOK_L1",
        "query": "Quy trình thu ngân xử lý hóa đơn bán lẻ có đổi điểm tích lũy?",
        "expected_id": 88,
        "expected_title": "Quy trình thu ngân xử lý hóa đơn bán lẻ có đổi điểm tích lũy"
    },
    {
        "id": 29,
        "category": "RUNBOOK_L1",
        "query": "Khi khách trả hàng thì xử lý thế nào?",
        "expected_id": 90,
        "expected_title": "Quy trình xử lý khách trả lại hàng đã mua bằng hóa đơn bán lẻ"
    },
    {
        "id": 30,
        "category": "RUNBOOK_L1",
        "query": "Xử lý lỗi không sửa được hóa đơn do đã phát sinh phiếu thu chi?",
        "expected_id": 99,
        "expected_title": "Xử lý lỗi không sửa được hóa đơn do đã phát sinh phiếu thu/chi"
    }
]

# =============================================================================
# 3. BENCHMARK EXECUTION & EVALUATION
# =============================================================================
def run_retrieval_benchmark():
    print("=" * 100)
    print("THỬ NGHIỆM RAG RETRIEVAL CHO MASTERPRO COPILOT")
    print(f"Cấu hình: Provider='{os.getenv('EMBEDDING_PROVIDER', 'hybrid_vietnamese')}', Model='{os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')}'")
    print("=" * 100)

    from sqlalchemy.orm import joinedload
    db = SessionLocal()
    docs = db.query(Document).options(joinedload(Document.versions)).order_by(Document.id).all()
    # Generate Structure-Aware Chunks (Strategy D) while session is open
    chunks = chunk_strategy_d_structure_aware(docs)
    db.close()
    print(f"\n[Bước 1] Chuẩn bị tri thức: Đã load và chunk 100 tài liệu theo Strategy D.")


    # 2. Embed and Index
    retriever = VietnameseEmbeddingRetriever()
    retriever.fit_and_embed(chunks)

    # Save index artifact
    index_file = os.path.join(current_dir, "vector_index.json")
    retriever.save_index(index_file)

    # 3. Evaluate 30 queries
    print("\n" + "=" * 100)
    print(f"{'#':<3} | {'Query (Câu hỏi thử nghiệm)':<45} | {'Expected (Mục tiêu)':<25} | {'Top-1 Retr':<10} | {'Score':<6} | {'Top-1':<5} | {'Top-3':<5}")
    print("-" * 100)

    top1_correct = 0
    top3_correct = 0
    reciprocal_ranks = []
    detailed_reports = []

    for idx, tq in enumerate(TEST_QUERIES, 1):
        results = retriever.search(tq["query"], top_k=3)
        top1 = results[0] if results else None
        top_ids = [r["document_id"] for r in results]

        is_top1 = (top1["document_id"] == tq["expected_id"]) if top1 else False
        is_top3 = tq["expected_id"] in top_ids

        if is_top1:
            top1_correct += 1
        if is_top3:
            top3_correct += 1

        # Calculate Reciprocal Rank
        if tq["expected_id"] in top_ids:
            rank = top_ids.index(tq["expected_id"]) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

        detailed_reports.append({
            "test_id": idx,
            "category": tq["category"],
            "query": tq["query"],
            "expected_id": tq["expected_id"],
            "expected_title": tq["expected_title"],
            "top1_id": top1["document_id"] if top1 else None,
            "top1_title": top1["title"] if top1 else None,
            "top1_score": round(top1["score"], 4) if top1 else 0.0,
            "top1_category": top1["category"] if top1 else None,
            "top1_module": top1["module"] if top1 else None,
            "top3_results": results,
            "is_top1_match": is_top1,
            "is_top3_match": is_top3
        })

        q_disp = tq["query"][:43] + ".." if len(tq["query"]) > 43 else tq["query"]
        exp_disp = tq["expected_title"][:23] + ".." if len(tq["expected_title"]) > 23 else tq["expected_title"]
        top1_disp = f"ID {top1['document_id']}" if top1 else "N/A"
        score_disp = f"{top1['score']:.3f}" if top1 else "0.000"

        print(f"{idx:<3} | {q_disp:<45} | {exp_disp:<25} | {top1_disp:<10} | {score_disp:<6} | {'ĐÚNG' if is_top1 else 'SAI':<5} | {'ĐÚNG' if is_top3 else 'SAI':<5}")

    # 4. Summary Statistics
    total_q = len(TEST_QUERIES)
    precision_at_1 = (top1_correct / total_q) * 100
    recall_at_3 = (top3_correct / total_q) * 100
    mrr = np.mean(reciprocal_ranks)
    mean_sim_score = np.mean([r["top1_score"] for r in detailed_reports])

    print("-" * 100)
    print("\n" + "=" * 100)
    print("BÁO CÁO THỐNG KÊ HIỆU NĂNG RAG RETRIEVAL (30 CÂU HỎI)")
    print("=" * 100)
    print(f" * Tổng số câu hỏi kiểm thử       : {total_q} câu")
    print(f"   - Phân bố                      : 10 HDSD | 10 FAQ | 10 RUNBOOK_L1")
    print(f" * Độ chính xác Top-1 (Hit@1)     : {top1_correct}/{total_q} ({precision_at_1:.1f}%)")
    print(f" * Độ chính xác Top-3 (Hit@3)     : {top3_correct}/{total_q} ({recall_at_3:.1f}%)")
    print(f" * Mean Reciprocal Rank (MRR)     : {mrr:.4f} (Thang điểm 0 -> 1.0)")
    print(f" * Điểm tương đồng trung bình Top-1: {mean_sim_score:.4f}")

    # Category Breakdown
    print("\nChi tiết độ chính xác theo Category:")
    for cat in ["HDSD", "FAQ", "RUNBOOK_L1"]:
        cat_reports = [r for r in detailed_reports if r["category"] == cat]
        c_top1 = sum(1 for r in cat_reports if r["is_top1_match"])
        c_top3 = sum(1 for r in cat_reports if r["is_top3_match"])
        print(f" - [{cat:<10}]: Top-1 = {c_top1:>2}/10 ({(c_top1/10)*100:.0f}%) | Top-3 = {c_top3:>2}/10 ({(c_top3/10)*100:.0f}%)")

    # Output 3 detailed samples (1 HDSD, 1 FAQ, 1 Runbook L1)
    print("\n" + "=" * 100)
    print("CHI TIẾT 3 MẪU TRUY VẤN TIÊU BIỂU (HDSD, FAQ, RUNBOOK L1)")
    print("=" * 100)
    for sample_idx in [1, 12, 21]:
        item = detailed_reports[sample_idx - 1]
        print(f"\n[CÂU #{item['test_id']}] [{item['category']}]")
        print(f" 1. Query           : \"{item['query']}\"")
        print(f" 2. Expected Document: [ID {item['expected_id']}] {item['expected_title']}")
        print(f" 3. Top-K Retrieved:")
        for r in item["top3_results"]:
            mark = "-> [TARGET MATCH]" if r["document_id"] == item["expected_id"] else ""
            print(f"    - Rank #{r['rank']}: [ID {r['document_id']:>2}] [{r['category']}] [{r['module']}] {r['title']} (Score: {r['score']:.4f}) {mark}")
        print(f" 4. Đánh giá        : {'ĐÚNG (Chính xác 100%)' if item['is_top1_match'] else 'CẦN RE-RANK'}")
        print("-" * 80)

if __name__ == "__main__":
    run_retrieval_benchmark()
