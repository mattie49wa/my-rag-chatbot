from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    api_title: str = "Document Query API"
    api_version: str = "1.0.0"

    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    # Embedding Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Chunking Settings
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Vector Store Settings
    faiss_index_path: str = "./faiss_index"
    top_k_chunks: int = 10

    # PDF Processing
    max_pdf_size_mb: int = 50
    pdf_download_timeout: int = 30

    # Redis Settings (for async jobs)
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
