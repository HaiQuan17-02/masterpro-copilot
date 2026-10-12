"""
Knowledge Lifecycle Service (Week 9).
Manages document states (draft, under_review, approved, superseded, archived),
version replacement, and Qdrant index synchronization.
"""

import os
import sys
import json
import uuid
import time
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ai_dir = os.path.join(backend_dir, "..", "ai")
if ai_dir not in sys.path:
    sys.path.insert(0, ai_dir)

from qdrant_manager import QdrantVectorStore
from heading_aware_chunker import HeadingAwareChunker
from app.schemas.lifecycle import (
    LifecycleStatus,
    LifecycleDocumentCreate,
    LifecycleDocumentOut,
    LifecycleActionResponse,
    ReindexReport
)


class KnowledgeLifecycleService:
    def __init__(self, data_dir: str = "backend/app/data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "knowledge_lifecycle.json")
        self._lock = threading.Lock()

        # Vector store singleton
        storage_path = os.path.join(ai_dir, "qdrant_storage")
        self.store = QdrantVectorStore.get_shared_instance(storage_path=storage_path)
        self.chunker = HeadingAwareChunker(chunk_size=500, chunk_overlap=80)

        self._documents: Dict[str, Dict[str, Any]] = self._init_or_load()

    def _init_or_load(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # Seed with initial approved sample documents
        sample_docs = {
            "doc_hdsd_001": {
                "document_id": "doc_hdsd_001",
                "title": "Hướng dẫn đăng nhập phần mềm MasterPro",
                "category": "HDSD",
                "module": "Đăng nhập",
                "version_id": "v1.0",
                "status": LifecycleStatus.APPROVED.value,
                "content": "# Đăng nhập MasterPro\n\n## Các bước thực hiện\n1. Nhập Tên đăng nhập và Mật khẩu được cấp.\n2. Chọn Chi nhánh làm việc.\n3. Nhấn nút Đăng nhập để vào hệ thống.",
                "source": "HDSD_MasterPro_Chung.md",
                "supersedes_doc_id": None,
                "superseded_by": None,
                "chunks_count": 2,
                "role_access": ["all"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "approved_by": "System Admin"
            },
            "doc_hdsd_004": {
                "document_id": "doc_hdsd_004",
                "title": "Cấu hình máy in và thiết lập thông số hệ thống",
                "category": "HDSD",
                "module": "Hệ thống",
                "version_id": "v1.0",
                "status": LifecycleStatus.APPROVED.value,
                "content": "# Thiết lập máy in POS\n\n## Kết nối máy in\n- Kiểm tra cổng kết nối USB / LAN.\n- Vào Thiết lập hệ thống -> Chọn mẫu in hóa đơn K80.\n- Khởi động lại phần mềm sau khi lưu cấu hình.",
                "source": "HDSD_ThietBi_POS.md",
                "supersedes_doc_id": None,
                "superseded_by": None,
                "chunks_count": 2,
                "role_access": ["cashier", "admin"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "approved_by": "System Admin"
            }
        }
        self._save(sample_docs)
        return sample_docs

    def _save(self, docs: Dict[str, Dict[str, Any]]):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(docs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to persist lifecycle docs: {e}")

    def list_documents(
        self,
        status: Optional[str] = None,
        module: Optional[str] = None
    ) -> List[LifecycleDocumentOut]:
        with self._lock:
            result = []
            for doc in self._documents.values():
                if status and doc.get("status") != status:
                    continue
                if module and doc.get("module") != module:
                    continue
                result.append(LifecycleDocumentOut(**doc))
            return sorted(result, key=lambda d: d.updated_at, reverse=True)

    def get_document(self, doc_id: str) -> Optional[LifecycleDocumentOut]:
        with self._lock:
            data = self._documents.get(doc_id)
            return LifecycleDocumentOut(**data) if data else None

    def create_document(
        self,
        payload: LifecycleDocumentCreate,
        author: str = "Admin",
        initial_status: LifecycleStatus = LifecycleStatus.DRAFT
    ) -> LifecycleDocumentOut:
        with self._lock:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
            now_iso = datetime.now().isoformat()
            new_doc = {
                "document_id": doc_id,
                "title": payload.title,
                "category": payload.category,
                "module": payload.module,
                "version_id": payload.version_id,
                "status": initial_status.value,
                "content": payload.content,
                "source": payload.source or "MasterPro Portal",
                "supersedes_doc_id": payload.supersedes_doc_id,
                "superseded_by": None,
                "chunks_count": 0,
                "role_access": payload.role_access or ["all"],
                "created_at": now_iso,
                "updated_at": now_iso,
                "approved_by": None
            }
            self._documents[doc_id] = new_doc
            self._save(self._documents)
            return LifecycleDocumentOut(**new_doc)

    def submit_for_review(self, doc_id: str) -> LifecycleActionResponse:
        with self._lock:
            doc = self._documents.get(doc_id)
            if not doc:
                raise ValueError("Không tìm thấy tài liệu")
            doc["status"] = LifecycleStatus.UNDER_REVIEW.value
            doc["updated_at"] = datetime.now().isoformat()
            self._save(self._documents)
            return LifecycleActionResponse(
                status="success",
                message="Tài liệu đã được gửi thẩm định (Under Review)",
                document_id=doc_id,
                current_status=LifecycleStatus.UNDER_REVIEW
            )

    def approve_and_index(self, doc_id: str, approver: str = "Chief Admin") -> LifecycleActionResponse:
        with self._lock:
            doc = self._documents.get(doc_id)
            if not doc:
                raise ValueError("Không tìm thấy tài liệu")

            # 1. Xử lý tài liệu cũ bị thay thế (Superseded) nếu có
            supersedes_id = doc.get("supersedes_doc_id")
            if supersedes_id and supersedes_id in self._documents:
                old_doc = self._documents[supersedes_id]
                old_doc["status"] = LifecycleStatus.SUPERSEDED.value
                old_doc["superseded_by"] = doc_id
                old_doc["updated_at"] = datetime.now().isoformat()
                # Xóa vector của tài liệu cũ khỏi Qdrant để tránh ô nhiễm kết quả
                self.store.delete_by_document_id(supersedes_id)

            # 2. Phân đoạn chunking tài liệu mới
            chunks = self.chunker.chunk_document(
                markdown_text=doc["content"],
                metadata={
                    "document_id": doc_id,
                    "title": doc["title"],
                    "category": doc["category"],
                    "module": doc["module"],
                    "version_id": doc["version_id"],
                    "source": doc["source"],
                    "role_access": doc.get("role_access", ["all"])
                }
            )

            # 3. Nạp chunks vào Qdrant Vector Store
            upsert_count = self.store.upsert_chunks(chunks)

            # 4. Cập nhật trạng thái Approved
            doc["status"] = LifecycleStatus.APPROVED.value
            doc["approved_by"] = approver
            doc["chunks_count"] = len(chunks)
            doc["updated_at"] = datetime.now().isoformat()
            self._save(self._documents)

            return LifecycleActionResponse(
                status="success",
                message=f"Đã duyệt và lập chỉ mục {upsert_count} chunks vào Qdrant thành công" + (f" (Thay thế {supersedes_id})" if supersedes_id else ""),
                document_id=doc_id,
                current_status=LifecycleStatus.APPROVED,
                chunks_indexed=upsert_count
            )

    def archive_document(self, doc_id: str) -> LifecycleActionResponse:
        with self._lock:
            doc = self._documents.get(doc_id)
            if not doc:
                raise ValueError("Không tìm thấy tài liệu")

            doc["status"] = LifecycleStatus.ARCHIVED.value
            doc["updated_at"] = datetime.now().isoformat()
            # Gỡ bỏ các vector khỏi Qdrant
            self.store.delete_by_document_id(doc_id)
            self._save(self._documents)

            return LifecycleActionResponse(
                status="success",
                message="Đã chuyển tài liệu sang trạng thái Lưu trữ (Archived) và gỡ khỏi Qdrant",
                document_id=doc_id,
                current_status=LifecycleStatus.ARCHIVED,
                chunks_indexed=0
            )

    def reindex_all_active(self) -> ReindexReport:
        with self._lock:
            start_t = time.perf_counter()
            approved_count = 0
            total_chunks = 0
            superseded_count = 0
            archived_count = 0

            for doc_id, doc in self._documents.items():
                st = doc.get("status")
                if st == LifecycleStatus.APPROVED.value:
                    approved_count += 1
                    chunks = self.chunker.chunk_document(
                        markdown_text=doc["content"],
                        metadata={
                            "document_id": doc_id,
                            "title": doc["title"],
                            "category": doc["category"],
                            "module": doc["module"],
                            "version_id": doc["version_id"],
                            "source": doc["source"],
                            "role_access": doc.get("role_access", ["all"])
                        }
                    )
                    upserted = self.store.upsert_chunks(chunks)
                    total_chunks += upserted
                    doc["chunks_count"] = len(chunks)
                elif st == LifecycleStatus.SUPERSEDED.value:
                    superseded_count += 1
                    self.store.delete_by_document_id(doc_id)
                elif st == LifecycleStatus.ARCHIVED.value:
                    archived_count += 1
                    self.store.delete_by_document_id(doc_id)

            self._save(self._documents)
            elapsed_ms = round((time.perf_counter() - start_t) * 1000, 2)

            return ReindexReport(
                total_documents=len(self._documents),
                approved_documents=approved_count,
                superseded_documents=superseded_count,
                archived_documents=archived_count,
                total_chunks_indexed=total_chunks,
                duration_ms=elapsed_ms,
                message=f"Đã tái lập chỉ mục toàn bộ {approved_count} tài liệu active ({total_chunks} chunks)."
            )


# Global singleton
_lifecycle_instance: Optional[KnowledgeLifecycleService] = None

def get_lifecycle_service() -> KnowledgeLifecycleService:
    global _lifecycle_instance
    if _lifecycle_instance is None:
        _lifecycle_instance = KnowledgeLifecycleService()
    return _lifecycle_instance
