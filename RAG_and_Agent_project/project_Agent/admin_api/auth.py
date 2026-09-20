"""
后台管理员登录鉴权

使用标准库（hmac + base64 + json + time）签发/校验 HMAC 签名 token，
不引入额外依赖。token 有效期 8 小时。

管理员账号默认 admin / 123456，可通过环境变量 ADMIN_USERNAME / ADMIN_PASSWORD 覆盖。
"""

import base64
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
ADMIN_USERNAME: str = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "123456")

# 签名密钥（生产环境请通过 ADMIN_SECRET_KEY 环境变量覆盖）
SECRET_KEY: str = os.environ.get("ADMIN_SECRET_KEY", "langchain-rag-admin-secret")

TOKEN_TTL_SECONDS: int = 8 * 60 * 60  # 8 小时


# ---------------------------------------------------------------------------
# token 签发 / 校验
# ---------------------------------------------------------------------------
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(payload_b64: str) -> str:
    digest = hmac.new(SECRET_KEY.encode("utf-8"), payload_b64.encode("ascii"), hashlib.sha256).digest()
    return _b64url_encode(digest)


def create_token(username: str) -> str:
    """为指定用户签发一个签名 token。"""
    payload = {"username": username, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    payload_b64 = _b64url_encode(json.dumps(payload).encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64)}"


def verify_token(token: str) -> dict | None:
    """校验 token，成功返回 payload 字典，失败返回 None。"""
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError:
        return None

    if not hmac.compare_digest(_sign(payload_b64), signature):
        return None

    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None

    if payload.get("exp", 0) < int(time.time()):
        return None

    return payload


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str


# ---------------------------------------------------------------------------
# FastAPI 依赖
# ---------------------------------------------------------------------------
def require_admin(authorization: str | None = Header(default=None)) -> dict:
    """校验 Bearer token，返回 payload；未登录/过期/非法时抛出 401。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或缺少认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(authorization[len("Bearer "):].strip())
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def verify_credentials(username: str, password: str) -> bool:
    """校验管理员账号密码。"""
    # 使用 hmac.compare_digest 避免时序攻击
    return hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(
        password, ADMIN_PASSWORD
    )
