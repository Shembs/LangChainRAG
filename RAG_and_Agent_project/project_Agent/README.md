# 扫地机器人智能客服（ReAct Agent + RAG）

基于 LangChain ReAct Agent 的对话式客服，集成 RAG 向量知识库。项目包含两个界面：

| 界面 | 技术栈 | 端口 | 说明 |
|------|--------|------|------|
| 用户端 | Streamlit | 8502（本地默认 8501） | 聊天 + 快捷提问 + 多会话管理 |
| 后台管理 | Vue 3 + FastAPI | 8001（前端 dev 5173） | 知识库上传 + AI 模型调整，需管理员登录 |

## 目录结构

```
project_Agent/
├── app.py                 # 用户端 Streamlit 入口
├── admin_server.py        # 后台管理后端入口（FastAPI）
├── admin_api/             # 后台管理后端包（鉴权 / 知识库 / 模型配置）
├── admin_frontend/        # 后台管理前端（Vue 3 + Vite + Element Plus）
│   └── dist/              # 前端构建产物（已纳入版本控制，可直接托管）
├── agent/                 # ReAct Agent 及工具 / 中间件
├── RAG/                   # 向量库与检索总结服务
├── model/                 # 模型工厂（对话模型 / 嵌入模型）
├── utils/                 # 配置、文件、日志等工具
├── config/                # 配置文件（rag.yml / chroma.yml / prompts.yml / agent.yml）
├── prompts/               # 系统 / RAG / 报告提示词
└── data/                  # 知识库文档（挂载卷）
```

## 运行方式

### 1. 用户端（Streamlit）

```bash
cd RAG_and_Agent_project/project_Agent
streamlit run app.py
```

浏览器打开 http://localhost:8501 ，侧边栏支持多会话（新增 / 删除 / 切换）与快捷提问。

### 2. 后台管理后端（FastAPI）

```bash
cd RAG_and_Agent_project/project_Agent
pip install -r ../../requirements.txt   # 首次运行安装依赖（含 python-multipart）
python admin_server.py
```

默认监听 http://localhost:8001 。

### 3. 后台管理前端（Vue）

**方式 A — 生产形态（推荐，无需 Node）：** 直接访问 http://localhost:8001 ，FastAPI 已托管 `admin_frontend/dist` 构建产物。

**方式 B — 开发形态（需 Node）：**

```bash
cd RAG_and_Agent_project/project_Agent/admin_frontend
npm install
npm run dev          # http://localhost:5173，已代理 /api 到 8001
```

修改前端源码后重新构建：

```bash
npm run build        # 产物输出到 admin_frontend/dist
```

### 4. 后台登录

访问后台后，使用管理员账号登录：

- **账号：`admin`**
- **密码：`123456`**

（可通过环境变量 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 覆盖。）

## 后台功能

### 知识库管理

- 上传 `.txt` / `.pdf` / `.docx` 文档到 `data/` 目录，自动触发向量库增量索引（md5 去重）。
- 查看已上传文件列表、删除文件、手动重建索引。

### AI 模型调整

可配置项（保存后写入 `config/*.yml`）：

| 配置项 | 文件 | 生效方式 |
|--------|------|----------|
| 对话模型名称 `chat_model_name` | `config/rag.yml` | 重启服务后生效 |
| 嵌入模型名称 `embedding_model_name` | `config/rag.yml` | 重启服务后生效 |
| 温度 `temperature` | `config/rag.yml` | 重启服务后生效 |
| 检索条数 `k` | `config/chroma.yml` | 保存后即时生效 |
| 分片大小 `chunk_size` | `config/chroma.yml` | 重建索引后生效 |
| 分片重叠 `chunk_overlap` | `config/chroma.yml` | 重建索引后生效 |

## Docker 部署

后台管理服务使用独立的 `Dockerfile.admin`（多阶段构建 Vue + Python），与已有服务互不影响：

```bash
docker compose up -d admin      # 后台管理服务，端口 8001
```

其余服务（rag-qa / rag-agent / aispeak）沿用原有 `Dockerfile` 与 `docker compose` 编排。

## 环境变量

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | 对话模型 API Key |
| `DASHSCOPE_API_KEY` | 嵌入模型 API Key |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | 管理员账号（默认 admin / 123456） |
| `ADMIN_SECRET_KEY` | token 签名密钥（生产环境建议覆盖） |
| `API_PORT` | 后台管理服务端口（默认 8001） |
