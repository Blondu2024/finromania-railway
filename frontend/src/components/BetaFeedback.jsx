import React, { useState, useEffect } from 'react';
import { X, MessageSquare, AlertTriangle, Send, Bug, Lightbulb, HelpCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Banner de disclaimer pentru versiunea BETA
export function BetaDisclaimer() {
  const [dismissed, setDismissed] = useState(false);
  
  useEffect(() => {
    // Check dacă a fost deja închis
    const wasDismissed = localStorage.getItem('beta_disclaimer_dismissed');
    if (wasDismissed) {
      setDismissed(true);
    }
  }, []);
  
  const handleDismiss = () => {
    localStorage.setItem('beta_disclaimer_dismissed', 'true');
    setDismissed(true);
  };
  
  if (dismissed) return null;
  
  return (
    <div className="bg-amber-500 text-amber-950 py-2 px-4">
      <div className="container mx-auto flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2 flex-1">
          <AlertTriangle className="w-4 h-4 flex-shrink-0" />
          <span className="text-sm">
            <strong>Versiune BETA</strong> - Platforma este în dezvoltare activă. 
            Datele pot conține erori. Nu luați decizii financiare bazate exclusiv pe aceste informații.
          </span>
        </div>
        <div className="flex items-center gap-2">
          <a href="mailto:feedback@finromania.ro?subject=Feedback%20FinRomania%20BETA" className="text-amber-950 hover:underline text-sm font-medium">
            Trimite feedback →
          </a>
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-6 w-6 p-0 hover:bg-amber-400"
            onClick={handleDismiss}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

// Badge BETA pentru header
export function BetaBadge() {
  return (
    <Badge 
      variant="outline" 
      className="ml-2 bg-amber-500/10 text-amber-600 border-amber-500/30 text-xs font-bold animate-pulse"
    >
      BETA
    </Badge>
  );
}

// Buton Feedback Floating
export function FeedbackButton() {
  const [isOpen, setIsOpen] = useState(false);
  const [feedbackType, setFeedbackType] = useState('bug');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    setLoading(true);
    
    try {
      // Salvăm feedback-ul în backend
      await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: feedbackType,
          message: message.trim(),
          email: email.trim() || 'anonim',
          page: window.location.pathname,
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
      });
      
      setSubmitted(true);
      setTimeout(() => {
        setIsOpen(false);
        setSubmitted(false);
        setMessage('');
        setEmail('');
      }, 2000);
    } catch (error) {
      // Fallback: deschide email
      const subject = encodeURIComponent(`[${feedbackType.toUpperCase()}] Feedback FinRomania`);
      const body = encodeURIComponent(`Tip: ${feedbackType}\nPagina: ${window.location.href}\n\nMesaj:\n${message}`);
      window.location.href = `mailto:feedback@finromania.ro?subject=${subject}&body=${body}`;
    } finally {
      setLoading(false);
    }
  };

  const feedbackTypes = [
    { id: 'bug', label: 'Bug/Eroare', icon: Bug, color: 'text-red-500' },
    { id: 'idea', label: 'Sugestie', icon: Lightbulb, color: 'text-yellow-500' },
    { id: 'question', label: 'Întrebare', icon: HelpCircle, color: 'text-blue-500' },
  ];

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 group"
        title="Trimite feedback"
      >
        <MessageSquare className="w-6 h-6" />
        <span className="absolute -top-2 -right-2 bg-amber-500 text-amber-950 text-xs font-bold px-2 py-0.5 rounded-full">
          BETA
        </span>
      </button>

      {/* Modal Feedback */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={() => setIsOpen(false)}>
          <Card className="w-full max-w-md" onClick={e => e.stopPropagation()}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                  Feedback BETA
                </CardTitle>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" onClick={() => setIsOpen(false)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-sm text-muted-foreground">
                Ajută-ne să îmbunătățim platforma! Raportează bug-uri sau sugestii.
              </p>
            </CardHeader>
            
            <CardContent>
              {submitted ? (
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-green-600">Mulțumim!</h3>
                  <p className="text-muted-foreground">Feedback-ul tău a fost trimis.</p>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Feedback Type */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Tip feedback</label>
                    <div className="flex gap-2">
                      {feedbackTypes.map(type => (
                        <button
                          key={type.id}
                          type="button"
                          onClick={() => setFeedbackType(type.id)}
                          className={`flex-1 flex flex-col items-center gap-1 p-3 rounded-lg border-2 transition-all ${
                            feedbackType === type.id 
                              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
                              : 'border-border hover:border-blue-300'
                          }`}
                        >
                          <type.icon className={`w-5 h-5 ${type.color}`} />
                          <span className="text-xs">{type.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  {/* Message */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Mesajul tău *</label>
                    <Textarea
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder={
                        feedbackType === 'bug' 
                          ? 'Descrie problema întâmpinată...' 
                          : feedbackType === 'idea'
                          ? 'Care e sugestia ta?'
                          : 'Cu ce te putem ajuta?'
                      }
                      rows={4}
                      required
                    />
                  </div>
                  
                  {/* Email (optional) */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Email (opțional)</label>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="pentru a te contacta cu soluția"
                    />
                  </div>
                  
                  {/* Info despre pagina curentă */}
                  <div className="text-xs text-muted-foreground bg-muted p-2 rounded">
                    📍 Pagina: {window.location.pathname}
                  </div>
                  
                  {/* Submit */}
                  <Button 
                    type="submit" 
                    className="w-full" 
                    disabled={!message.trim() || loading}
                  >
                    {loading ? (
                      'Se trimite...'
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Trimite Feedback
                      </>
                    )}
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}

export default FeedbackButton;
