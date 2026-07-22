from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_serializer


class DocumentResponse(BaseModel):
    id: UUID
    title: str
    file_type: str
    file_size_bytes: Optional[int] = None
    category: Optional[str] = None
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class ChunkResponse(BaseModel):
    id: UUID
    chunk_index: int
    content: str
    token_count: Optional[int] = None
    page_number: Optional[int] = None
    section_title: Optional[str] = None

    @field_serializer("id")
    def serialize_id(self, id: UUID, _info) -> str:
        return str(id)

    model_config = {"from_attributes": True}


class KnowledgeStats(BaseModel):
    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents_by_status: dict
    documents_by_category: dict
