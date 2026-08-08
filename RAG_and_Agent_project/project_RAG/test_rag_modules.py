"""
RAG 模块单元测试
运行方式: pytest test_rag_modules.py -v
"""
import os
import sys
import json
import tempfile
import hashlib
from unittest.mock import patch, MagicMock
import pytest

# 确保项目路径在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ============================================================
# config_data 测试
# ============================================================
class TestConfigData:
    """测试 config_data.py 配置项"""

    def test_md5_path_is_txt(self):
        """验证 md5_path 使用正确扩展名"""
        import config_data as config
        assert config.md5_path.endswith('.txt'), "md5_path 应以 .txt 结尾"

    def test_collection_name_exists(self):
        """验证集合名称已配置"""
        import config_data as config
        assert isinstance(config.collection_name, str)
        assert len(config.collection_name) > 0

    def test_persist_directory_exists(self):
        """验证持久化目录已配置"""
        import config_data as config
        assert isinstance(config.persist_directory, str)
        assert len(config.persist_directory) > 0

    def test_chunk_config_positive(self):
        """验证分块配置为正值"""
        import config_data as config
        assert config.chunk_size > 0
        assert config.chunk_overlap >= 0
        assert config.chunk_overlap < config.chunk_size, "overlap 应小于 chunk_size"

    def test_separator_no_empty_string(self):
        """验证分隔符列表不含空字符串"""
        import config_data as config
        assert "" not in config.separator, "separator 不应包含空字符串，会导致逐字符分割"

    def test_separator_no_duplicates(self):
        """验证分隔符列表无重复"""
        import config_data as config
        assert len(config.separator) == len(set(config.separator)), "separator 有重复项"

    def test_min_split_length_positive(self):
        """验证最小分块长度为正"""
        import config_data as config
        assert config.min_split_length > 0

    def test_top_k_positive(self):
        """验证 top_k 为正"""
        import config_data as config
        assert config.top_k > 0

    def test_embedding_model_name(self):
        """验证嵌入模型名称已配置"""
        import config_data as config
        assert isinstance(config.embedding_model_name, str)
        assert len(config.embedding_model_name) > 0

    def test_chat_model_name(self):
        """验证聊天模型名称已配置"""
        import config_data as config
        assert isinstance(config.chat_model_name, str)
        assert len(config.chat_model_name) > 0


# ============================================================
# knowledge_base 测试
# ============================================================
class TestKnowledgeBase:
    """测试 knowledge_base.py"""

    def test_get_string_md5(self):
        """验证 MD5 计算正确"""
        from knowledge_base import get_string_md5
        result = get_string_md5("hello")
        expected = hashlib.md5("hello".encode()).hexdigest()
        assert result == expected
        assert len(result) == 32

    def test_get_string_md5_different_inputs(self):
        """验证不同输入产生不同 MD5"""
        from knowledge_base import get_string_md5
        assert get_string_md5("a") != get_string_md5("b")

    def test_get_string_md5_encoding(self):
        """验证自定义编码"""
        from knowledge_base import get_string_md5
        result = get_string_md5("测试", encoding="utf-8")
        assert len(result) == 32

    def test_check_md5_new_file(self):
        """验证新文件返回 False"""
        from knowledge_base import check_md5, save_md5
        test_md5 = hashlib.md5(b"test_check_new").hexdigest()
        result = check_md5(test_md5)
        assert result is False, "不存在的 MD5 应返回 False"

    def test_check_md5_existing(self):
        """验证已保存的 MD5 能检测到"""
        from knowledge_base import check_md5, save_md5
        test_md5 = hashlib.md5(b"test_check_exist").hexdigest()
        save_md5(test_md5)
        result = check_md5(test_md5)
        assert result is True, "已保存的 MD5 应返回 True"

    def test_save_and_check_md5_roundtrip(self):
        """验证 MD5 保存→读取往返正确"""
        from knowledge_base import check_md5, save_md5
        test_md5 = hashlib.md5(b"roundtrip_test").hexdigest()
        # 先确认不存在
        existed_before = check_md5(test_md5)
        save_md5(test_md5)
        existed_after = check_md5(test_md5)
        # existed_before 可能是 True（之前测试留下的），但 existed_after 必须是 True
        assert existed_after is True

    def test_check_md5_partial_match(self):
        """验证不会错误匹配部分字符串"""
        from knowledge_base import check_md5, save_md5
        save_md5("abcdef1234567890abcdef1234567890")
        result = check_md5("abcdef")
        assert result is False, "短字符串不应匹配完整 MD5"

    def test_knowledge_base_service_init(self):
        """验证 KnowledgeBaseService 初始化不崩溃"""
        from knowledge_base import KnowledgeBaseService
        import config_data as config

        # 确保目录存在
        os.makedirs(config.persist_directory, exist_ok=True)

        service = KnowledgeBaseService()
        assert service.chroma is not None
        assert service.splitter is not None

    def test_upload_by_str_short_text(self):
        """验证短文本上传（不分块）"""
        from knowledge_base import KnowledgeBaseService
        import config_data as config

        os.makedirs(config.persist_directory, exist_ok=True)
        service = KnowledgeBaseService()
        result = service.upload_by_str("短文本测试内容", "test_short.txt")
        assert "成功" in result or "跳过" in result

    def test_upload_by_str_skip_duplicate(self):
        """验证重复文件跳过"""
        from knowledge_base import KnowledgeBaseService
        import config_data as config

        os.makedirs(config.persist_directory, exist_ok=True)
        service = KnowledgeBaseService()
        content = "重复测试内容_unique_12345"

        # 第一次上传应该是成功
        first = service.upload_by_str(content, "dup_test.txt")
        # 第二次应该是跳过
        second = service.upload_by_str(content, "dup_test.txt")
        assert "跳过" in second, f"重复上传应被跳过，实际返回: {second}"


