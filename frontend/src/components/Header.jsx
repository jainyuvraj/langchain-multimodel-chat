import React from 'react';
import { Cpu } from 'lucide-react';
import { UserMenu } from './UserMenu';

export function Header({ activeProvider, activeModel }) {
  const getProviderName = (id) => {
    if (id === 'google') return 'Google Gemini';
    if (id === 'groq') return 'Groq (Llama 3 / DeepSeek / Qwen / Mixtral)';
    if (id === 'openai') return 'OpenAI';
    if (id === 'anthropic') return 'Anthropic Claude';
    return id;
  };

  return (
    <header className="top-nav">
      <div className="active-model-badge-container" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div className={`active-model-badge ${activeProvider}`}>
          <Cpu size={16} />
          <span>{getProviderName(activeProvider)} • {activeModel}</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <div className="status-indicator" />
          <span>Vector Memory & DB Ready</span>
        </div>

        {/* User Authentication & Profile Menu */}
        <UserMenu />
      </div>
    </header>
  );
}
