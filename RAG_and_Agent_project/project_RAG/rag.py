from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from vector_store import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_deepseek import ChatDeepSeek
from langchain_core.output_parsers import StrOutputParser
from file_history_store import get_history
from langchain_core.runnables import RunnableLambda


class RagService:
    def __init__(self):
        self.vector_service = VectorStoreService(
            embedding = DashScopeEmbeddings(model = config.embedding_model_name),
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system",
                    "你是智能客服助手。请按以下规则回答用户问题：\n"
                    "1. 如果参考资料中有相关信息，请基于参考资料准确回答，注明来源\n"
                    "2. 如果参考资料不足或无相关内容，可以结合你自己的知识给出有帮助的回答\n"
                    "3. 回答要简洁、专业\n\n"
                    "参考资料：{context}"
                ),
                MessagesPlaceholder("history"),
                ("user","{input}")
            ]
        )

        self.chat_model = ChatDeepSeek(model = config.chat_model_name)

        self.chain = self.get_chain()

    def get_chain(self):
        retriever = self.vector_service.get_retriever()

        def format_document(docs):
            if not docs:
                return "无参考资料"
            return "\n\n".join(f"文档片段：{d.page_content}\n元数据：{d.metadata}" for d in docs)

        retrieval_chain = (lambda x: x["input"]) | retriever | format_document

        chain = (
                RunnablePassthrough.assign(context=retrieval_chain)
                | self.prompt_template
                | self.chat_model
                | StrOutputParser()
        )

        return RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",
        )


if __name__ == '__main__':
    # sssionID配置
    session_config = {
        "configurable":{
            "session_id": "user001"
        }
    }
    res = RagService().chain.invoke({"input":"我的体重是多少"},session_config)
    print(res)



