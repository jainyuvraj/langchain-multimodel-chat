import React from 'react';
import { 
  Sparkles, Zap, Bot, Brain, Sliders, Trash2, 
  Layers, Settings 
} from 'lucide-react';

export function Sidebar({
  providers,
  activeProvider,
  onProviderChange,
  activeModel,
  onModelChange,
  systemPrompt,
  onSystemPromptChange,
  temperature,
  onTemperatureChange,
  maxTokens,
  onMaxTokensChange,
  enableInterChatMemory,
  onEnableInterChatMemoryChange,
  onClearChat,
}) {
  // Fallback models if providers api is loading
  const currentProviderObj = providers.find((p) => p.id === activeProvider);
  const availableModels = currentProviderObj ? currentProviderObj.models : [
    { id: activeModel, name: activeModel, description: '' }
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="logo-group">
          <div className="logo-icon">
            <Sparkles size={20} />
          </div>
          <span className="logo-text">LangChain101 AI</span>
        </div>
      </div>

      {/* Control Settings */}
      <div className="sidebar-content">
        {/* Model Provider Tabs */}
        <div>
          <div className="section-title">
            <Layers size={14} />
            <span>LLM Provider</span>
          </div>
          <div className="provider-pills">
            <button
              className={`provider-pill ${activeProvider === 'google' ? 'active google' : ''}`}
              onClick={() => onProviderChange('google')}
            >
              <Sparkles size={16} />
              <span>Gemini</span>
            </button>

            <button
              className={`provider-pill ${activeProvider === 'groq' ? 'active groq' : ''}`}
              onClick={() => onProviderChange('groq')}
            >
              <Zap size={16} />
              <span>Open Models</span>
            </button>

            {/* <button
              className={`provider-pill ${activeProvider === 'openai' ? 'active openai' : ''}`}
              onClick={() => onProviderChange('openai')}
            >
              <Bot size={16} />
              <span>OpenAI</span>
            </button>

            <button
              className={`provider-pill ${activeProvider === 'anthropic' ? 'active anthropic' : ''}`}
              onClick={() => onProviderChange('anthropic')}
            >
              <Brain size={16} />
              <span>Claude</span>
            </button>*/}
          </div>
        </div> 

        {/* Specific Model Dropdown */}
        <div>
          <div className="section-title">
            <Settings size={14} />
            <span>Select Model</span>
          </div>
          <select
            className="custom-select"
            value={activeModel}
            onChange={(e) => onModelChange(e.target.value)}
          >
            {availableModels.map((m) => (
              <option key={m.id} value={m.id}>
                {m.name} {m.recommended ? '⭐ (Recommended)' : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Temperature & Max Tokens Sliders */}
        <div className="slider-group">
          <div className="section-title">
            <Sliders size={14} />
            <span>Parameters</span>
          </div>

          <div className="slider-header">
            <span>Temperature</span>
            <span>{temperature}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            className="custom-slider"
            value={temperature}
            onChange={(e) => onTemperatureChange(parseFloat(e.target.value))}
          />

          <div className="slider-header" style={{ marginTop: '12px' }}>
            <span>Max Tokens</span>
            <span>{maxTokens}</span>
          </div>
          <input
            type="range"
            min="256"
            max="8192"
            step="256"
            className="custom-slider"
            value={maxTokens}
            onChange={(e) => onMaxTokensChange(parseInt(e.target.value, 10))}
          />

          {/* Cross-Thread Vector Memory Toggle */}
          <div style={{ marginTop: '16px', background: 'var(--bg-secondary)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.82rem', fontWeight: '600', color: 'var(--text-primary)' }}>Cross-Thread Memory</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  {enableInterChatMemory ? 'ON (All User Threads)' : 'OFF (Current Chat Only)'}
                </span>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={enableInterChatMemory}
                  onChange={(e) => onEnableInterChatMemoryChange(e.target.checked)}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        {/* System Prompt Customizer */}
        <div>
          <div className="section-title">System Prompt</div>
          <textarea
            className="custom-textarea"
            value={systemPrompt}
            onChange={(e) => onSystemPromptChange(e.target.value)}
            placeholder="Instruct how the AI assistant should behave..."
          />
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="sidebar-footer">
        <button className="btn-secondary" onClick={onClearChat}>
          <Trash2 size={16} />
          <span>Clear Conversation</span>
        </button>
      </div>
    </aside>
  );
}
