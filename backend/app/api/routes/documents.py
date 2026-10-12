from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse, DocumentDetailResponse, ImportReportResponse
from app.services.document_importer import KnowledgeBaseImporter
from app.data.masterpro_dataset import MASTERPRO_DATASET

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("", response_model=List[DocumentResponse], summary="Lấy danh sách tài liệu Document")
def get_documents(
    category: Optional[str] = Query(None, description="Lọc theo category: HDSD, FAQ, RUNBOOK_L1"),
    module: Optional[str] = Query(None, description="Lọc theo module (Kho hàng, Bán hàng, ...)"),
    status: Optional[str] = Query(None, description="Lọc theo status: APPROVED, DRAFT"),
    skip: int = Query(0, ge=0, description="Offset phân trang"),
    limit: int = Query(100, ge=1, le=200, description="Số lượng bản ghi mỗi trang"),
    db: Session = Depends(get_db)
):
    cat_val = category if isinstance(category, str) and category.strip() else None
    mod_val = module if isinstance(module, str) and module.strip() else None
    st_val = status if isinstance(status, str) and status.strip() else None
    skip_val = skip if isinstance(skip, int) else 0
    limit_val = limit if isinstance(limit, int) else 100

    repo = DocumentRepository(db)
    return repo.get_all(category=cat_val, module=mod_val, status=st_val, skip=skip_val, limit=limit_val)



@router.get("/search", response_model=List[DocumentResponse], summary="Tìm kiếm tài liệu phục vụ tra cứu & Citation")
def search_documents(
    q: str = Query(..., min_length=1, description="Từ khóa tìm kiếm trong title, content hoặc note"),
    limit: int = Query(10, ge=1, le=50, description="Số kết quả tối đa trả về"),
    db: Session = Depends(get_db)
):
    repo = DocumentRepository(db)
    return repo.search(keyword=q, limit=limit)

@router.get("/stats", summary="Thống kê cơ sở tri thức Document & Versions")
def get_document_stats(db: Session = Depends(get_db)):
    total = db.query(Document).count()
    
    # Category breakdown
    cat_stats = (
        db.query(Document.category, func.count(Document.id))
        .group_by(Document.category)
        .all()
    )
    
    # Module breakdown
    mod_stats = (
        db.query(Document.module, func.count(Document.id))
        .group_by(Document.module)
        .all()
    )

    # Status breakdown
    status_stats = (
        db.query(Document.status, func.count(Document.id))
        .group_by(Document.status)
        .all()
    )

    return {
        "total_documents": total,
        "by_category": {cat: count for cat, count in cat_stats},
        "by_module": {mod: count for mod, count in mod_stats},
        "by_status": {st: count for st, count in status_stats}
    }

@router.get("/{doc_id}", response_model=DocumentDetailResponse, summary="Lấy chi tiết Document kèm lịch sử DocumentVersion")
def get_document_by_id(doc_id: int, db: Session = Depends(get_db)):
    repo = DocumentRepository(db)
    doc = repo.get_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy tài liệu với ID={doc_id}")
    return doc

@router.post("/import", response_model=ImportReportResponse, summary="Kích hoạt import Knowledge Base qua API")
def trigger_import(
    version: str = Query("1.0", description="Phiên bản mặc định ban đầu"),
    status: str = Query("APPROVED", description="Trạng thái ban đầu"),
    db: Session = Depends(get_db)
):
    importer = KnowledgeBaseImporter(db=db, default_version=version, default_status=status)
    report = importer.import_documents(MASTERPRO_DATASET)
    return report
