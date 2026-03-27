import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { 
  Users, Activity, Brain, LogIn, TrendingUp, 
  Calendar, Shield, AlertCircle 
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AdminDashboard() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [aiStats, setAiStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    
    if (!user.is_admin) {
      navigate('/');
      return;
    }

    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      const [dashboardRes, aiStatsRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/dashboard`, { headers }),
        fetch(`${API_URL}/api/admin/ai-stats?days=7`, { headers })
      ]);

      if (!dashboardRes.ok || !aiStatsRes.ok) {
        throw new Error('Nu ai acces la dashboard');
      }

      const dashboardData = await dashboardRes.json();
      const aiStatsData = await aiStatsRes.json();

      setDashboard(dashboardData);
      setAiStats(aiStatsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!user?.is_admin) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <Shield className="w-16 h-16 mx-auto text-red-500 mb-4" />
            <h2 className="text-xl font-bold mb-2">Acces Restricționat</h2>
            <p className="text-muted-foreground">
              Această pagină este disponibilă doar pentru administratori.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
            <h2 className="text-xl font-bold mb-2">Eroare</h2>
            <p className="text-muted-foreground">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-600" />
          Admin Dashboard
        </h1>
        <Badge variant="outline" className="text-green-600 border-green-600">
          Admin: {user.email}
        </Badge>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Utilizatori</p>
                <p className="text-3xl font-bold">{dashboard?.overview?.total_users || 0}</p>
              </div>
              <Users className="w-10 h-10 text-blue-500 opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Login-uri</p>
                <p className="text-3xl font-bold">{dashboard?.overview?.total_logins || 0}</p>
              </div>
              <LogIn className="w-10 h-10 text-green-500 opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Credite AI Folosite</p>
                <p className="text-3xl font-bold">{dashboard?.overview?.total_ai_credits_used || 0}</p>
              </div>
              <Brain className="w-10 h-10 text-blue-500 opacity-50" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Interacțiuni AI</p>
                <p className="text-3xl font-bold">{dashboard?.overview?.companion_interactions || 0}</p>
              </div>
              <Activity className="w-10 h-10 text-orange-500 opacity-50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Today's Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Activitate Azi
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-4xl font-bold text-green-600">{dashboard?.today?.logins || 0}</p>
              <p className="text-sm text-muted-foreground">Login-uri</p>
            </div>
            <div className="text-center p-4 bg-muted/50 rounded-lg">
              <p className="text-4xl font-bold text-blue-600">{dashboard?.today?.ai_requests || 0}</p>
              <p className="text-sm text-muted-foreground">Cereri AI</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* AI Usage Stats */}
      {aiStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5" />
              Utilizare AI (Ultimele 7 zile)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Daily chart simple */}
              <div className="flex items-end gap-1 h-24">
                {aiStats.daily_usage?.map((day, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-blue-500 rounded-t"
                      style={{ 
                        height: `${Math.max(4, (day.credits / Math.max(...aiStats.daily_usage.map(d => d.credits || 1))) * 80)}px` 
                      }}
                    />
                    <span className="text-xs text-muted-foreground mt-1">
                      {new Date(day.date).toLocaleDateString('ro-RO', { weekday: 'short' })}
                    </span>
                  </div>
                ))}
              </div>

              {/* Top Users */}
              {aiStats.top_users?.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Top Utilizatori AI</h4>
                  <div className="space-y-2">
                    {aiStats.top_users.slice(0, 5).map((u, i) => (
                      <div key={i} className="flex items-center justify-between p-2 bg-muted/30 rounded">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{i + 1}</Badge>
                          <span className="text-sm">{u.email}</span>
                        </div>
                        <Badge className="bg-blue-600">
                          {u.ai_credits_used} credite
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Usage by Feature */}
              {aiStats.usage_by_feature?.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Utilizare pe Funcționalitate</h4>
                  <div className="flex flex-wrap gap-2">
                    {aiStats.usage_by_feature.map((f, i) => (
                      <Badge key={i} variant="secondary">
                        {f.feature}: {f.count}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Users */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Utilizatori Recenți
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Email</th>
                  <th className="text-left py-2">Nume</th>
                  <th className="text-center py-2">Login-uri</th>
                  <th className="text-center py-2">Credite AI</th>
                  <th className="text-left py-2">Ultima conectare</th>
                  <th className="text-center py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {dashboard?.recent_users?.map((u, i) => (
                  <tr key={i} className="border-b hover:bg-muted/50">
                    <td className="py-2">{u.email}</td>
                    <td className="py-2">{u.name || '-'}</td>
                    <td className="text-center py-2">{u.total_logins || 0}</td>
                    <td className="text-center py-2">
                      <Badge variant="outline" className="text-blue-600">
                        {u.ai_credits_used || 0}
                      </Badge>
                    </td>
                    <td className="py-2 text-muted-foreground">
                      {u.last_login ? new Date(u.last_login).toLocaleString('ro-RO') : '-'}
                    </td>
                    <td className="text-center py-2">
                      {u.is_admin ? (
                        <Badge className="bg-blue-600">Admin</Badge>
                      ) : (
                        <Badge variant="secondary">User</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
