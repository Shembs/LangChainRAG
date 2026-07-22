"""Chat service: save messages, manage sessions."""
import uuid
from datetime import datetime, timezone
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message


async def save_user_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    content: str,
) -> Message:
    """Save a user message and update conversation metadata."""
    msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=content,
    )
    db.add(msg)

    # Update conversation
    conv = await db.get(Conversation, conversation_id)
    if conv:
        conv.message_count = (conv.message_count or 0) + 1
        conv.updated_at = datetime.now(timezone.utc)

    await db.flush()
    return msg


async def save_assistant_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    content: str,
    citations: list = None,
    response_time_ms: int = None,
) -> Message:
    """Save an assistant message with citations and timing."""
    msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content,
        citations=citations or [],
        response_time_ms=response_time_ms,
    )
    db.add(msg)

    # Update conversation
    conv = await db.get(Conversation, conversation_id)
    if conv:
        conv.message_count = (conv.message_count or 0) + 1
        conv.updated_at = datetime.now(timezone.utc)

    await db.flush()
    return msg


async def auto_generate_title(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    question: str,
) -> None:
    """Auto-generate a conversation title from the first question.

    Uses a simple approach: takes first 20 chars of the question.
    In production, this would use an LLM call.
    """
    conv = await db.get(Conversation, conversation_id)
    if conv and (conv.title == "新对话" or not conv.title):
        # Simple approach: truncate the question
        title = question[:20].replace("\n", " ").strip()
        if len(question) > 20:
            title += "..."
        conv.title = title or "新对话"
