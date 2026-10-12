"""
API Endpoints for Knowledge Lifecycle and Document Versioning (Week 9).
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from app.schemas.lifecycle import (
    LifecycleStatus,
    LifecycleDocumentCreate,
    LifecycleDocumentOut,
    LifecycleActionResponse,
    ReindexReport
)
from app.services.lifecycle_service import get_lifecycle_service

router = APIRouter(prefix="/lifecycle", tags=["Knowledge Lifecycle & Versioning"])


@router.get("/documents", response_model=List[LifecycleDocumentOut], summary="Danh sách tài liệu tri thức theo trạng thái vòng đời")
def list_documents(
    status: Optional[str] = Query(None, description="draft, under_review, approved, superseded, archived"),
    module: Optional[str] = Query(None, description="Lọc theo phân hệ")
):
    service = get_lifecycle_service()
    return service.list_documents(status=status, module=module)


@router.get("/documents/{doc_id}", response_model=LifecycleDocumentOut, summary="Lấy chi tiết tài liệu")
def get_document(doc_id: str):
    service = get_lifecycle_service()
    doc = service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return doc


@router.post("/documents", response_model=LifecycleDocumentOut, summary="Soạn thảo / Nộp tài liệu tri thức mới")
def create_document(payload: LifecycleDocumentCreate, direct_submit: bool = Query(False, description="Tự động nộp thẩm định")):
    service = get_lifecycle_service()
    initial_st = LifecycleStatus.UNDER_REVIEW if direct_submit else LifecycleStatus.DRAFT
    return service.create_document(payload, initial_status=initial_st)


@router.post("/documents/{doc_id}/submit", response_model=LifecycleActionResponse, summary="Gửi tài liệu sang bước Thẩm định (Under Review)")
def submit_document(doc_id: str):
    service = get_lifecycle_service()
    try:
        return service.submit_for_review(doc_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/{doc_id}/approve", response_model=LifecycleActionResponse, summary="Phê duyệt tài liệu, nạp vào Qdrant và đánh dấu phiên bản cũ là Superseded")
def approve_document(doc_id: str, approver: str = Query("Admin", description="Tên người duyệt")):
    service = get_lifecycle_service()
    try:
        return service.approve_and_index(doc_id, approver=approver)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/documents/{doc_id}/archive", response_model=LifecycleActionResponse, summary="Lưu trữ tài liệu và gỡ bỏ vector khỏi Qdrant")
def archive_document(doc_id: str):
    service = get_lifecycle_service()
    try:
        return service.archive_document(doc_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reindex", response_model=ReindexReport, summary="Tái lập chỉ mục toàn bộ tài liệu Approved vào Qdrant")
def reindex_all():
    service = get_lifecycle_service()
    return service.reindex_all_active()
