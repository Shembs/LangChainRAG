"""Knowledge base management API routes (admin only)."""
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Form
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.knowledge import (
    DocumentResponse,
    DocumentListResponse,
    ChunkResponse,
    KnowledgeStats,
)
from app.config import settings

router = APIRouter()


@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    category: str = Form("通用"),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or more documents to the knowledge base (admin only).

    The documents will be processed asynchronously via Celery.
    Full processing (chunking + embedding) will be implemented in Phase 2.
    """
    uploaded_docs = []
    os.makedirs(settings.upload_dir, exist_ok=True)

    for file in files:
        # Validate file type
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext not in ("pdf", "txt", "csv", "md", "docx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {ext}",
            )

        # Save file
        content = await file.read()
        content_hash = hashlib.sha256(content).hexdigest()

        # Check for duplicates
        q = select(Document).where(Document.content_hash == content_hash)
        result = await db.execute(q)
        if result.scalar_one_or_none():
            continue  # Skip duplicates silently

        doc_id = uuid.uuid4()
        file_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            id=doc_id,
            title=file.filename,
            file_type=ext,
            file_size_bytes=len(content),
            content_hash=content_hash,
            category=category,
            status="pending",
            uploaded_by=current_user.id,
        )
        db.add(doc)
        uploaded_docs.append(doc)

    await db.flush()

    # Trigger async processing via Celery
    from app.tasks.ingestion_tasks import process_document
    for doc in uploaded_docs:
        process_document.delay(str(doc.id))

    return {
        "message": f"成功上传 {len(uploaded_docs)} 个文档，正在后台处理中...",
        "document_ids": [str(d.id) for d in uploaded_docs],
    }


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="搜索文档标题"),
    category: str = Query("", description="按分类筛选"),
    status_filter: str = Query("", description="按状态筛选"),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """List all documents in the knowledge base (admin only)."""
    conditions = []

    if search:
        conditions.append(Document.title.ilike(f"%{search}%"))
    if category:
        conditions.append(Document.category == category)
    if status_filter:
        conditions.append(Document.status == status_filter)

    # Count
    count_q = select(func.count(Document.id))
    if conditions:
        count_q = count_q.where(*conditions)
    total = (await db.execute(count_q)).scalar()

    # Fetch
    q = select(Document).order_by(Document.created_at.desc())
    if conditions:
        q = q.where(*conditions)
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    docs = result.scalars().all()

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in docs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a single document's details (admin only)."""
    doc = await db.get(Document, uuid.UUID(doc_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    return DocumentResponse.model_validate(doc)


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document and its chunks/embeddings (admin only)."""
    doc = await db.get(Document, uuid.UUID(doc_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    # Delete the file from disk if it exists
    # (file_path is stored in the document metadata — simplified for now)

    await db.delete(doc)
    return {"message": "文档已删除"}


@router.get("/documents/{doc_id}/chunks")
async def get_document_chunks(
    doc_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all chunks for a document (admin only)."""
    doc = await db.get(Document, uuid.UUID(doc_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    q = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.chunk_index)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(q)
    chunks = result.scalars().all()

    # Count
    count_q = select(func.count(DocumentChunk.id)).where(
        DocumentChunk.document_id == doc.id
    )
    total = (await db.execute(count_q)).scalar()

    return {
        "items": [ChunkResponse.model_validate(c) for c in chunks],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats", response_model=KnowledgeStats)
async def get_knowledge_stats(
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get knowledge base statistics (admin only)."""
    # Total documents
    total_docs = (await db.execute(select(func.count(Document.id)))).scalar()

    # Total chunks
    total_chunks = (await db.execute(select(func.count(DocumentChunk.id)))).scalar()

    # Total size
    total_size = (await db.execute(
        select(func.coalesce(func.sum(Document.file_size_bytes), 0))
    )).scalar()

    # By status
    status_q = await db.execute(
        select(Document.status, func.count(Document.id)).group_by(Document.status)
    )
    by_status = {row[0]: row[1] for row in status_q.all()}

    # By category
    cat_q = await db.execute(
        select(Document.category, func.count(Document.id)).group_by(Document.category)
    )
    by_category = {row[0]: row[1] for row in cat_q.all()}

    return KnowledgeStats(
        total_documents=total_docs,
        total_chunks=total_chunks,
        total_size_bytes=total_size or 0,
        documents_by_status=by_status,
        documents_by_category=by_category,
    )
