import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  Users, Activity, Brain, Eye, TrendingUp, Clock, 
  BarChart3, PieChart, RefreshCw, ChevronRight, Search,
  Zap, Award, BookOpen, Bell, Mail, Shield, AlertTriangle,
  ArrowUp, ArrowDown, Minus, Calendar, Globe
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Stat Card Component
const StatCard = ({ title, value, subtitle, icon: Icon, trend, trendValue, color = "blue", loading }) => {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    green: "from-green-500 to-green-600",
    slate: "from-slate-500 to-slate-600",
    orange: "from-orange-500 to-orange-600",
    pink: "from-pink-500 to-pink-600",
    cyan: "from-cyan-500 to-cyan-600",
  };

  const TrendIcon = trend === 'up' ? ArrowUp : trend === 'down' ? ArrowDown : Minus;
  const trendColor = trend === 'up' ? 'text-green-400' : trend === 'down' ? 'text-red-400' : 'text-gray-400';

  return (
    <Card className="relative overflow-hidden border-0 shadow-lg">
      <div className={`absolute inset-0 bg-gradient-to-br ${colorClasses[color]} opacity-10`} />
      <CardContent className="p-6 relative">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            {loading ? (
              <div className="h-8 w-20 bg-gray-200 dark:bg-gray-700 animate-pulse rounded mt-1" />
            ) : (
              <p className="text-3xl font-bold">{value}</p>
            )}
            {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
            {trendValue && (
              <div className={`flex items-center gap-1 mt-2 ${trendColor}`}>
                <TrendIcon className="w-3 h-3" />
                <span className="text-xs font-medium">{trendValue}</span>
              </div>
            )}
          </div>
          <div className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]}`}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Mini Chart Component
const MiniChart = ({ data, color = "#3b82f6" }) => {
  if (!data || data.length === 0) return null;
  
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((val - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg className="w-full h-16" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="2"
        vectorEffect="non-scaling-stroke"
      />
    </svg>
  );
};

// Users Table Component
const UsersTable = ({ users, loading, onViewUser }) => (
  <div className="overflow-x-auto">
    <table className="w-full">
      <thead>
        <tr className="border-b border-gray-200 dark:border-gray-700">
          <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Utilizator</th>
          <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Creat</th>
          <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Ultima Login</th>
          <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">Logins</th>
          <th className="text-center py-3 px-4 text-sm font-medium text-muted-foreground">AI Credits</th>
          <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Acțiuni</th>
        </tr>
      </thead>
      <tbody>
        {loading ? (
          [...Array(5)].map((_, i) => (
            <tr key={i} className="border-b border-gray-100 dark:border-gray-800">
              <td className="py-3 px-4"><div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 animate-pulse rounded" /></td>
              <td className="py-3 px-4"><div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 animate-pulse rounded" /></td>
              <td className="py-3 px-4"><div className="h-4 w-20 bg-gray-200 dark:bg-gray-700 animate-pulse rounded" /></td>
              <td className="py-3 px-4"><div className="h-4 w-8 bg-gray-200 dark:bg-gray-700 animate-pulse rounded mx-auto" /></td>
              <td className="py-3 px-4"><div className="h-4 w-16 bg-gray-200 dark:bg-gray-700 animate-pulse rounded mx-auto" /></td>
              <td className="py-3 px-4"><div className="h-4 w-12 bg-gray-200 dark:bg-gray-700 animate-pulse rounded ml-auto" /></td>
            </tr>
          ))
        ) : (
          users.map((user, i) => (
            <tr key={user.user_id || i} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              <td className="py-3 px-4">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-600 to-blue-400 flex items-center justify-center text-white text-sm font-medium">
                    {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{user.name || 'Fără nume'}</p>
                    <p className="text-xs text-muted-foreground">{user.email}</p>
                  </div>
                  {user.is_admin && (
                    <span className="px-2 py-0.5 bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 text-xs rounded-full">
                      Admin
                    </span>
                  )}
                </div>
              </td>
              <td className="py-3 px-4 text-sm text-muted-foreground">
                {user.created_at ? new Date(user.created_at).toLocaleDateString('ro-RO') : '-'}
              </td>
              <td className="py-3 px-4 text-sm text-muted-foreground">
                {user.last_login ? new Date(user.last_login).toLocaleDateString('ro-RO') : '-'}
              </td>
              <td className="py-3 px-4 text-center">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 text-xs rounded-full font-medium">
                  {user.total_logins || 0}
                </span>
              </td>
              <td className="py-3 px-4 text-center">
                <div className="flex items-center justify-center gap-2">
                  <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all ${
                        user.ai_limit_reached ? 'bg-red-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${Math.min(100, ((user.ai_credits_used || 0) / 10) * 100)}%` }}
                    />
                  </div>
                  <span className={`text-xs font-medium ${user.ai_limit_reached ? 'text-red-500' : ''}`}>
                    {user.ai_credits_used || 0}/10
                  </span>
                </div>
              </td>
              <td className="py-3 px-4 text-right">
                <Button variant="ghost" size="sm" onClick={() => onViewUser(user)}>
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </td>
            </tr>
          ))
        )}
      </tbody>
    </table>
  </div>
);

