import React, { createContext, useContext, useState, useEffect } from 'react';
import { guestLogin, fetchMe } from '../services/api';

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
      // Check for token from OAuth redirect query param
      const urlParams = new URLSearchParams(window.location.search);
      const urlToken = urlParams.get('token');
      if (urlToken) {
        localStorage.setItem('auth_token', urlToken);
        setToken(urlToken);
        window.history.replaceState({}, document.title, window.location.pathname);
      }

      const savedToken = localStorage.getItem('auth_token');
      if (savedToken) {
        try {
          const userData = await fetchMe();
          setUser(userData);
          return;
        } catch (e) {
          console.warn('Saved auth token invalid, attempting guest login...');
        }
      }

      // Guest Login Fallback
      try {
        const res = await guestLogin('Guest Developer');
        localStorage.setItem('auth_token', res.access_token);
        setToken(res.access_token);
        setUser(res.user);
      } catch (err) {
        console.warn('Backend offline, using default offline guest session.');
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
