import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Search for .env in backend, parent directory, and current directory
env_paths = [
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parent.parent.parent / ".env",
    Path.cwd() / ".env"
]
for p in env_paths:
    if p.exists():
        load_dotenv(p)
        break
else:
    load_dotenv()


class Settings(BaseModel):
    # API Keys
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    OPENAI_API_KEY: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    HUGGINGFACE_API_KEY: str = Field(default_factory=lambda: os.getenv("HUGGINGFACE_API_KEY", ""))

    # Models
    GEMINI_MODEL: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    GEMINI_EMBEDDING_MODEL: str = Field(default_factory=lambda: os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"))
    OPENAI_MODEL: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o"))
    HUGGINGFACE_MODEL: str = Field(default_factory=lambda: os.getenv("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"))

    # MySQL Database Settings
    MYSQL_HOST: str = Field(default_factory=lambda: os.getenv("MYSQL_HOST", "localhost"))
    MYSQL_PORT: int = Field(default_factory=lambda: int(os.getenv("MYSQL_PORT", "3306")))
    MYSQL_USER: str = Field(default_factory=lambda: os.getenv("MYSQL_USER", "root"))
    MYSQL_PASSWORD: str = Field(default_factory=lambda: os.getenv("MYSQL_PASSWORD", ""))
    MYSQL_DATABASE: str = Field(default_factory=lambda: os.getenv("MYSQL_DATABASE", "omnimind_ai"))

    # Server settings
    BACKEND_PORT: int = Field(default_factory=lambda: int(os.getenv("BACKEND_PORT", "8000")))
    ALLOWED_ORIGINS: List[str] = ["*"]

    # File Upload Limits
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/m4a", "audio/ogg", "audio/webm"]
    ALLOWED_DOC_TYPES: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]

    # RAG Settings
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    TOP_K_CHUNKS: int = 4
    SIMILARITY_THRESHOLD: float = 0.25


settings = Settings()
