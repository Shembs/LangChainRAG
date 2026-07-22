"""Post-processing: extract citations and format the final answer."""
import re
from typing import List, Tuple


def extract_citation_markers(answer: str) -> List[int]:
    """Extract citation markers like [1], [2] from the generated answer.

    Args:
        answer: The generated answer text.

    Returns:
        List of unique citation indices used in the answer.
    """
    pattern = r"\[(\d+)\]"
    matches = re.findall(pattern, answer)
    indices = sorted(set(int(m) for m in matches))
    return indices


def format_answer_with_sources(
    answer: str,
    citations: List[dict],
) -> Tuple[str, List[dict]]:
    """Format the final answer and filter citations to only those referenced.

    Args:
        answer: The raw LLM-generated answer.
        citations: All citations from context building.

    Returns:
        Tuple of (formatted_answer, filtered_citations).
    """
    # Extract which citations were actually referenced
    used_indices = extract_citation_markers(answer)

    # Filter citations to only those used
    used_citations = []
    for idx in used_indices:
        if 1 <= idx <= len(citations):
            used_citations.append(citations[idx - 1])

    # If no explicit citations found but we have sources, add a source section
    if not used_indices and citations:
        answer += "\n\n---\n**参考来源：**\n"
        for i, citation in enumerate(citations):
            answer += f"\n[{i + 1}] {citation['doc_title']} — {citation['preview'][:100]}..."

    return answer, used_citations
