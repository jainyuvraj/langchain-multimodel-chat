import React, { useEffect, useRef } from 'react';
import { Sparkles } from 'lucide-react';
import { MessageBubble } from './MessageBubble';

export function ChatWindow({ messages, onSelectSuggestion }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const suggestions = [
    "Compare Python vs Go for high-concurrency microservices.",
    "Write a clean React hook for streaming API responses.",
    "Explain LangChain chains vs agents with code examples.",
    "Draft a launch announcement for a multi-model AI app."
  ];

  return (
    <div className="messages-container">
      {messages.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Sparkles size={32} />
          </div>
          <h2 className="empty-title">PolyModel AI Workspace</h2>
          <p className="empty-desc">
            Switch effortlessly between <strong>Google Gemini</strong>, <strong>OpenAI</strong>, and <strong>Anthropic Claude</strong> models powered by LangChain.
          </p>
          <div className="suggestion-chips">
            {suggestions.map((text, idx) => (
              <button
                key={idx}
                className="suggestion-chip"
                onClick={() => onSelectSuggestion(text)}
              >
                {text}
              </button>
            ))}
          </div>
        </div>
      ) : (
        messages.map((msg, index) => (
          <MessageBubble key={index} message={msg} />
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}
