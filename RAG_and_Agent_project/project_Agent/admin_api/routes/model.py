"""
AI 模型配置路由
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from admin_api.auth import require_admin
from admin_api import config_service

router = APIRouter(prefix="/api/admin/model", tags=["model-config"])


@router.get("")
def get_config(_admin: dict = Depends(require_admin)):
    """获取当前模型 / 检索配置。"""
    return config_service.get_model_config()


@router.put("")
def update_config(payload: dict[str, Any], _admin: dict = Depends(require_admin)):
    """更新模型 / 检索配置（写回 config/*.yml）。"""
    try:
        return config_service.update_model_config(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
