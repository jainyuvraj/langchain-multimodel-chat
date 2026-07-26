import { useState, useEffect, useRef } from 'react';
import { fetchProviders, streamChatCompletion } from '../services/api';

const DEFAULT_SYSTEM_PROMPT = "You are a helpful, creative, and precise AI assistant.";

export function useChat() {
  const [providers, setProviders] = useState([]);
  const [activeProvider, setActiveProvider] = useState('google');
  const [activeModel, setActiveModel] = useState('gemini-flash-latest');
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_SYSTEM_PROMPT);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [apiKeys, setApiKeys] = useState(() => {
    const saved = localStorage.getItem('chat_api_keys');
    return saved ? JSON.parse(saved) : { google: '', openai: '', anthropic: '' };
  });

  const abortControllerRef = useRef(null);

  // Fetch providers on initial mount
  useEffect(() => {
    fetchProviders()
      .then((data) => {
        setProviders(data);
      })
      .catch((err) => {
        console.warn('Backend not available yet, using fallback provider list.');
      });
  }, []);

  // Save API keys to localStorage
  useEffect(() => {
    localStorage.setItem('chat_api_keys', JSON.stringify(apiKeys));
  }, [apiKeys]);

  // Update active model when provider changes
  const handleProviderChange = (providerId) => {
    setActiveProvider(providerId);
    const providerObj = providers.find((p) => p.id === providerId);
    if (providerObj && providerObj.models.length > 0) {
      setActiveModel(providerObj.models[0].id);
    } else {
      if (providerId === 'google') setActiveModel('gemini-flash-latest');
      else if (providerId === 'openai') setActiveModel('gpt-4o');
      else if (providerId === 'anthropic') setActiveModel('claude-3-5-sonnet-20240620');
    }
  };

  const handleApiKeyChange = (provider, key) => {
    setApiKeys((prev) => ({ ...prev, [provider]: key }));
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

    // Placeholder for streaming assistant response
    const assistantMessage = { role: 'assistant', content: '', provider: activeProvider, model: activeModel };
    
    setMessages([...updatedMessages, assistantMessage]);
    setIsStreaming(true);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    const payload = {
      provider: activeProvider,
      model: activeModel,
      messages: updatedMessages,
      system_prompt: systemPrompt,
      temperature,
      max_tokens: maxTokens,
      api_keys: apiKeys,
    };

    let accumulatedText = '';

    await streamChatCompletion(
      payload,
      (token) => {
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
    messages,
    isStreaming,
    apiKeys,
    handleProviderChange,
    handleApiKeyChange,
    sendMessage,
    stopStreaming,
    clearChat,
  };
}
