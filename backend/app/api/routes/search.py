from fastapi import APIRouter, HTTPException
from app.schemas.search import SearchQueryRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["Search & Retrieval"])

@router.post("", response_model=SearchResponse, summary="Tìm kiếm ngữ nghĩa tri thức tài liệu MasterPro qua Qdrant")
async def search_documents(request: SearchQueryRequest):
    try:
        service = SearchService.get_instance()
        result = service.search(
            query=request.query,
            limit=request.limit,
            score_threshold=request.score_threshold,
            category=request.category,
            module=request.module,
            user_role=request.user_role
        )
        return SearchResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn Qdrant: {str(e)}")

@router.get("/filters", summary="Lấy danh sách các bộ lọc Category và Module có sẵn")
async def get_search_filters():
    service = SearchService.get_instance()
    return service.get_available_filters()
