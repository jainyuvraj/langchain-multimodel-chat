from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.config import settings
from backend.db import get_db
from backend.models_db import UserDB
from backend.schemas import UserSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[UserDB]:
    """Retrieve current user from JWT token, or return/create default guest user if no token."""
    if not token:
        # Fallback to default developer guest account
        guest_email = "guest.dev@polymodel.ai"
        user = db.query(UserDB).filter(UserDB.email == guest_email).first()
        if not user:
            user = UserDB(
                email=guest_email,
                name="Guest Developer",
                provider="guest"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return get_current_user_optional(None, db)
    except JWTError:
        return get_current_user_optional(None, db)

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if user is None:
        return get_current_user_optional(None, db)
    return user

def get_current_user(
    user: Optional[UserDB] = Depends(get_current_user_optional)
) -> UserDB:
    """Enforce authenticated user requirement."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
