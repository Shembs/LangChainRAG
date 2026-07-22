"""PGVector vector store operations."""
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import async_session_factory
from app.models.document_chunk import DocumentChunk
from app.models.chunk_embedding import ChunkEmbedding


async def store_embeddings(
    db: AsyncSession,
    chunk_ids: List[uuid.UUID],
    embeddings: List[List[float]],
    model_name: str,
) -> List[ChunkEmbedding]:
    """Store embeddings for document chunks in PGVector.

    Args:
        db: Database session.
        chunk_ids: List of chunk UUIDs.
        embeddings: List of embedding vectors (matching order).
        model_name: Name of the embedding model used.

    Returns:
        List of created ChunkEmbedding objects.
    """
    embedding_objs = []
    for chunk_id, vector in zip(chunk_ids, embeddings):
        emb = ChunkEmbedding(
            chunk_id=chunk_id,
            embedding=vector,
            embedding_model=model_name,
        )
        db.add(emb)
        embedding_objs.append(emb)

    await db.flush()
    return embedding_objs


async def similarity_search(
    query_embedding: List[float],
    top_k: int = 15,
) -> List[Tuple[DocumentChunk, float]]:
    """Perform cosine similarity search via PGVector.

    Args:
        query_embedding: The query vector (1536-dim).
        top_k: Number of top results to return.

    Returns:
        List of (DocumentChunk, similarity_score) tuples, sorted by score descending.
    """
    from app.models.document import Document

    async with async_session_factory() as db:
        # Use PGVector's <=> operator for cosine distance
        # Convert to similarity: 1 - distance
        embedding_str = f"[{','.join(str(v) for v in query_embedding)}]"

        query = text("""
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                dc.token_count,
                dc.page_number,
                dc.section_title,
                dc.created_at,
                1 - (ce.embedding <=> :query_vec::vector) AS similarity
            FROM chunk_embeddings ce
            JOIN document_chunks dc ON dc.id = ce.chunk_id
            JOIN documents d ON d.id = dc.document_id
            WHERE d.status = 'completed'
            ORDER BY ce.embedding <=> :query_vec::vector
            LIMIT :top_k
        """)

        result = await db.execute(
            query,
            {"query_vec": embedding_str, "top_k": top_k},
        )
        rows = result.fetchall()

        chunks = []
        for row in rows:
            chunk = DocumentChunk(
                id=row[0],
                document_id=row[1],
                chunk_index=row[2],
                content=row[3],
                token_count=row[4],
                page_number=row[5],
                section_title=row[6],
                created_at=row[7],
            )
            similarity = float(row[8])
            chunks.append((chunk, similarity))

        return chunks


async def delete_embeddings_by_document(db: AsyncSession, document_id: uuid.UUID) -> int:
    """Delete all embeddings for a document (cascaded through chunks)."""
    q = text("""
        DELETE FROM chunk_embeddings
        WHERE chunk_id IN (
            SELECT id FROM document_chunks WHERE document_id = :doc_id
        )
    """)
    result = await db.execute(q, {"doc_id": document_id})
    return result.rowcount


async def keyword_search(
    query: str,
    top_k: int = 10,
) -> List[DocumentChunk]:
    """Perform BM25-style keyword search using PostgreSQL full-text search (tsvector).

    Args:
        query: The keyword query.
        top_k: Number of results to return.

    Returns:
        List of DocumentChunk objects.
    """
    from app.models.document import Document

    async with async_session_factory() as db:
        # Use PostgreSQL full-text search with ts_rank
        q = text("""
            SELECT
                dc.id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                dc.token_count,
                dc.page_number,
                dc.section_title,
                dc.created_at,
                ts_rank(dc.content_tsv, plainto_tsquery('simple', :query)) AS rank
            FROM document_chunks dc
            JOIN documents d ON d.id = dc.document_id
            WHERE d.status = 'completed'
              AND dc.content_tsv @@ plainto_tsquery('simple', :query)
            ORDER BY rank DESC
            LIMIT :top_k
        """)

        result = await db.execute(q, {"query": query, "top_k": top_k})
        rows = result.fetchall()

        chunks = []
        for row in rows:
            chunk = DocumentChunk(
                id=row[0],
                document_id=row[1],
                chunk_index=row[2],
                content=row[3],
                token_count=row[4],
                page_number=row[5],
                section_title=row[6],
                created_at=row[7],
            )
            chunks.append(chunk)

        return chunks
