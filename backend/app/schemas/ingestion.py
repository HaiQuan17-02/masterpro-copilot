from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class IngestTextRequest(BaseModel):
    title: str = Field(..., min_length=1, description="Tiêu đề tài liệu")
    content: str = Field(..., min_length=5, description="Nội dung Markdown hoặc văn bản tài liệu")
    category: str = Field(default="HDSD", description="Nhóm tài liệu (HDSD, RUNBOOK_L1, FAQ)")
    module: str = Field(default="Chung", description="Phân hệ chức năng (Kho hàng, Bán hàng, Sổ quỹ, v.v.)")
    document_id: Optional[str] = Field(default=None, description="Mã định danh tài liệu (nếu có)")
    version_id: Optional[str] = Field(default="v1.0", description="Phiên bản tài liệu")
    source: Optional[str] = Field(default="Tải lên bởi người dùng", description="Nguồn trích xuất")
    chunk_size: Optional[int] = Field(default=500, description="Kích thước chunk tối đa (ký tự)")
    chunk_overlap: Optional[int] = Field(default=80, description="Độ dài overlap giữa các chunk")

class IngestionJobResponse(BaseModel):
    job_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED
    document_id: Optional[str] = None
    chunks_count: int = 0
    message: str
    elapsed_time_s: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

class IngestionStatsResponse(BaseModel):
    total_vectors: int
    collection_name: str
    active_jobs: int
    completed_jobs: int
    supported_formats: List[str]
