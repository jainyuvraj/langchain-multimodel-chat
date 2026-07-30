import React, { createContext, useContext, useState, useEffect } from 'react';
import { guestLogin, fetchMe, API_BASE_URL } from '../services/api';

const AuthContext = createContext();

const DEFAULT_GUEST_USER = {
  id: 'guest_dev_id',
  email: 'guest@polymodel.ai',
  name: 'Guest Developer',
  provider: 'guest',
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(DEFAULT_GUEST_USER);
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'));
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      // 1. Check for token in URL from Google OAuth redirect
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      
      let effectiveToken = urlToken || localStorage.getItem('auth_token');

      if (urlToken) {
        localStorage.setItem('auth_token', urlToken);
        setToken(urlToken);
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      // 2. If a saved token exists, attempt verification
      if (effectiveToken) {
        try {
          const res = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${effectiveToken}`
            }
          });
          if (res.ok) {
            const userData = await res.json();
            setUser(userData);
            setToken(effectiveToken);
            return;
          } else if (res.status === 401 || res.status === 403) {
            // Token is expired/invalid -> Clear it
            console.warn('Auth token expired or invalid.');
            localStorage.removeItem('auth_token');
            setToken(null);
          } else {
            // Server error or warming up (500, 502, 503) -> DO NOT erase saved token!
            console.warn('Backend server returned temporary error status:', res.status);
            setToken(effectiveToken);
            return;
          }
        } catch (e) {
          // Network error or server cold start -> Preserve saved token!
          console.warn('Network error verifying token, retaining saved token:', e);
          setToken(effectiveToken);
          return;
        }
      }

      // 3. Only fallback to Guest Login if NO user token exists
      try {
        const res = await guestLogin('Guest Developer');
        localStorage.setItem('auth_token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
      } catch (err) {
        setUser(DEFAULT_GUEST_USER);
      }
    };

    initAuth();
  }, []);

  const handleGuestLogin = async (name = 'Guest Developer') => {
    try {
      const res = await guestLogin(name);
      localStorage.setItem('auth_token', res.access_token);
      setToken(res.access_token);
      setUser(res.user);
    } catch (err) {
      console.warn('Failed to perform guest login:', err);
      setUser({ ...DEFAULT_GUEST_USER, name });
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(DEFAULT_GUEST_USER);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAuthModalOpen,
        setIsAuthModalOpen,
        handleGuestLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    return {
      user: DEFAULT_GUEST_USER,
      token: null,
      loading: false,
      isAuthModalOpen: false,
      setIsAuthModalOpen: () => {},
      handleGuestLogin: () => {},
      logout: () => {},
    };
  }
  return context;
}
