import os
import sys
import time
import uuid
from typing import Dict, Any, Optional, List

# Ensure ai module is accessible
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ai_dir = os.path.join(backend_dir, "..", "ai")
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from heading_aware_chunker import HeadingAwareChunker
from qdrant_manager import QdrantVectorStore


class IngestionJob:
    def __init__(self, job_id: str, document_id: str, title: str):
        self.job_id = job_id
        self.document_id = document_id
        self.title = title
        self.status = "PENDING"  # PENDING, PROCESSING, COMPLETED, FAILED
        self.chunks_count = 0
        self.start_time = time.perf_counter()
        self.end_time: Optional[float] = None
        self.error_message: Optional[str] = None
        self.details: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        elapsed = (self.end_time or time.perf_counter()) - self.start_time
        return {
            "job_id": self.job_id,
            "status": self.status,
            "document_id": self.document_id,
            "chunks_count": self.chunks_count,
            "message": self.error_message or f"Xử lý hoàn tất {self.chunks_count} chunks.",
            "elapsed_time_s": round(elapsed, 3),
            "details": self.details
        }


class IngestionService:
    """
    Ingestion Worker Service for MasterPro Copilot (Week 5).
    Pipeline: Raw Content -> HeadingAwareChunker -> Embeddings -> Qdrant Upsert.
    """
    _instance: Optional["IngestionService"] = None

    def __init__(self):
        storage_path = os.path.join(ai_dir, "qdrant_storage")
        self.store = QdrantVectorStore.get_shared_instance(storage_path=storage_path)
        self.jobs: Dict[str, IngestionJob] = {}

    @classmethod
    def get_instance(cls) -> "IngestionService":
        if cls._instance is None:
            cls._instance = IngestionService()
        return cls._instance

    def ingest_text_document(
        self,
        title: str,
        content: str,
        category: str = "HDSD",
        module: str = "Chung",
        document_id: Optional[str] = None,
        version_id: str = "v1.0",
        source: str = "Người dùng tải lên",
        chunk_size: int = 500,
        chunk_overlap: int = 80
    ) -> IngestionJob:
        """
        Synchronous / Worker step: Ingests a text/markdown document into Qdrant.
        """
        doc_id = document_id or f"doc_upload_{uuid.uuid4().hex[:8]}"
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        job = IngestionJob(job_id=job_id, document_id=doc_id, title=title)
        self.jobs[job_id] = job

        try:
            job.status = "PROCESSING"

            # 1. Initialize HeadingAwareChunker
            chunker = HeadingAwareChunker(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )

            # 2. Build Markdown format with structural context
            formatted_md = f"# [{category}] [{module}] {title}\n\n{content}"
            metadata = {
                "document_id": doc_id,
                "version_id": version_id,
                "category": category,
                "module": module,
                "title": title,
                "source": source
            }

            # 3. Chunking
            chunks = chunker.chunk_document(formatted_md, metadata=metadata)
            job.chunks_count = len(chunks)

            # 4. Upsert into Qdrant
            upserted = self.store.upsert_chunks(chunks)

            job.status = "COMPLETED"
            job.end_time = time.perf_counter()
            job.details = {
                "document_id": doc_id,
                "title": title,
                "category": category,
                "module": module,
                "chunks_upserted": upserted,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "total_collection_points": self.store.count()
            }
        except Exception as e:
            job.status = "FAILED"
            job.end_time = time.perf_counter()
            job.error_message = f"Lỗi Ingestion: {str(e)}"

        return job

    def get_job_status(self, job_id: str) -> Optional[IngestionJob]:
        return self.jobs.get(job_id)

    def get_stats(self) -> Dict[str, Any]:
        total_vectors = self.store.count()
        active = sum(1 for j in self.jobs.values() if j.status in ("PENDING", "PROCESSING"))
        completed = sum(1 for j in self.jobs.values() if j.status == "COMPLETED")

        return {
            "total_vectors": total_vectors,
            "collection_name": self.store.collection_name,
            "active_jobs": active,
            "completed_jobs": completed,
            "supported_formats": [".md", ".txt", ".markdown"]
        }
