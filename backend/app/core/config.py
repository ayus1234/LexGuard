from typing import List, Union, Optional
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    PROJECT_NAME: str = "LexGuard Backend"
    API_V1_PREFIX: str = "/api/v1"
    
    # 50 MB default maximum upload size
    MAX_UPLOAD_SIZE_MB: int = 50

    # Gemini AI Model Configuration
    GEMINI_API_KEY_PRIMARY: Optional[str] = None
    GEMINI_API_KEY_FALLBACK: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    MAX_ANALYSIS_CHAR_COUNT: int = 150000

    # Database Configuration (PostgreSQL + pgvector)
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lexguard"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30

    # Retrieval & Vector Store Configuration
    EMBEDDING_DIMENSION: int = 3072
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHUNK_TARGET_SIZE: int = 1000
    CHUNK_OVERLAP: int = 150
    MIN_CHUNK_SIZE: int = 100
    EMBEDDING_BATCH_SIZE: int = 32
    RETRIEVAL_MIN_SCORE: float = 0.55

    # Allowed CORS Origins
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Temporary storage for processing
    TEMP_STORAGE_PATH: str = "./tmp_uploads"

    # Public Application URL & Sharing
    APP_URL: str = "http://localhost:3000"
    SHARE_TOKEN_TTL_HOURS: int = 48

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    @property
    def async_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def temp_storage_dir(self) -> Path:
        path = Path(self.TEMP_STORAGE_PATH).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def chroma_persist_dir(self) -> Path:
        path = Path(self.CHROMA_PERSIST_DIRECTORY).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
