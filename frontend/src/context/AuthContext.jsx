/**
 * Auth Context
 * ─────────────
 * Global authentication state management.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../utils/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const { ok, data } = await api.getMe();
      if (ok) {
        setUser(data);
      } else {
        api.clearTokens();
      }
    } catch {
      api.clearTokens();
    }
    setLoading(false);
  }

  async function login(email, password) {
    const result = await api.login(email, password);
    if (result.ok) {
      const { tokens, user: userData } = result.data;
      api.setTokens(tokens.access_token, tokens.refresh_token);
      setUser(userData);
    }
    return result;
  }

  async function register(email, username, password) {
    const result = await api.register(email, username, password);
    if (result.ok) {
      const { tokens, user: userData } = result.data;
      api.setTokens(tokens.access_token, tokens.refresh_token);
      setUser(userData);
    }
    return result;
  }

  function logout() {
    api.clearTokens();
    setUser(null);
  }

  const value = { user, loading, login, register, logout, isAuthenticated: !!user };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
