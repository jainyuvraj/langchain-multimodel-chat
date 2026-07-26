from fastapi import APIRouter, HTTPException, status
from backend.schemas import TokenSchema, UserSchema

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenSchema)
async def login_placeholder():
    """
    Modular Auth Hook for Future OAuth / JWT integration.
    Allows easy plug-in of OAuth2 / OpenID Connect providers in the future.
    """
    return {
        "access_token": "dev_guest_access_token_placeholder",
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserSchema)
async def get_current_user_placeholder():
    """Retrieve currently authenticated user profile placeholder."""
    return {
        "id": "guest_123",
        "email": "guest@example.com",
        "name": "Guest Developer",
    }
