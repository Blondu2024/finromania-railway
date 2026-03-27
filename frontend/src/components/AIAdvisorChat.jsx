import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Lock, Crown, AlertCircle, Sparkles, TrendingUp, BarChart3, BookOpen, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LEVEL_INFO = {
  beginner: {
    name: 'Începător',
    icon: BookOpen,
    color: 'text-green-500',
    bgColor: 'bg-green-500/10',
    description: 'Focus pe dividende și acțiuni BET'
  },
  intermediate: {
    name: 'Mediu',
    icon: BarChart3,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    description: 'Indicatori tehnici și analiză avansată'
  },
  advanced: {
    name: 'Expert',
    icon: TrendingUp,
    color: 'text-blue-500',
    bgColor: 'bg-blue-500/10',
    description: 'Analiză fundamentală și grafice pro'
  }
};

const AIAdvisorChat = ({ symbol = null, marketType = 'bvb' }) => {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const messagesEndRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    if (user && token) {
      fetchSubscriptionStatus();
      // Add welcome message
      setMessages([{
        role: 'assistant',
        content: `Salut! Sunt AI Advisor-ul tău financiar. ${symbol ? `Văd că analizezi ${symbol}.` : ''} Cu ce te pot ajuta astăzi?`,
        timestamp: new Date()
      }]);
    }
  }, [user, token, symbol]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/subscriptions/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSubscriptionStatus(data);
      }
    } catch (error) {
      console.error('Error fetching subscription status:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/ai-advisor/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          symbol: symbol,
          market_type: marketType,
          include_market_data: true,
          session_id: sessionId
        })
      });

      const data = await response.json();

      if (!data.success) {
        if (data.error === 'limit_reached') {
          setShowUpgradeModal(true);
          setMessages(prev => [...prev, {
            role: 'system',
            content: data.message,
            isLimitReached: true,
            upgradePrompt: data.upgrade_prompt,
            timestamp: new Date()
          }]);
        } else if (data.error === 'symbol_not_allowed') {
          setMessages(prev => [...prev, {
            role: 'system',
            content: data.message,
            isWarning: true,
            allowedSymbols: data.allowed_symbols,
            timestamp: new Date()
          }]);
        } else {
          throw new Error(data.message || 'Unknown error');
        }
      } else {
        setSessionId(data.session_id);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response,
          level: data.level,
          chartLines: data.chart_lines,
          timestamp: new Date()
        }]);

        // Update queries info
        if (data.queries_info) {
          setSubscriptionStatus(prev => ({
            ...prev,
            ai_queries: data.queries_info
          }));
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'system',
        content: 'A apărut o eroare. Te rog să încerci din nou.',
        isError: true,
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (question) => {
    setInput(question);
  };

  if (!user) {
    return (
      <Card className="bg-zinc-900 border-zinc-700">
        <CardContent className="p-6 text-center">
          <Lock className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Conectează-te pentru AI Advisor</h3>
          <p className="text-gray-400 mb-4">Trebuie să fii autentificat pentru a folosi AI Advisor.</p>
          <Button variant="default" onClick={() => window.location.href = '/login'}>
            Conectează-te
          </Button>
        </CardContent>
      </Card>
    );
  }

  const currentLevel = subscriptionStatus?.experience?.current_level || 'beginner';
  const levelInfo = LEVEL_INFO[currentLevel];
  const LevelIcon = levelInfo?.icon || BookOpen;
  const queriesRemaining = subscriptionStatus?.ai_queries?.remaining;
  const isUnlimited = subscriptionStatus?.ai_queries?.is_unlimited;

  return (
    <Card className="bg-zinc-900 border-zinc-700 flex flex-col h-[600px]">
      {/* Header */}
      <CardHeader className="border-b border-zinc-700 pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg">
              <Bot className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <CardTitle className="text-white flex items-center gap-2">
                AI Advisor
                {subscriptionStatus?.subscription?.is_pro && (
                  <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                    <Crown className="w-3 h-3 mr-1" />
                    PRO
                  </Badge>
                )}
              </CardTitle>
              <div className="flex items-center gap-2 mt-1">
                <Badge className={`${levelInfo?.bgColor} ${levelInfo?.color}`}>
                  <LevelIcon className="w-3 h-3 mr-1" />
                  {levelInfo?.name}
                </Badge>
                {symbol && (
                  <Badge variant="outline" className="text-gray-400 border-gray-600">
                    {symbol}
                  </Badge>
                )}
              </div>
            </div>
          </div>
          
          {/* Queries counter */}
          {!isUnlimited && (
            <div className="text-right">
              <p className="text-xs text-gray-500">Întrebări rămase</p>
              <p className={`text-lg font-bold ${queriesRemaining <= 1 ? 'text-red-400' : 'text-green-400'}`}>
                {queriesRemaining}/5
              </p>
            </div>
          )}
        </div>
      </CardHeader>

      {/* Messages */}
      <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[85%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : msg.isLimitReached
                  ? 'bg-amber-500/20 border border-amber-500/50'
                  : msg.isError
                  ? 'bg-red-500/20 border border-red-500/50'
                  : msg.isWarning
                  ? 'bg-yellow-500/20 border border-yellow-500/50'
                  : 'bg-zinc-800 text-gray-100'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-2">
                  <Bot className="w-4 h-4 text-blue-400" />
                  <span className="text-xs text-gray-400">AI Advisor</span>
                </div>
              )}
              
              <div className="whitespace-pre-wrap text-sm">
                {msg.content}
              </div>

              {msg.isLimitReached && msg.upgradePrompt && (
                <div className="mt-3 p-3 bg-zinc-900 rounded-lg">
                  <p className="font-semibold text-amber-400 flex items-center gap-2">
                    <Crown className="w-4 h-4" />
                    {msg.upgradePrompt.title}
                  </p>
                  <p className="text-gray-300 text-sm mt-1">{msg.upgradePrompt.description}</p>
                  <Button 
                    className="mt-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
                    size="sm"
                  >
                    {msg.upgradePrompt.cta} - {msg.upgradePrompt.price}
                  </Button>
                </div>
              )}

              {msg.allowedSymbols && (
                <div className="mt-2">
                  <p className="text-xs text-gray-400">Simboluri disponibile la nivelul tău:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {msg.allowedSymbols.slice(0, 10).map(s => (
                      <Badge key={s} variant="outline" className="text-xs">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {msg.chartLines && (
                <div className="mt-3 p-2 bg-zinc-900 rounded text-xs">
                  <p className="text-gray-400 mb-1">📐 Linii pentru grafic:</p>
                  {msg.chartLines.supports?.map((s, i) => (
                    <p key={`s-${i}`} className="text-green-400">• Suport: {s.price} RON</p>
                  ))}
                  {msg.chartLines.resistances?.map((r, i) => (
                    <p key={`r-${i}`} className="text-red-400">• Rezistență: {r.price} RON</p>
                  ))}
                </div>
              )}
              
              <p className="text-xs text-gray-500 mt-2">
                {new Date(msg.timestamp).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-zinc-800 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                <span className="text-gray-400 text-sm">Analizez datele...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </CardContent>

      {/* Quick Questions */}
      {messages.length <= 2 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-gray-500 mb-2">Întrebări sugerate:</p>
          <div className="flex flex-wrap gap-2">
            {symbol ? (
              <>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => handleQuickQuestion(`Care sunt perspectivele pentru ${symbol}?`)}
                >
                  Perspective {symbol}
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => handleQuickQuestion(`Analizează dividendele pentru ${symbol}`)}
                >
                  Dividende
                </Button>
              </>
            ) : (
              <>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => handleQuickQuestion('Care sunt cele mai bune acțiuni pentru dividende pe BVB?')}
                >
                  Top Dividende BVB
                </Button>
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="text-xs"
                  onClick={() => handleQuickQuestion('Explică-mi ce înseamnă P/E ratio')}
                >
                  Ce e P/E?
                </Button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="p-4 border-t border-zinc-700">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Întreabă despre ${symbol || 'piața BVB'}...`}
            className="flex-1 bg-zinc-800 border border-slate-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            disabled={loading}
          />
          <Button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </form>
        
        {!isUnlimited && queriesRemaining <= 2 && queriesRemaining > 0 && (
          <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Mai ai doar {queriesRemaining} întrebări gratuite azi
          </p>
        )}
      </div>
    </Card>
  );
};

export default AIAdvisorChat;
