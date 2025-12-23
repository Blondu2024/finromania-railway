import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, Users, BarChart3, Newspaper, Star, Mail, TrendingUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Skeleton } from '../components/ui/skeleton';
import { Badge } from '../components/ui/badge';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.is_admin) fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [statsRes, analyticsRes, usersRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/stats`, { credentials: 'include' }),
        fetch(`${API_URL}/api/admin/analytics/visits?days=7`, { credentials: 'include' }),
        fetch(`${API_URL}/api/admin/users?limit=10`, { credentials: 'include' })
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (analyticsRes.ok) setAnalytics(await analyticsRes.json());
      if (usersRes.ok) {
        const data = await usersRes.json();
        setUsers(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold">Acces Restricționat</h2>
        <p className="text-muted-foreground">Trebuie să fii conectat.</p>
      </div>
    );
  }

  if (!user.is_admin) {
    return (
      <div className="text-center py-12">
        <Shield className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold">Acces Interzis</h2>
        <p className="text-muted-foreground">Nu ai permisiuni de administrator.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <div className="grid md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Shield className="w-8 h-8 text-purple-600" />
          Dashboard Admin
        </h1>
        <p className="text-muted-foreground">Statistici și administrare platformă</p>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Users className="w-4 h-4" />
                <span className="text-sm">Utilizatori</span>
              </div>
              <p className="text-2xl font-bold">{stats.totals?.users || 0}</p>
              <p className="text-xs text-green-600">+{stats.last_7_days?.new_users || 0} săptămâna asta</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Newspaper className="w-4 h-4" />
                <span className="text-sm">Articole</span>
              </div>
              <p className="text-2xl font-bold">{stats.totals?.articles || 0}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Star className="w-4 h-4" />
                <span className="text-sm">Watchlist</span>
              </div>
              <p className="text-2xl font-bold">{stats.totals?.watchlist_items || 0}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <TrendingUp className="w-4 h-4" />
                <span className="text-sm">Tranzacții</span>
              </div>
              <p className="text-2xl font-bold">{stats.totals?.portfolio_transactions || 0}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-muted-foreground mb-1">
                <Mail className="w-4 h-4" />
                <span className="text-sm">Newsletter</span>
              </div>
              <p className="text-2xl font-bold">{stats.totals?.newsletter_subscribers || 0}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Today's Activity */}
      {stats && (
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Login-uri Azi</p>
              <p className="text-3xl font-bold">{stats.today?.logins || 0}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Vizite Azi</p>
              <p className="text-3xl font-bold">{stats.today?.page_visits || 0}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Analytics Chart */}
      {analytics.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Activitate Ultimele 7 Zile</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={analytics}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="visits" stroke="#3b82f6" name="Vizite" strokeWidth={2} />
                  <Line type="monotone" dataKey="logins" stroke="#10b981" name="Login-uri" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Users */}
      <Card>
        <CardHeader>
          <CardTitle>Utilizatori Recenți</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {users.map((u, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-3">
                  {u.picture ? (
                    <img src={u.picture} alt="" className="w-10 h-10 rounded-full" />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                      <span className="text-blue-600 font-bold">{u.name?.[0]}</span>
                    </div>
                  )}
                  <div>
                    <p className="font-medium">{u.name}</p>
                    <p className="text-sm text-muted-foreground">{u.email}</p>
                  </div>
                </div>
                <div className="text-right">
                  {u.is_admin && <Badge variant="secondary">Admin</Badge>}
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(u.created_at).toLocaleDateString('ro-RO')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
