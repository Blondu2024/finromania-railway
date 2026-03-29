import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, HelpCircle, Loader2, Lock, Crown, MessageCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Quick answers pentru afișare inițială
const QUICK_ANSWERS = [
  { q: "Cât e impozitul pe BVB?", a: "3% pentru deținere ≥1 an, 6% pentru <1 an (2026)" },
  { q: "Trebuie Declarația Unică?", a: "DA pentru international, NU pentru BVB" },
  { q: "Ce e W-8BEN?", a: "Formular SUA - reduce impozitul de la 30% la 15%" },
  { q: "Când datorez CASS?", a: "Venit investiții > 24.300 RON/an (inclusiv cu salariu)" },
];

const SUGGESTED_QUESTIONS = [
  "Cum completez Declarația Unică?",
  "Ce documente am nevoie de la broker?",
  "Pot compensa pierderile cu câștigurile?",
  "Care e diferența între BVB și Trading 212 fiscal?",
  "Trebuie să declar ETF-urile?",
];

const FiscalAIChat = ({ compact = false }) => {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(!compact);
  const [queriesInfo, setQueriesInfo] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e, questionOverride = null) => {
    e?.preventDefault();
    const question = questionOverride || input.trim();
    if (!question || loading) return;

    if (!user || !token) {
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'Trebuie să fii autentificat pentru a folosi AI Fiscal Advisor.',
        isError: true
      }]);
      return;
    }

    const userMessage = {
      role: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/ai-fiscal/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          question: question,
          session_id: sessionId
        })
      });

      const data = await response.json();

      if (!data.success) {
        if (data.error === 'limit_reached') {
          setMessages(prev => [...prev, {
            role: 'system',
            content: data.message,
            isLimitReached: true,
            upgradeMessage: data.upgrade_message
          }]);
        } else {
          throw new Error(data.message || 'Eroare la procesare');
        }
      } else {
        setSessionId(data.session_id);
        setQueriesInfo(data.queries_info);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          disclaimer: data.disclaimer,
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'A apărut o eroare. Te rog să încerci din nou.',
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (question) => {
    handleSubmit(null, question);
  };

  // Compact mode - just a button to expand
  if (compact && !isExpanded) {
    return (
      <Card 
        className="bg-gradient-to-r from-blue-700 to-blue-500 text-white cursor-pointer hover:shadow-lg transition-all"
        onClick={() => setIsExpanded(true)}
      >
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <MessageCircle className="w-6 h-6" />
              </div>
              <div>
                <p className="font-semibold">Întrebări despre fiscalitate?</p>
                <p className="text-sm text-white/80">Întreabă AI-ul nostru fiscal</p>
              </div>
            </div>
            <ChevronDown className="w-5 h-5" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-zinc-900 border-zinc-700 flex flex-col h-[500px]">
      {/* Header */}
      <CardHeader className="border-b border-zinc-700 pb-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Bot className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <CardTitle className="text-white text-base">AI Fiscal Advisor</CardTitle>
              <p className="text-xs text-gray-400">Întrebări despre impozite la bursă</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {queriesInfo && !queriesInfo.is_unlimited && (
              <Badge variant="outline" className={`text-xs ${queriesInfo.remaining <= 1 ? 'border-red-500 text-red-400' : 'border-gray-600 text-gray-400'}`}>
                {queriesInfo.remaining}/5 întrebări
              </Badge>
            )}
            {compact && (
              <Button variant="ghost" size="sm" onClick={() => setIsExpanded(false)}>
                <ChevronUp className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 ? (
          <div className="space-y-4">
            {/* Quick Answers */}
            <div>
              <p className="text-xs text-gray-500 mb-2">Răspunsuri rapide:</p>
              <div className="grid grid-cols-2 gap-2">
                {QUICK_ANSWERS.map((qa, idx) => (
                  <div key={idx} className="bg-zinc-800 rounded-lg p-2">
                    <p className="text-xs font-medium text-white">{qa.q}</p>
                    <p className="text-xs text-gray-400 mt-1">{qa.a}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Suggested Questions */}
            <div>
              <p className="text-xs text-gray-500 mb-2">Întreabă:</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_QUESTIONS.slice(0, 3).map((q, idx) => (
                  <Button 
                    key={idx}
                    variant="outline" 
                    size="sm" 
                    className="text-xs h-auto py-1 px-2"
                    onClick={() => handleQuickQuestion(q)}
                  >
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[90%] rounded-lg p-3 ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : msg.isLimitReached
                    ? 'bg-amber-500/20 border border-amber-500/50'
                    : msg.isError
                    ? 'bg-red-500/20 border border-red-500/50'
                    : 'bg-zinc-800 text-gray-100'
                }`}
              >
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2">
                    <Bot className="w-4 h-4 text-blue-400" />
                    <span className="text-xs text-gray-400">AI Fiscal</span>
                  </div>
                )}
                
                <div className="text-sm whitespace-pre-wrap">
                  {msg.content}
                </div>

                {msg.disclaimer && (
                  <p className="text-xs text-amber-400 mt-2 border-t border-zinc-700 pt-2">
                    {msg.disclaimer}
                  </p>
                )}

                {msg.isLimitReached && msg.upgradeMessage && (
                  <div className="mt-2 pt-2 border-t border-amber-500/30">
                    <p className="text-xs text-amber-300">{msg.upgradeMessage}</p>
                    <Button size="sm" className="mt-2 bg-amber-500 hover:bg-amber-600 text-xs">
                      <Crown className="w-3 h-3 mr-1" />
                      Activează PRO
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-gray-400 text-sm">Analizez întrebarea...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Input */}
      <div className="p-3 border-t border-zinc-700 flex-shrink-0">
        {!user ? (
          <div className="text-center">
            <Lock className="w-5 h-5 text-gray-500 mx-auto mb-1" />
            <p className="text-xs text-gray-500">Conectează-te pentru AI Fiscal</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Întreabă despre impozite..."
              className="flex-1 bg-zinc-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              disabled={loading}
            />
            <Button 
              type="submit" 
              disabled={loading || !input.trim()}
              size="sm"
              className="bg-blue-600 hover:bg-blue-700"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </form>
        )}
      </div>
    </Card>
  );
};

export default FiscalAIChat;
