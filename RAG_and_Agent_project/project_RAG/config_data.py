md5_path = './md5.txt'

# 知识库配置
# 集合名称
collection_name = 'rag'
persist_directory = './chroma_db'

# 文本分块配置
chunk_size = 1000
chunk_overlap = 100
separator = ['\n', '\r\n', '\r', '.', '!', '?', '。', '！', '？', '，', ' ']
min_split_length = 1000  # 文本超过此长度时才进行分块

# 检索配置
top_k = 2  # 检索返回的文档数量


# 嵌入模型,聊天模型
embedding_model_name = "text-embedding-v4"
chat_model_name = 'deepseek-v4-pro'

session_config = {
    "configurable": {
        "session_id": "user001"
    }
}