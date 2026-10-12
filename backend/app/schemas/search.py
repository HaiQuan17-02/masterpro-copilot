from typing import List, Optional, Any
from pydantic import BaseModel, Field

class SearchQueryRequest(BaseModel):
    query: str = Field(..., description="Nội dung câu hỏi hoặc từ khóa tra cứu", min_length=1)
    limit: int = Field(default=3, description="Số lượng kết quả Top-K", ge=1, le=10)
    score_threshold: float = Field(default=0.30, description="Ngưỡng lọc cosine similarity tối thiểu", ge=0.0, le=1.0)
    category: Optional[str] = Field(default=None, description="Lọc theo nhóm tài liệu (HDSD, RUNBOOK_L1, FAQ)")
    module: Optional[str] = Field(default=None, description="Lọc theo phân hệ (Kho hàng, Bán hàng, Sổ quỹ, v.v.)")
    user_role: Optional[str] = Field(default=None, description="Vai trò: cashier, inventory, accountant, admin")

class SearchHitItem(BaseModel):
    score: float
    document_id: Optional[str] = None
    version_id: Optional[str] = None
    category: Optional[str] = None
    module: Optional[str] = None
    title: Optional[str] = None
    heading_path: Optional[str] = None
    chunk_index: Optional[int] = None
    content: str
    source: Optional[str] = None
    page: Optional[Any] = None

class SearchResponse(BaseModel):
    query: str
    user_role: Optional[str] = "all"
    total: int
    results: List[SearchHitItem]
    latency_ms: float
