import React, { useState } from 'react';
import { Mail, Check, Loader2 } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function NewsletterSignup({ variant = 'inline' }) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    try {
      const res = await fetch(`${API_URL}/api/newsletter/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await res.json();
      
      if (res.ok) {
        setStatus('success');
        setMessage(data.message || 'Te-ai abonat cu succes!');
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.detail || 'A apărut o eroare');
      }
    } catch (error) {
      setStatus('error');
      setMessage('Nu s-a putut efectua abonarea');
    }

    // Reset after 3 seconds
    setTimeout(() => {
      setStatus('idle');
      setMessage('');
    }, 3000);
  };

  if (variant === 'card') {
    return (
      <Card className="bg-gradient-to-r from-blue-600 to-blue-700 text-white">
        <CardContent className="p-6">
          <div className="flex items-center gap-2 mb-2">
            <Mail className="w-5 h-5" />
            <h3 className="font-semibold">Newsletter FinRomania</h3>
          </div>
          <p className="text-sm text-blue-100 mb-4">
            Primește seara mesajul tău personal cu cele mai importante știri financiare.
          </p>
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              type="email"
              placeholder="Email-ul tău"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="bg-white/10 border-white/20 text-white placeholder:text-blue-200"
              disabled={status === 'loading' || status === 'success'}
            />
            <Button 
              type="submit" 
              variant="secondary"
              disabled={status === 'loading' || status === 'success'}
            >
              {status === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
              {status === 'success' && <Check className="w-4 h-4" />}
              {status === 'idle' && 'Abonează-te'}
              {status === 'error' && 'Reîncearcă'}
            </Button>
          </form>
          {message && (
            <p className={`text-sm mt-2 ${status === 'success' ? 'text-green-200' : 'text-red-200'}`}>
              {message}
            </p>
          )}
        </CardContent>
      </Card>
    );
  }

  // Inline variant
  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="email"
        placeholder="Abonează-te la newsletter"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-48"
        disabled={status === 'loading' || status === 'success'}
      />
      <Button type="submit" size="sm" disabled={status === 'loading' || status === 'success'}>
        {status === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
        {status === 'success' && <Check className="w-4 h-4" />}
        {(status === 'idle' || status === 'error') && <Mail className="w-4 h-4" />}
      </Button>
    </form>
  );
}
