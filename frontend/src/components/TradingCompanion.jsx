import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, X, Send, Shield, AlertTriangle, 
  Loader2, ChevronDown, Lightbulb, HelpCircle
} from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Reminder Modal - appears when viewing stock details
export const TradingReminder = ({ isOpen, onClose, onOpenCompanion }) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-md w-full overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-amber-500 to-orange-500 p-6 text-white">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-xl font-bold">⚠️ Înainte să decizi...</h2>
                <p className="text-amber-100 text-sm">Un moment de reflecție</p>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            <p className="text-muted-foreground">
              Nu lua decizii bazate pe emoții. Mulți investitori au pierdut bani pentru că au acționat pripit.
            </p>

            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 space-y-2">
              <p className="font-medium text-blue-700 dark:text-blue-300">Întreabă-te:</p>
              <ul className="text-sm text-blue-600 dark:text-blue-400 space-y-1">
                <li>• Știu de ce vreau să fac această mișcare?</li>
                <li>• Am un plan dacă merge prost?</li>
                <li>• Sunt influențat de emoții acum?</li>
              </ul>
            </div>

            <p className="text-sm text-muted-foreground">
              💡 Poți discuta cu <strong>&quot;Verifică Înainte&quot;</strong> - asistentul AI care te ajută să gândești clar.
            </p>
          </div>

          {/* Actions */}
          <div className="p-4 border-t bg-muted/30 flex gap-3">
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={onClose}
            >
              Am înțeles
            </Button>
            <Button 
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600"
              onClick={() => {
                onClose();
                onOpenCompanion();
              }}
            >
              <Shield className="w-4 h-4 mr-2" />
              Consultă AI-ul
            </Button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

// Check if reminder should be shown (once per day for logged users)
export const shouldShowReminder = (isLoggedIn) => {
  if (!isLoggedIn) return true; // Always show for non-logged users
  
  const lastShown = localStorage.getItem('trading_reminder_last_shown');
  if (!lastShown) return true;
  
  const lastDate = new Date(lastShown).toDateString();
  const today = new Date().toDateString();
  
  return lastDate !== today;
};

// Mark reminder as shown today
export const markReminderShown = () => {
  localStorage.setItem('trading_reminder_last_shown', new Date().toISOString());
};

