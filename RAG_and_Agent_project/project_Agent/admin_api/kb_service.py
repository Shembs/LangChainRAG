"""
知识库管理服务（FastAPI 侧）

复用 utils/kb_upload.py 中的 refresh_knowledge_base / get_kb_file_list /
delete_kb_file，仅对 FastAPI UploadFile 提供字节保存适配。
"""

from fastapi import UploadFile

from utils.kb_upload import (
    save_file_bytes,
    refresh_knowledge_base,
    get_kb_file_list,
    delete_kb_file,
)


async def save_upload(file: UploadFile) -> dict:
    """保存单个 FastAPI UploadFile 到 data/ 目录。

    Returns:
        dict: {"name", "success", "path"/"message"}
    """
    filename = file.filename or "unnamed"
    data = await file.read()

    saved_path = save_file_bytes(filename, data)
    if saved_path:
        return {"name": filename, "success": True, "path": saved_path}
    return {"name": filename, "success": False, "message": "文件类型不支持或保存失败"}


__all__ = [
    "save_upload",
    "refresh_knowledge_base",
    "get_kb_file_list",
    "delete_kb_file",
]
