"""
Indexer Script for MasterPro Copilot (Week 4).

Extracts MasterPro operational documents (HDSD, RUNBOOK_L1, FAQ),
chunks them using HeadingAwareChunker, and indexes them into Qdrant Vector Store.
"""

import os
import sys
import io
import re

# Ensure UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure paths
ai_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.abspath(os.path.join(ai_dir, ".."))
backend_dir = os.path.abspath(os.path.join(workspace_dir, "backend"))

if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from heading_aware_chunker import HeadingAwareChunker
from qdrant_manager import QdrantVectorStore

def parse_seed_documents():
    """Parses document tuples from seed_documents.py cleanly."""
    seed_file = os.path.join(backend_dir, "seed_documents.py")
    if not os.path.exists(seed_file):
        raise FileNotFoundError(f"seed_documents.py not found at {seed_file}")

    with open(seed_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to extract: ('CATEGORY', 'MODULE', 'TITLE', 'CONTENT', 'NOTE')
    pattern = re.compile(
        r"\(\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*\)",
        re.MULTILINE
    )
    matches = pattern.findall(content)
    documents = []

    for idx, (cat, mod, title, body, note) in enumerate(matches, 1):
        doc_id = f"doc_{cat.lower()}_{idx:03d}"
        documents.append({
            "id": doc_id,
            "document_id": doc_id,
            "version_id": "v1.0",
            "category": cat.strip(),
            "module": mod.strip(),
            "title": title.strip(),
            "content": body.strip(),
            "note": note.strip(),
            "source": f"Tài liệu vận hành MasterPro ({cat})"
        })

    return documents

def run_indexing(limit: int = 50):
    print("=" * 80)
    print("BẮT ĐẦU NẠP & INDEX TÀI LIỆU VÀO QDRANT VECTOR STORE (TUẦN 4)")
    print("=" * 80)

    docs = parse_seed_documents()
    selected_docs = docs[:limit]
    print(f"Đã trích xuất {len(selected_docs)} tài liệu mẫu từ seed_documents.py")

    chunker = HeadingAwareChunker(chunk_size=500, chunk_overlap=80)
    all_chunks = []

    for doc in selected_docs:
        # Format markdown content with heading and notes
        md_text = f"# [{doc['category']}] [{doc['module']}] {doc['title']}\n\n{doc['content']}"
        if doc.get("note"):
            md_text += f"\n\nLưu ý nghiệp vụ: {doc['note']}"

        metadata = {
            "document_id": doc["id"],
            "version_id": doc["version_id"],
            "category": doc["category"],
            "module": doc["module"],
            "title": doc["title"],
            "source": doc["source"],
            "note": doc["note"]
        }

        chunks = chunker.chunk_document(md_text, metadata=metadata)
        all_chunks.extend(chunks)

    print(f"Tổng số chunks tạo ra từ {len(selected_docs)} tài liệu: {len(all_chunks)} chunks.")

    # Initialize Qdrant Vector Store with persistent storage
    store = QdrantVectorStore()
    inserted = store.upsert_chunks(all_chunks)
    total_in_qdrant = store.count()

    print(f"Đã lưu thành công {inserted} vector chunks vào Qdrant collection '{store.collection_name}'.")
    print(f"Tổng số points trong Qdrant hiện tại: {total_in_qdrant}")

    # Test sample search
    test_query = "cách khắc phục lỗi kẹt giấy máy in hóa đơn"
    print(f"\n[Test Search] Query: '{test_query}'")
    hits = store.search(test_query, limit=2)
    for h in hits:
        print(f"-> Score: {h['score']} | {h['heading_path']}")
        print(f"   Snippet: {h['content'][:120]}...\n")

    return total_in_qdrant

if __name__ == "__main__":
    run_indexing(limit=50)
