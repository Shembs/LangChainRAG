"""
知识库模块
"""
import os
import config_data as config
import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datetime import datetime

def check_md5(md5_str: str):
    """检查文件是否已存在（通过 MD5 去重）"""
    if not os.path.exists(config.md5_path):
        with open(config.md5_path, 'w', encoding='utf-8') as f:
            pass  # 创建空文件
        return False

    with open(config.md5_path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            if line == md5_str:
                return True
    return False

def save_md5(md5_str: str):
    """保存文件md5"""
    with open(config.md5_path, 'a', encoding='utf-8') as f:
        f.write(md5_str + '\n')

def get_string_md5(input_str: str,encoding='utf-8'):
    """获取文件md5"""
    # 将字符串转换为字节流
    str_bytes = input_str.encode(encoding=encoding)

    md5_obj = hashlib.md5()
    md5_obj.update(str_bytes)
    md5_hex = md5_obj.hexdigest()

    return md5_hex


class KnowledgeBaseService:
    """知识库服务类"""

    def __init__(self):
        """初始化知识库服务类"""
        # 确保持久化目录存在
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embedding_model_name),
            persist_directory=config.persist_directory,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separator,
            length_function=len,
        )

    def upload_by_str(self, data, file_name):
        """将传入的字符串进行向量化，存储到知识库中"""
        # 获取字符串 MD5 值，用于去重
        md5_hex = get_string_md5(data)

        if check_md5(md5_hex):
            return "[跳过] 文件已存在"

        # 文本超过最小分块长度时才进行分割
        if len(data) > config.min_split_length:
            knowledge_list: list[str] = self.splitter.split_text(data)
        else:
            knowledge_list: list[str] = [data]

        metadata = {
            "source": file_name,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "admin",
        }

        self.chroma.add_texts(
            knowledge_list,
            metadatas=[metadata for _ in knowledge_list],
        )

        save_md5(md5_hex)

        return "[成功] 文件上传成功"



if __name__ == '__main__':
    kb_service = KnowledgeBaseService()
    r = kb_service.upload_by_str("周杰伦","周杰伦.txt")
    print(r)
