"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.core.db import engine, Base
from app.core.redis_client import init_redis, close_redis
from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.admin_knowledge import router as admin_knowledge_router
from app.api.v1.system import router as system_router
from app.models import *  # noqa: ensure all models are imported for create_all
import app.tasks.ingestion_tasks  # noqa: ensure Celery tasks are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)
    await init_redis()
    from app.data.seed import seed_admin
    await seed_admin()
    yield
    # Shutdown
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="RAG 知识库问答系统",
    description="基于 LangChain 的企业级 RAG 知识库问答系统，面向电商商品信息场景",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["问答"])
app.include_router(admin_knowledge_router, prefix="/api/v1/admin/knowledge", tags=["知识库管理"])
app.include_router(system_router, prefix="/api/v1/system", tags=["系统"])


@app.get("/")
async def root():
    return {"message": "RAG 知识库问答系统 API", "version": "1.0.0"}