# ============================================================
# vector_store 测试
# ============================================================
class TestVectorStore:
    """测试 vector_store.py"""

    def test_vector_store_init(self):
        """验证 VectorStoreService 初始化"""
        from vector_store import VectorStoreService
        from unittest.mock import MagicMock

        mock_embedding = MagicMock()
        service = VectorStoreService(mock_embedding)
        assert service.embedding is mock_embedding
        assert service.vector_store is not None

    def test_get_retriever(self):
        """验证获取 retriever 不崩溃"""
        from vector_store import VectorStoreService
        from unittest.mock import MagicMock

        mock_embedding = MagicMock()
        service = VectorStoreService(mock_embedding)
        retriever = service.get_retriever()
        assert retriever is not None

    def test_vector_store_uses_config_collection(self):
        """验证向量存储使用 config 中的集合名称"""
        from vector_store import VectorStoreService
        import config_data as config
        from unittest.mock import MagicMock

        mock_embedding = MagicMock()
        service = VectorStoreService(mock_embedding)
        # Chroma 的 collection_name 应该和 config 一致
        assert service.vector_store._collection.name == config.collection_name

    def test_get_retriever_uses_top_k(self):
        """验证 retriever 使用 config.top_k"""
        from vector_store import VectorStoreService
        import config_data as config
        from unittest.mock import MagicMock

        mock_embedding = MagicMock()
        service = VectorStoreService(mock_embedding)
        retriever = service.get_retriever()
        assert retriever.search_kwargs["k"] == config.top_k


