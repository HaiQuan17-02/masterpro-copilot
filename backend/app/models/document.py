# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_code = Column(Unicode(50), unique=True, nullable=False, index=True)
    category = Column(Unicode(50), nullable=False, index=True)
    module = Column(Unicode(100), nullable=False, index=True)
    title = Column(Unicode(255), nullable=False, index=True)
    source = Column(Unicode(255), nullable=False, default="Tài liệu vận hành MasterPro")
    current_version = Column(Unicode(50), nullable=False, default="1.0")
    status = Column(Unicode(50), nullable=False, default="APPROVED", index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationship with versions
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="desc(DocumentVersion.id)"
    )

    __table_args__ = (
        UniqueConstraint("category", "title", name="uq_documents_category_title"),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, code='{self.document_code}', title='{self.title[:30]}', version='{self.current_version}')>"


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Unicode(50), nullable=False, default="1.0")
    title = Column(Unicode(255), nullable=False)
    content = Column(UnicodeText, nullable=False)
    note = Column(UnicodeText, nullable=True)
    source = Column(Unicode(255), nullable=False, default="Tài liệu vận hành MasterPro")
    status = Column(Unicode(50), nullable=False, default="APPROVED", index=True)
    change_summary = Column(Unicode(255), nullable=True, default="Khởi tạo phiên bản ban đầu")
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationship back to Document
    document = relationship("Document", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("document_id", "version", name="uq_document_versions_doc_version"),
    )

    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, doc_id={self.document_id}, v='{self.version}', status='{self.status}')>"


class MasterProDocument(Base):
    __tablename__ = "masterpro_documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(Unicode(50), nullable=False, index=True)
    module = Column(Unicode(100), nullable=False, index=True)
    title = Column(Unicode(255), nullable=False)
    content = Column(UnicodeText, nullable=False)
    note = Column(UnicodeText, nullable=True)
    source = Column(Unicode(255), nullable=False, default="Tài liệu vận hành MasterPro")
    version = Column(Unicode(50), nullable=False, default="1.0")
    review_status = Column(Unicode(50), nullable=False, default="Đã kiểm duyệt", index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
