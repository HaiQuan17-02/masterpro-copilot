from fastapi import APIRouter
from app.core.database import check_db_connection
from app.services.search_service import SearchService
from ai.providers.hybrid_manager import HybridProviderManager

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Comprehensive Health check endpoint")
def health():
    db_status = check_db_connection()
    
    # Check Qdrant status
    qdrant_status = {"status": "unknown"}
    try:
        search_svc = SearchService.get_instance()
        col_info = search_svc.store.client.get_collection(
            search_svc.store.collection_name
        )
        qdrant_status = {
            "status": "connected",
            "collection": search_svc.store.collection_name,
            "points_count": getattr(col_info, "points_count", 0),
            "vectors_count": getattr(col_info, "vectors_count", 0)
        }
    except Exception as e:
        qdrant_status = {
            "status": "degraded",
            "error": str(e)
        }

    # Check Provider status
    try:
        provider_info = HybridProviderManager.get_instance().get_status()
    except Exception as e:
        provider_info = {"status": "unknown", "error": str(e)}

    is_healthy = (
        db_status.get("status") in ("connected", "mocked") and
        qdrant_status.get("status") == "connected"
    )

    return {
        "status": "healthy" if is_healthy else "degraded",
        "service": "MasterPro Copilot Backend",
        "version": "1.0.0",
        "database": db_status,
        "qdrant": qdrant_status,
        "provider": provider_info
    }
