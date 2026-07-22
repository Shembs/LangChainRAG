"""Context assembly: deduplicate and format retrieved chunks."""
import hashlib
from typing import List, Tuple

from app.models.document_chunk import DocumentChunk


def jaccard_similarity(text1: str, text2: str) -> float:
    """Compute Jaccard similarity between two texts based on word tokens."""
    words1 = set(text1.split())
    words2 = set(text2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def deduplicate_chunks(
    chunks: List[Tuple[DocumentChunk, float]],
    threshold: float = 0.7,
) -> List[Tuple[DocumentChunk, float]]:
    """Remove near-duplicate chunks using Jaccard similarity.

    Keeps the higher-scoring chunk when duplicates are found.

    Args:
        chunks: List of (chunk, score) from reranker.
        threshold: Jaccard similarity threshold for dedup.

    Returns:
        Deduplicated list.
    """
    kept = []
    seen_contents = []  # Track kept contents for comparison

    for chunk, score in chunks:
        is_dup = False
        for seen in seen_contents:
            if jaccard_similarity(chunk.content, seen) > threshold:
                is_dup = True
                break
        if not is_dup:
            kept.append((chunk, score))
            seen_contents.append(chunk.content)

    return kept


def build_context(
    chunks: List[Tuple[DocumentChunk, float]],
    max_tokens: int = 4000,
) -> tuple[str, List[dict]]:
    """Build context string and citation list from retrieved chunks.

    Args:
        chunks: Ranked and deduplicated (chunk, score) list.
        max_tokens: Approximate max token limit (4 chars ≈ 1 token).

    Returns:
        Tuple of (context_string, citations_list).
    """
    context_parts = []
    citations = []

    token_budget = max_tokens * 4  # Approximate 4 chars per token
    used_tokens = 0

    for i, (chunk, score) in enumerate(chunks):
        # Get document title from the chunk's document relationship
        doc_title = "未知文档"

        chunk_text = f"[来源 {i + 1}] 文档: {doc_title}\n"
        if chunk.section_title:
            chunk_text += f"章节: {chunk.section_title}\n"
        chunk_text += f"内容: {chunk.content}\n\n"

        chunk_tokens = len(chunk_text)
        if used_tokens + chunk_tokens > token_budget:
            break

        context_parts.append(chunk_text)
        used_tokens += chunk_tokens

        citations.append({
            "chunk_id": str(chunk.id),
            "doc_title": doc_title,
            "preview": chunk.content[:200].strip(),
            "score": round(score, 4),
        })

    context = "".join(context_parts)
    return context, citations
