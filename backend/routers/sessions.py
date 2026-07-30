from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.models_db import UserDB, ChatSessionDB, ChatMessageDB
from backend.schemas import ChatSessionSchema, CreateSessionRequestSchema, MessageSchema
from backend.auth_service import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("", response_model=List[ChatSessionSchema])
async def list_user_sessions(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all chat sessions (chatID) belonging to current userID."""
    sessions = (
        db.query(ChatSessionDB)
        .filter(ChatSessionDB.user_id == current_user.id)
        .order_by(ChatSessionDB.updated_at.desc())
        .all()
    )
    return sessions

@router.post("", response_model=ChatSessionSchema)
async def create_new_session(
    payload: CreateSessionRequestSchema,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session (Restricted to 1 thread for Guest users)."""
    if current_user.provider == "guest":
        existing_count = db.query(ChatSessionDB).filter(ChatSessionDB.user_id == current_user.id).count()
        if existing_count >= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guest users are limited to 1 chat thread. Please sign in with Google to create unlimited chat threads."
            )

    session = ChatSessionDB(
        user_id=current_user.id,
        title=payload.title or "New Conversation",
        provider=payload.provider or "google",
        model=payload.model or "gemini-flash-latest",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/{chat_id}/messages", response_model=List[MessageSchema])
async def get_session_messages(
    chat_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve message history for a specific chatID belonging to current userID."""
    session = (
        db.query(ChatSessionDB)
        .filter(ChatSessionDB.id == chat_id, ChatSessionDB.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    return [
        MessageSchema(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            timestamp=msg.timestamp
        )
        for msg in session.messages
    ]

@router.delete("/{chat_id}")
async def delete_session(
    chat_id: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a chat session."""
    session = (
        db.query(ChatSessionDB)
        .filter(ChatSessionDB.id == chat_id, ChatSessionDB.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    db.delete(session)
    db.commit()
    return {"status": "deleted", "chat_id": chat_id}
