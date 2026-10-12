"""
Pydantic Schemas for Knowledge Lifecycle and Document Versioning (Week 9).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class LifecycleStatus(str, Enum):
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class LifecycleDocumentCreate(BaseModel):
    title: str = Field(..., description="Tiêu đề tài liệu nghiệp vụ", min_length=3)
    content: str = Field(..., description="Nội dung chi tiết Markdown", min_length=10)
    category: str = Field(default="HDSD", description="HDSD, RUNBOOK_L1, FAQ")
    module: str = Field(default="Bán hàng", description="Phân hệ chức năng")
    version_id: str = Field(default="v1.0", description="Mã phiên bản: v1.0, v2.0...")
    source: Optional[str] = Field(default="Tài liệu MasterPro ERP/POS", description="Nguồn dữ liệu")
    supersedes_doc_id: Optional[str] = Field(None, description="Mã tài liệu cũ mà tài liệu này sẽ thay thế (nếu có)")
    role_access: Optional[List[str]] = Field(default=["all"], description="Phân quyền truy cập vai trò")


class LifecycleDocumentOut(BaseModel):
    document_id: str
    title: str
    category: str
    module: str
    version_id: str
    status: LifecycleStatus
    content: str
    source: str
    supersedes_doc_id: Optional[str] = None
    superseded_by: Optional[str] = None
    chunks_count: int = 0
    role_access: List[str] = ["all"]
    created_at: str
    updated_at: str
    approved_by: Optional[str] = None


class LifecycleActionResponse(BaseModel):
    status: str
    message: str
    document_id: str
    current_status: LifecycleStatus
    chunks_indexed: Optional[int] = 0


class ReindexReport(BaseModel):
    total_documents: int
    approved_documents: int
    superseded_documents: int
    archived_documents: int
    total_chunks_indexed: int
    duration_ms: float
    message: str
