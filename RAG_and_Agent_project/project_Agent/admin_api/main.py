"""
后台管理 FastAPI 应用

- 提供 /api/admin/* 管理接口（登录、知识库、模型配置）
- 若存在 admin_frontend/dist/，则作为单页应用静态资源托管
"""

import os

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from admin_api.auth import LoginRequest, LoginResponse, create_token, verify_credentials
from admin_api.routes import kb as kb_routes
from admin_api.routes import model as model_routes

app = FastAPI(title="扫地机器人智能客服 — 后台管理 API", version="1.0.0")

# CORS：开发阶段全开（Vite dev 服务器跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 管理接口路由
# ---------------------------------------------------------------------------
app.include_router(kb_routes.router)
app.include_router(model_routes.router)


@app.post("/api/admin/login", response_model=LoginResponse)
def login(req: LoginRequest):
    """管理员登录，校验通过后返回签名 token。"""
    if not verify_credentials(req.username, req.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )
    return LoginResponse(token=create_token(req.username), username=req.username)


@app.get("/api/admin/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# 前端静态资源托管（生产形态：npm run build 后直接访问本服务）
# ---------------------------------------------------------------------------
_DIST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "admin_frontend", "dist")

if os.path.isdir(_DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST_DIR, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        # API 路径不走 SPA 回退（已由上方路由处理，此处兜底排除 /api 前缀）
        if full_path.startswith("api/"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")

        candidate = os.path.join(_DIST_DIR, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)

        return FileResponse(os.path.join(_DIST_DIR, "index.html"))
