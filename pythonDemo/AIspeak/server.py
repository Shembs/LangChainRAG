"""
Noir AI — 多模型聊天助手后端服务
为 Vue 前端提供统一的 API 接口，支持 SSE 流式响应
启动方式: uvicorn server:app --reload --port 8000
"""

import json
import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

# 与 models_config.py 同级，直接导入
from models_config import PROVIDERS, get_extra_params

# 数据库模块（可选依赖，未安装 pymysql 时自动降级）
try:
    from database.db_manager import DatabaseManager, get_db
    _db = get_db()
    DB_AVAILABLE = True
except Exception:
    _db = None
    DB_AVAILABLE = False

app = FastAPI(title="Noir AI API", version="2.0")

# 允许跨域（Vue 前端通常在不同端口开发）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 启动事件 ====================

@app.on_event("startup")
async def startup_event():
    """服务启动时打印可用路由和配置信息"""
    print("=" * 50)
    print("  Noir AI API v2.0 已启动")
    print(f"  数据库状态: {'已连接' if DB_AVAILABLE else '未连接（降级模式）'}")
    print(f"  已加载提供商: {', '.join(PROVIDERS.keys())}")
    print("-" * 50)
    print("  可用接口:")
    print("    http://localhost:8000/                  — 服务状态")
    print("    http://localhost:8000/api/health        — 健康检查")
    print("    http://localhost:8000/api/providers     — 提供商列表")
    print("    http://localhost:8000/api/chat/stream   — SSE 流式聊天")
    print("    http://localhost:8000/api/conversations — 对话列表")
    print("    http://localhost:8000/docs              — API 文档(Swagger)")
    print("=" * 50)


# ==================== 数据模型 ====================

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: str
    model: str
    temperature: float = 0.7
    system_prompt: str = "你是一个有帮助的AI助手"
    messages: list[Message] = []
    conversation_id: int | None = None  # 关联已有对话，None 则自动创建新对话


class ChatResponse(BaseModel):
    content: str
    model: str
    conversation_id: int | None = None  # 返回对话ID供前端持久化


class ProviderStatus(BaseModel):
    id: str
    name: str
    api_key_env: str
    api_key_set: bool
    models: list[str]


# ==================== API 路由 ====================

@app.get("/")
async def root():
    """根路由 — 验证服务器是否正常运行"""
    return {
        "service": "Noir AI API",
        "version": "2.0",
        "db_available": DB_AVAILABLE,
        "endpoints": [
            "GET  /                  — 服务状态",
            "GET  /api/health        — 健康检查",
            "GET  /api/providers     — 提供商列表",
            "POST /api/chat          — 非流式聊天",
            "POST /api/chat/stream   — SSE 流式聊天",
            "GET  /api/conversations — 对话列表",
            "GET  /api/stats         — 统计信息",
        ],
    }


@app.get("/api/providers")
async def get_providers():
    """获取所有提供商及其状态（用于前端动态渲染）"""
    result = []
    for provider_id, config in PROVIDERS.items():
        api_key = os.environ.get(config["api_key_env"])
        result.append(ProviderStatus(
            id=provider_id,
            name=config["name"],
            api_key_env=config["api_key_env"],
            api_key_set=bool(api_key),
            models=config["models"],
        ))
    return result


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """非流式聊天接口"""
    config = PROVIDERS.get(request.provider)
    if not config:
        raise HTTPException(status_code=400, detail=f"未知的提供商: {request.provider}")

    api_key = os.environ.get(config["api_key_env"])
    if not api_key:
        raise HTTPException(status_code=401, detail=f"请先设置环境变量 {config['api_key_env']}")

    client = OpenAI(api_key=api_key, base_url=config["base_url"])

    messages = [{"role": "system", "content": request.system_prompt}]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    api_kwargs = {
        "model": request.model,
        "temperature": request.temperature,
        "messages": messages,
        "stream": False,
    }
    api_kwargs.update(get_extra_params(request.provider))

    response = client.chat.completions.create(**api_kwargs)
    content = response.choices[0].message.content

    # ---- 保存到数据库 ----
    conv_id = _save_chat_to_db(
        request, content, request.messages[-1].content if request.messages else ""
    )

    return ChatResponse(content=content, model=request.model, conversation_id=conv_id)


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """SSE 流式聊天接口"""
    config = PROVIDERS.get(request.provider)
    if not config:
        raise HTTPException(status_code=400, detail=f"未知的提供商: {request.provider}")

    api_key = os.environ.get(config["api_key_env"])
    if not api_key:
        raise HTTPException(status_code=401, detail=f"请先设置环境变量 {config['api_key_env']}")

    client = OpenAI(api_key=api_key, base_url=config["base_url"])

    messages = [{"role": "system", "content": request.system_prompt}]
    for msg in request.messages:
        messages.append({"role": msg.role, "content": msg.content})

    api_kwargs = {
        "model": request.model,
        "temperature": request.temperature,
        "messages": messages,
        "stream": True,
    }
    api_kwargs.update(get_extra_params(request.provider))

    async def generate():
        full_content = ""
        try:
            stream = client.chat.completions.create(**api_kwargs)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    delta = chunk.choices[0].delta.content
                    full_content += delta
                    yield f"data: {json.dumps({'delta': delta, 'done': False}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0)

            # ---- 保存到数据库 ----
            conv_id = _save_chat_to_db(
                request, full_content,
                request.messages[-1].content if request.messages else ""
            )
            yield f"data: {json.dumps({'delta': '', 'done': True, 'conversation_id': conv_id}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'delta': '', 'done': True, 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": "2.0",
        "db_available": DB_AVAILABLE,
    }


