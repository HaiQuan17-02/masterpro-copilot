from fastapi import APIRouter
from app.core.database import check_db_connection

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health check endpoint")
def health():
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status.get("status") == "connected" else "degraded",
        "service": "MasterPro Copilot Backend",
        "database": db_status
    }

