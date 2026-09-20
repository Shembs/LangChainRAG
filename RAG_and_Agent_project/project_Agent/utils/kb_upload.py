"""
知识库上传处理工具

提供文件保存到 data/ 目录、触发向量库增量索引的功能。
用于 Streamlit 前端侧边栏的知识库管理。
"""

import os
from pathlib import Path
from typing import Optional

from utils.path_tool import get_abs_path
from utils.config_handler import chroma_conf
from utils.logger_handler import logger


# 允许上传的文件扩展名（与 chroma.yml 中的 allow_knowledge_file_type 保持一致）
ALLOWED_EXTENSIONS: tuple[str, ...] = tuple(
    chroma_conf.get("allow_knowledge_file_type", ["pdf", "txt", "docx"])
)


def save_file_bytes(filename: str, data: bytes) -> Optional[str]:
    """将文件字节写入 data/ 目录（Streamlit 与 FastAPI 共用）。

    Args:
        filename: 原始文件名（含扩展名）。
        data: 文件的二进制内容。

    Returns:
        str: 保存成功的文件绝对路径；失败或类型不允许时返回 None。
    """
    # 检查文件扩展名
    file_ext = Path(filename).suffix.lstrip(".").lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"[知识库上传]不支持的文件类型: .{file_ext}（允许: {ALLOWED_EXTENSIONS}）")
        return None

    data_dir = get_abs_path(chroma_conf["data_path"])
    os.makedirs(data_dir, exist_ok=True)

    save_path = os.path.join(data_dir, filename)

    # 避免覆盖已有文件：添加序号后缀
    if os.path.exists(save_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            save_path = os.path.join(data_dir, f"{base}_{counter}{ext}")
            counter += 1

    try:
        with open(save_path, "wb") as f:
            f.write(data)
        logger.info(f"[知识库上传]文件已保存: {save_path}")
        return save_path
    except Exception as e:
        logger.error(f"[知识库上传]保存文件失败: {e}", exc_info=True)
        return None


def save_uploaded_file(uploaded_file) -> Optional[str]:
    """将 Streamlit UploadedFile 保存到 data/ 目录。

    Args:
        uploaded_file: Streamlit 的 UploadedFile 对象，需有 .name 和 .getbuffer() 方法。

    Returns:
        str: 保存成功的文件绝对路径；失败或类型不允许时返回 None。
    """
    return save_file_bytes(uploaded_file.name, uploaded_file.getbuffer())


def refresh_knowledge_base() -> dict:
    """触发向量库重新加载文档（增量索引，md5 去重）。

    Returns:
        dict: 包含状态信息的字典。
            - success (bool): 是否成功
            - message (str): 状态消息
    """
    try:
        from RAG.vector_store import VectorStoreService

        vs = VectorStoreService()
        vs.load_document()
        logger.info("[知识库上传]向量库增量索引完成")
        return {"success": True, "message": "知识库索引更新成功"}
    except Exception as e:
        logger.error(f"[知识库上传]向量库索引更新失败: {e}", exc_info=True)
        return {"success": False, "message": f"索引更新失败: {e}"}


def get_kb_file_list() -> list[dict]:
    """获取 data/ 目录中已上传的知识库文件列表。

    Returns:
        list[dict]: 文件信息列表，每项包含 name, size, mtime。
    """
    data_dir = get_abs_path(chroma_conf["data_path"])
    if not os.path.isdir(data_dir):
        return []

    files = []
    for fname in os.listdir(data_dir):
        fpath = os.path.join(data_dir, fname)
        if os.path.isfile(fpath):
            ext = Path(fname).suffix.lstrip(".").lower()
            if ext in ALLOWED_EXTENSIONS:
                stat = os.stat(fpath)
                files.append({
                    "name": fname,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "mtime": stat.st_mtime,
                })

    # 按修改时间降序排列
    files.sort(key=lambda x: x["mtime"], reverse=True)
    return files


def delete_kb_file(filename: str) -> dict:
    """删除 data/ 目录中的指定文件。

    Args:
        filename: 要删除的文件名（不含路径）。

    Returns:
        dict: 包含状态信息的字典。
    """
    data_dir = get_abs_path(chroma_conf["data_path"])
    file_path = os.path.join(data_dir, filename)

    if not os.path.isfile(file_path):
        return {"success": False, "message": f"文件不存在: {filename}"}

    try:
        os.remove(file_path)
        logger.info(f"[知识库上传]文件已删除: {file_path}")
        return {"success": True, "message": f"已删除: {filename}"}
    except Exception as e:
        logger.error(f"[知识库上传]删除文件失败: {e}", exc_info=True)
        return {"success": False, "message": f"删除失败: {e}"}