// Main Trading Companion Component
const TradingCompanion = ({ 
  stockSymbol, 
  stockName, 
  currentPrice, 
  changePercent,
  stockType = 'bvb',
  forceOpen = false,
  onOpenChange = null
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tips, setTips] = useState([]);
  const [aiQueriesRemaining, setAiQueriesRemaining] = useState(null);
  const [subscriptionLevel, setSubscriptionLevel] = useState('free');
  const messagesEndRef = useRef(null);
  const { user, token } = useAuth();

  // Fetch AI limits when component opens
  useEffect(() => {
    if (isOpen && user && token) {
      fetch(`${API_URL}/api/subscriptions/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          const level = data?.subscription?.subscription_level || 'free';
          const aiUsed = data?.ai_queries?.used_today || 0;
          const aiLimit = data?.ai_queries?.limit || 5;
          const remaining = data?.ai_queries?.remaining || 0;
          
          setSubscriptionLevel(level);
          setAiQueriesRemaining(remaining);
          console.log('[TradingCompanion] AI Queries Remaining:', remaining, 'Level:', level);
        })
        .catch(err => {
          console.error('[TradingCompanion] Failed to fetch limits:', err);
        });
    }
  }, [isOpen, user, token]);

  // Handle forceOpen prop
  useEffect(() => {
    if (forceOpen) {
      setIsOpen(true);
      if (onOpenChange) onOpenChange(false); // Reset forceOpen
    }
  }, [forceOpen, onOpenChange]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Fetch quick tips when companion opens
  useEffect(() => {
    if (isOpen && stockSymbol) {
      fetchTips();
    }
  }, [isOpen, stockSymbol]);

  const fetchTips = async () => {
    try {
      const res = await fetch(
        `${API_URL}/api/companion/tips/${encodeURIComponent(stockSymbol)}?stock_type=${stockType}&change_percent=${changePercent || 0}`
      );
      if (res.ok) {
        const data = await res.json();
        setTips(data.tips || []);
      }
    } catch (err) {
      console.error('Error fetching tips:', err);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userMessage = message.trim();
    setMessage('');
    setConversation(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const headers = {
        'Content-Type': 'application/json'
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(`${API_URL}/api/companion/ask`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          symbol: stockSymbol,
          stock_name: stockName,
          current_price: currentPrice,
          change_percent: changePercent,
          user_question: userMessage,
          stock_type: stockType
        })
      });

      if (res.ok) {
        const data = await res.json();
        setConversation(prev => [...prev, { 
          role: 'assistant', 
          content: data.response,
          disclaimer: data.disclaimer
        }]);
        
        // Refresh AI limits after successful query
        if (user && token && subscriptionLevel !== 'pro') {
          setAiQueriesRemaining(prev => Math.max(0, (prev || 5) - 1));
        }
      } else if (res.status === 429) {
        // AI limit reached
        const errorData = await res.json();
        setConversation(prev => [...prev, { 
          role: 'assistant', 
          content: `🔒 ${errorData.detail?.message || 'Ai atins limita de întrebări AI.'}\n\n💎 **Upgrade la PRO:**\n- Întrebări AI nelimitate\n- Grafice intraday profesionale\n- Date live actualizate la 3s\n\n[Vezi /pricing pentru detalii]`,
          isError: true,
          isLimitReached: true
        }]);
      } else {
        const errorText = await res.text();
        setConversation(prev => [...prev, { 
          role: 'assistant', 
          content: 'Nu am putut procesa cererea. Încearcă din nou.',
          isError: true
        }]);
      }
    } catch (err) {
      console.error('Error:', err);
      setConversation(prev => [...prev, { 
        role: 'assistant', 
        content: 'Eroare de conexiune. Verifică internetul și încearcă din nou.',
        isError: true
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Suggested questions based on context
  const suggestedQuestions = [
    `${stockSymbol} a ${(changePercent || 0) < 0 ? 'scăzut' : 'crescut'} - e moment bun să intru?`,
    `Ce riscuri ar trebui să știu despre ${stockSymbol}?`,
    `Sunt începător - cum ar trebui să abordez ${stockSymbol}?`,
    `Am deja ${stockSymbol} - să mai cumpăr sau să aștept?`
  ];

  return (
    <>
      {/* Floating Button */}
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-40 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center gap-2"
      >
        <Shield className="w-5 h-5" />
        <span className="hidden sm:inline font-medium">Verifică Înainte</span>
        <HelpCircle className="w-4 h-4 sm:hidden" />
      </motion.button>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-2rem)] max-h-[70vh] flex flex-col bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border overflow-hidden"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <Shield className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold">🤔 Verifică Înainte</h3>
                    <p className="text-xs text-blue-200">
                      {stockSymbol ? `Analizăm ${stockSymbol}` : 'Asistent Trading'}
                    </p>
                    {user && aiQueriesRemaining !== null && (
                      <p className="text-xs text-blue-100 mt-1">
                        {subscriptionLevel === 'pro' ? (
                          <span className="flex items-center gap-1">
                            <span className="text-amber-300">👑 PRO:</span> Întrebări nelimitate
                          </span>
                        ) : (
                          <span className={aiQueriesRemaining === 0 ? 'text-red-300 font-bold' : ''}>
                            {aiQueriesRemaining === 0 ? '🔒 Limită atinsă!' : `💬 ${aiQueriesRemaining} întrebări rămase azi`}
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white/20"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
            </div>

            {/* Stock Context Badge */}
            {stockSymbol && (
              <div className="px-4 py-2 bg-muted/50 border-b flex items-center justify-between text-sm">
                <span className="font-medium">{stockName || stockSymbol}</span>
                <span className={`font-bold ${(changePercent || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {currentPrice?.toLocaleString('ro-RO')} ({changePercent >= 0 ? '+' : ''}{changePercent?.toFixed(2)}%)
                </span>
              </div>
            )}

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px]">
              {/* Welcome Message */}
              {conversation.length === 0 && (
                <div className="space-y-4">
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                    <p className="text-sm text-blue-700 dark:text-blue-300">
                      👋 Salut! Sunt aici să te ajut să gândești clar înainte de orice decizie de investiții.
                      <br /><br />
                      Nu îți spun ce să faci - dar te ajut să pui întrebările potrivite.
                    </p>
                  </div>

                  {/* Quick Tips */}
                  {tips.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-muted-foreground flex items-center gap-1">
                        <Lightbulb className="w-3 h-3" /> Gânduri rapide:
                      </p>
                      {tips.map((tip, idx) => (
                        <div key={idx} className="text-xs bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 rounded p-2">
                          {tip}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Suggested Questions */}
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">
                      Sau întreabă direct:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {suggestedQuestions.slice(0, 2).map((q, idx) => (
                        <button
                          key={idx}
                          onClick={() => {
                            setMessage(q);
                          }}
                          className="text-xs bg-muted hover:bg-muted/80 rounded-full px-3 py-1.5 transition-colors text-left"
                        >
                          {q.length > 40 ? q.slice(0, 40) + '...' : q}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Conversation */}
              {conversation.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-2 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : msg.isError
                        ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    {msg.disclaimer && (
                      <p className="text-xs mt-2 pt-2 border-t border-current/20 opacity-70">
                        {msg.disclaimer}
                      </p>
                    )}
                  </div>
                </div>
              ))}

              {/* Loading */}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-muted rounded-2xl px-4 py-2">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 border-t bg-muted/30">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Întreabă orice despre această acțiune..."
                  className="flex-1 px-4 py-2 rounded-full border bg-background focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  disabled={loading}
                />
                <Button
                  onClick={sendMessage}
                  disabled={!message.trim() || loading}
                  size="icon"
                  className="rounded-full bg-blue-600 hover:bg-blue-700"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-center text-muted-foreground mt-2">
                Nu sunt sfaturi financiare • Doar gânduri pentru reflecție
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default TradingCompanion;
