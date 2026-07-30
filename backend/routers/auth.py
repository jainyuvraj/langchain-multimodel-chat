import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models_db import UserDB
from backend.schemas import TokenSchema, UserSchema, GuestLoginRequestSchema
from backend.auth_service import create_access_token, get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/guest-login", response_model=TokenSchema)
async def guest_login(payload: GuestLoginRequestSchema = None, db: Session = Depends(get_db)):
    """Authenticate or register default Guest Developer."""
    name = (payload and payload.name) or "Guest Developer"
    guest_email = (payload and payload.email) or "guest.dev@polymodel.ai"

    user = db.query(UserDB).filter(UserDB.email == guest_email).first()
    if not user:
        user = UserDB(
            email=guest_email,
            name=name,
            provider="guest"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: UserDB = Depends(get_current_user)):
    """Get authenticated user profile."""
    return current_user

@router.get("/google/url")
async def get_google_oauth_url():
    """OAuth Redirect URL for Google Login."""
    if not settings.GOOGLE_CLIENT_ID:
        # Fallback to dev mode warning if GOOGLE_CLIENT_ID not configured
        return {
            "url": None, 
            "configured": False,
            "message": "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in server .env file."
        }
    
    redirect_uri = "http://localhost:8000/api/auth/google/callback"
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&scope=openid%20email%20profile&access_type=offline"
    )
    return {"url": url, "configured": True}

@router.get("/google/callback")
async def google_oauth_callback(code: str = Query(...), db: Session = Depends(get_db)):
    """Google OAuth2 Callback Handler."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=400, detail="Google OAuth not configured in .env")

    redirect_uri = "http://localhost:8000/api/auth/google/callback"

    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange authorization code with Google")
        
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        # Fetch Google User Info
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_info_res.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
        
        google_user = user_info_res.json()

    email = google_user.get("email")
    name = google_user.get("name", email.split("@")[0])
    avatar = google_user.get("picture")

    # Upsert user in database
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        user = UserDB(
            email=email,
            name=name,
            avatar_url=avatar,
            provider="google"
        )
        db.add(user)
    else:
        user.name = name
        user.avatar_url = avatar
        user.provider = "google"

    db.commit()
    db.refresh(user)

    # Issue JWT Token and redirect to frontend with token parameter
    jwt_token = create_access_token({"sub": user.id, "email": user.email})
    frontend_redirect_url = f"http://localhost:5173?token={jwt_token}"
    return RedirectResponse(url=frontend_redirect_url)
