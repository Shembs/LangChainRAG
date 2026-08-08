#!/bin/bash
# ========================================================
# LangChainRAG — Docker 入口脚本
# 根据 APP_MODE 环境变量启动不同服务
# ========================================================

set -e

echo "============================================"
echo " LangChainRAG — Docker Container"
echo " APP_MODE: ${APP_MODE:-rag-qa}"
echo "============================================"

case "${APP_MODE}" in
    rag-qa)
        echo ">>> 启动 RAG 知识库问答服务 (端口 8501)"
        exec streamlit run RAG_and_Agent_project/project_RAG/app_qa.py \
            --server.port=${STREAMLIT_SERVER_PORT:-8501} \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --browser.gatherUsageStats=false
        ;;
    rag-uploader)
        echo ">>> 启动 RAG 文件上传服务 (端口 8501)"
        exec streamlit run RAG_and_Agent_project/project_RAG/app_file_uploader.py \
            --server.port=${STREAMLIT_SERVER_PORT:-8501} \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --browser.gatherUsageStats=false
        ;;
    rag-agent)
        echo ">>> 启动 ReAct Agent 智能客服 (端口 8502)"
        exec streamlit run RAG_and_Agent_project/project_Agent/app.py \
            --server.port=${STREAMLIT_SERVER_PORT:-8502} \
            --server.address=0.0.0.0 \
            --server.headless=true \
            --browser.gatherUsageStats=false
        ;;
    aispeak)
        echo ">>> 启动 Noir AI 多模型聊天 API (端口 8000)"
        cd pythonDemo/AIspeak
        exec uvicorn server:app --host 0.0.0.0 --port ${API_PORT:-8000}
        ;;
    *)
        echo "ERROR: 未知的 APP_MODE: ${APP_MODE}"
        echo "可选值: rag-qa | rag-uploader | rag-agent | aispeak"
        exit 1
        ;;
esac
