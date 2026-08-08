"""
多模型配置文件
定义所有支持的AI模型提供商、模型列表及API配置
新增模型只需在 PROVIDERS 字典中添加相应配置即可
"""

import os
from openai import OpenAI

# ==================== 模型提供商配置 ====================
# 每个提供商包含：
#   - base_url: API地址
#   - api_key_env: 环境变量名，用于获取API Key
#   - models: 该提供商支持的模型列表
#   - extra_params: 提供商特有的额外参数（可选）

# PROVIDERS 字典的 key 为 provider_id（短标识，前后端统一），name 为显示名称
PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "api_key_env": "DEEPSEEK_API_KEY",
        "models": [
            "deepseek-v4-pro",
            "deepseek-chat",
            "deepseek-reasoner",
        ],
        # DeepSeek 特有参数：支持 thinking 模式
        "extra_params": {
            "reasoning_effort": "high",
            "extra_body": {"thinking": {"type": "enabled"}},
        },
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "o3-mini",
        ],
        "extra_params": {},
    },
    "qwen": {
        "name": "通义千问 (阿里)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key_env": "DASHSCOPE_API_KEY",
        "models": [
            "qwen-turbo",
            "qwen-plus",
            "qwen-max",
            "qwen-max-longcontext",
        ],
        "extra_params": {},
    },
    "moonshot": {
        "name": "Moonshot (月之暗面)",
        "base_url": "https://api.moonshot.cn/v1",
        "api_key_env": "MOONSHOT_API_KEY",
        "models": [
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
        ],
        "extra_params": {},
    },
    "zhipu": {
        "name": "智谱AI (GLM)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "api_key_env": "ZHIPUAI_API_KEY",
        "models": [
            "glm-4-plus",
            "glm-4",
            "glm-4-flash",
            "glm-4-air",
        ],
        "extra_params": {},
    },
    "yi": {
        "name": "零一万物",
        "base_url": "https://api.lingyiwanwu.com/v1",
        "api_key_env": "YI_API_KEY",
        "models": [
            "yi-lightning",
            "yi-large",
            "yi-medium",
        ],
        "extra_params": {},
    },
}


def get_provider_list() -> list:
    """获取所有提供商 ID 列表"""
    return list(PROVIDERS.keys())


def get_provider_display_name(provider_id: str) -> str:
    """获取提供商的显示名称"""
    config = PROVIDERS.get(provider_id)
    return config["name"] if config else provider_id


def get_provider_display_map() -> dict:
    """获取 {provider_id: display_name} 映射，用于 UI 下拉框"""
    return {pid: cfg["name"] for pid, cfg in PROVIDERS.items()}


def get_models_by_provider(provider_id: str) -> list:
    """获取指定提供商下的模型列表"""
    provider = PROVIDERS.get(provider_id)
    return provider["models"] if provider else []


def get_provider_by_model(model_name: str) -> str | None:
    """根据模型名称反向查找所属提供商 ID"""
    for provider_id, config in PROVIDERS.items():
        if model_name in config["models"]:
            return provider_id
    return None


def create_client(provider_id: str) -> OpenAI | None:
    """
    根据提供商 ID 创建对应的 OpenAI 客户端
    返回 None 表示 API Key 未配置
    """
    config = PROVIDERS.get(provider_id)
    if not config:
        return None

    api_key = os.environ.get(config["api_key_env"])
    if not api_key:
        return None

    return OpenAI(api_key=api_key, base_url=config["base_url"])


def get_extra_params(provider_id: str) -> dict:
    """获取提供商特有的额外参数"""
    config = PROVIDERS.get(provider_id)
    return config.get("extra_params", {}) if config else {}