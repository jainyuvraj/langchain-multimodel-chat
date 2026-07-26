import React, { useState } from 'react';
import { User, Bot, Copy, Check, AlertTriangle } from 'lucide-react';

export function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`message-wrapper ${isUser ? 'user' : 'assistant'}`}>
      <div className={`message-avatar ${isUser ? 'user' : 'assistant'}`}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>

      <div className="message-content-box">
        <div className="message-header">
          <span>{isUser ? 'You' : `${message.provider ? message.provider.toUpperCase() : 'AI Assistant'} (${message.model || ''})`}</span>
          {!isUser && message.content && (
            <button
              onClick={handleCopy}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
              }}
            >
              {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          )}
        </div>

        <div className="message-body">
          {message.isError && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444', marginBottom: '6px' }}>
              <AlertTriangle size={16} />
              <span style={{ fontWeight: 600 }}>Error encountered</span>
            </div>
          )}
          {message.content ? (
            message.content
          ) : (
            <span style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
              Thinking and generating response...
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
