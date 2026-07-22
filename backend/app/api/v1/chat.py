"""Chat and conversation API routes."""
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db, async_session_factory
from app.api.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import (
    AskRequest,
    ConversationResponse,
    ConversationListResponse,
    CreateConversationRequest,
    UpdateConversationRequest,
)
from app.services.chat_service import (
    save_user_message,
    save_assistant_message,
    auto_generate_title,
)
from app.rag.rag_chain import run_rag_pipeline, get_chat_history_text

router = APIRouter()


@router.get("/sessions", response_model=ConversationListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's chat sessions."""
    count_q = select(func.count(Conversation.id)).where(
        Conversation.user_id == current_user.id
    )
    total = (await db.execute(count_q)).scalar()

    q = (
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(q)
    sessions = result.scalars().all()

    return ConversationListResponse(
        items=[ConversationResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.post("/sessions", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    conv = Conversation(
        user_id=current_user.id,
        title=data.title or "新对话",
    )
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return ConversationResponse.model_validate(conv)


@router.patch("/sessions/{session_id}", response_model=ConversationResponse)
async def update_session(
    session_id: str,
    data: UpdateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Rename or update a session."""
    conv = await db.get(Conversation, uuid.UUID(session_id))
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    if data.title is not None:
        conv.title = data.title
    conv.updated_at = datetime.now(timezone.utc)

    return ConversationResponse.model_validate(conv)


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session and all its messages."""
    conv = await db.get(Conversation, uuid.UUID(session_id))
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    await db.delete(conv)
    return {"message": "会话已删除"}


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all messages in a chat session."""
    conv = await db.get(Conversation, uuid.UUID(session_id))
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    q = (
        select(Message)
        .where(Message.conversation_id == conv.id)
        .order_by(Message.created_at)
    )
    result = await db.execute(q)
    messages = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "citations": m.citations or [],
            "response_time_ms": m.response_time_ms,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]


@router.post("/ask")
async def ask_question(
    data: AskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Ask a question and get a streaming RAG answer via SSE."""

    # Validate conversation ownership
    conv = await db.get(Conversation, uuid.UUID(data.conversation_id))
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # Save user message
    await save_user_message(db, conv.id, data.question)
    await db.commit()

    # Auto-generate title if this is the first message
    if conv.message_count <= 2:
        await auto_generate_title(db, conv.id, data.question)
        await db.commit()

    # Get chat history
    chat_history = await get_chat_history_text(data.conversation_id)

    async def event_stream():
        full_answer = ""
        citations = []
        response_time = 0

        async for event in run_rag_pipeline(
            question=data.question,
            chat_history=chat_history,
            conversation_id=data.conversation_id,
        ):
            yield event

            # Extract JSON data from SSE event (handles both single-line
            # "data: {...}" and multi-line "event: X\ndata: {...}" formats)
            data_str = None
            if "\ndata: " in event:
                data_str = event.split("\ndata: ", 1)[1].split("\n")[0]
            elif event.startswith("data: "):
                data_str = event.removeprefix("data: ").strip()

            if data_str:
                try:
                    parsed = json.loads(data_str)
                except (json.JSONDecodeError, KeyError):
                    parsed = None

                if parsed:
                    # Citation event
                    if "citations" in parsed:
                        citations = parsed.get("citations", [])
                    # Done event
                    elif "total_tokens" in parsed:
                        response_time = parsed.get("response_time_ms", 0)
                    # Text delta
                    elif parsed.get("type") == "text":
                        full_answer += parsed.get("content", "")

        # Save assistant message after streaming completes
        if full_answer:
            async with async_session_factory() as save_db:
                async with save_db.begin():
                    await save_assistant_message(
                        save_db,
                        uuid.UUID(data.conversation_id),
                        full_answer,
                        citations=citations,
                        response_time_ms=response_time,
                    )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
