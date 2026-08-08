
"""
RAG (Retrieval-Augmented Generation) 项目安装配置
安装命令: pip install -e .    (开发模式，代码修改即时生效)
         pip install .        (正式安装)
"""
from setuptools import setup, find_packages

setup(
    name="rag",
    version="0.1.0",
    description="RAG 检索增强生成项目 — 文档加载、向量存储、总结服务",
    author="Agent Team",
    packages=find_packages(),
    install_requires=[
        "langchain-core>=0.3.0",
        "langchain-chroma>=0.2.0",
        "langchain-text-splitters>=0.3.0",
        "langchain-community>=0.3.0",
        "langchain-deepseek>=0.1.0",
        "pyyaml>=6.0",
        "chromadb>=0.5.0",
    ],
    python_requires=">=3.10",
)
