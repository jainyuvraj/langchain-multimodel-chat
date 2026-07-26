/**
 * Modular API Service Layer for LangChain Multi-Model Chatbot.
 * Modularized for future Database & OAuth token additions.
 */

const API_BASE_URL = '/api';

/**
 * Fetch available model providers and sub-models from backend.
 */
export async function fetchProviders() {
  try {
    const response = await fetch(`${API_BASE_URL}/models/providers`);
    if (!response.ok) {
      throw new Error(`Failed to fetch providers (Status ${response.status})`);
    }
    return await response.json();
  } catch (error) {
    console.error('API Error in fetchProviders:', error);
    throw error;
  }
}

/**
 * Stream chat completions using Server-Sent Events (SSE).
 * @param {Object} payload Chat request parameters
 * @param {Function} onToken Callback for each received stream token
 * @param {Function} onError Callback for errors
 * @param {Function} onComplete Callback when stream finishes
 * @param {AbortSignal} signal AbortController signal
 */
export async function streamChatCompletion(payload, onToken, onError, onComplete, signal) {
  try {
    // Modular Auth Header Hook (for future OAuth JWT tokens)
    const authToken = localStorage.getItem('auth_token');
    const headers = {
      'Content-Type': 'application/json',
      ...(authToken ? { Authorization: `Bearer ${authToken}` } : {}),
    };

    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server returned error status ${response.status}: ${errorText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Keep incomplete trailing line in buffer

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
              onToken(tokenStr);
            }
          }
        } catch (e) {
          console.warn('Failed to parse SSE JSON line:', dataStr);
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