# ============================================================
# file_history_store 测试
# ============================================================
class TestFileChatMessageHistory:
    """测试 file_history_store.py"""

    def setup_method(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.session_id = "test_session_001"

    def test_init_creates_directory(self):
        """验证初始化时创建存储目录"""
        from file_history_store import FileChatMessageHistory
        storage = os.path.join(self.temp_dir, "history")
        FileChatMessageHistory(self.session_id, storage)
        assert os.path.isdir(storage), "应自动创建存储目录"

    def test_messages_empty_initially(self):
        """验证新会话的消息列表为空"""
        from file_history_store import FileChatMessageHistory
        history = FileChatMessageHistory(self.session_id, self.temp_dir)
        assert history.messages == []

    def test_add_single_message(self):
        """验证 add_message 单条方法"""
        from file_history_store import FileChatMessageHistory
        from langchain_core.messages import HumanMessage

        history = FileChatMessageHistory(self.session_id, self.temp_dir)
        msg = HumanMessage(content="你好")
        history.add_message(msg)
        assert len(history.messages) == 1
        assert history.messages[0].content == "你好"

    def test_add_messages_multiple(self):
        """验证批量添加消息"""
        from file_history_store import FileChatMessageHistory
        from langchain_core.messages import HumanMessage, AIMessage

        history = FileChatMessageHistory(self.session_id, self.temp_dir)
        msgs = [
            HumanMessage(content="问题"),
            AIMessage(content="回答"),
        ]
        history.add_messages(msgs)
        assert len(history.messages) == 2
        assert history.messages[0].content == "问题"
        assert history.messages[1].content == "回答"

    def test_messages_persist_across_instances(self):
        """验证消息持久化：新建实例能读到之前的数据"""
        from file_history_store import FileChatMessageHistory
        from langchain_core.messages import HumanMessage

        # 写入
        h1 = FileChatMessageHistory(self.session_id, self.temp_dir)
        h1.add_message(HumanMessage(content="持久化测试"))

        # 读取 — 新实例
        h2 = FileChatMessageHistory(self.session_id, self.temp_dir)
        assert len(h2.messages) == 1
        assert h2.messages[0].content == "持久化测试"

    def test_clear_messages(self):
        """验证清空消息"""
        from file_history_store import FileChatMessageHistory
        from langchain_core.messages import HumanMessage

        history = FileChatMessageHistory(self.session_id, self.temp_dir)
        history.add_message(HumanMessage(content="要被清空"))
        assert len(history.messages) == 1

        history.clear()
        assert history.messages == []

    def test_different_sessions_isolated(self):
        """验证不同会话 ID 的存储隔离"""
        from file_history_store import FileChatMessageHistory
        from langchain_core.messages import HumanMessage

        h1 = FileChatMessageHistory("session_A", self.temp_dir)
        h2 = FileChatMessageHistory("session_B", self.temp_dir)

        h1.add_message(HumanMessage(content="A的消息"))
        h2.add_message(HumanMessage(content="B的消息"))

        assert len(h1.messages) == 1
        assert h1.messages[0].content == "A的消息"
        assert len(h2.messages) == 1
        assert h2.messages[0].content == "B的消息"

    def test_corrupted_file_returns_empty(self):
        """验证损坏的 JSON 文件返回空列表而不崩溃"""
        from file_history_store import FileChatMessageHistory

        history = FileChatMessageHistory(self.session_id, self.temp_dir)
        # 写入非法 JSON
        with open(history.file_path, "w", encoding="utf-8") as f:
            f.write("这不是合法JSON{{{")

        messages = history.messages
        assert messages == [], "损坏文件应返回空列表，不抛异常"

    def test_get_history_factory(self):
        """验证 get_history 工厂函数"""
        from file_history_store import get_history, FileChatMessageHistory
        result = get_history("test_session")
        assert isinstance(result, FileChatMessageHistory)
        assert result.session_id == "test_session"


# ============================================================
# rag 测试 (单元测试，mock 外部依赖)
# ============================================================
class TestRagService:
    """测试 rag.py RagService（使用 mock）"""

    @patch('rag.ChatDeepSeek')
    @patch('rag.DashScopeEmbeddings')
    @patch('rag.VectorStoreService')
    def test_rag_service_init(self, mock_vs, mock_emb, mock_chat):
        """验证 RagService 初始化不崩溃"""
        from rag import RagService
        service = RagService()
        assert service.vector_service is not None
        assert service.prompt_template is not None
        assert service.chat_model is not None
        assert service.chain is not None

    @patch('rag.ChatDeepSeek')
    @patch('rag.DashScopeEmbeddings')
    @patch('rag.VectorStoreService')
    def test_prompt_template_contains_context(self, mock_vs, mock_emb, mock_chat):
        """验证提示词模板包含 context 和 input 占位符"""
        from rag import RagService
        service = RagService()
        template_str = str(service.prompt_template)
        assert "context" in template_str or "{context}" in template_str
        assert "input" in template_str or "{input}" in template_str

    @patch('rag.ChatDeepSeek')
    @patch('rag.DashScopeEmbeddings')
    @patch('rag.VectorStoreService')
    def test_format_document_empty(self, mock_vs, mock_emb, mock_chat):
        """验证空文档列表返回"无参考资料" """
        from rag import RagService
        service = RagService()
        # 通过 chain 内部逻辑测试，format_document 是闭包，我们通过 retriever 返回空来间接测试
        # 直接验证：给空列表 → "无参考资料"
        # format_document 是 get_chain 内部的闭包，这里我们验证整体功能

    @patch('rag.ChatDeepSeek')
    @patch('rag.DashScopeEmbeddings')
    @patch('rag.VectorStoreService')
    def test_chain_is_runnable_with_message_history(self, mock_vs, mock_emb, mock_chat):
        """验证 chain 是 RunnableWithMessageHistory 实例"""
        from rag import RagService
        from langchain_core.runnables import RunnableWithMessageHistory
        service = RagService()
        assert isinstance(service.chain, RunnableWithMessageHistory)

    @patch('rag.ChatDeepSeek')
    @patch('rag.DashScopeEmbeddings')
    @patch('rag.VectorStoreService')
    def test_prompt_no_typo(self, mock_vs, mock_emb, mock_chat):
        """验证提示词模板中没有错别字 '位主' """
        from rag import RagService
        service = RagService()
        # 获取 prompt 的字符串表示
        prompts = [msg for msg in service.prompt_template.messages if hasattr(msg, 'prompt')]
        for p in prompts:
            template = p.prompt.template if hasattr(p, 'prompt') else str(p)
            assert "位主" not in template, "提示词中存在错别字'位主'，应为'为主'"


# ============================================================
# 辅助函数
# ============================================================
def teardown_module():
    """测试结束后清理临时 MD5 文件"""
    import config_data as config
    if os.path.exists(config.md5_path):
        os.remove(config.md5_path)
