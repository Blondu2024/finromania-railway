import React from 'react';
import { Star, Plus, Check } from 'lucide-react';
import { Button } from './ui/button';
import { useAuth } from '../context/AuthContext';
import { useState } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AddToWatchlistButton({ symbol, type, name, onAdd }) {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [added, setAdded] = useState(false);

  const handleAdd = async () => {
    if (!user) {
      window.location.href = '/login';
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/watchlist`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        credentials: 'include',
        body: JSON.stringify({ symbol, type, name })
      });

      if (res.ok) {
        setAdded(true);
        onAdd?.();
        setTimeout(() => setAdded(false), 2000);
      } else if (res.status === 400) {
        setAdded(true); // Already in watchlist
      } else {
        const error = await res.json();
        console.error('Watchlist error:', error);
      }
    } catch (error) {
      console.error('Error adding to watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleAdd}
      disabled={loading || added}
      className={added ? 'bg-yellow-50 border-yellow-300' : ''}
    >
      {added ? (
        <><Check className="w-4 h-4 mr-1 text-green-600" /> Adăugat</>
      ) : (
        <><Star className="w-4 h-4 mr-1" /> Watchlist</>
      )}
    </Button>
  );
}
