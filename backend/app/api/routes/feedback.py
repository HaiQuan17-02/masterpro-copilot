"""
API Endpoints for User Feedback and L2 Ticket Escalation (Week 7).
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackStats,
    EscalationCreate,
    EscalationTicket
)
from app.services.feedback_service import get_feedback_service

router = APIRouter(tags=["Feedback & Escalation"])


@router.post("/feedback", summary="Gửi đánh giá Like/Dislike cho tin nhắn Copilot")
def submit_feedback(payload: FeedbackCreate):
    if payload.rating not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Rating phải là 'like' hoặc 'dislike'")
    service = get_feedback_service()
    item = service.add_feedback(payload)
    return {
        "status": "success",
        "message": "Cảm ơn bạn đã gửi phản hồi!",
        "feedback_id": item["feedback_id"]
    }


@router.get("/feedback/stats", response_model=FeedbackStats, summary="Thống kê tỉ lệ hữu ích và phản hồi")
def get_feedback_stats():
    service = get_feedback_service()
    return service.get_stats()


@router.post("/escalation", response_model=EscalationTicket, summary="Chuyển tiếp câu hỏi lên hỗ trợ Kỹ thuật L2")
def create_escalation(payload: EscalationCreate):
    if not payload.query.strip():
        raise HTTPException(status_code=422, detail="Query không được rỗng")
    service = get_feedback_service()
    ticket = service.create_escalation(payload)
    return ticket


@router.get("/escalation/tickets", response_model=List[EscalationTicket], summary="Danh sách ticket leo thang L2")
def list_escalation_tickets(status: Optional[str] = Query(None, description="Lọc theo status: pending, in_progress, resolved")):
    service = get_feedback_service()
    return service.list_escalations(status=status)


@router.patch("/escalation/tickets/{ticket_id}", response_model=EscalationTicket, summary="Cập nhật trạng thái ticket L2")
def update_ticket_status(ticket_id: str, status: str = Query(..., description="pending, in_progress, resolved")):
    service = get_feedback_service()
    updated = service.update_escalation_status(ticket_id, status)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy ticket")
    return updated
