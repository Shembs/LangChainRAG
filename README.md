# RAG 企业级知识库问答系统

基于 **LangChain** + **FastAPI** + **React** 的企业级 RAG（检索增强生成）知识库问答系统，面向电商平台商品信息场景。

## 功能特性

- 🔐 **用户认证**：注册、登录、修改密码，JWT 无状态认证
- 👑 **权限分级**：管理员（知识库管理）vs 普通用户（仅问答）
- 📚 **知识库管理**：文档上传（PDF/TXT/CSV/MD/DOCX）、自动分块、向量化存储
- 🤖 **智能问答**：基于 RAG 的知识库问答，支持引用来源标注
- 💬 **多会话管理**：多用户独立会话、对话历史持久化
- ⚡ **流式响应**：SSE 逐字输出，首字延迟 < 2s
- 🔍 **混合检索**：PGVector 向量检索 + PostgreSQL 全文检索 + RRF 融合
- 📊 **引用来源**：回答中标注知识库引用片段，可展开查看原文
- 🎨 **暗色模式**：Ant Design 5 主题切换
- 📝 **操作审计**：管理员操作日志

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python + FastAPI |
| RAG 框架 | LangChain + LangGraph |
| 前端 | React 18 + TypeScript + Ant Design 5 + Vite |
| 数据库 | PostgreSQL 16 + PGVector（向量存储） |
| 缓存 | Redis 7（三层缓存） |
| LLM | DeepSeek V4 Pro (`deepseek-V4Pro`) |
| Embedding | DeepSeek Embedding API（1536 维） |
| 异步任务 | Celery + Redis |
| 部署 | Docker Compose + Nginx |

## 快速启动

### 1. 环境准备

```bash
# 安装 Docker 和 Docker Compose
# 复制环境变量文件
cp backend/.env.example backend/.env

# 编辑 .env，填入你的 DeepSeek API Key
# LLM_API_KEY=sk-your-deepseek-key
# EMBEDDING_API_KEY=sk-your-deepseek-key
```

### 2. Docker Compose 一键启动

```bash
docker compose up -d
```

服务启动后：
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 前端页面：http://localhost:80

### 3. 本地开发

**后端：**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

**Celery Worker（文档处理）：**
```bash
cd backend
celery -A app.tasks.ingestion_tasks worker --loglevel=info -P solo
```

### 4. 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |

## 项目结构

```
LangChainRAG/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   ├── core/              # 核心模块（DB, Redis, Security）
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── rag/               # RAG 核心引擎
│   │   │   ├── ingestion/     # 文档加载/分块/Embedding
│   │   │   ├── retrieval/     # 查询重写/混合检索/重排序
│   │   │   └── generation/    # LLM 生成/后处理
│   │   └── middleware/        # 中间件（限流/异常处理）
│   └── tasks/                 # Celery 异步任务
├── frontend/                   # React 前端
│   └── src/
│       ├── pages/             # 页面组件
│       ├── components/        # 通用组件
│       ├── stores/            # Zustand 状态管理
│       ├── api/               # API 客户端
│       └── hooks/             # 自定义 Hooks
├── nginx/                     # Nginx 配置
└── docker-compose.yml         # Docker 编排
```

## RAG 流水线

```
用户问题
  → 缓存检查 (Redis L1/L2)
  → 查询重写 (DeepSeek)
  → 混合检索 (PGVector 向量 + tsvector BM25 + RRF 融合)
  → LLM 重排序 (DeepSeek 打分)
  → 上下文去重 + 构建
  → DeepSeek 流式生成 (SSE)
  → 引用来源提取
  → 带引用的回答
```

## API 概览

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `/api/v1/auth/*` | 注册/登录/修改密码 |
| 问答 | `/api/v1/chat/*` | 提问(SSE)/会话管理 |
| 知识库 | `/api/v1/admin/knowledge/*` | 文档管理(管理员) |
| 系统 | `/api/v1/system/*` | 健康检查/审计日志 |
