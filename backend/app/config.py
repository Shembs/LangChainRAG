from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # LLM
    llm_api_base: str = "https://api.deepseek.com/v1"
    llm_api_key: str = Field(default="sk-xxx", validation_alias="DEEPSEEK_API_KEY")
    llm_model: str = "deepseek-V4Pro"

    # Embedding (复用 LLM 的 API Key)
    embedding_api_base: str = "https://api.deepseek.com/v1"
    embedding_api_key: str = Field(default="sk-xxx", validation_alias="DEEPSEEK_API_KEY")
    embedding_model: str = "deepseek-V4Pro"

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5444/rag_kb"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret_key: str = "change-this-to-a-random-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Admin Seed
    admin_username: str = "admin"
    admin_password: str = "123456"

    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Upload
    max_upload_size_mb: int = 50
    upload_dir: str = "./data/uploads"

    # Chunking defaults
    default_chunk_size: int = 500
    default_chunk_overlap: int = 80

    # Retrieval
    retrieval_top_k: int = 15
    rerank_top_k: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}


settings = Settings()
