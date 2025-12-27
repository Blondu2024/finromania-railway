import React, { useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

export default function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();
  const { processSession } = useAuth();
  const hasProcessed = useRef(false);

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      const hash = location.hash;
      const sessionIdMatch = hash.match(/session_id=([^&]+)/);
      
      if (sessionIdMatch) {
        const sessionId = sessionIdMatch[1];
        console.log('Processing session:', sessionId);
        
        const result = await processSession(sessionId);
        
        if (result) {
          console.log('Auth successful, redirecting to home');
          // Clear the hash and redirect to home
          window.history.replaceState(null, '', '/');
          // Small delay to ensure state is updated
          setTimeout(() => {
            navigate('/', { replace: true });
          }, 100);
        } else {
          console.log('Auth failed, redirecting to login');
          navigate('/login', { replace: true });
        }
      } else {
        console.log('No session_id found in hash');
        navigate('/', { replace: true });
      }
    };

    processAuth();
  }, [location.hash, processSession, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
        <p className="text-muted-foreground">Se procesează autentificarea...</p>
      </div>
    </div>
  );
}
