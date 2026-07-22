"""Chunking strategies optimized for different document types."""
from typing import Dict, List

from langchain_core.documents import Document as LCDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

# Chunking configurations by document type
CHUNKING_CONFIG: Dict[str, dict] = {
    "product_specs": {
        "chunk_size": 500,
        "chunk_overlap": 80,
        "separators": ["\n\n", "\n", "。", ".", "；", ";", " "],
    },
    "usage_guide": {
        "chunk_size": 800,
        "chunk_overlap": 150,
        "separators": ["\n\n## ", "\n\n", "\n", "。", ".", " "],
    },
    "faq": {
        "chunk_size": 300,
        "chunk_overlap": 50,
        "separators": ["\n\nQ:", "\n\n问：", "\n\n", "\n"],
    },
    "pricing": {
        "chunk_size": 400,
        "chunk_overlap": 60,
        "separators": ["\n\n", "\n", ",", " "],
    },
    "default": {
        "chunk_size": settings.default_chunk_size,
        "chunk_overlap": settings.default_chunk_overlap,
        "separators": ["\n\n", "\n", "。", ".", "；", ";", " "],
    },
}


def detect_document_category(title: str, file_type: str) -> str:
    """Detect the document category based on its title for chunking strategy.

    Rules:
    - Files with 'FAQ' or '问答' → faq
    - Files with '价格', 'price', '报价' → pricing
    - Files with '规格', 'spec', '参数' → product_specs
    - Files with '指南', 'guide', '说明', '使用' → usage_guide
    - CSV files → pricing (assume product listings)
    - Otherwise → default
    """
    title_lower = title.lower()

    if file_type == "csv":
        return "pricing"
    if any(kw in title_lower for kw in ["faq", "问答", "常见问题"]):
        return "faq"
    if any(kw in title_lower for kw in ["价格", "price", "报价", "价目"]):
        return "pricing"
    if any(kw in title_lower for kw in ["规格", "spec", "参数", "配置"]):
        return "product_specs"
    if any(kw in title_lower for kw in ["指南", "guide", "说明", "使用", "教程", "操作"]):
        return "usage_guide"

    return "default"


def chunk_document(
    docs: List[LCDocument],
    title: str = "",
    file_type: str = "",
) -> List[LCDocument]:
    """Split documents into chunks using the optimal strategy for their type.

    Args:
        docs: Loaded LangChain documents.
        title: Document title for category detection.
        file_type: File extension.

    Returns:
        List of chunked LangChain documents.
    """
    category = detect_document_category(title, file_type)
    config = CHUNKING_CONFIG.get(category, CHUNKING_CONFIG["default"])

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=config["separators"],
        keep_separator=True,
        length_function=len,
    )

    chunks = splitter.split_documents(docs)

    # Add chunk metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["chunk_category"] = category

    return chunks
