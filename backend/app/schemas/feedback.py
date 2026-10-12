"""
Schemas for User Feedback and L2 Ticket Escalation (Week 7).
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FeedbackCreate(BaseModel):
    message_id: str = Field(..., description="ID của tin nhắn Copilot được đánh giá")
    rating: str = Field(..., description="'like' hoặc 'dislike'")
    reason: Optional[str] = Field(None, description="Lý do: sai bước, thiếu thông tin, văn bản cũ, v.v.")
    comment: Optional[str] = Field(None, description="Ý kiến đóng góp chi tiết của người dùng")
    cited_doc_ids: Optional[List[str]] = Field(default=[], description="Danh sách tài liệu được trích dẫn liên quan")
    query: Optional[str] = Field(None, description="Câu hỏi gốc của người dùng")


class FeedbackItem(BaseModel):
    feedback_id: str
    message_id: str
    rating: str
    reason: Optional[str]
    comment: Optional[str]
    cited_doc_ids: List[str]
    query: Optional[str]
    created_at: str


class FeedbackStats(BaseModel):
    total: int
    likes: int
    dislikes: int
    helpful_rate_percent: float
    reason_breakdown: Dict[str, int]


class EscalationCreate(BaseModel):
    query: str = Field(..., description="Vấn đề nghiệp vụ người dùng gặp phải")
    bot_response: str = Field(..., description="Câu trả lời của Copilot chưa thỏa đáng")
    conversation_id: Optional[str] = Field(None, description="ID phiên hội thoại")
    user_note: Optional[str] = Field(None, description="Mô tả bổ sung của người dùng hoặc nhân viên")
    priority: str = Field(default="medium", description="'low', 'medium', 'high', 'urgent'")
    user_role: Optional[str] = Field(default="cashier", description="Vai trò: cashier, inventory, accountant, admin")
    retrieved_chunks: Optional[List[Dict[str, Any]]] = Field(default=[], description="Ngữ cảnh RAG đã dùng")


class EscalationTicket(BaseModel):
    ticket_id: str
    query: str
    bot_response: str
    conversation_id: Optional[str]
    user_note: Optional[str]
    priority: str
    status: str  # pending, in_progress, resolved
    user_role: str
    retrieved_chunks_count: int
    created_at: str
    updated_at: str
