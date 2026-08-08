"""
总结服务，用于对文档进行总结，用户提问后，根据文档内容生成总结

当知识库中无相关文档时，返回 [知识库未匹配] 标记，
由上游 Agent 根据此标记决定是否使用 LLM 自身知识回答。
"""
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
# 修正: rag → RAG，与目录名大小写一致，否则 pip install 后 ModuleNotFoundError
from RAG.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from utils.config_handler import chroma_conf
from utils.logger_handler import logger

# ---------------------------------------------------------------------------
# 相似度阈值常量
# Chroma 使用余弦距离：0=完全相同, 1=正交/无关, 2=完全相反
# 距离 > 此阈值视为知识库无匹配
# ---------------------------------------------------------------------------
_KB_SIMILARITY_THRESHOLD: float = 1.0

# 知识库未匹配时的返回标记（Agent prompt 需识别此标记）
KB_NOT_FOUND_MARKER: str = "[知识库未匹配]"


def print_prompt(prompt):
    print("="*50)
    print(prompt.to_string())
    print("="*50)
    return prompt


class RagSummarizerService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        # 修正1: self.vector_store.retriever() → self.vector_store.get_retriever()
        #        VectorStoreService 中定义的方法是 get_retriever()，原名称会导致 AttributeError
        self.retriever = self.vector_store.get_retriever()
        # 修正2: load_rag_prompt → load_rag_prompt()
        #        load_rag_prompt 是一个函数，必须调用才能获取 prompt 字符串，
        #        否则 PromptTemplate.from_template() 会收到函数对象而报错
        self.prompt_text = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = chat_model
        self.chain = self.__init__chain()

    # 修正3: __init__chain 从 __init__ 内部提升为类级方法（缩进从 8 空格改为 4 空格）
    #        原代码将 def __init__chain 嵌套在 __init__ 内部，导致：
    #        1) 它是 __init__ 的局部函数，self 无法通过 self.__init__chain() 找到它
    #        2) 定义出现在调用 self.__init__chain() 之后，即使作为局部变量也存在顺序问题
    def __init__chain(self):
        chain = self.prompt_template | print_prompt | self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:
        """从向量库检索相关文档，并基于相似度阈值过滤不相关结果。

        改用 similarity_search_with_score 替代 retriever.invoke()，
        以便获取每个文档的相似度分数，过滤掉相似度过低的无关文档。

        Args:
            query: 检索查询字符串。

        Returns:
            list[Document]: 相似度高于阈值的文档列表；无匹配时返回空列表。
        """
        k: int = chroma_conf.get("k", 3)
        try:
            docs_with_scores = self.vector_store.vector_store.similarity_search_with_score(
                query, k=k
            )
        except Exception as e:
            logger.error(f"[RAG检索]相似度检索失败: {e}", exc_info=True)
            return []

        relevant_docs: list[Document] = []
        for doc, score in docs_with_scores:
            if score < _KB_SIMILARITY_THRESHOLD:
                relevant_docs.append(doc)
                logger.info(f"[RAG检索]匹配文档(score={score:.4f}): {doc.page_content[:80]}...")
            else:
                logger.info(f"[RAG检索]过滤低相关文档(score={score:.4f} > {_KB_SIMILARITY_THRESHOLD})")

        if not relevant_docs:
            logger.info(f"[RAG检索]查询 '{query[:50]}...' 未找到相关文档（阈值={_KB_SIMILARITY_THRESHOLD}）")

        return relevant_docs

    def rag_summarize(self, query: str) -> str:
        """基于知识库文档生成总结回答。

        当向量库中无相关文档时（相似度均低于阈值），返回 KB_NOT_FOUND_MARKER 标记，
        由上游 Agent 识别此标记后使用 LLM 自身知识回答。

        Args:
            query: 用户查询字符串。

        Returns:
            str: 总结文本，或 KB_NOT_FOUND_MARKER 标记。
        """
        content_docs = self.retriever_docs(query)

        # 无匹配文档时返回标记，让 Agent 使用自身 LLM 知识回答
        if not content_docs:
            return KB_NOT_FOUND_MARKER

        context = ""
        counter = 0
        for doc in content_docs:
            counter += 1
            context += f"[参考资料{counter}]\n{doc.page_content} |参考元数据: {doc.metadata}\n\n"

        # 修正7: chain.inject() → chain.invoke()
        #        LangChain LCEL 链使用 .invoke() 方法执行，.inject() 不存在
        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == '__main__':
    rag = RagSummarizerService()

    rag.rag_summarize("小户型适合那种扫地机器人")