// Page Analytics Component
const TopPages = ({ pages, loading }) => (
  <div className="space-y-3">
    {loading ? (
      [...Array(5)].map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 animate-pulse rounded" />
        </div>
      ))
    ) : (
      pages.slice(0, 8).map((page, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="w-6 text-center text-sm font-medium text-muted-foreground">#{i + 1}</div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium truncate">{page.page || '/'}</span>
              <span className="text-sm text-muted-foreground">{page.views}</span>
            </div>
            <div className="w-full h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 to-blue-400 rounded-full"
                style={{ width: `${(page.views / (pages[0]?.views || 1)) * 100}%` }}
              />
            </div>
          </div>
        </div>
      ))
    )}
  </div>
);

// Main Dashboard Component
export default function AdminDashboardPro() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  const [pageAnalytics, setPageAnalytics] = useState(null);
  const [aiAnalytics, setAiAnalytics] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [realtime, setRealtime] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('overview');

  // Check admin access
  useEffect(() => {
    if (!user) {
      navigate('/');
      return;
    }
    // Allow specific emails or is_admin flag
    const allowedEmails = ['tanasecristian2007@gmail.com', 'contact@finromania.ro'];
    if (!user.is_admin && !allowedEmails.includes(user.email)) {
      navigate('/');
    }
  }, [user, navigate]);

  const fetchData = useCallback(async () => {
    if (!token) return;
    
    setLoading(true);
    
    try {
      const headers = { 'Authorization': `Bearer ${token}` };
      
      // Fetch all data in parallel
      const [overviewRes, usersRes, pagesRes, aiRes, growthRes, realtimeRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/v2/overview`, { headers }),
        fetch(`${API_URL}/api/admin/v2/users/list?limit=25`, { headers }),
        fetch(`${API_URL}/api/admin/v2/analytics/pages?days=7`, { headers }),
        fetch(`${API_URL}/api/admin/v2/analytics/ai-usage?days=7`, { headers }),
        fetch(`${API_URL}/api/admin/v2/analytics/growth?days=30`, { headers }),
        fetch(`${API_URL}/api/admin/v2/realtime`, { headers }),
      ]);

      if (overviewRes.ok) setOverview(await overviewRes.json());
      if (usersRes.ok) setUsers((await usersRes.json()).users);
      if (pagesRes.ok) setPageAnalytics(await pagesRes.json());
      if (aiRes.ok) setAiAnalytics(await aiRes.json());
      if (growthRes.ok) setGrowth(await growthRes.json());
      if (realtimeRes.ok) setRealtime(await realtimeRes.json());
      
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
    // Refresh realtime data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const filteredUsers = users.filter(u => 
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Admin Dashboard</h1>
                <p className="text-xs text-muted-foreground">FinRomania Analytics</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              {realtime && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-sm font-medium text-green-700 dark:text-green-400">
                    {realtime.active_sessions} activi
                  </span>
                </div>
              )}
              <Button variant="outline" size="sm" onClick={fetchData} disabled={loading}>
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {[
            { id: 'overview', label: 'Prezentare', icon: PieChart },
            { id: 'users', label: 'Utilizatori', icon: Users },
            { id: 'analytics', label: 'Analytics', icon: Activity },
            { id: 'ai', label: 'AI Usage', icon: Brain },
          ].map(tab => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'default' : 'outline'}
              size="sm"
              onClick={() => setActiveTab(tab.id)}
              className="whitespace-nowrap"
            >
              <tab.icon className="w-4 h-4 mr-2" />
              {tab.label}
            </Button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Main Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                title="Total Utilizatori"
                value={overview?.users?.total || 0}
                subtitle={`+${overview?.users?.new_this_week || 0} săptămâna asta`}
                icon={Users}
                color="blue"
                loading={loading}
                trend="up"
                trendValue={`+${overview?.users?.new_today || 0} azi`}
              />
              <StatCard
                title="Activi (24h)"
                value={overview?.users?.active_24h || 0}
                subtitle={`${overview?.users?.active_7d || 0} în 7 zile`}
                icon={Activity}
                color="green"
                loading={loading}
              />
              <StatCard
                title="AI Requests"
                value={overview?.ai_usage?.total_credits_used || 0}
                subtitle={`${overview?.ai_usage?.requests_today || 0} azi`}
                icon={Brain}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="Page Views"
                value={overview?.page_views?.today || 0}
                subtitle={`${overview?.page_views?.this_week || 0} săptămâna asta`}
                icon={Eye}
                color="orange"
                loading={loading}
              />
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                title="Sesiuni Active"
                value={overview?.sessions?.active_now || 0}
                subtitle="în acest moment"
                icon={Globe}
                color="cyan"
                loading={loading}
              />
              <StatCard
                title="Timp Mediu"
                value={overview?.sessions?.avg_duration_formatted || '0m 0s'}
                subtitle="per sesiune"
                icon={Clock}
                color="pink"
                loading={loading}
              />
              <StatCard
                title="Newsletter"
                value={overview?.engagement?.newsletter_subscribers || 0}
                subtitle="abonați"
                icon={Mail}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="La Limită AI"
                value={overview?.ai_usage?.users_at_limit || 0}
                subtitle={`limită: ${overview?.ai_usage?.monthly_limit_per_user || 10}/lună`}
                icon={AlertTriangle}
                color="orange"
                loading={loading}
              />
            </div>

            {/* Engagement Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                title="Watchlist Items"
                value={overview?.engagement?.watchlist_items || 0}
                icon={Award}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="Quiz-uri Complete"
                value={overview?.engagement?.quiz_completions || 0}
                icon={BookOpen}
                color="green"
                loading={loading}
              />
              <StatCard
                title="Lecții Finalizate"
                value={overview?.engagement?.lessons_completed || 0}
                icon={TrendingUp}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="Sesiuni Azi"
                value={overview?.sessions?.today || 0}
                icon={Calendar}
                color="cyan"
                loading={loading}
              />
            </div>

            {/* Charts Row */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Top Pages */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Eye className="w-5 h-5" />
                    Top Pagini Vizitate
                  </CardTitle>
                  <CardDescription>Ultimele 7 zile</CardDescription>
                </CardHeader>
                <CardContent>
                  <TopPages pages={pageAnalytics?.top_pages || []} loading={loading} />
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Activitate Recentă
                  </CardTitle>
                  <CardDescription>Ultimele logări și înregistrări</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {realtime?.latest_signups?.slice(0, 5).map((signup, i) => (
                      <div key={i} className="flex items-center gap-3 p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
                        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
                          <Users className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{signup.email}</p>
                          <p className="text-xs text-muted-foreground">
                            {signup.created_at ? new Date(signup.created_at).toLocaleString('ro-RO') : '-'}
                          </p>
                        </div>
                        <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-800 text-green-800 dark:text-green-200 rounded-full">
                          Nou
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Toți Utilizatorii</CardTitle>
                    <CardDescription>{users.length} utilizatori înregistrați</CardDescription>
                  </div>
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <Input
                      placeholder="Caută utilizator..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <UsersTable 
                  users={filteredUsers} 
                  loading={loading} 
                  onViewUser={(u) => console.log('View user:', u)}
                />
              </CardContent>
            </Card>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-6">
            {/* Growth Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Creștere Utilizatori
                </CardTitle>
                <CardDescription>Ultimele 30 de zile</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-48">
                  <MiniChart 
                    data={growth?.daily_growth?.map(d => d.total_users) || []} 
                    color="#3b82f6"
                  />
                </div>
                <div className="flex justify-between mt-4 text-sm text-muted-foreground">
                  <span>30 zile în urmă</span>
                  <span className="font-medium text-foreground">
                    +{growth?.total_new_users || 0} utilizatori noi
                  </span>
                  <span>Azi</span>
                </div>
              </CardContent>
            </Card>

            {/* Daily Views Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="w-5 h-5" />
                  Vizualizări Zilnice
                </CardTitle>
                <CardDescription>Ultimele 7 zile</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-7 gap-2">
                  {pageAnalytics?.daily_views?.map((day, i) => (
                    <div key={i} className="text-center">
                      <div className="h-24 bg-gray-100 dark:bg-gray-800 rounded-lg relative overflow-hidden">
                        <div 
                          className="absolute bottom-0 w-full bg-gradient-to-t from-blue-500 to-blue-400 transition-all"
                          style={{ 
                            height: `${(day.views / Math.max(...pageAnalytics.daily_views.map(d => d.views), 1)) * 100}%` 
                          }}
                        />
                      </div>
                      <p className="text-xs mt-2 font-medium">{day.views}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(day.date).toLocaleDateString('ro-RO', { weekday: 'short' })}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* AI Tab */}
        {activeTab === 'ai' && (
          <div className="space-y-6">
            {/* AI Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                title="Total Credite"
                value={aiAnalytics?.total_credits_used || overview?.ai_usage?.total_credits_used || 0}
                icon={Brain}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="Requests Azi"
                value={overview?.ai_usage?.requests_today || 0}
                icon={Zap}
                color="orange"
                loading={loading}
              />
              <StatCard
                title="Limită Lunară"
                value={`${overview?.ai_usage?.monthly_limit_per_user || 10}/user`}
                icon={Shield}
                color="blue"
                loading={loading}
              />
              <StatCard
                title="La Limită"
                value={overview?.ai_usage?.users_at_limit || 0}
                subtitle="utilizatori"
                icon={AlertTriangle}
                color="pink"
                loading={loading}
              />
            </div>

            {/* Top AI Users */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  Top Utilizatori AI
                </CardTitle>
                <CardDescription>Sortați după credite consumate</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {aiAnalytics?.top_users?.map((u, i) => (
                    <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white text-sm font-bold">
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{u.email}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full transition-all ${
                                u.usage_percent >= 100 ? 'bg-red-500' : u.usage_percent >= 80 ? 'bg-yellow-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${Math.min(100, u.usage_percent)}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {u.ai_credits_used}/10
                          </span>
                        </div>
                      </div>
                      {u.usage_percent >= 100 && (
                        <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs rounded-full">
                          Limitat
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* AI Usage by Feature */}
            <Card>
              <CardHeader>
                <CardTitle>Utilizare per Funcție</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {aiAnalytics?.usage_by_feature?.map((f, i) => (
                    <div key={i} className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 text-center">
                      <p className="text-2xl font-bold">{f.count}</p>
                      <p className="text-sm text-muted-foreground capitalize">
                        {f.feature?.replace(/_/g, ' ') || 'Necunoscut'}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
