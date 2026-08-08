# ========================================================
# LangChainRAG — 多服务 Docker 镜像
#
# 构建: docker build -t langchain-rag .
# 运行: docker compose up -d
#
# 服务:
#   - rag-qa:     RAG 知识库问答 (Streamlit, 端口 8501)
#   - rag-agent:  ReAct Agent 智能客服 (Streamlit, 端口 8502)
#   - aispeak:    Noir AI 多模型聊天 (FastAPI, 端口 8000)
# ========================================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目源码
COPY . .

# 创建数据目录（运行时挂载卷）
RUN mkdir -p /app/data /app/chroma_db /app/chat_history

# 暴露端口
# 8000: FastAPI (AIspeak)
# 8501: Streamlit (RAG Q&A)
# 8502: Streamlit (Agent)
EXPOSE 8000 8501 8502

# 健康检查（根据 APP_MODE 检查对应端口）
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${STREAMLIT_SERVER_PORT:-8501}/_stcore/health')" || exit 1

# 默认启动 RAG Q&A 服务，可通过 APP_MODE 切换
# APP_MODE 可选值: rag-qa | rag-agent | rag-uploader
ENV APP_MODE=rag-qa

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
