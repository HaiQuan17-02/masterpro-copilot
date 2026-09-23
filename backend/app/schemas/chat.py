from typing import List, Optional
from pydantic import BaseModel

class CitationItem(BaseModel):
    title: str
    document: str
    page: Optional[int] = None
    chunk_id: Optional[str] = None
    score: Optional[float] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    citations: List[CitationItem] = []
    provider: str
    model: str
