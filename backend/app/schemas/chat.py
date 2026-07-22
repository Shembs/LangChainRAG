from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class AskRequest(BaseModel):
    conversation_id: str = Field(..., description="会话 ID")
    question: str = Field(..., min_length=1, max_length=5000, description="用户问题")


class CitationSchema(BaseModel):
    chunk_id: str
    doc_title: str
    preview: str
    score: float


class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    citations: Optional[List[CitationSchema]] = None
    response_time_ms: Optional[int] = None
    created_at: datetime

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)

    model_config = {"from_attributes": True}


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int


class CreateConversationRequest(BaseModel):
    title: Optional[str] = Field(default="新对话", max_length=500)


class UpdateConversationRequest(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
