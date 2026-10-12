from typing import List, Optional, Tuple
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session, joinedload
from app.models.document import Document, DocumentVersion

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        return (
            self.db.query(Document)
            .options(joinedload(Document.versions))
            .filter(Document.id == doc_id)
            .first()
        )

    def get_by_code(self, doc_code: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .options(joinedload(Document.versions))
            .filter(Document.document_code == doc_code)
            .first()
        )

    def find_by_category_and_title(self, category: str, title: str) -> Optional[Document]:
        return (
            self.db.query(Document)
            .filter(
                Document.category == category.strip(),
                Document.title == title.strip()
            )
            .first()
        )

    def get_all(
        self,
        category: Optional[str] = None,
        module: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        query = self.db.query(Document).options(joinedload(Document.versions))
        if category:
            query = query.filter(Document.category == category)
        if module:
            query = query.filter(Document.module == module)
        if status:
            query = query.filter(Document.status == status)
        return query.order_by(Document.id.asc()).offset(skip).limit(limit).all()

    def search(self, keyword: str, limit: int = 10) -> List[Document]:
        search_pattern = f"%{keyword}%"
        # Search in Document title or module, or join with DocumentVersion content/note
        return (
            self.db.query(Document)
            .join(Document.versions)
            .filter(
                (Document.title.ilike(search_pattern))
                | (Document.module.ilike(search_pattern))
                | (DocumentVersion.content.ilike(search_pattern))
                | (DocumentVersion.note.ilike(search_pattern))
            )
            .distinct()
            .order_by(Document.id.asc())
            .limit(limit)
            .all()
        )

    def create_document_with_version(
        self,
        document_code: str,
        category: str,
        module: str,
        title: str,
        content: str,
        note: Optional[str] = None,
        source: str = "Tài liệu vận hành MasterPro",
        version: str = "1.0",
        status: str = "APPROVED",
        change_summary: str = "Khởi tạo phiên bản ban đầu"
    ) -> Tuple[Document, DocumentVersion]:
        doc = Document(
            document_code=document_code,
            category=category,
            module=module,
            title=title,
            source=source,
            current_version=version,
            status=status
        )
        self.db.add(doc)
        self.db.flush()  # To obtain doc.id

        doc_ver = DocumentVersion(
            document_id=doc.id,
            version=version,
            title=title,
            content=content,
            note=note,
            source=source,
            status=status,
            change_summary=change_summary
        )
        self.db.add(doc_ver)
        return doc, doc_ver

    def count(self, category: Optional[str] = None) -> int:
        query = self.db.query(Document)
        if category:
            query = query.filter(Document.category == category)
        return query.count()
