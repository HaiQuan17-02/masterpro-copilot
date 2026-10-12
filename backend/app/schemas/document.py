from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# --- Document Version Schemas ---
class DocumentVersionBase(BaseModel):
    version: str = Field("1.0", description="Phiên bản tài liệu")
    title: str = Field(..., description="Tiêu đề phiên bản")
    content: str = Field(..., description="Nội dung phiên bản")
    note: Optional[str] = Field(None, description="Ghi chú / Citation")
    source: str = Field("Tài liệu vận hành MasterPro", description="Nguồn dữ liệu")
    status: str = Field("APPROVED", description="Trạng thái: DRAFT, APPROVED, ARCHIVED")
    change_summary: Optional[str] = Field("Khởi tạo phiên bản ban đầu", description="Tóm tắt thay đổi")

class DocumentVersionResponse(DocumentVersionBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Document Schemas ---
class DocumentBase(BaseModel):
    category: str = Field(..., description="Nhóm: HDSD, FAQ, RUNBOOK_L1")
    module: str = Field(..., description="Phân hệ chức năng")
    title: str = Field(..., description="Tiêu đề tài liệu")
    source: str = Field("Tài liệu vận hành MasterPro", description="Nguồn tài liệu gốc")
    current_version: str = Field("1.0", description="Phiên bản hiện tại")
    status: str = Field("APPROVED", description="Trạng thái: DRAFT, APPROVED, ARCHIVED")

class DocumentCreate(DocumentBase):
    content: str = Field(..., description="Nội dung ban đầu")
    note: Optional[str] = Field(None, description="Ghi chú ban đầu")

class DocumentResponse(DocumentBase):
    id: int
    document_code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentDetailResponse(DocumentResponse):
    versions: List[DocumentVersionResponse] = []

# --- Import / Seeding Schemas ---
class DocumentImportItem(BaseModel):
    category: str
    module: str
    title: str
    content: str
    note: Optional[str] = None
    source: Optional[str] = "Tài liệu vận hành MasterPro"
    version: Optional[str] = "1.0"
    status: Optional[str] = "APPROVED"

class ImportReportResponse(BaseModel):
    total_processed: int
    total_documents: int
    hdsd_count: int
    faq_count: int
    runbook_l1_count: int
    error_count: int
    duplicate_count: int
    errors: List[str] = []
