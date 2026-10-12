from fastapi import APIRouter, Query, Body, HTTPException, Header
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel, Field
from app.services.rag_engine import RAGEngine

router = APIRouter(prefix="/chat", tags=["RAG Streaming"])

class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Câu hỏi người dùng")
    user_role: Optional[str] = Field(None, description="Vai trò: cashier, inventory, accountant, admin")

@router.post("/stream", summary="SSE Streaming Chat Endpoint (Server-Sent Events)")
async def chat_stream_post(
    request: ChatStreamRequest,
    x_user_role: Optional[str] = Header(None)
):
    role = request.user_role or x_user_role or "admin"
    engine = RAGEngine.get_instance()
    return StreamingResponse(
        engine.query_stream(request.message, user_role=role),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/stream", summary="GET SSE Streaming Chat Endpoint for EventSource compatibility")
async def chat_stream_get(
    q: str = Query(..., min_length=1, description="Câu hỏi nghiệp vụ"),
    role: Optional[str] = Query(None, description="Vai trò người dùng"),
    x_user_role: Optional[str] = Header(None)
):
    user_r = role or x_user_role or "admin"
    engine = RAGEngine.get_instance()
    return StreamingResponse(
        engine.query_stream(q, user_role=user_r),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
