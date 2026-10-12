import sys
import os
import io

# Ensure UTF-8 output encoding in Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ensure backend and ai modules are discoverable
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.core.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from chunker import DocumentChunker

def prepare_rag_chunks():
    """
    Fetches all 100 approved documents from SQL Server (MasterDB),
    formats content with heading context, and chunks them with metadata
    ready for Embedding and Vector Search.
    """
    db = SessionLocal()
    repo = DocumentRepository(db)
    
    docs = repo.get_all(review_status="Đã kiểm duyệt", limit=200)
    print(f"Loaded {len(docs)} documents from database MasterDB.")

    chunker = DocumentChunker(chunk_size=500, chunk_overlap=80)
    all_chunks = []

    for doc in docs:
        # Full text formatted with hierarchical context for optimal embedding
        full_text = f"# [{doc.category}] [{doc.module}] {doc.title}\n\n{doc.content}"
        if doc.note:
            full_text += f"\n\nLưu ý: {doc.note}"

        metadata = {
            "document": f"masterpro_{doc.category.lower()}_{doc.id:03d}",
            "document_id": doc.id,
            "category": doc.category,
            "module": doc.module,
            "title": doc.title,
            "source": doc.source,
            "version": doc.version,
            "review_status": doc.review_status,
            "citation": doc.note if doc.note else f"Tài liệu {doc.category} - {doc.title}"
        }


        doc_chunks = chunker.split_text(full_text, metadata=metadata)
        all_chunks.extend(doc_chunks)

    print(f"Generated a total of {len(all_chunks)} chunks from {len(docs)} documents.")
    
    # Preview first 3 chunks
    print("\n--- SAMPLE GENERATED CHUNKS FOR EMBEDDING ---")
    for i, c in enumerate(all_chunks[:3], 1):
        print(f"\n[Chunk #{i}] ID: {c['chunk_id']}")
        print(f"Metadata: {c['metadata']}")
        print(f"Content:\n{c['content']}")
        print("-" * 50)

    db.close()
    return all_chunks

if __name__ == "__main__":
    prepare_rag_chunks()
