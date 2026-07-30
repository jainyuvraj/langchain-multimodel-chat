import React from 'react';
import { MessageSquare, Plus, Trash2, Database, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function ChatHistorySidebar({
  sessions = [],
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}) {
  const { user, setIsAuthModalOpen } = useAuth();
  const safeSessions = Array.isArray(sessions) ? sessions : [];
  const isGuest = !user || user.provider === 'guest';
  const isNewChatDisabled = isGuest && safeSessions.length >= 1;

  return (
    <div className="chat-history-sidebar">
      <div className="history-header">
        <button
          className={`btn-new-chat ${isNewChatDisabled ? 'disabled' : ''}`}
          disabled={isNewChatDisabled}
          onClick={onNewChat}
          title={isNewChatDisabled ? 'Guest users are limited to 1 chat thread. Sign in with Google for unlimited threads.' : 'Create New Chat Thread'}
        >
          {isNewChatDisabled ? <Lock size={15} /> : <Plus size={16} />}
          <span>{isNewChatDisabled ? '1-Chat Limit (Guest)' : 'New Chat'}</span>
        </button>
      </div>

      <div className="history-list-title">
        <Database size={12} />
        <span>Vector & DB Threads</span>
      </div>

      <div className="history-list">
        {safeSessions.length === 0 ? (
          <div className="empty-history-text">No saved conversations yet.</div>
        ) : (
          safeSessions.map((session) => (
            <div
              key={session.id}
              className={`history-item ${activeChatId === session.id ? 'active' : ''}`}
              onClick={() => onSelectChat(session.id)}
            >
              <MessageSquare size={15} className="history-icon" />
              <div className="history-details">
                <span className="history-title">{session.title || 'Untitled Chat'}</span>
                <span className="history-model">{session.provider.toUpperCase()}</span>
              </div>
              <button
                className="btn-delete-chat"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteChat(session.id);
                }}
                title="Delete chat thread"
              >
                <Trash2 size={13} />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Guest Mode Banner */}
      {isGuest && (
        <div className="guest-limit-banner" onClick={() => setIsAuthModalOpen(true)}>
          <Lock size={14} color="#f43f5e" />
          <span>Sign In with Google for Unlimited Threads</span>
        </div>
      )}
    </div>
  );
}
