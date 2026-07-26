import React from 'react';
import { useChat } from './hooks/useChat';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';

export default function App() {
  const {
    providers,
    activeProvider,
    activeModel,
    setActiveModel,
    systemPrompt,
    setSystemPrompt,
    temperature,
    setTemperature,
    maxTokens,
    setMaxTokens,
    messages,
    isStreaming,
    apiKeys,
    handleProviderChange,
    handleApiKeyChange,
    sendMessage,
    stopStreaming,
    clearChat,
  } = useChat();

  return (
    <div className="app-container">
      {/* Sidebar Controls */}
      <Sidebar
        providers={providers}
        activeProvider={activeProvider}
        onProviderChange={handleProviderChange}
        activeModel={activeModel}
        onModelChange={setActiveModel}
        systemPrompt={systemPrompt}
        onSystemPromptChange={setSystemPrompt}
        temperature={temperature}
        onTemperatureChange={setTemperature}
        maxTokens={maxTokens}
        onMaxTokensChange={setMaxTokens}
        onClearChat={clearChat}
      />

      {/* Main Workspace Area */}
      <main className="main-chat-area">
        <Header activeProvider={activeProvider} activeModel={activeModel} />
        <ChatWindow messages={messages} onSelectSuggestion={sendMessage} />
        <ChatInput
          onSendMessage={sendMessage}
          isStreaming={isStreaming}
          onStopStreaming={stopStreaming}
        />
      </main>
    </div>
  );
}
