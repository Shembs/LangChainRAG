"""Query rewriting for better retrieval."""
from langchain_openai import ChatOpenAI
from app.config import settings


REWRITE_PROMPT = """你是一个电商商品知识库的查询优化助手。你的任务是将用户的问题改写成更适合检索的形式。

改写规则：
1. 将口语化表达改为正式的商品查询用语
2. 补充电商领域的同义词和常见缩写（如 "16PM" → "iPhone 16 Pro Max"）
3. 如果用户问题包含多个子问题，拆分为独立的查询语句
4. 保留原始问题的核心意图

用户问题：{question}

请返回改写后的问题（只返回改写后的问题，不要加任何解释）：

改写后的问题：
"""


def get_rewrite_llm() -> ChatOpenAI:
    """Get an LLM instance for query rewriting."""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_api_base,
        temperature=0.0,
        max_tokens=200,
    )


async def rewrite_query(question: str) -> str:
    """Rewrite a user question for better retrieval.

    Args:
        question: Original user question.

    Returns:
        Rewritten question optimized for retrieval.
    """
    llm = get_rewrite_llm()
    prompt = REWRITE_PROMPT.format(question=question)
    try:
        response = llm.invoke(prompt)
        rewritten = response.content.strip()
        # Fallback to original if rewriting fails or returns empty
        if not rewritten or len(rewritten) < 2:
            return question
        return rewritten
    except Exception:
        return question
