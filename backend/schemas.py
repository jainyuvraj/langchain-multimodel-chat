from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MessageSchema(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="Role of message sender: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Text content of message")
    timestamp: Optional[datetime] = None

class ApiKeysSchema(BaseModel):
    google: Optional[str] = None
    openai: Optional[str] = None
    anthropic: Optional[str] = None
    groq: Optional[str] = None

class ChatRequestSchema(BaseModel):
    chat_id: Optional[str] = Field(None, description="Active conversation thread ID")
    provider: str = Field(..., description="Provider name: 'google', 'groq', 'openai', 'anthropic'")
    model: str = Field(..., description="Specific model name")
    messages: List[MessageSchema] = Field(..., description="List of previous conversation messages")
    system_prompt: Optional[str] = Field("You are a helpful, creative, and precise AI assistant.", description="Custom system prompt")
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(2048, ge=1, le=8192)
    enable_inter_chat_memory: bool = Field(False, description="Toggle between Chat-specific Memory (OFF) and All User Threads Memory (ON)")
    api_keys: Optional[ApiKeysSchema] = None

class ModelInfoSchema(BaseModel):
    id: str
    name: str
    description: str
    recommended: bool = False

class ProviderModelsSchema(BaseModel):
    id: str
    name: str
    icon: str
    requires_key: bool = True
    models: List[ModelInfoSchema]

# Auth & User Schemas
class UserSchema(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    provider: str = "guest"

    class Config:
        from_attributes = True

class GuestLoginRequestSchema(BaseModel):
    name: Optional[str] = "Guest Developer"
    email: Optional[str] = None

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema

# Chat Session Schemas
class ChatSessionSchema(BaseModel):
    id: str
    user_id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CreateSessionRequestSchema(BaseModel):
    title: Optional[str] = "New Conversation"
    provider: Optional[str] = "google"
    model: Optional[str] = "gemini-flash-latest"
