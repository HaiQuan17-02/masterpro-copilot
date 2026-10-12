import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.document import Document, DocumentVersion
from app.repositories.document_repository import DocumentRepository

VALID_CATEGORIES = {"HDSD", "FAQ", "RUNBOOK_L1"}
VALID_STATUSES = {"DRAFT", "APPROVED", "ARCHIVED"}

class DocumentValidationError(Exception):
    pass

class KnowledgeBaseImporter:
    """
    Importer service for MasterPro Knowledge Base.
    Features:
    - Pre-insert validation
    - Idempotency & deduplication protection
    - Dual-table insertion (Document + DocumentVersion)
    - Structured import reporting
    """

    def __init__(self, db: Session, default_version: str = "1.0", default_status: str = "APPROVED"):
        self.db = db
        self.repo = DocumentRepository(db)
        self.default_version = default_version
        self.default_status = default_status

    def validate_item(self, item: Dict[str, Any], index: int) -> Tuple[bool, str]:
        category = item.get("category", "").strip() if item.get("category") else ""
        module = item.get("module", "").strip() if item.get("module") else ""
        title = item.get("title", "").strip() if item.get("title") else ""
        content = item.get("content", "").strip() if item.get("content") else ""

        if not category:
            return False, f"Bản ghi #{index}: Thiếu category"
        if category not in VALID_CATEGORIES:
            return False, f"Bản ghi #{index}: Category '{category}' không hợp lệ (hợp lệ: {VALID_CATEGORIES})"
        if not module:
            return False, f"Bản ghi #{index}: Thiếu module"
        if not title:
            return False, f"Bản ghi #{index}: Thiếu title"
        if not content:
            return False, f"Bản ghi #{index}: Thiếu content"
        return True, ""

    def generate_document_code(self, category: str, seq_number: int) -> str:
        cat_prefix = {
            "HDSD": "HDSD",
            "FAQ": "FAQ",
            "RUNBOOK_L1": "RB1"
        }.get(category, "DOC")
        return f"DOC_{cat_prefix}_{seq_number:03d}"

    def import_documents(self, raw_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        report = {
            "total_processed": len(raw_items),
            "total_documents": 0,
            "hdsd_count": 0,
            "faq_count": 0,
            "runbook_l1_count": 0,
            "error_count": 0,
            "duplicate_count": 0,
            "errors": []
        }

        # Keep track of sequence numbers per category for document_code generation
        seq_counters = {
            "HDSD": self.repo.count(category="HDSD"),
            "FAQ": self.repo.count(category="FAQ"),
            "RUNBOOK_L1": self.repo.count(category="RUNBOOK_L1")
        }

        for idx, item in enumerate(raw_items, 1):
            is_valid, error_msg = self.validate_item(item, idx)
            if not is_valid:
                report["error_count"] += 1
                report["errors"].append(error_msg)
                continue

            category = item["category"].strip()
            module = item["module"].strip()
            title = item["title"].strip()
            content = item["content"].strip()
            note = item.get("note", "").strip() if item.get("note") else None
            source = item.get("source", "Tài liệu vận hành MasterPro").strip()
            version = item.get("version", self.default_version).strip()
            status = item.get("status", self.default_status).strip()

            # Deduplication check: check if (category, title) exists
            existing_doc = self.repo.find_by_category_and_title(category, title)
            if existing_doc:
                report["duplicate_count"] += 1
                continue

            # Increment sequence number and generate document_code
            seq_counters[category] += 1
            doc_code = self.generate_document_code(category, seq_counters[category])

            try:
                self.repo.create_document_with_version(
                    document_code=doc_code,
                    category=category,
                    module=module,
                    title=title,
                    content=content,
                    note=note,
                    source=source,
                    version=version,
                    status=status,
                    change_summary="Khởi tạo phiên bản ban đầu 1.0"
                )
                self.db.commit()

                report["total_documents"] += 1
                if category == "HDSD":
                    report["hdsd_count"] += 1
                elif category == "FAQ":
                    report["faq_count"] += 1
                elif category == "RUNBOOK_L1":
                    report["runbook_l1_count"] += 1

            except Exception as e:
                self.db.rollback()
                report["error_count"] += 1
                report["errors"].append(f"Bản ghi #{idx} ('{title[:30]}'): Lỗi SQL - {str(e)}")

        return report
