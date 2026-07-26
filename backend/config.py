import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Multi-Model LangChain Chatbot"
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite Dev Server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]
    
    # Provider Default API Keys (loaded from .env if present)
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Modular Placeholders for Future Extensions
    # Database
    DATABASE_URL: Optional[str] = "sqlite:///./chat_history.db"
    
    # OAuth / Auth Configuration
    SECRET_KEY: str = "super-secret-dev-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
