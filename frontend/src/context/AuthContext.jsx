import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { signInWithGoogle, firebaseSignOut } from '../config/firebase';

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
    const storedUser = localStorage.getItem(USER_KEY);
    
    console.log('[Auth] Checking auth, stored token:', storedToken ? 'exists' : 'none');
    
    if (storedToken && storedUser) {
      try {
        // Verify token is still valid
        const response = await fetch(`${API_URL}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${storedToken}` }
        });
        
        console.log('[Auth] /me response status:', response.status);
        
        if (response.ok) {
          const userData = await response.json();
          console.log('[Auth] User authenticated:', userData.name || userData.email);
          setUser(userData);
          setToken(storedToken);
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
        } else {
          console.log('[Auth] Token invalid, clearing...');
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
          setToken(null);
          setUser(null);
        }
      } catch (error) {
        console.error('[Auth] Error checking auth:', error);
        // Keep user logged in even if verification fails (offline mode)
        try {
          const userData = JSON.parse(storedUser);
          setUser(userData);
          setToken(storedToken);
          console.log('[Auth] Using cached user data');
        } catch (e) {
          console.error('[Auth] Failed to parse stored user:', e);
          localStorage.removeItem(TOKEN_KEY);
          localStorage.removeItem(USER_KEY);
          setToken(null);
          setUser(null);
        }
      }
    }
    
    setLoading(false);
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // OLD Emergent login - kept as fallback
  const loginEmergent = () => {
    const redirectUrl = window.location.origin + '/auth/callback';
    console.log('[Auth] Redirecting to Emergent login with callback:', redirectUrl);
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
  };

  // NEW Firebase Google login
  const login = async () => {
    console.log('[Auth] Starting Firebase Google login...');
    setLoading(true);
    
    try {
      const result = await signInWithGoogle();
      
      if (result.success) {
        console.log('[Auth] Firebase login successful, sending to backend...');
        
        // Send to our backend to create/update user and get session
        const response = await fetch(`${API_URL}/api/auth/firebase/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id_token: result.idToken,
            user_info: result.user
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          console.log('[Auth] Backend login successful:', data.email);
          
          // Save token and user
          localStorage.setItem(TOKEN_KEY, data.session_token);
          setToken(data.session_token);
          
          const userData = {
            user_id: data.user_id,
            email: data.email,
            name: data.name,
            picture: data.picture
          };
          
          localStorage.setItem(USER_KEY, JSON.stringify(userData));
          setUser(userData);
          
          return userData;
        } else {
          const error = await response.json();
          console.error('[Auth] Backend login error:', error);
          alert('Eroare la autentificare. Încearcă din nou.');
        }
      } else {
        console.error('[Auth] Firebase login failed:', result.error);
        // Don't show error for user cancellation
        if (!result.error?.includes('popup-closed')) {
          alert('Nu s-a putut realiza conectarea. Încearcă din nou.');
        }
      }
    } catch (error) {
      console.error('[Auth] Login error:', error);
      alert('Eroare la conectare. Verifică conexiunea la internet.');
    } finally {
      setLoading(false);
    }
    
    return null;
  };

  const logout = async () => {
    try {
      // Sign out from Firebase
      await firebaseSignOut();
      
      // Sign out from backend
      if (token) {
        await fetch(`${API_URL}/api/auth/firebase/logout`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
      }
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

  // Process Emergent session (kept for backwards compatibility)
  const processSession = async (sessionId) => {
    console.log('[Auth] Processing Emergent session:', sessionId.substring(0, 10) + '...');
    try {
      const response = await fetch(`${API_URL}/api/auth/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
        
        const sessionToken = data.session_token;
        
        if (sessionToken) {
          console.log('[Auth] Saving token to localStorage');
          localStorage.setItem(TOKEN_KEY, sessionToken);
          setToken(sessionToken);
        } else {
          console.error('[Auth] No session_token in response!');
        }
        
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
    <AuthContext.Provider value={{ 
      user, 
      token, 
      loading, 
      login,           // Firebase Google login
      loginEmergent,   // Old Emergent login (backup)
      logout, 
      processSession, 
      checkAuth 
    }}>
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
