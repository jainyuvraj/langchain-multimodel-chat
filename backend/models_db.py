import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, default="guest")  # 'guest', 'google', 'github'
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSessionDB", back_populates="user", cascade="all, delete-orphan")

class ChatSessionDB(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)  # chatId
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)  # userId
    title = Column(String, default="New Conversation")
    provider = Column(String, default="google")
    model = Column(String, default="gemini-flash-latest")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("UserDB", back_populates="sessions")
    messages = relationship("ChatMessageDB", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessageDB.timestamp")

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    chat_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    session = relationship("ChatSessionDB", back_populates="messages")
