from typing import List
from fastapi import APIRouter
from backend.schemas import ProviderModelsSchema
from backend.llm_helper import AVAILABLE_PROVIDERS

router = APIRouter(prefix="/api/models", tags=["models"])

@router.get("/providers", response_model=List[ProviderModelsSchema])
async def get_providers():
    """Retrieve available LLM providers, model options, and metadata."""
    return AVAILABLE_PROVIDERS
