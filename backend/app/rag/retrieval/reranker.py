"""LLM-based reranking for retrieved chunks."""
from typing import List, Tuple
from langchain_openai import ChatOpenAI
from app.config import settings
from app.models.document_chunk import DocumentChunk


RERANK_PROMPT = """你是一个信息检索质量评估专家。请评估以下文本片段与用户问题的相关度。

用户问题：{question}

以下是检索到的多个文本片段，请为每个片段打分（1-10分，10分表示完全相关）：

{chunks}

请严格按照以下 JSON 格式返回结果（只返回 JSON，不要加任何其他内容）：
[{{"index": 0, "score": 8}}, {{"index": 1, "score": 3}}, ...]
"""


def get_rerank_llm() -> ChatOpenAI:
    """Get an LLM instance for reranking."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        temperature=0.0,
        max_tokens=500,
    )


async def llm_rerank(
    question: str,
    chunks: List[Tuple[DocumentChunk, float]],
    top_k: int = 5,
) -> List[Tuple[DocumentChunk, float]]:
    """Rerank retrieved chunks using DeepSeek LLM for relevance scoring.

    If fewer than top_k chunks, return all of them without reranking.

    Args:
        question: The user's question.
        chunks: List of (chunk, retrieval_score) from hybrid search.
        top_k: Number of top results to return after reranking.

    Returns:
        Reranked list of (chunk, llm_score) tuples.
    """
    if len(chunks) <= top_k:
        return chunks

    # Format chunks for LLM evaluation
    chunks_text = ""
    for i, (chunk, _) in enumerate(chunks):
        # Truncate long chunks to save tokens
        preview = chunk.content[:300].replace("\n", " ").strip()
        chunks_text += f"片段 {i}：{preview}\n\n"

    prompt = RERANK_PROMPT.format(question=question, chunks=chunks_text)

    llm = get_rerank_llm()
    try:
        response = llm.invoke(prompt)
        import json
        import re

        # Extract JSON from response (may have markdown code block)
        content = response.content.strip()
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if json_match:
            scores = json.loads(json_match.group())
        else:
            scores = json.loads(content)

        # Map scores back to chunks
        reranked = []
        for score_item in scores:
            idx = score_item.get("index", 0)
            llm_score = score_item.get("score", 5)
            if idx < len(chunks):
                chunk, _ = chunks[idx]
                reranked.append((chunk, float(llm_score) / 10.0))  # Normalize to 0-1

        # Sort by LLM score descending
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]

    except Exception:
        # Fallback: return original top_k
        return chunks[:top_k]
