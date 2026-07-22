"""DeepSeek Embedding API wrapper."""
from typing import List
from langchain_openai import OpenAIEmbeddings
from app.config import settings


def get_embedding_model() -> OpenAIEmbeddings:
    """Create an OpenAI-compatible embedding model for DeepSeek API.

    DeepSeek's embedding endpoint is OpenAI-compatible.
    Returns an embedding model with 1536-dimensional vectors.
    """
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.embedding_api_key,
        openai_api_base=settings.embedding_api_base,
        dimensions=1536,
    )


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts using DeepSeek API.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each is List[float] of 1536 dims).
    """
    model = get_embedding_model()
    embeddings = model.embed_documents(texts)
    return embeddings


async def embed_query(query: str) -> List[float]:
    """Generate an embedding for a single query text.

    Args:
        query: The query string to embed.

    Returns:
        Embedding vector (List[float] of 1536 dims).
    """
    model = get_embedding_model()
    embedding = model.embed_query(query)
    return embedding
