import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { useChat } from './hooks/useChat';
import { Sidebar } from './components/Sidebar';
import { ChatHistorySidebar } from './components/ChatHistorySidebar';
import { Header } from './components/Header';
import { ChatWindow } from './components/ChatWindow';
import { ChatInput } from './components/ChatInput';
import { AuthModal } from './components/AuthModal';

function MainApp() {
  const { isAuthModalOpen, setIsAuthModalOpen } = useAuth();
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
    enableInterChatMemory,
    setEnableInterChatMemory,
    sessions,
    activeChatId,
    messages,
    isStreaming,
    handleProviderChange,
    selectChat,
    handleNewChat,
    handleDeleteChat,
    sendMessage,
    stopStreaming,
    clearChat,
  } = useChat();

  return (
    <div className="app-container">
      {/* Saved Chat Threads Sidebar */}
      <ChatHistorySidebar
        sessions={sessions}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      {/* Model Controls Sidebar */}
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
        enableInterChatMemory={enableInterChatMemory}
        onEnableInterChatMemoryChange={setEnableInterChatMemory}
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

      {/* User Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
      />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
