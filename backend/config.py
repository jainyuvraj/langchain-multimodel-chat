import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "PolyModel AI - Multi-Model Vector Chatbot"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite Dev Server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Provider System API Keys
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Database Configuration (SQLite + SQLAlchemy)
    DATABASE_URL: str = "sqlite:///./chat_database.db"
    
    # ChromaDB Vector Store Directory
    CHROMADB_DIR: str = "./chroma_vector_db"

    # JWT Authentication & OAuth Configuration
    SECRET_KEY: str = "polymodel-ai-jwt-secret-key-production-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Days

    # OAuth Client Configurations (Google & GitHub)
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
