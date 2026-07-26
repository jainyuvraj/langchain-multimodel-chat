from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class MessageSchema(BaseModel):
    role: str = Field(..., description="Role of the message sender: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Text content of the message")

class ApiKeysSchema(BaseModel):
    google: Optional[str] = Field(None, description="Google Gemini API Key")
    openai: Optional[str] = Field(None, description="OpenAI API Key")
    anthropic: Optional[str] = Field(None, description="Anthropic API Key")

class ChatRequestSchema(BaseModel):
    provider: str = Field(..., description="Provider name: 'google', 'openai', or 'anthropic'")
    model: str = Field(..., description="Specific model name (e.g. 'gemini-2.0-flash', 'gpt-4o', 'claude-3-5-sonnet-20240620')")
    messages: List[MessageSchema] = Field(..., description="List of previous conversation messages")
    system_prompt: Optional[str] = Field("You are a helpful, knowledgeable AI assistant.", description="Custom system prompt")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(2048, ge=1, le=8192, description="Maximum completion tokens")
    api_keys: Optional[ApiKeysSchema] = Field(None, description="Optional custom API key overrides")

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

# Future Auth / Database Schemas Placeholder
class UserSchema(BaseModel):
    id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
