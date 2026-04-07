import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  MessageSquare, Send, ArrowLeft, Users, Lock, Crown,
  Hash, Wallet, BarChart3, GraduationCap, Receipt, Globe, Trash2
} from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API_URL.replace('https://', 'wss://').replace('http://', 'ws://');

const ICONS = {
  wallet: Wallet,
  chart: BarChart3,
  graduation: GraduationCap,
  receipt: Receipt,
  globe: Globe,
  message: MessageSquare,
};

const COLORS = {
  green: 'from-green-500 to-green-600',
  blue: 'from-blue-500 to-blue-600',
  purple: 'from-purple-500 to-purple-600',
  orange: 'from-orange-500 to-orange-600',
  cyan: 'from-cyan-500 to-cyan-600',
  slate: 'from-slate-500 to-slate-600',
};

// ============================================
// CHANNEL LIST (sidebar)
// ============================================
function ChannelList({ channels, activeId, onSelect, loading }) {
  if (loading) return <div className="p-4 text-sm text-muted-foreground">Se incarca...</div>;

  return (
    <div className="space-y-1 p-2">
      {channels.map((ch) => {
        const Icon = ICONS[ch.icon] || Hash;
        const isActive = ch.id === activeId;

        return (
          <button
            key={ch.id}
            onClick={() => onSelect(ch)}
            className={`w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-left transition-all ${
              isActive
                ? 'bg-blue-500 text-white shadow-md'
                : 'hover:bg-accent text-foreground'
            }`}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium truncate">{ch.name}</span>
                {ch.online_count > 0 && (
                  <span className={`flex items-center gap-1 text-xs ${isActive ? 'text-white/80' : 'text-green-500'}`}>
                    <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                    {ch.online_count}
                  </span>
                )}
              </div>
              {ch.last_message && (
                <p className={`text-xs truncate mt-0.5 ${isActive ? 'text-white/60' : 'text-muted-foreground'}`}>
                  {ch.last_message.author}: {ch.last_message.content}
                </p>
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ============================================
// MESSAGE BUBBLE
// ============================================
function MessageBubble({ msg, isOwn, onDelete }) {
  const time = new Date(msg.created_at).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' });

  return (
    <div className={`flex gap-2.5 px-4 py-1 hover:bg-accent/30 group ${isOwn ? '' : ''}`}>
      {msg.author_picture ? (
        <img src={msg.author_picture} alt="" className="w-8 h-8 rounded-full mt-0.5 flex-shrink-0" />
      ) : (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mt-0.5 flex-shrink-0">
          <span className="text-white text-xs font-bold">{msg.author_name?.[0]?.toUpperCase()}</span>
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="font-semibold text-sm">{msg.author_name}</span>
          <span className="text-xs text-muted-foreground">{time}</span>
          {isOwn && (
            <button
              onClick={() => onDelete(msg.message_id)}
              className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-red-500 transition-all"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          )}
        </div>
        <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
      </div>
    </div>
  );
}

// ============================================
// MAIN COMPONENT
// ============================================
export default function CommunityPage() {
  const { user, token } = useAuth();

  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [onlineCount, setOnlineCount] = useState(0);
  const [canWrite, setCanWrite] = useState(false);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [typingUser, setTypingUser] = useState(null);
  const [showSidebar, setShowSidebar] = useState(true);

  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const typingTimeout = useRef(null);
  const isPro = user?.subscription_level === 'pro';

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Fetch channels
  useEffect(() => {
    fetch(`${API_URL}/api/community/channels`)
      .then(r => r.json())
      .then(data => {
        setChannels(data.channels);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Connect WebSocket when channel changes
  useEffect(() => {
    if (!activeChannel) return;

    // Load message history
    fetch(`${API_URL}/api/community/channels/${activeChannel.id}/messages?limit=50`)
      .then(r => r.json())
      .then(data => {
        setMessages(data.messages);
        setOnlineCount(data.online_count);
        scrollToBottom();
      });

    // Connect WebSocket
    const ws = new WebSocket(`${WS_URL}/api/community/ws/${activeChannel.id}`);
    wsRef.current = ws;

    ws.onopen = () => {
      // Send auth
      ws.send(JSON.stringify({
        type: 'auth',
        token: token || null
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'auth_ok') {
        setCanWrite(data.can_write);
      } else if (data.type === 'new_message') {
        setMessages(prev => [...prev, data.message]);
      } else if (data.type === 'message_deleted') {
        setMessages(prev => prev.filter(m => m.message_id !== data.message_id));
      } else if (data.type === 'online_count') {
        setOnlineCount(data.count);
      } else if (data.type === 'typing') {
        if (data.user_name !== user?.name) {
          setTypingUser(data.user_name);
          clearTimeout(typingTimeout.current);
          typingTimeout.current = setTimeout(() => setTypingUser(null), 2000);
        }
      }
    };

    ws.onclose = () => {
      // Reconnect after 3s
      setTimeout(() => {
        if (activeChannel && wsRef.current === ws) {
          // Will trigger re-run of this effect via state
        }
      }, 3000);
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [activeChannel, token, user?.name, scrollToBottom]);

  // Send message
  const handleSend = () => {
    if (!inputText.trim() || !wsRef.current || !canWrite) return;

    wsRef.current.send(JSON.stringify({
      type: 'message',
      content: inputText.trim()
    }));

    setInputText('');
  };

  // Send typing indicator
  const handleTyping = () => {
    if (wsRef.current && canWrite) {
      wsRef.current.send(JSON.stringify({ type: 'typing' }));
    }
  };

  // Delete message
  const handleDelete = async (messageId) => {
    if (!token) return;
    await fetch(`${API_URL}/api/community/messages/${messageId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
  };

  // Select channel
  const selectChannel = (ch) => {
    setActiveChannel(ch);
    setMessages([]);
    setShowSidebar(false); // Hide sidebar on mobile
  };

  // ============================================
  // RENDER
  // ============================================
  return (
    <>
      <SEO title="Chat Comunitate | FinRomania" description="Chat live cu investitori romani" />

      <div className="flex h-[calc(100vh-3.5rem)] overflow-hidden">
        {/* Sidebar — Channel List */}
        <div className={`${showSidebar ? 'flex' : 'hidden'} md:flex flex-col w-full md:w-64 border-r bg-card flex-shrink-0`}>
          <div className="p-3 border-b">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <MessageSquare className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="font-bold text-sm">Comunitate</h2>
                <p className="text-xs text-muted-foreground">Chat live investitori</p>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            <ChannelList
              channels={channels}
              activeId={activeChannel?.id}
              onSelect={selectChannel}
              loading={loading}
            />
          </div>

          {!isPro && (
            <div className="p-3 border-t bg-amber-50 dark:bg-amber-950/20">
              <div className="flex items-center gap-2 text-xs">
                <Lock className="w-3.5 h-3.5 text-amber-500" />
                <span className="text-amber-700 dark:text-amber-400">Citesti gratuit. <a href="/pricing" className="underline font-medium">PRO</a> pentru a scrie.</span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Area */}
        {activeChannel ? (
          <div className="flex-1 flex flex-col min-w-0">
            {/* Channel Header */}
            <div className="h-12 border-b flex items-center gap-3 px-4 bg-card flex-shrink-0">
              <button onClick={() => { setActiveChannel(null); setShowSidebar(true); }} className="md:hidden">
                <ArrowLeft className="w-5 h-5" />
              </button>
              <Hash className="w-4 h-4 text-muted-foreground" />
              <span className="font-semibold text-sm">{activeChannel.name}</span>
              <div className="flex items-center gap-1.5 ml-auto text-xs text-muted-foreground">
                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                {onlineCount} online
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto py-4 space-y-1">
              {messages.length === 0 && (
                <div className="text-center py-16 text-muted-foreground">
                  <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-20" />
                  <p className="font-medium">Niciun mesaj inca</p>
                  <p className="text-sm mt-1">Fii primul care scrie in #{activeChannel.name}!</p>
                </div>
              )}

              {messages.map((msg) => (
                <MessageBubble
                  key={msg.message_id}
                  msg={msg}
                  isOwn={msg.author_id === user?.user_id}
                  onDelete={handleDelete}
                />
              ))}

              {typingUser && (
                <div className="px-4 py-1 text-xs text-muted-foreground italic">
                  {typingUser} scrie...
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            {canWrite ? (
              <div className="border-t p-3 bg-card flex-shrink-0">
                <div className="flex gap-2">
                  <input
                    value={inputText}
                    onChange={(e) => { setInputText(e.target.value); handleTyping(); }}
                    onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSend())}
                    placeholder={`Scrie in #${activeChannel.name}...`}
                    className="flex-1 px-4 py-2.5 rounded-xl border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    maxLength={1000}
                  />
                  <Button onClick={handleSend} disabled={!inputText.trim()} className="rounded-xl px-4">
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div className="border-t p-3 bg-amber-50 dark:bg-amber-950/20 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <Lock className="w-4 h-4 text-amber-500" />
                    <span className="text-amber-700 dark:text-amber-400">
                      {user ? 'Upgrade la PRO ca sa scrii mesaje' : 'Logheaza-te si upgrade la PRO'}
                    </span>
                  </div>
                  <Button size="sm" className="bg-amber-500 hover:bg-amber-600 rounded-lg" asChild>
                    <a href="/pricing">
                      <Crown className="w-3.5 h-3.5 mr-1" /> PRO
                    </a>
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* No channel selected — show welcome */
          <div className="flex-1 hidden md:flex items-center justify-center text-center p-8">
            <div>
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mx-auto mb-4">
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-bold mb-2">Comunitate FinRomania</h2>
              <p className="text-muted-foreground text-sm max-w-sm">
                Alege un canal din stanga si intra in discutie cu alti investitori romani. Mesajele apar live, instant.
              </p>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
