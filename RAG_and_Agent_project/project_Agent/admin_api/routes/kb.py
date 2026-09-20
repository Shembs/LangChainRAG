"""
知识库管理路由
"""

from fastapi import APIRouter, Depends, File, UploadFile

from admin_api.auth import require_admin
from admin_api import kb_service

router = APIRouter(prefix="/api/admin/kb", tags=["knowledge-base"])


@router.get("/files")
def list_files(_admin: dict = Depends(require_admin)):
    """列出 data/ 目录下已上传的知识库文件。"""
    return kb_service.get_kb_file_list()


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    _admin: dict = Depends(require_admin),
):
    """上传一个或多个知识文档，保存后触发向量库增量索引。"""
    saved, failed = [], []
    for file in files:
        result = await kb_service.save_upload(file)
        (saved if result["success"] else failed).append(result)

    refresh_result = None
    if saved:
        refresh_result = kb_service.refresh_knowledge_base()

    return {
        "saved": saved,
        "failed": failed,
        "refresh": refresh_result,
    }


@router.post("/refresh")
def refresh_index(_admin: dict = Depends(require_admin)):
    """手动触发向量库增量索引。"""
    return kb_service.refresh_knowledge_base()


@router.delete("/files/{filename}")
def delete_file(filename: str, _admin: dict = Depends(require_admin)):
    """删除 data/ 目录下的指定文件。"""
    return kb_service.delete_kb_file(filename)
