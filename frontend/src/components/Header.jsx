import React from 'react';
import { Cpu, ShieldCheck, UserCheck } from 'lucide-react';

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

      {/* Modular Header Action & OAuth Placeholder */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <div className="status-indicator" />
          <span>LangChain Engine Ready</span>
        </div>

        {/* Placeholder OAuth Login Button */}
        <button 
          className="btn-secondary" 
          style={{ padding: '6px 12px', fontSize: '0.8rem', borderRadius: '999px' }}
          onClick={() => alert("OAuth Integration Placeholder: Google / GitHub Login ready to connect in backend/routers/auth.py")}
          title="Modular OAuth Integration Hook"
        >
          <UserCheck size={14} />
          <span>Sign In (OAuth Ready)</span>
        </button>
      </div>
    </header>
  );
}
