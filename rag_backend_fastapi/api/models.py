"""Pydantic models for API requests and responses"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    answer: str
    context_used: bool
    chunks_count: int


class UploadResponse(BaseModel):
    doc_id: str
    file_url: str
    chunks_count: int
    status: str
    message: str


class HistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    created_at: Optional[str] = None


class HistoryResponse(BaseModel):
    history: List[HistoryItem]
    count: int


class HealthResponse(BaseModel):
    status: str
    vectorstore: Optional[Dict] = None

