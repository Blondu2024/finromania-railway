import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Bot, User, Sparkles, Bug, Lightbulb, HelpCircle, CheckCircle } from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SUGGESTIONS_KEYS = [
  'finAssistant.suggestion1',
  'finAssistant.suggestion2',
  'finAssistant.suggestion3',
  'finAssistant.suggestion4',
];

export default function FinAssistant() {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [feedbackMode, setFeedbackMode] = useState(null); // null, 'bug', 'idea', 'question'
  const [feedbackText, setFeedbackText] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([{ role: 'assistant', content: t('finAssistant.welcome') }]);
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, feedbackMode]);

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/advisor/assistant`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });

      if (res.ok) {
        const data = await res.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        // Try to get error details
        let errorMsg = t('finAssistant.error');
        try {
          const errorData = await res.json();
          console.error('Assistant API error:', res.status, errorData);
        } catch (e) {
          console.error('Assistant API error:', res.status);
        }
        setMessages(prev => [...prev, { role: 'assistant', content: errorMsg }]);
      }
    } catch (err) {
      console.error('Assistant connection error:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: t('finAssistant.connectionError')
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const submitFeedback = async () => {
    if (!feedbackText.trim()) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: feedbackMode,
          message: feedbackText,
          page: window.location.pathname
        })
      });

      if (res.ok) {
        setFeedbackSent(true);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: t('finAssistant.feedbackSuccess', { type: feedbackMode === 'bug' ? t('finAssistant.bugReport') : feedbackMode === 'idea' ? t('finAssistant.yourIdea') : t('finAssistant.yourQuestion') })
        }]);
        setTimeout(() => {
          setFeedbackMode(null);
          setFeedbackText('');
          setFeedbackSent(false);
        }, 2000);
      } else {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: t('finAssistant.feedbackError')
        }]);
      }
    } catch (err) {
      console.error('Feedback error:', err);
    } finally {
      setLoading(false);
    }
  };

  const feedbackLabels = {
    bug: { icon: Bug, label: t('finAssistant.reportBug'), color: 'text-red-500' },
    idea: { icon: Lightbulb, label: t('finAssistant.sendIdea'), color: 'text-yellow-500' },
    question: { icon: HelpCircle, label: t('finAssistant.askQuestion'), color: 'text-blue-500' }
  };

  return (
    <>
      {/* Floating Button - moved higher to avoid BETA badge */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-24 right-6 z-50 w-14 h-14 bg-gradient-to-r from-blue-700 to-blue-500 rounded-full shadow-lg flex items-center justify-center hover:shadow-xl transition-shadow group"
            data-testid="assistant-open-btn"
          >
            <Bot className="w-7 h-7 text-white" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white animate-pulse" />

            {/* Tooltip */}
            <div className="absolute right-full mr-3 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
              {t('finAssistant.askAnything')}
              <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1 w-2 h-2 bg-gray-900 rotate-45" />
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Window - positioned higher */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-[360px] h-[500px] bg-white dark:bg-gray-900 rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700"
            data-testid="assistant-chat-window"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-700 to-blue-500 px-4 py-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-white font-semibold text-sm">FinRomania Assistant</h3>
                  <p className="text-white/70 text-xs flex items-center gap-1">
                    <span className="w-2 h-2 bg-green-400 rounded-full" />
                    Online
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors"
                data-testid="assistant-close-btn"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start gap-2 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.role === 'user'
                        ? 'bg-blue-100 dark:bg-blue-900'
                        : 'bg-blue-100 dark:bg-blue-900'
                    }`}>
                      {msg.role === 'user'
                        ? <User className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                        : <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      }
                    </div>
                    <div className={`px-3 py-2 rounded-2xl text-sm ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-md'
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 rounded-bl-md'
                    }`}>
                      {msg.content}
                    </div>
                  </div>
                </motion.div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    </div>
                    <div className="bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-2xl rounded-bl-md">
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Feedback Mode Form */}
            {feedbackMode && (
              <div className="px-4 pb-2 border-t dark:border-gray-700 pt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium flex items-center gap-2">
                    {feedbackMode === 'bug' && <Bug className="w-4 h-4 text-red-500" />}
                    {feedbackMode === 'idea' && <Lightbulb className="w-4 h-4 text-yellow-500" />}
                    {feedbackMode === 'question' && <HelpCircle className="w-4 h-4 text-blue-500" />}
                    {feedbackLabels[feedbackMode]?.label}
                  </span>
                  <button
                    onClick={() => { setFeedbackMode(null); setFeedbackText(''); }}
                    className="text-xs text-muted-foreground hover:text-foreground"
                  >
                    {t('common.cancel')}
                  </button>
                </div>
                {feedbackSent ? (
                  <div className="flex items-center gap-2 text-green-600 py-2">
                    <CheckCircle className="w-5 h-5" />
                    <span className="text-sm">{t('finAssistant.feedbackSent')}</span>
                  </div>
                ) : (
                  <>
                    <Textarea
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      placeholder={
                        feedbackMode === 'bug' ? t('finAssistant.placeholderBug') :
                        feedbackMode === 'idea' ? t('finAssistant.placeholderIdea') :
                        t('finAssistant.placeholderQuestion')
                      }
                      className="text-sm resize-none h-20 mb-2"
                    />
                    <Button
                      onClick={submitFeedback}
                      disabled={loading || !feedbackText.trim()}
                      className="w-full bg-gradient-to-r from-blue-700 to-blue-500"
                      size="sm"
                    >
                      {loading ? t('common.sending') : t('common.send')}
                    </Button>
                  </>
                )}
              </div>
            )}

            {/* Suggestions & Feedback Buttons */}
            {!feedbackMode && messages.length <= 3 && (
              <div className="px-4 pb-2">
                <p className="text-xs text-muted-foreground mb-2">{t('finAssistant.quickSuggestions')}</p>
                <div className="flex flex-wrap gap-1 mb-3">
                  {SUGGESTIONS_KEYS.map((key, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendMessage(t(key))}
                      className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                    >
                      {t(key)}
                    </button>
                  ))}
                </div>

                <p className="text-xs text-muted-foreground mb-2">{t('finAssistant.orSendFeedback')}</p>
                <div className="flex gap-1">
                  <button
                    onClick={() => setFeedbackMode('bug')}
                    className="flex-1 text-xs px-2 py-1.5 bg-red-50 dark:bg-red-900/20 text-red-600 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors flex items-center justify-center gap-1"
                  >
                    <Bug className="w-3 h-3" /> Bug
                  </button>
                  <button
                    onClick={() => setFeedbackMode('idea')}
                    className="flex-1 text-xs px-2 py-1.5 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 rounded-lg hover:bg-yellow-100 dark:hover:bg-yellow-900/40 transition-colors flex items-center justify-center gap-1"
                  >
                    <Lightbulb className="w-3 h-3" /> {t('finAssistant.idea')}
                  </button>
                  <button
                    onClick={() => setFeedbackMode('question')}
                    className="flex-1 text-xs px-2 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors flex items-center justify-center gap-1"
                  >
                    <HelpCircle className="w-3 h-3" /> {t('finAssistant.question')}
                  </button>
                </div>
              </div>
            )}

            {/* Input - show only when not in feedback mode */}
            {!feedbackMode && (
              <form onSubmit={handleSubmit} className="p-3 border-t dark:border-gray-700">
                <div className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={t('finAssistant.inputPlaceholder')}
                    disabled={loading}
                    className="flex-1 text-sm"
                    data-testid="assistant-input"
                  />
                  <Button
                    type="submit"
                    size="icon"
                    disabled={loading || !input.trim()}
                    className="bg-gradient-to-r from-blue-700 to-blue-500 hover:opacity-90"
                    data-testid="assistant-send-btn"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </form>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
