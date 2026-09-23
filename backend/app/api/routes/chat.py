from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_provider import get_ai_provider

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, summary="Send message to MasterPro Copilot")
async def chat_endpoint(request: ChatRequest):
    provider = get_ai_provider()
    result = await provider.generate_response(request.message)
    return ChatResponse(**result)
