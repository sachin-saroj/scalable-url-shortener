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
    try {
      const { ok, data } = await api.getMe();
      if (ok) {
        setUser(data);
      }
    } catch {
      // Ignored, user is not logged in
    }
    setLoading(false);
  }

  async function login(email, password) {
    const result = await api.login(email, password);
    if (result.ok) {
      const { user: userData } = result.data;
      setUser(userData);
    }
    return result;
  }

  async function register(email, username, password) {
    const result = await api.register(email, username, password);
    if (result.ok) {
      const { user: userData } = result.data;
      setUser(userData);
    }
    return result;
  }

  async function logout() {
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout failed:', err);
    }
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
