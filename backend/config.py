"""
ATS Resume Scorer - Application Configuration
Loads settings from .env file using pydantic-settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    # ── Supabase ──────────────────────────────────────────────
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field("", env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_JWT_SECRET: str = Field("", env="SUPABASE_JWT_SECRET")

    # ── Groq ──────────────────────────────────────────────────
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    GROQ_MODEL: str = "llama3-70b-8192"

    # ── JWT / Security ────────────────────────────────────────
    SECRET_KEY: str = Field("changeme-super-secret-32chars!!", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Google OAuth ──────────────────────────────────────────
    GOOGLE_CLIENT_ID: str = Field("", env="GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = Field("", env="GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = Field(
        "http://localhost:8000/auth/google/callback", env="GOOGLE_REDIRECT_URI"
    )

    # ── URLs ──────────────────────────────────────────────────
    BACKEND_URL: str = "http://localhost:8000"
    FRONTEND_URL: str = "http://localhost:8501"

    # ── File Upload ───────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: list = ["pdf", "doc", "docx"]

    # ── NLP Models ────────────────────────────────────────────
    SPACY_MODEL: str = "en_core_web_md"
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
