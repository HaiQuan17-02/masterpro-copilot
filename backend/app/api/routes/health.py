from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", summary="Health check endpoint")
def health():
    return {
        "status": "healthy",
        "service": "MasterPro Copilot Backend"
    }
