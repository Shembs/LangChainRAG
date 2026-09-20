from abc import ABC, abstractmethod
from typing import Optional, Union
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_deepseek import ChatDeepSeek
from utils.config_handler import rag_conf


class BaseModelFactory(ABC):
    @abstractmethod
    def build(self) -> Optional[Union[Embeddings| BaseChatModel]]:
        """返回嵌入模型或聊天模型实例"""
        pass


class ChatModelFactory(BaseModelFactory):
    # 修正1: 实现抽象方法 build()（原代码只定义了 generate()，
    #        未实现父类 BaseModelFactory 的抽象方法 build()，
    #        导致实例化时抛出 TypeError: Can't instantiate abstract class）
    def build(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatDeepSeek(
            model=rag_conf["chat_model_name"],
            temperature=rag_conf.get("temperature", 0.7),
        )


class EmbeddingModelFactory(BaseModelFactory):
    # 修正2: EmbddingModelFactory → EmbeddingModelFactory（拼写错误）
    def build(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


chat_model = ChatModelFactory().build()

# 修正3: 类名从 EmbddingModelFactory 改为 EmbeddingModelFactory
embedding_model = EmbeddingModelFactory().build()
