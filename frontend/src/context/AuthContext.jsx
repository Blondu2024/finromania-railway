import React, { createContext, useContext, useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const TOKEN_KEY = 'finromania_token';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, [token]);

  const checkAuth = async () => {
    // Try localStorage token first
    const storedToken = localStorage.getItem(TOKEN_KEY);
    
    if (storedToken) {
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${storedToken}` },
          credentials: 'include'
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setToken(storedToken);
          setLoading(false);
          return;
        } else {
          // Token invalid, clear it
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
        }
      } catch (error) {
        console.error('Auth check with token error:', error);
      }
    }
    
    // Fallback to cookie
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/auth/callback';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  const logout = async () => {
    try {
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      await fetch(`${API_URL}/api/auth/logout`, {
        method: 'POST',
        headers,
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      setToken(null);
      setUser(null);
      window.location.href = '/';
    }
  };

  const processSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ session_id: sessionId })
      });
      
      if (response.ok) {
        const data = await response.json();
        // Store token in localStorage for persistence
        if (data.session_token) {
          localStorage.setItem(TOKEN_KEY, data.session_token);
          setToken(data.session_token);
        }
        setUser(data.user || data);
        return data.user || data;
      }
      return null;
    } catch (error) {
      console.error('Session processing error:', error);
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, processSession, checkAuth }}>
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
