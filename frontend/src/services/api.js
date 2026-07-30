/**
 * Modular API Service Layer for LangChain Multi-Model Chatbot.
 * Handles SSE streaming, JWT authentication, and Chat Session persistence.
 */

const API_BASE_URL = '/api';

function getAuthHeaders() {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/**
 * Guest Login API
 */
export async function guestLogin(name = 'Guest Developer') {
  const res = await fetch(`${API_BASE_URL}/auth/guest-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error('Guest login failed');
  return await res.json();
}

/**
 * Fetch current authenticated user profile
 */
export async function fetchMe() {
  const res = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch user profile');
  return await res.json();
}

/**
 * Fetch list of user chat sessions (chatID threads)
 */
export async function fetchSessions() {
  const res = await fetch(`${API_BASE_URL}/sessions`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch sessions');
  return await res.json();
}

/**
 * Create a new chat session
 */
export async function createSession(title = 'New Conversation', provider = 'google', model = 'gemini-flash-latest') {
  const res = await fetch(`${API_BASE_URL}/sessions`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title, provider, model }),
  });
  if (!res.ok) throw new Error('Failed to create session');
  return await res.json();
}

/**
 * Fetch message history for a specific chatID
 */
export async function fetchSessionMessages(chatId) {
  const res = await fetch(`${API_BASE_URL}/sessions/${chatId}/messages`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to fetch session messages');
  return await res.json();
}

/**
 * Delete a chat session
 */
export async function deleteSession(chatId) {
  const res = await fetch(`${API_BASE_URL}/sessions/${chatId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error('Failed to delete session');
  return await res.json();
}

/**
 * Fetch available model providers and sub-models from backend
 */
export async function fetchProviders() {
  const response = await fetch(`${API_BASE_URL}/models/providers`);
  if (!response.ok) throw new Error('Failed to fetch providers');
  return await response.json();
}

/**
 * Stream chat completions using Server-Sent Events (SSE).
 */
export async function streamChatCompletion(payload, onToken, onError, onComplete, signal) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server returned error ${response.status}: ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data: ')) continue;

        const dataStr = trimmed.slice(6);
        if (dataStr === '[DONE]') {
          onComplete && onComplete();
          return;
        }

        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.token) {
            let tokenStr = '';
            if (typeof parsed.token === 'string') {
              tokenStr = parsed.token;
            } else if (Array.isArray(parsed.token)) {
              tokenStr = parsed.token.map(t => typeof t === 'string' ? t : (t.text || '')).join('');
            } else if (typeof parsed.token === 'object') {
              tokenStr = parsed.token.text || parsed.token.content || JSON.stringify(parsed.token);
            }
            if (tokenStr) {
              onToken(tokenStr, parsed.chat_id);
            }
          }
        } catch (e) {
          console.warn('Failed to parse SSE JSON:', dataStr);
        }
      }
    }
    onComplete && onComplete();
  } catch (err) {
    if (err.name === 'AbortError') {
      console.log('Stream aborted by user.');
    } else {
      console.error('Stream error:', err);
      onError && onError(err.message || 'Stream connection failed.');
    }
  }
}
