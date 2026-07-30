import json
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models_db import UserDB, ChatSessionDB, ChatMessageDB
from backend.schemas import ChatRequestSchema
from backend.llm_helper import LLMService
from backend.vector_service import VectorMemoryService
from backend.auth_service import get_current_user_optional

router = APIRouter(prefix="/api/chat", tags=["chat"])

async def event_generator(request: ChatRequestSchema, user_id: str, chat_id: str, assistant_msg_id: str):
    """
    Format streamed tokens as SSE with page-refresh resilience.
    Pre-creates assistant DB record and continuously updates DB & Vector Memory even if client disconnects.
    """
    accumulated_response = []

    try:
        async for token in LLMService.stream_chat_tokens(request, user_id=user_id, chat_id=chat_id):
            accumulated_response.append(token)
            payload = json.dumps({"token": token, "chat_id": chat_id, "message_id": assistant_msg_id})
            yield f"data: {payload}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        error_payload = json.dumps({"token": f"[ERROR]: {str(e)}", "chat_id": chat_id})
        yield f"data: {error_payload}\n\n"
        yield "data: [DONE]\n\n"

    finally:
        # ALWAYS Save whatever text was generated so far into SQLite DB & Vector Memory
        # (even if user closed tab, refreshed page, or disconnected mid-stream!)
        full_text = "".join(accumulated_response).strip()
        if full_text and not full_text.startswith("[ERROR]:"):
            db = next(get_db())
            try:
                msg = db.query(ChatMessageDB).filter(ChatMessageDB.id == assistant_msg_id).first()
                if msg:
                    msg.content = full_text
                else:
                    msg = ChatMessageDB(
                        id=assistant_msg_id,
                        chat_id=chat_id,
                        role="assistant",
                        content=full_text,
                        timestamp=datetime.utcnow()
                    )
                    db.add(msg)
                
                # Update session title if default
                session = db.query(ChatSessionDB).filter(ChatSessionDB.id == chat_id).first()
                if session and session.title == "New Conversation":
                    first_msg = request.messages[0].content if request.messages else "Chat"
                    session.title = first_msg[:30] + ("..." if len(first_msg) > 30 else "")
                    session.updated_at = datetime.utcnow()

                db.commit()

                # Index in ChromaDB Vector Memory
                VectorMemoryService.add_message(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_id=assistant_msg_id,
                    role="assistant",
                    content=full_text,
                    title=session.title if session else "Chat Thread"
                )
            except Exception as e:
                print(f"[DB/Vector Save Error]: {str(e)}")
            finally:
                db.close()

@router.post("/stream")
async def chat_stream(
    request: ChatRequestSchema,
    current_user: UserDB = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Stream completions with Vector Memory context retrieval & SQL persistence."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")

    user_id = current_user.id

    # Resolve or create ChatSession (chatID) safely without primary key clashes
    chat_id = request.chat_id
    session = None

    if chat_id:
        session = db.query(ChatSessionDB).filter(ChatSessionDB.id == chat_id).first()
        if session and session.user_id != user_id:
            session.user_id = user_id
            db.commit()

    if not session:
        first_text = request.messages[0].content if request.messages else "New Chat"
        session_title = first_text[:30] + ("..." if len(first_text) > 30 else "")
        new_id = chat_id if chat_id else str(uuid.uuid4())
        session = ChatSessionDB(
            id=new_id,
            user_id=user_id,
            title=session_title,
            provider=request.provider,
            model=request.model
        )
        try:
            db.add(session)
            db.commit()
            db.refresh(session)
        except Exception:
            db.rollback()
            # Fallback for ID collision: generate a fresh UUID
            session.id = str(uuid.uuid4())
            db.add(session)
            db.commit()
            db.refresh(session)

        chat_id = session.id
        request.chat_id = chat_id

    # Save latest user message to DB & Vector Memory
    latest_user_msg = request.messages[-1]
    if latest_user_msg.role == "user":
        user_msg_id = str(uuid.uuid4())
        db_user_msg = ChatMessageDB(
            id=user_msg_id,
            chat_id=chat_id,
            role="user",
            content=latest_user_msg.content,
            timestamp=datetime.utcnow()
        )
        db.add(db_user_msg)
        db.commit()

        # Index in ChromaDB Vector Memory with session title metadata
        VectorMemoryService.add_message(
            user_id=user_id,
            chat_id=chat_id,
            message_id=user_msg_id,
            role="user",
            content=latest_user_msg.content,
            title=session.title if session else "Chat Thread"
        )

    # Pre-generate assistant message ID for page refresh resilience
    assistant_msg_id = str(uuid.uuid4())

    return StreamingResponse(
        event_generator(request, user_id=user_id, chat_id=chat_id, assistant_msg_id=assistant_msg_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
