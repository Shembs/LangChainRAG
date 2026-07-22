"""Document loaders for various file types using LangChain."""
from pathlib import Path
from typing import List

from langchain_core.documents import Document as LCDocument
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
)


def load_document(file_path: str, file_type: str) -> List[LCDocument]:
    """Load a document from disk using the appropriate LangChain loader.

    Args:
        file_path: Absolute path to the document file.
        file_type: File extension (pdf, txt, csv, md, docx).

    Returns:
        List of LangChain Document objects.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    loader_map = {
        "pdf": lambda p: PyPDFLoader(str(p)),
        "txt": lambda p: TextLoader(str(p), encoding="utf-8"),
        "csv": lambda p: CSVLoader(str(p), encoding="utf-8"),
        "md": lambda p: UnstructuredMarkdownLoader(str(p)),
        "docx": lambda p: Docx2txtLoader(str(p)),
    }

    loader_fn = loader_map.get(file_type.lower())
    if loader_fn is None:
        raise ValueError(f"Unsupported file type: {file_type}")

    loader = loader_fn(path)
    docs = loader.load()

    # Add source filename to metadata
    for doc in docs:
        doc.metadata["source_file"] = path.name

    return docs


def preprocess_text(docs: List[LCDocument]) -> List[LCDocument]:
    """Clean and normalize document text.

    - Remove excessive whitespace
    - Normalize Chinese punctuation
    - Remove empty documents
    """
    cleaned = []
    for doc in docs:
        text = doc.page_content
        # Remove excessive newlines
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        # Strip leading/trailing whitespace
        text = text.strip()
        if text:  # Skip empty documents
            doc.page_content = text
            cleaned.append(doc)
    return cleaned
