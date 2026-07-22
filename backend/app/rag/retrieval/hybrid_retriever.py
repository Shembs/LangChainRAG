"""Hybrid retrieval: Vector + BM25 keyword search with RRF fusion."""
import asyncio
from typing import List, Tuple

from app.models.document_chunk import DocumentChunk
from app.rag.ingestion.embedder import embed_query
from app.rag.ingestion.vector_store import similarity_search, keyword_search


def reciprocal_rank_fusion(
    vector_results: List[Tuple[DocumentChunk, float]],
    keyword_results: List[DocumentChunk],
    k: int = 60,
    top_n: int = 15,
) -> List[Tuple[DocumentChunk, float]]:
    """Combine vector and keyword search results using Reciprocal Rank Fusion.

    Args:
        vector_results: List of (chunk, similarity_score) from vector search.
        keyword_results: List of chunks from BM25 keyword search.
        k: RRF constant (default 60).
        top_n: Number of top results to return after fusion.

    Returns:
        Merged and ranked list of (chunk, fused_score).
    """
    scores: dict[str, Tuple[DocumentChunk, float]] = {}

    # Vector scores (rank-based)
    for rank, (chunk, sim_score) in enumerate(vector_results):
        rrf_score = 1.0 / (k + rank + 1)
        chunk_id = str(chunk.id)
        # Blend RRF with raw similarity for better ordering
        blended = rrf_score + sim_score * 0.3
        scores[chunk_id] = (chunk, blended)

    # Keyword scores (rank-based)
    for rank, chunk in enumerate(keyword_results):
        rrf_score = 1.0 / (k + rank + 1)
        chunk_id = str(chunk.id)
        if chunk_id in scores:
            # Add RRF score for existing entry
            existing_chunk, existing_score = scores[chunk_id]
            scores[chunk_id] = (existing_chunk, existing_score + rrf_score)
        else:
            scores[chunk_id] = (chunk, rrf_score)

    # Sort by fused score descending
    sorted_results = sorted(scores.values(), key=lambda x: x[1], reverse=True)

    return sorted_results[:top_n]


async def hybrid_search(
    query: str,
    top_k: int = 15,
) -> List[Tuple[DocumentChunk, float]]:
    """Perform hybrid search: vector + keyword with RRF fusion.

    Both searches run concurrently for lower latency.

    Args:
        query: The search query.
        top_k: Number of results to return after fusion.

    Returns:
        List of (chunk, fused_score) tuples.
    """
    # Generate query embedding
    query_vec = await embed_query(query)

    # Run both searches concurrently
    vector_result, keyword_result = await asyncio.gather(
        similarity_search(query_vec, top_k=20),
        keyword_search(query, top_k=10),
    )

    # Fuse results
    fused = reciprocal_rank_fusion(
        vector_results=vector_result,
        keyword_results=keyword_result,
        k=60,
        top_n=top_k,
    )

    return fused
