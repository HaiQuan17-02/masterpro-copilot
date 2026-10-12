import os
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from app.schemas.ingestion import IngestTextRequest, IngestionJobResponse, IngestionStatsResponse
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["Ingestion Pipeline"])


@router.post("/text", response_model=IngestionJobResponse, summary="Nạp tài liệu dạng văn bản Markdown vào Qdrant")
async def ingest_text(request: IngestTextRequest):
    service = IngestionService.get_instance()
    job = service.ingest_text_document(
        title=request.title,
        content=request.content,
        category=request.category,
        module=request.module,
        document_id=request.document_id,
        version_id=request.version_id,
        source=request.source,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap
    )

    if job.status == "FAILED":
        raise HTTPException(status_code=500, detail=job.error_message)

    return IngestionJobResponse(**job.to_dict())


@router.post("/file", response_model=IngestionJobResponse, summary="Tải lên file tài liệu (.md, .txt) và phân đoạn nạp vào Qdrant")
async def ingest_file(
    file: UploadFile = File(..., description="File tài liệu Markdown hoặc Text (.md, .txt)"),
    category: str = Form("HDSD"),
    module: str = Form("Chung"),
    title: Optional[str] = Form(None)
):
    filename = file.filename or "uploaded_doc.md"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".md", ".txt", ".markdown"]:
        raise HTTPException(status_code=400, detail=f"Định dạng file '{ext}' không được hỗ trợ. Chỉ chấp nhận .md, .txt")

    try:
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể đọc file: {str(e)}")

    doc_title = title or os.path.splitext(filename)[0].replace("_", " ")

    service = IngestionService.get_instance()
    job = service.ingest_text_document(
        title=doc_title,
        content=content,
        category=category,
        module=module,
        source=f"File upload: {filename}"
    )

    if job.status == "FAILED":
        raise HTTPException(status_code=500, detail=job.error_message)

    return IngestionJobResponse(**job.to_dict())


@router.get("/status/{job_id}", response_model=IngestionJobResponse, summary="Kiểm tra trạng thái tiến trình Ingestion Job")
async def get_job_status(job_id: str):
    service = IngestionService.get_instance()
    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy Ingestion Job với ID '{job_id}'")
    return IngestionJobResponse(**job.to_dict())


@router.get("/stats", response_model=IngestionStatsResponse, summary="Thống kê toàn bộ Vector Store & Ingestion Worker")
async def get_ingestion_stats():
    service = IngestionService.get_instance()
    stats = service.get_stats()
    return IngestionStatsResponse(**stats)
