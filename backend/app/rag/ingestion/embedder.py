"""Local embedding model via HuggingFace sentence-transformers."""
import os
from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import settings

# Singleton instance
_embedding_model: HuggingFaceEmbeddings | None = None


def get_embedding_model() -> HuggingFaceEmbeddings:
    """Create or retrieve the local HuggingFace embedding model.

    Uses BAAI/bge-small-zh-v1.5 by default — 512-dimensional vectors,
    optimized for Chinese text, lightweight (~200MB download).

    Automatically uses HF_ENDPOINT mirror if set (for regions where
    huggingface.co is inaccessible).
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each is List[float] of 512 dims).
    """
    model = get_embedding_model()
    return model.embed_documents(texts)


async def embed_query(query: str) -> List[float]:
    """Generate an embedding for a single query text.

    Args:
        query: The query string to embed.

    Returns:
        Embedding vector (List[float] of 512 dims).
    """
    model = get_embedding_model()
    return model.embed_query(query)
