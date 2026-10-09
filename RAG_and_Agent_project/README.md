# RAG 与 Agent 实战项目

基于 [LangChain](https://www.langchain.com/) 生态构建的检索增强生成（RAG）与智能体（Agent）示例项目，包含两个相互独立的子项目，覆盖从基础 RAG 到多工具 ReAct Agent 的完整实践链路。

| 子项目 | 类型 | 应用场景 | 前端 | 核心能力 |
|--------|------|----------|------|----------|
| [project_RAG](./project_RAG) | 基础 RAG 知识库问答 | 服装选购咨询 | Streamlit | 文档向量化 + 检索增强生成 + 多轮对话 |
| [project_Agent](./project_Agent) | ReAct Agent 智能客服 | 扫地机器人智能客服 | Streamlit（用户端）+ Vue 3（后台管理） | 多工具 Agent + RAG + 知识库 / 模型管理后台 |

## 技术栈

- **语言 / 框架**：Python 3.10+、Streamlit、FastAPI、Vue 3 + Vite + Element Plus
- **大模型**：DeepSeek（对话模型）、阿里云百炼 DashScope（嵌入模型）
- **Agent / RAG**：LangChain、LangGraph、ChromaDB
- **其他**：PyYAML、Uvicorn、Pydantic、Axios、Vue Router、Pinia

## 目录结构

```
RAG_and_Agent_project/
├── project_RAG/                # 基础 RAG 知识库问答
│   ├── app_qa.py               # Streamlit 问答界面
│   ├── app_file_uploader.py    # 知识库文档上传界面
│   ├── rag.py                  # RAG 服务（检索 → 增强 → 生成）
│   ├── knowledge_base.py       # 知识库构建（分块 + 向量化 + MD5 去重）
│   ├── vector_store.py         # 向量存储与检索
│   ├── file_history_store.py   # 会话历史管理
│   ├── config_data.py          # 项目配置
│   └── data/                   # 知识库文档
└── project_Agent/              # ReAct Agent 智能客服（扫地机器人）
    ├── app.py                  # 用户端（Streamlit）
    ├── admin_server.py         # 后台管理后端入口（FastAPI）
    ├── admin_api/              # 后台后端：鉴权 / 知识库 / 模型配置
    ├── admin_frontend/         # 后台前端（Vue 3 + Vite + Element Plus）
    ├── agent/                  # ReAct Agent、业务工具与中间件
    ├── RAG/                    # 向量库与检索总结服务
    ├── model/                  # 模型工厂（对话模型 / 嵌入模型）
    ├── utils/                  # 配置、文件、日志、提示词等工具
    ├── config/                 # 配置文件（rag / chroma / prompts / agent）
    ├── prompts/                # 系统 / RAG / 报告提示词
    ├── setup.py                # 包安装配置
    └── data/                   # 知识库文档与外部数据
```

---

## 子项目一：project_RAG —— 基础 RAG 知识库问答

基于 LangChain + ChromaDB 的检索增强生成问答系统，演示 RAG 的核心链路：文档加载 → 文本分块 → 向量化入库 → 检索 → 上下文增强 → 大模型生成。

### 核心流程

```
用户提问 → ChromaDB 向量检索 → 拼接上下文 → DeepSeek 生成回答（流式输出）
```

### 主要模块

| 模块 | 说明 |
|------|------|
| `rag.py` | `RagService`：组装检索链与对话链，支持多轮对话记忆 |
| `knowledge_base.py` | `KnowledgeBaseService`：文本分块、向量化入库、MD5 去重 |
| `vector_store.py` | `VectorStoreService`：ChromaDB 向量存储与检索 |
| `app_qa.py` | Streamlit 问答界面（流式回复、建议提问、清空对话） |
| `app_file_uploader.py` | Streamlit 知识库文档上传界面 |
| `file_history_store.py` | 会话历史存取 |
| `config_data.py` | 分块、检索、模型等配置 |

### 运行

```bash
cd project_RAG
streamlit run app_qa.py
```

浏览器访问 http://localhost:8501 。

---

## 子项目二：project_Agent —— ReAct Agent 智能客服

基于 LangChain `create_agent` 构建的 ReAct 智能体，集成 RAG 向量知识库、多个业务工具与中间件，面向扫地机器人领域提供对话式智能客服；同时提供 Vue 3 + FastAPI 的后台管理系统，用于知识库维护与模型参数调整。

### 界面

| 界面 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 用户端 | Streamlit | 8501（默认） | 聊天 + 快捷提问 + 多会话管理 |
| 后台管理 | Vue 3 + FastAPI | 8001（前端 dev 5173） | 知识库上传 + AI 模型调整，需管理员登录 |

### 核心特性

- **ReAct Agent**：模型自主规划并调用工具完成多轮任务
- **RAG 检索总结**：基于相似度阈值过滤检索结果，知识库无匹配时自动回退到大模型自身知识
- **业务工具**：RAG 总结、天气查询、用户城市 / ID 获取、当前月份、外部数据查询、报告内容填充
- **中间件**：工具调用监控、模型调用日志、动态提示词切换（报告模式）
- **多会话管理**：会话新增 / 删除 / 切换，本地持久化
- **后台管理**：知识库上传（增量索引、MD5 去重）、文件删除、手动重建索引、AI 模型参数调整
- **管理员鉴权**：基于 HMAC 签名的登录 token（有效期 8 小时）

### 运行

#### 1. 用户端（Streamlit）

```bash
cd project_Agent
streamlit run app.py
```

#### 2. 后台管理后端（FastAPI）

```bash
cd project_Agent
python admin_server.py
```

默认监听 http://127.0.0.1:8001 ，并托管已构建的前端产物。

#### 3. 后台管理前端（Vue）

**生产形态（推荐）**：直接访问 http://localhost:8001 ，FastAPI 已托管 `admin_frontend/dist` 构建产物。

**开发形态（需 Node.js）**：

```bash
cd project_Agent/admin_frontend
npm install
npm run dev     # http://localhost:5173，已代理 /api 到 8001
```

修改前端源码后重新构建：

```bash
npm run build   # 产物输出到 admin_frontend/dist
```

#### 4. 后台登录

默认管理员账号：`admin` / `123456`（可通过环境变量 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 覆盖）。

### 后台功能

#### 知识库管理

- 上传 `.pdf` / `.docx` / `.txt` 文档到 `data/` 目录，自动触发向量库增量索引（MD5 去重）
- 查看已上传文件列表、删除文件、手动重建索引

#### AI 模型调整

可配置项保存后写入 `config/*.yml`：

| 配置项 | 文件 | 生效方式 |
|--------|------|----------|
| 对话模型 `chat_model_name` | `config/rag.yml` | 重启服务后生效 |
| 嵌入模型 `embedding_model_name` | `config/rag.yml` | 重启服务后生效 |
| 温度 `temperature` | `config/rag.yml` | 重启服务后生效 |
| 检索条数 `k` | `config/chroma.yml` | 保存后即时生效 |
| 分片大小 `chunk_size` | `config/chroma.yml` | 重建索引后生效 |
| 分片重叠 `chunk_overlap` | `config/chroma.yml` | 重建索引后生效 |

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | 对话模型 API Key |
| `DASHSCOPE_API_KEY` | 嵌入模型 API Key |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 后台管理员账号（默认 admin / 123456） |
| `ADMIN_SECRET_KEY` | 登录 token 签名密钥（生产环境建议覆盖） |
| `API_PORT` | 后台管理服务端口（默认 8001） |

## 依赖

- Python 3.10+
- 核心 Python 包（`project_Agent` 已提供 `setup.py`，可在其目录下 `pip install -e .` 安装）：`langchain`、`langchain-core`、`langchain-chroma`、`langchain-community`、`langchain-deepseek`、`chromadb`、`pyyaml` 等
- 界面与后端：`streamlit`、`fastapi`、`uvicorn`、`pydantic`、`python-multipart`
- 后台前端：Node.js（仅开发形态需要）
