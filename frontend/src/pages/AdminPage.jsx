import React, { useState, useEffect } from 'react';
import { Shield, Crown, Users, TrendingUp, MessageSquare, Bug, Lightbulb, HelpCircle, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminPage() {
  const { user, token } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [targetEmail, setTargetEmail] = useState('');
  const [subLevel, setSubLevel] = useState('pro');
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [upgradeResult, setUpgradeResult] = useState(null);
  
  // Feedback state
  const [activeTab, setActiveTab] = useState('users'); // users | feedback
  const [feedback, setFeedback] = useState([]);
  const [feedbackFilter, setFeedbackFilter] = useState({ status: '', type: '' });

  useEffect(() => {
    if (user && token && user.is_admin) {
      fetchStats();
      fetchUsers();
      fetchFeedback();
    }
  }, [user, token]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/api/admin/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users || []);
      }
    } catch (err) {
      console.error(err);
    }
  };
  
  const fetchFeedback = async () => {
    try {
      let url = `${API_URL}/api/admin/feedback`;
      const params = new URLSearchParams();
      if (feedbackFilter.status) params.append('status', feedbackFilter.status);
      if (feedbackFilter.type) params.append('feedback_type', feedbackFilter.type);
      if (params.toString()) url += `?${params.toString()}`;
      
      const res = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setFeedback(data.feedback || []);
      }
    } catch (err) {
      console.error('Error fetching feedback:', err);
    }
  };
  
  const updateFeedbackStatus = async (feedbackId, newStatus) => {
    try {
      const res = await fetch(`${API_URL}/api/admin/feedback/${feedbackId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (res.ok) {
        fetchFeedback();
        fetchStats();
      } else {
        const err = await res.json();
        alert(`❌ Eroare: ${err.detail}`);
      }
    } catch (err) {
      alert(`❌ Eroare: ${err.message}`);
    }
  };
  
  // Re-fetch feedback when filter changes
  useEffect(() => {
    if (user && token && user.is_admin && activeTab === 'feedback') {
      fetchFeedback();
    }
  }, [feedbackFilter, activeTab]);

  const handleSetSubscription = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const res = await fetch(`${API_URL}/api/admin/set-subscription`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          email: targetEmail,
          subscription_level: subLevel,
          duration_days: days
        })
      });
      
      if (res.ok) {
        alert(`✅ User ${targetEmail} setat ca ${subLevel.toUpperCase()}!`);
        setTargetEmail('');
        fetchUsers();
        fetchStats();
      } else {
        const err = await res.json();
        alert(`❌ Eroare: ${err.detail}`);
      }
    } catch (err) {
      alert(`❌ Eroare: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <Card>
          <CardContent className="p-8 text-center">
            <Shield className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <p>Autentificare necesară</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="max-w-4xl mx-auto p-8">
        <Card>
          <CardContent className="p-8 text-center">
            <Shield className="w-12 h-12 mx-auto text-red-400 mb-4" />
            <p className="text-xl font-bold">Acces Interzis</p>
            <p className="text-muted-foreground">Doar administratorii pot accesa această pagină.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <SEO title="Admin Dashboard | FinRomania" />
      
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <Badge className="bg-blue-500 text-white">{user.email}</Badge>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Users className="w-8 h-8 text-blue-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Users</p>
                    <p className="text-2xl font-bold">{stats.total_users}</p>
                    <p className="text-xs text-green-600">+{stats.recent_signups_7d} în ultimele 7 zile</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <Crown className="w-8 h-8 text-amber-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">PRO Users</p>
                    <p className="text-2xl font-bold">{stats.pro_users}</p>
                    <p className="text-xs text-amber-600">{stats.pro_percentage}% din total</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-8 h-8 text-green-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Active Users (7d)</p>
                    <p className="text-2xl font-bold">{stats.active_users_7d}</p>
                    <p className="text-xs text-muted-foreground">{stats.free_users} FREE</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-6">
                <div>
                  <p className="text-sm text-muted-foreground">AI Queries Total</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.total_ai_queries}</p>
                  <p className="text-xs text-muted-foreground">Toate întrebările AI</p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:ring-2 hover:ring-orange-400 transition-all" onClick={() => setActiveTab('feedback')}>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <MessageSquare className="w-8 h-8 text-orange-500" />
                  <div>
                    <p className="text-sm text-muted-foreground">Feedback BETA</p>
                    <p className="text-2xl font-bold">{stats.total_feedback || 0}</p>
                    <p className="text-xs text-orange-600">{stats.new_feedback || 0} noi</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Upgrade All to PRO Button */}
        {stats && stats.free_users > 0 && (
          <Card className="border-green-500/50 bg-green-500/5" data-testid="upgrade-all-pro-card">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <p className="font-semibold text-sm">{stats.free_users} useri sunt inca FREE</p>
                <p className="text-xs text-muted-foreground">Upgrade toti la PRO gratuit pana pe 5 iunie 2026</p>
              </div>
              <Button 
                size="sm"
                className="bg-green-600 hover:bg-green-700"
                data-testid="upgrade-all-btn"
                disabled={loading}
                onClick={async () => {
                  setLoading(true);
                  try {
                    const res = await fetch(`${API_URL}/api/admin/upgrade-all-to-pro`, {
                      method: 'POST',
                      headers: { 'Authorization': `Bearer ${token}` }
                    });
                    const data = await res.json();
                    setUpgradeResult(data);
                    fetchStats();
                    fetchUsers();
                  } catch (err) {
                    console.error(err);
                  } finally {
                    setLoading(false);
                  }
                }}
              >
                <Crown className="w-4 h-4 mr-1" />
                Upgrade Toti la PRO
              </Button>
            </CardContent>
          </Card>
        )}

        {upgradeResult && (
          <Card className="border-green-500 bg-green-500/10">
            <CardContent className="p-3 text-sm text-green-700 dark:text-green-400">
              {upgradeResult.message}
            </CardContent>
          </Card>
        )}

        {/* Tabs Navigation */}
        <div className="flex gap-2 border-b pb-2">
          <Button
            variant={activeTab === 'users' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('users')}
            data-testid="admin-tab-users"
          >
            <Users className="w-4 h-4 mr-2" />
            Utilizatori
          </Button>
          <Button
            variant={activeTab === 'feedback' ? 'default' : 'ghost'}
            onClick={() => setActiveTab('feedback')}
            data-testid="admin-tab-feedback"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Feedback BETA
            {stats?.new_feedback > 0 && (
              <Badge className="ml-2 bg-orange-500 text-white">{stats.new_feedback}</Badge>
            )}
          </Button>
        </div>

        {/* Tab Content: Users */}
        {activeTab === 'users' && (
          <>
            {/* Set Subscription Form */}
        <Card>
          <CardHeader>
            <CardTitle>Setează Subscription pentru User</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSetSubscription} className="space-y-4">
              <div>
                <Label>Email Utilizator</Label>
                <Input
                  type="email"
                  value={targetEmail}
                  onChange={(e) => setTargetEmail(e.target.value)}
                  placeholder="email@example.com"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Subscription Level</Label>
                  <select
                    value={subLevel}
                    onChange={(e) => setSubLevel(e.target.value)}
                    className="w-full p-2 border rounded-md"
                  >
                    <option value="free">FREE</option>
                    <option value="pro">PRO</option>
                  </select>
                </div>
                
                {subLevel === 'pro' && (
                  <div>
                    <Label>Zile PRO</Label>
                    <Input
                      type="number"
                      value={days}
                      onChange={(e) => setDays(parseInt(e.target.value))}
                      min="1"
                      max="365"
                    />
                  </div>
                )}
              </div>
              
              <Button type="submit" disabled={loading} className="w-full">
                {loading ? 'Se procesează...' : 'Setează Subscription'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Users List */}
        <Card>
          <CardHeader>
            <CardTitle>Utilizatori Recenți ({users.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {users.map((u) => (
                <div key={u.user_id} className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors">
                  <div className="flex-1">
                    <p className="font-semibold">{u.email}</p>
                    <p className="text-sm text-muted-foreground">{u.name}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                      <span>AI Credits: {u.ai_credits_used || 0}</span>
                      {u.last_login && (
                        <span>Last login: {new Date(u.last_login).toLocaleDateString('ro-RO')}</span>
                      )}
                      {u.created_at && (
                        <span>Înregistrat: {new Date(u.created_at).toLocaleDateString('ro-RO')}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={u.subscription_level === 'pro' ? 'bg-amber-500' : 'bg-gray-500'}>
                      {u.subscription_level?.toUpperCase() || 'FREE'}
                    </Badge>
                    {u.is_admin && <Badge className="bg-blue-500">ADMIN</Badge>}
                    
                    {/* Quick Actions */}
                    {u.subscription_level === 'pro' ? (
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={async () => {
                          if (window.confirm(`Downgrade ${u.email} la FREE?`)) {
                            setLoading(true);
                            try {
                              const res = await fetch(`${API_URL}/api/admin/set-subscription`, {
                                method: 'POST',
                                headers: {
                                  'Content-Type': 'application/json',
                                  'Authorization': `Bearer ${token}`
                                },
                                body: JSON.stringify({
                                  email: u.email,
                                  subscription_level: 'free',
                                  duration_days: 0
                                })
                              });
                              if (res.ok) {
                                alert(`✅ ${u.email} acum este FREE`);
                                fetchUsers();
                                fetchStats();
                              } else {
                                alert('❌ Eroare la downgrade');
                              }
                            } catch (err) {
                              alert(`❌ Eroare: ${err.message}`);
                            } finally {
                              setLoading(false);
                            }
                          }
                        }}
                        disabled={loading}
                      >
                        → FREE
                      </Button>
                    ) : (
                      <Button
                        size="sm"
                        className="bg-amber-500 hover:bg-amber-600"
                        onClick={async () => {
                          const days = prompt(`Câte zile PRO pentru ${u.email}?`, '30');
                          if (days && parseInt(days) > 0) {
                            setLoading(true);
                            try {
                              const res = await fetch(`${API_URL}/api/admin/set-subscription`, {
                                method: 'POST',
                                headers: {
                                  'Content-Type': 'application/json',
                                  'Authorization': `Bearer ${token}`
                                },
                                body: JSON.stringify({
                                  email: u.email,
                                  subscription_level: 'pro',
                                  duration_days: parseInt(days)
                                })
                              });
                              if (res.ok) {
                                alert(`✅ ${u.email} acum este PRO (${days} zile)`);
                                fetchUsers();
                                fetchStats();
                              } else {
                                alert('❌ Eroare la upgrade');
                              }
                            } catch (err) {
                              alert(`❌ Eroare: ${err.message}`);
                            } finally {
                              setLoading(false);
                            }
                          }
                        }}
                        disabled={loading}
                      >
                        → PRO
                      </Button>
                    )}
                    
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setTargetEmail(u.email);
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                      }}
                    >
                      Editează
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
          </>
        )}

        {/* Tab Content: Feedback */}
        {activeTab === 'feedback' && (
          <Card data-testid="feedback-management-section">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Gestionare Feedback BETA ({feedback.length})
              </CardTitle>
              
              {/* Filters */}
              <div className="flex flex-wrap gap-4 mt-4">
                <div className="flex items-center gap-2">
                  <Label className="text-sm">Status:</Label>
                  <select
                    value={feedbackFilter.status}
                    onChange={(e) => setFeedbackFilter(prev => ({ ...prev, status: e.target.value }))}
                    className="p-2 border rounded-md text-sm"
                    data-testid="feedback-filter-status"
                  >
                    <option value="">Toate</option>
                    <option value="new">🔴 Nou</option>
                    <option value="in_progress">🟡 În Lucru</option>
                    <option value="resolved">🟢 Rezolvat</option>
                  </select>
                </div>
                
                <div className="flex items-center gap-2">
                  <Label className="text-sm">Tip:</Label>
                  <select
                    value={feedbackFilter.type}
                    onChange={(e) => setFeedbackFilter(prev => ({ ...prev, type: e.target.value }))}
                    className="p-2 border rounded-md text-sm"
                    data-testid="feedback-filter-type"
                  >
                    <option value="">Toate</option>
                    <option value="bug">🐛 Bug</option>
                    <option value="idea">💡 Idee</option>
                    <option value="question">❓ Întrebare</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              {feedback.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Nu există feedback încă.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {feedback.map((item) => (
                    <div 
                      key={item.id} 
                      className={`p-4 rounded-lg border transition-colors ${
                        item.status === 'new' ? 'bg-red-50 border-red-200 dark:bg-red-950/20 dark:border-red-800' :
                        item.status === 'in_progress' ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-950/20 dark:border-yellow-800' :
                        'bg-green-50 border-green-200 dark:bg-green-950/20 dark:border-green-800'
                      }`}
                      data-testid={`feedback-item-${item.id}`}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          {/* Header row */}
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            {/* Type badge */}
                            <Badge className={
                              item.type === 'bug' ? 'bg-red-500' :
                              item.type === 'idea' ? 'bg-blue-500' :
                              'bg-gray-500'
                            }>
                              {item.type === 'bug' && <Bug className="w-3 h-3 mr-1" />}
                              {item.type === 'idea' && <Lightbulb className="w-3 h-3 mr-1" />}
                              {item.type === 'question' && <HelpCircle className="w-3 h-3 mr-1" />}
                              {item.type === 'bug' ? 'Bug' : item.type === 'idea' ? 'Idee' : 'Întrebare'}
                            </Badge>
                            
                            {/* Status badge */}
                            <Badge variant="outline" className={
                              item.status === 'new' ? 'border-red-400 text-red-600' :
                              item.status === 'in_progress' ? 'border-yellow-400 text-yellow-600' :
                              'border-green-400 text-green-600'
                            }>
                              {item.status === 'new' && <AlertCircle className="w-3 h-3 mr-1" />}
                              {item.status === 'in_progress' && <Clock className="w-3 h-3 mr-1" />}
                              {item.status === 'resolved' && <CheckCircle className="w-3 h-3 mr-1" />}
                              {item.status === 'new' ? 'Nou' : item.status === 'in_progress' ? 'În Lucru' : 'Rezolvat'}
                            </Badge>
                            
                            <span className="text-xs text-muted-foreground">
                              {new Date(item.created_at).toLocaleString('ro-RO')}
                            </span>
                          </div>
                          
                          {/* Message */}
                          <p className="text-sm mb-2 whitespace-pre-wrap">{item.message}</p>
                          
                          {/* Meta info */}
                          <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                            <span>📧 {item.email}</span>
                            {item.page && <span>📄 {item.page}</span>}
                          </div>
                        </div>
                        
                        {/* Action buttons */}
                        <div className="flex flex-col gap-1">
                          {item.status !== 'new' && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-xs border-red-300 text-red-600 hover:bg-red-50"
                              onClick={() => updateFeedbackStatus(item.id, 'new')}
                              data-testid={`feedback-status-new-${item.id}`}
                            >
                              🔴 Nou
                            </Button>
                          )}
                          {item.status !== 'in_progress' && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-xs border-yellow-300 text-yellow-600 hover:bg-yellow-50"
                              onClick={() => updateFeedbackStatus(item.id, 'in_progress')}
                              data-testid={`feedback-status-progress-${item.id}`}
                            >
                              🟡 În Lucru
                            </Button>
                          )}
                          {item.status !== 'resolved' && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-xs border-green-300 text-green-600 hover:bg-green-50"
                              onClick={() => updateFeedbackStatus(item.id, 'resolved')}
                              data-testid={`feedback-status-resolved-${item.id}`}
                            >
                              🟢 Rezolvat
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