# ==================== 数据库辅助函数 ====================

def _save_chat_to_db(request: ChatRequest, assistant_content: str, user_content: str) -> int | None:
    """将用户消息和 AI 回复保存到数据库，返回对话ID"""
    if not DB_AVAILABLE or _db is None:
        return None

    try:
        conv_id = request.conversation_id

        if conv_id is None:
            # 新对话：创建并保存用户消息
            conv_id = _db.create_conversation(request.provider, request.model)
            if user_content:
                _db.add_message(conv_id, "user", user_content)
                _db.rename_conversation_by_first_message(conv_id)

        # 始终保存 AI 回复
        if assistant_content:
            _db.add_message(conv_id, "assistant", assistant_content, model=request.model)

        return conv_id
    except Exception as e:
        print(f"[DB] 保存消息失败: {e}")
        return conv_id


# ==================== 对话管理 API ====================

@app.get("/api/conversations")
async def list_conversations(limit: int = 20, offset: int = 0):
    """获取对话列表"""
    if not DB_AVAILABLE:
        return {"conversations": [], "db_available": False}

    conversations = _db.get_conversations(limit=limit, offset=offset)
    # 转换 datetime 为字符串
    for conv in conversations:
        for key in ("created_at", "updated_at"):
            if key in conv and conv[key]:
                conv[key] = conv[key].strftime("%Y-%m-%d %H:%M:%S")
    return {"conversations": conversations, "db_available": True}


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: int):
    """获取单个对话的详细信息及所有消息"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="数据库不可用")

    conv = _db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    for key in ("created_at", "updated_at"):
        if key in conv and conv[key]:
            conv[key] = conv[key].strftime("%Y-%m-%d %H:%M:%S")

    messages = _db.get_messages(conversation_id)
    for msg in messages:
        if msg.get("created_at"):
            msg["created_at"] = msg["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return {
        "conversation": conv,
        "messages": messages,
        "db_available": True,
    }


@app.get("/api/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: int):
    """获取某个对话的所有消息"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="数据库不可用")

    messages = _db.get_messages(conversation_id)
    for msg in messages:
        if msg.get("created_at"):
            msg["created_at"] = msg["created_at"].strftime("%Y-%m-%d %H:%M:%S")
    return {"messages": messages}


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: int):
    """删除对话及其所有消息"""
    if not DB_AVAILABLE:
        raise HTTPException(status_code=503, detail="数据库不可用")

    _db.delete_conversation(conversation_id)
    return {"status": "deleted", "conversation_id": conversation_id}


@app.get("/api/stats")
async def get_stats():
    """获取使用统计"""
    if not DB_AVAILABLE:
        return {"stats": {}, "db_available": False}

    return {"stats": _db.get_conversation_stats(), "db_available": True}


# ==================== 静态文件（Vue 前端） ====================
# 必须放在所有 API 路由之后，否则会拦截 API 请求
import os as _os
_vue_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "vue-chat")
if _os.path.isdir(_vue_dir):
    app.mount("/", StaticFiles(directory=_vue_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)