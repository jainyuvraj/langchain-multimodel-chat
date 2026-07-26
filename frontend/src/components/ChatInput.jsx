import React, { useState, useRef, useEffect } from 'react';
import { Send, Square } from 'lucide-react';

export function ChatInput({ onSendMessage, isStreaming, onStopStreaming }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [text]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (text.trim() && !isStreaming) {
      onSendMessage(text);
      setText('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="input-area-wrapper">
      <form onSubmit={handleSubmit} className="chat-input-card">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder="Ask anything... (Press Enter to send, Shift+Enter for newline)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
        />

        {isStreaming ? (
          <button
            type="button"
            className="btn-send"
            style={{ background: '#ef4444' }}
            onClick={onStopStreaming}
            title="Stop generation"
          >
            <Square size={16} fill="white" />
          </button>
        ) : (
          <button
            type="submit"
            className="btn-send"
            disabled={!text.trim()}
            title="Send Message"
          >
            <Send size={16} />
          </button>
        )}
      </form>
      <div className="input-footer-note">
        PolyModel AI • Modular LangChain Architecture (FastAPI + React JSX)
      </div>
    </div>
  );
}
