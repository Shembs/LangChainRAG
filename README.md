# LangChain RAG & Agent 智能客服

一个基于 **LangChain + 大语言模型（LLM）** 的智能客服 / 检索增强生成（RAG）实践项目，涵盖从基础 RAG 问答、ReAct 智能体（Agent），到多模型聊天助手与后台管理系统的完整技术栈。

---

## 一、项目背景

本项目以「智能客服」为应用场景，探索并落地大模型在企业知识库问答、个性化服务中的工程化方案：

- **RAG 知识库问答**：将本地文档（如服装选购指南、产品说明）切分、向量化并持久化到向量数据库，用户提问时先检索相关片段，再交由大模型结合上下文作答，显著降低「幻觉」、提升答案的准确性。
- **ReAct 智能体**：在 RAG 之上引入「思考 → 行动 → 观察」的推理循环，让模型能自主调用工具（天气查询、用户数据查询、外部数据获取、报告生成等），完成多步骤、可解释的复杂任务。
- **多模型聊天助手**：封装 OpenAI、DeepSeek、通义千问、Moonshot、智谱、零一万物等多家大模型提供商，提供统一 API 与流式（SSE）响应。
- **后台管理系统**：提供知识库上传 / 管理、AI 模型参数在线调整等运营能力，使非技术人员也能维护知识库与模型配置。

项目结构按「学习演进」组织，从早期基础示例逐步沉淀为可容器化部署的完整系统。

---

## 二、技术栈

| 层次 | 技术 |
|------|------|
| 开发语言 | Python 3.10+、JavaScript（Vue 3） |
| AI 框架 | LangChain、LangGraph（`create_agent`、中间件、链式调用） |
| 大语言模型 | DeepSeek（`deepseek-v4-pro`）等，支持多提供商 OpenAI / 通义千问 / Moonshot / 智谱 / 零一万物 |
| 嵌入模型 | 阿里云 DashScope（`text-embedding-v4`） |
| 向量数据库 | ChromaDB（本地持久化，MD5 去重增量索引） |
| 后端框架 | FastAPI、Uvicorn（SSE 流式响应、REST API） |
| 用户端前端 | Streamlit（聊天界面） |
| 管理端前端 | Vue 3 + Vite + Element Plus + Pinia + Vue Router |
| 关系型数据库 | MySQL 8.0（多模型聊天助手的对话记录） |
| 部署 | Docker / Docker Compose |

---

## 三、项目结构

```
E:\project
├── RAG_and_Agent_project/          # 核心项目目录
│   ├── project_RAG/                # ① RAG 知识库问答（服装领域）
│   │   ├── app_qa.py               #    问答界面（Streamlit）
│   │   ├── app_file_uploader.py    #    知识库上传界面
│   │   ├── rag.py                  #    RAG 检索 + 生成服务
│   │   ├── vector_store.py         #    向量库（ChromaDB）封装
│   │   ├── knowledge_base.py       #    文档加载与索引
│   │   ├── config_data.py          #    配置（模型、分块、检索参数）
│   │   └── data/                   #    知识库文档（尺码/洗涤/颜色）
│   │
│   └── project_Agent/              # ② ReAct Agent 智能客服（扫地机器人领域）
│       ├── app.py                  #    用户端聊天界面（Streamlit）
│       ├── admin_server.py         #    后台管理后端入口（FastAPI）
│       ├── admin_api/              #    后台管理后端（鉴权/知识库/模型配置）
│       ├── admin_frontend/         #    后台管理前端（Vue 3 + Vite）
│       │   ├── src/                #    前端源码
│       │   └── dist/               #    构建产物（可直接托管）
│       ├── agent/                  #    ReAct Agent 核心
│       │   ├── react_agent.py      #    智能体封装（流式输出）
│       │   └── tools/              #    业务工具集与中间件
│       ├── RAG/                    #    向量库与检索总结服务
│       ├── model/                  #    模型工厂（对话/嵌入模型）
│       ├── config/                 #    YAML 配置（rag/chroma/prompts/agent）
│       ├── prompts/                #    系统/RAG/报告提示词
│       ├── utils/                  #    配置、文件、日志、路径等工具
│       └── data/                   #    知识库文档与外部数据（CSV）
│
├── pythonDemo/                     # 学习示例目录
│   ├── AIspeak/                    # ③ Noir AI 多模型聊天助手
│   │   ├── server.py               #    FastAPI 后端（SSE 流式聊天）
│   │   ├── AIproject.py            #    Streamlit 前端
│   │   ├── models_config.py        #    多模型提供商配置
│   │   ├── database/               #    MySQL 数据库模块（对话记录）
│   │   └── vue-chat/               #    Vue 聊天前端
│   │
│   └── lrean/                      # ④ 早期学习示例（Streamlit / API 调用）
│
├── Agent(RAG)/                     # 早期 RAG / Agent 学习项目（含独立虚拟环境）
│
├── Dockerfile                      # 主应用镜像（rag-qa / rag-agent / aispeak）
├── Dockerfile.admin                # 后台管理镜像（Vue 多阶段构建）
├── docker-compose.yml              # 服务编排（rag-qa / rag-agent / admin / aispeak / mysql）
├── requirements.txt                # Python 依赖清单
└── .env.example                    # 环境变量配置模板（API Key 等）
```

