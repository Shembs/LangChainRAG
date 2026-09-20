"""
AI 模型配置读写服务

读取 / 更新 config/rag.yml（对话模型、嵌入模型、温度）和
config/chroma.yml（检索条数、分片参数），写回后同步内存字典。

注意：模型名称 / 温度 / 嵌入模型等参数在服务启动时已用于构建模型实例，
修改后需重启服务方可生效；检索条数 k 在每次检索时读取，新值对后续检索即时生效。
"""

from typing import Any

import yaml

from utils.config_handler import rag_conf, chroma_conf
from utils.path_tool import get_abs_path

# ---------------------------------------------------------------------------
# 配置项定义（前端可编辑字段）
# ---------------------------------------------------------------------------
_RAG_EDITABLE_KEYS = ("chat_model_name", "embedding_model_name", "temperature")
_CHROMA_EDITABLE_KEYS = ("k", "chunk_size", "chunk_overlap")

_RAG_CONFIG_PATH = get_abs_path("config/rag.yml")
_CHROMA_CONFIG_PATH = get_abs_path("config/chroma.yml")


# ---------------------------------------------------------------------------
# 读取
# ---------------------------------------------------------------------------
def get_model_config() -> dict[str, Any]:
    """返回前端可编辑的模型/检索配置（当前内存中的值）。"""
    return {
        "chat_model_name": rag_conf.get("chat_model_name"),
        "embedding_model_name": rag_conf.get("embedding_model_name"),
        "temperature": rag_conf.get("temperature", 0.7),
        "k": chroma_conf.get("k", 3),
        "chunk_size": chroma_conf.get("chunk_size", 200),
        "chunk_overlap": chroma_conf.get("chunk_overlap", 100),
    }


# ---------------------------------------------------------------------------
# 校验
# ---------------------------------------------------------------------------
def _validate(data: dict[str, Any]) -> dict[str, Any]:
    """校验并规范化输入，返回清洗后的配置；不合法时抛出 ValueError。"""
    cleaned: dict[str, Any] = {}

    for key in ("chat_model_name", "embedding_model_name"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} 不能为空")
        cleaned[key] = value.strip()

    temperature = data.get("temperature", 0.7)
    try:
        temperature = float(temperature)
    except (TypeError, ValueError):
        raise ValueError("temperature 必须是数字")
    if not 0 <= temperature <= 2:
        raise ValueError("temperature 取值范围为 0 ~ 2")
    cleaned["temperature"] = temperature

    k = data.get("k", 3)
    try:
        k = int(k)
    except (TypeError, ValueError):
        raise ValueError("k 必须是整数")
    if not 1 <= k <= 20:
        raise ValueError("k 取值范围为 1 ~ 20")
    cleaned["k"] = k

    chunk_size = data.get("chunk_size", 200)
    try:
        chunk_size = int(chunk_size)
    except (TypeError, ValueError):
        raise ValueError("chunk_size 必须是整数")
    if not 50 <= chunk_size <= 2000:
        raise ValueError("chunk_size 取值范围为 50 ~ 2000")
    cleaned["chunk_size"] = chunk_size

    chunk_overlap = data.get("chunk_overlap", 100)
    try:
        chunk_overlap = int(chunk_overlap)
    except (TypeError, ValueError):
        raise ValueError("chunk_overlap 必须是整数")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap 取值范围为 0 ~ (chunk_size - 1)")
    cleaned["chunk_overlap"] = chunk_overlap

    return cleaned


# ---------------------------------------------------------------------------
# 写回
# ---------------------------------------------------------------------------
def _dump_yaml(path: str, data: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def update_model_config(data: dict[str, Any]) -> dict[str, Any]:
    """校验并持久化配置，同步内存字典。

    Args:
        data: 前端提交的配置字段。

    Returns:
        dict: 更新后的完整配置 + restart_required 标记。
    """
    cleaned = _validate(data)

    # 更新 rag.yml：仅覆盖可编辑字段，保留其余键（如 external_data_path）
    rag_updated = dict(rag_conf)
    for key in _RAG_EDITABLE_KEYS:
        rag_updated[key] = cleaned[key]
    _dump_yaml(_RAG_CONFIG_PATH, rag_updated)

    # 更新 chroma.yml：仅覆盖可编辑字段，保留其余键
    chroma_updated = dict(chroma_conf)
    for key in _CHROMA_EDITABLE_KEYS:
        chroma_updated[key] = cleaned[key]
    _dump_yaml(_CHROMA_CONFIG_PATH, chroma_updated)

    # 同步内存字典（utils.config_handler 中的模块级 dict 是共享引用）
    rag_conf.update({key: cleaned[key] for key in _RAG_EDITABLE_KEYS})
    chroma_conf.update({key: cleaned[key] for key in _CHROMA_EDITABLE_KEYS})

    return {
        **get_model_config(),
        "restart_required": True,
    }
