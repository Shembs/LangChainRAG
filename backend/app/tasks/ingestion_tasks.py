"""Celery tasks for async document processing pipeline."""
import uuid
from typing import List

from celery import Celery
from sqlalchemy import select

from app.config import settings
from app.core.db import async_session_factory
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

celery_app = Celery(
    "rag_tasks",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    """Full document processing pipeline: load → chunk → embed → store.

    Runs asynchronously so the upload API returns immediately.
    """
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_process_document_async(document_id))
    finally:
        loop.close()


async def _process_document_async(document_id: str):
    """Async implementation of document processing."""
    from app.rag.ingestion.loader import load_document, preprocess_text
    from app.rag.ingestion.chunker import chunk_document
    from app.rag.ingestion.embedder import embed_texts
    from app.rag.ingestion.vector_store import store_embeddings
    from app.config import settings

    doc_uuid = uuid.UUID(document_id)

    async with async_session_factory() as db:
        # 1. Load the document record
        result = await db.execute(select(Document).where(Document.id == doc_uuid))
        doc = result.scalar_one_or_none()
        if not doc:
            print(f"[Task] Document {document_id} not found")
            return

        # 2. Update status to processing
        doc.status = "processing"
        await db.commit()

        try:
            # 3. Load the document
            file_path = f"{settings.upload_dir}/{document_id}_{doc.title}"
            # Fallback: find the file by scanning upload dir
            import os
            actual_path = None
            if os.path.exists(settings.upload_dir):
                for fname in os.listdir(settings.upload_dir):
                    if document_id in fname:
                        actual_path = os.path.join(settings.upload_dir, fname)
                        break

            if actual_path is None:
                raise FileNotFoundError(f"Uploaded file not found for doc {document_id}")

            docs = load_document(actual_path, doc.file_type)
            docs = preprocess_text(docs)

            # 4. Chunk the document
            chunks = chunk_document(docs, title=doc.title, file_type=doc.file_type)

            # 5. Store chunks in DB
            chunk_objs = []
            for i, chunk in enumerate(chunks):
                chunk_obj = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=i,
                    content=chunk.page_content,
                    page_number=chunk.metadata.get("page"),
                    section_title=chunk.metadata.get("section_title", ""),
                )
                db.add(chunk_obj)
                chunk_objs.append(chunk_obj)

            await db.flush()

            # 6. Generate embeddings (batch by 32 for API efficiency)
            chunk_texts = [c.content for c in chunk_objs]
            chunk_ids = [c.id for c in chunk_objs]
            all_embeddings = []

            batch_size = 32
            for i in range(0, len(chunk_texts), batch_size):
                batch = chunk_texts[i : i + batch_size]
                batch_embeddings = await embed_texts(batch)
                all_embeddings.extend(batch_embeddings)

            # 7. Store embeddings
            await store_embeddings(
                db,
                chunk_ids,
                all_embeddings,
                model_name=settings.embedding_model,
            )

            # 8. Update document record
            doc.status = "completed"
            doc.chunk_count = len(chunks)
            await db.commit()

            print(f"[Task] Document {doc.title}: processed {len(chunks)} chunks successfully")

        except Exception as e:
            doc.status = "error"
            doc.error_message = str(e)
            await db.commit()
            print(f"[Task] Document {doc.title}: processing failed - {e}")
            raise
