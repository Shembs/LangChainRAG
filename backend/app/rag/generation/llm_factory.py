"""LLM factory for creating DeepSeek chat model instances."""
from langchain_openai import ChatOpenAI
from app.config import settings


def get_chat_llm(
    temperature: float = 0.1,
    streaming: bool = True,
    max_tokens: int = 2048,
) -> ChatOpenAI:
    """Create a DeepSeek ChatOpenAI instance.

    Args:
        temperature: Controls randomness (lower = more deterministic).
        streaming: Enable token-by-token streaming via SSE.
        max_tokens: Maximum output tokens.

    Returns:
        Configured ChatOpenAI LLM.
    """
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
    )
