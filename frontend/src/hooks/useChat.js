import { useState, useEffect, useRef } from 'react';
import { 
  fetchProviders, streamChatCompletion, 
  fetchSessions, createSession, deleteSession, fetchSessionMessages 
} from '../services/api';
import { useAuth } from '../context/AuthContext';

const DEFAULT_SYSTEM_PROMPT = "You are a helpful, creative, and precise AI assistant.";

export function useChat() {
  const { user } = useAuth();
  const [providers, setProviders] = useState([]);
  const [activeProvider, setActiveProvider] = useState('google');
  const [activeModel, setActiveModel] = useState('gemini-flash-latest');
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [enableInterChatMemory, setEnableInterChatMemory] = useState(false);

  const [sessions, setSessions] = useState([]);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);

  const abortControllerRef = useRef(null);

  // Fetch providers and user sessions
  useEffect(() => {
    fetchProviders().then(setProviders).catch(() => {});
  }, []);

  useEffect(() => {
    if (user) {
      loadSessions();
    }
  }, [user]);

  const loadSessions = async () => {
    try {
      const list = await fetchSessions();
      if (Array.isArray(list)) {
        setSessions(list);
        if (list.length > 0 && !activeChatId) {
          selectChat(list[0].id);
        }
      } else {
        setSessions([]);
      }
    } catch (e) {
      console.warn('Failed to load user chat sessions:', e);
      setSessions([]);
    }
  };

  const selectChat = async (chatId) => {
    if (!chatId) return;
    setActiveChatId(chatId);
    try {
      const history = await fetchSessionMessages(chatId);
      if (Array.isArray(history)) {
        setMessages(history.map(m => ({ role: m.role, content: m.content })));
      } else {
        setMessages([]);
      }
    } catch (e) {
      console.warn(`Failed to fetch messages for chat ${chatId}:`, e);
      setMessages([]);
    }
  };

  const handleNewChat = async () => {
    try {
      const newSession = await createSession('New Conversation', activeProvider, activeModel);
      setSessions(prev => [newSession, ...prev]);
      setActiveChatId(newSession.id);
      setMessages([]);
    } catch (e) {
      console.error('Failed to create new chat session:', e);
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await deleteSession(chatId);
      const remaining = sessions.filter(s => s.id !== chatId);
      setSessions(remaining);
      if (activeChatId === chatId) {
        if (remaining.length > 0) {
          selectChat(remaining[0].id);
        } else {
          setActiveChatId(null);
          setMessages([]);
        }
      }
    } catch (e) {
      console.error('Failed to delete chat session:', e);
    }
  };

  const handleProviderChange = (providerId) => {
    setActiveProvider(providerId);
    const providerObj = providers.find((p) => p.id === providerId);
    if (providerObj && providerObj.models.length > 0) {
      setActiveModel(providerObj.models[0].id);
    } else {
      if (providerId === 'google') setActiveModel('gemini-flash-latest');
      else if (providerId === 'groq') setActiveModel('llama-3.3-70b-versatile');
      else if (providerId === 'openai') setActiveModel('gpt-4o');
      else if (providerId === 'anthropic') setActiveModel('claude-3-5-sonnet-20240620');
    }
  };

  const clearChat = () => {
    if (isStreaming && abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setMessages([]);
    setIsStreaming(false);
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  const sendMessage = async (userText) => {
    if (!userText || !userText.trim() || isStreaming) return;

    const userMessage = { role: 'user', content: userText.trim() };
    const updatedMessages = [...messages, userMessage];

    const assistantMessage = { 
      role: 'assistant', 
      content: '', 
      provider: activeProvider, 
      model: activeModel 
    };
    
    setMessages([...updatedMessages, assistantMessage]);
    setIsStreaming(true);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const payload = {
      chat_id: activeChatId,
      provider: activeProvider,
      model: activeModel,
      messages: updatedMessages,
      system_prompt: systemPrompt,
      temperature,
      max_tokens: maxTokens,
      enable_inter_chat_memory: enableInterChatMemory,
    };

    let accumulatedText = '';

    await streamChatCompletion(
      payload,
      (token, chatIdFromBackend) => {
        if (chatIdFromBackend && chatIdFromBackend !== activeChatId) {
          setActiveChatId(chatIdFromBackend);
        }

        accumulatedText += token;
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = { ...next[lastIdx], content: accumulatedText };
          }
          return next;
        });
      },
      (errorMsg) => {
        setIsStreaming(false);
        setMessages((prev) => {
          const next = [...prev];
          const lastIdx = next.length - 1;
          if (lastIdx >= 0 && next[lastIdx].role === 'assistant') {
            next[lastIdx] = {
              ...next[lastIdx],
              content: accumulatedText ? `${accumulatedText}\n\n[⚠️ Stream Error: ${errorMsg}]` : `⚠️ ${errorMsg}`,
              isError: true,
            };
          }
          return next;
        });
      },
      () => {
        setIsStreaming(false);
        loadSessions(); // Refresh session titles/timestamps
      },
      abortController.signal
    );
  };

  return {
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
  };
}
