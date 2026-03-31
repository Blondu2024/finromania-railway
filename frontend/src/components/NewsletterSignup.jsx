import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Mail, Check, Loader2 } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function NewsletterSignup({ variant = 'inline' }) {
  const { t } = useTranslation();
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
        setMessage(data.message || t('newsletter.success'));
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.detail || t('newsletter.error'));
      }
    } catch (error) {
      setStatus('error');
      setMessage(t('newsletter.failed'));
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
            <h3 className="font-semibold">{t('newsletter.title')}</h3>
          </div>
          <p className="text-sm text-blue-100 mb-4">
            {t('newsletter.description')}
          </p>
          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              type="email"
              placeholder={t('newsletter.emailPlaceholder')}
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
              {status === 'idle' && t('newsletter.subscribe')}
              {status === 'error' && t('newsletter.retry')}
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
        placeholder={t('newsletter.subscribePlaceholder')}
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