---

## 四、核心模块说明

### ① `project_RAG` — RAG 知识库问答

面向服装领域（尺码推荐、洗涤养护、颜色选择）的检索增强问答系统：

- 本地文档 → 文本分块 → 向量化 → ChromaDB 持久化；
- 提问时先检索 Top-K 相关片段，再交由大模型结合上下文作答；
- 支持会话历史记忆，提供 Streamlit 问答与知识库上传两个界面。

### ② `project_Agent` — ReAct Agent 智能客服

面向扫地机器人用户的对话式智能客服，在 RAG 基础上引入 Agent 能力：

- **ReAct 推理链**：模型严格遵循「思考 → 行动 → 观察」循环，可解释性强；
- **业务工具集**：RAG 总结、天气查询、用户 ID / 城市 / 月份获取、外部数据获取、报告上下文注入等；
- **中间件**：工具调用监控、模型调用日志、动态 Prompt 切换（报告场景）；
- **知识库回退**：检索无匹配时自动回退至大模型自身知识，保证回答不中断；
- **流式输出**：实时展示 Agent 回复，提升交互体验；
- **后台管理**：知识库上传 / 删除 / 重建索引，AI 模型参数在线调整（需管理员登录）。

### ③ `pythonDemo/AIspeak` — 多模型聊天助手（Noir AI）

一个多模型聚合的聊天助手后端：

- 统一封装多家大模型提供商（OpenAI、DeepSeek、通义千问、Moonshot、智谱、零一万物）；
- FastAPI + SSE 流式响应，支持对话历史存储（MySQL）；
- 提供 Streamlit 与 Vue 两种前端。

### ④ `pythonDemo/lrean` 与 `Agent(RAG)` — 学习示例

早期学习大模型 API 调用、Streamlit 与 LangChain 的练习项目，保留作技术演进参考。

---

## 五、快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板并填入真实 API Key
cp .env.example .env
```

需配置的 API Key：`DEEPSEEK_API_KEY`（对话模型）、`DASHSCOPE_API_KEY`（嵌入模型）。

### 2. 启动服务

| 服务 | 说明 | 端口 | 启动命令 |
|------|------|------|----------|
| RAG 知识库问答 | 服装领域问答 | 8501 | `streamlit run app_qa.py`（`project_RAG/` 目录） |
| Agent 智能客服 | 扫地机器人用户端 | 8502 | `streamlit run app.py`（`project_Agent/` 目录） |
| 后台管理 | 知识库 / 模型管理 | 8001 | `python admin_server.py`（`project_Agent/` 目录） |
| 多模型聊天 | Noir AI 后端 | 8000 | `uvicorn server:app --port 8000`（`AIspeak/` 目录） |

### 3. Docker 一键部署

```bash
docker compose up -d
```

该命令会启动全部服务（rag-qa、rag-agent、admin、aispeak、mysql），并自动创建数据卷与网络。
