"""Main RAG pipeline orchestration.

This is the core of the Q&A system. It chains together:
  1. Query rewriting
  2. Hybrid retrieval (vector + BM25 + RRF)
  3. LLM reranking
  4. Context dedup & assembly
  5. LLM generation with SSE streaming
"""
import json
import time
import asyncio
from typing import AsyncGenerator, List, Tuple

from app.models.document_chunk import DocumentChunk
from app.rag.retrieval.query_rewriter import rewrite_query
from app.rag.retrieval.hybrid_retriever import hybrid_search
from app.rag.retrieval.reranker import llm_rerank
from app.rag.retrieval.context_builder import deduplicate_chunks, build_context
from app.rag.generation.llm_factory import get_chat_llm
from app.rag.generation.prompts import RAG_SYSTEM_PROMPT
from app.rag.generation.post_processor import format_answer_with_sources


async def run_rag_pipeline(
    question: str,
    chat_history: str = "",
    conversation_id: str = "",
) -> AsyncGenerator[str, None]:
    """Execute the full RAG pipeline and yield SSE events.

    Args:
        question: The user's question.
        chat_history: Formatted chat history string.
        conversation_id: Current conversation ID for context.

    Yields:
        SSE-formatted event strings.
    """
    t_start = time.time()
    retrieval_time = 0

    # Step 1: Query rewriting
    rewritten_query = await rewrite_query(question)

    # Step 2: Hybrid retrieval
    retrieval_start = time.time()
    search_results = await hybrid_search(rewritten_query, top_k=15)
    retrieval_time = (time.time() - retrieval_start) * 1000  # ms

    if not search_results:
        yield f"data: {json.dumps({'content': '抱歉，知识库中暂无与该问题相关的信息。请尝试换个问法。', 'type': 'text'})}\n\n"
        yield f"event: done\ndata: {json.dumps({'total_tokens': 0, 'response_time_ms': int((time.time() - t_start) * 1000), 'retrieval_time_ms': int(retrieval_time)})}\n\n"
        return

    # Step 3: Reranking
    ranked_chunks = await llm_rerank(rewritten_query, search_results, top_k=5)

    # Step 4: Dedup & build context
    deduped = deduplicate_chunks(ranked_chunks)
    context, citations = build_context(deduped)

    # Step 5: Build prompt
    prompt = RAG_SYSTEM_PROMPT.format(
        chat_history=chat_history,
        context=context,
        question=question,
    )

    # Step 6: Generate streaming response
    llm = get_chat_llm(streaming=True)
    full_answer = ""

    try:
        async for chunk in llm.astream(prompt):
            if chunk.content:
                full_answer += chunk.content
                yield f"data: {json.dumps({'content': chunk.content, 'type': 'text'})}\n\n"

        # Step 7: Send citations after generation
        if citations:
            yield f"event: citation\ndata: {json.dumps({'citations': citations})}\n\n"

        # Step 8: Send completion event
        response_time = int((time.time() - t_start) * 1000)
        yield f"event: done\ndata: {json.dumps({'total_tokens': len(full_answer) // 3, 'response_time_ms': response_time, 'retrieval_time_ms': int(retrieval_time)})}\n\n"

    except Exception as e:
        error_msg = f"生成回答时出错：{str(e)}"
        yield f"data: {json.dumps({'content': error_msg, 'type': 'error'})}\n\n"
        yield f"event: done\ndata: {json.dumps({'total_tokens': 0, 'response_time_ms': int((time.time() - t_start) * 1000), 'retrieval_time_ms': int(retrieval_time)})}\n\n"


async def get_chat_history_text(conversation_id: str, max_turns: int = 5) -> str:
    """Get recent chat history formatted for the prompt.

    Args:
        conversation_id: UUID of the conversation.
        max_turns: Max Q&A pairs to include.

    Returns:
        Formatted chat history string.
    """
    from app.core.db import async_session_factory
    from sqlalchemy import select
    from app.models.message import Message

    async with async_session_factory() as db:
        q = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_turns * 2)
        )
        result = await db.execute(q)
        messages = list(result.scalars().all())
        messages.reverse()

    if not messages:
        return ""

    history_parts = []
    for msg in messages:
        role_label = "用户" if msg.role == "user" else "助手"
        history_parts.append(f"{role_label}：{msg.content[:300]}")

    return "\n".join(history_parts)
