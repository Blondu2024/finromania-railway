import React, { useState, useEffect } from 'react';
import { Shield, Crown, Users, TrendingUp } from 'lucide-react';
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

  useEffect(() => {
    if (user && token && user.is_admin) {
      fetchStats();
      fetchUsers();
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
          </div>
        )}

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
                <div key={u.user_id} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div>
                    <p className="font-semibold">{u.email}</p>
                    <p className="text-sm text-muted-foreground">{u.name}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge className={u.subscription_level === 'pro' ? 'bg-amber-500' : 'bg-gray-500'}>
                      {u.subscription_level?.toUpperCase() || 'FREE'}
                    </Badge>
                    {u.is_admin && <Badge className="bg-blue-500">ADMIN</Badge>}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setTargetEmail(u.email)}
                    >
                      Modifică
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
