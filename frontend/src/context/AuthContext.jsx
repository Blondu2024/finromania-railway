import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const TOKEN_KEY = 'finromania_token';
const USER_KEY = 'finromania_user';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem(USER_KEY);
    return savedUser ? JSON.parse(savedUser) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    console.log('[Auth] Checking auth, stored token:', storedToken ? 'exists' : 'none');
    
    if (storedToken) {
      try {
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${storedToken}` },
          credentials: 'include'
        });
        
        console.log('[Auth] /me response status:', response.status);
        
        if (response.ok) {
          const userData = await response.json();
          console.log('[Auth] User data received:', userData.name || userData.email);
          setUser(userData);
          setToken(storedToken);
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
          setLoading(false);
          return;
        } else {
          console.log('[Auth] Token invalid, clearing...');
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
          setToken(null);
          setUser(null);
        }
      } catch (error) {
        console.error('[Auth] Error checking auth:', error);
      }
    }
    
    // Fallback to cookie
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        credentials: 'include'
      });
      
      if (response.ok) {
        const userData = await response.json();
        console.log('[Auth] Cookie auth successful:', userData.name || userData.email);
        setUser(userData);
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
      } else {
        setUser(null);
        localStorage.removeItem(USER_KEY);
      }
    } catch (error) {
      console.error('[Auth] Cookie auth error:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = () => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    const redirectUrl = window.location.origin + '/auth/callback';
    console.log('[Auth] Redirecting to login with callback:', redirectUrl);
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
      console.error('[Auth] Logout error:', error);
    } finally {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setToken(null);
      setUser(null);
      window.location.href = '/';
    }
  };

  const processSession = async (sessionId) => {
    console.log('[Auth] Processing session:', sessionId.substring(0, 10) + '...');
    try {
      const response = await fetch(`${API_URL}/api/auth/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ session_id: sessionId })
      });
      
      console.log('[Auth] Session response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('[Auth] Session data:', {
          hasToken: !!data.session_token,
          hasUser: !!(data.user_id || data.email),
          userName: data.name || data.email
        });
        
        // The response IS the user object with session_token added
        const sessionToken = data.session_token;
        
        if (sessionToken) {
          console.log('[Auth] Saving token to localStorage');
          localStorage.setItem(TOKEN_KEY, sessionToken);
          setToken(sessionToken);
        } else {
          console.error('[Auth] No session_token in response!');
        }
        
        // Remove session_token from user object before saving
        const { session_token, ...userData } = data;
        
        console.log('[Auth] Saving user to state and localStorage');
        localStorage.setItem(USER_KEY, JSON.stringify(userData));
        setUser(userData);
        
        return userData;
      } else {
        const errorText = await response.text();
        console.error('[Auth] Session error:', errorText);
      }
      return null;
    } catch (error) {
      console.error('[Auth] Session processing error:', error);
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
