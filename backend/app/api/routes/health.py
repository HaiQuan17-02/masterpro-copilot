from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Health Check")
async def health_check():
    return {
        "status": "ok",
        "service": "masterpro-copilot-backend"
    }
