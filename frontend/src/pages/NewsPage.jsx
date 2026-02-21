import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Newspaper, RefreshCw, Clock, Building2, Globe, Flag } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function NewsCard({ article, isInternational }) {
  const publishedDate = new Date(article.published_at);
  const timeAgo = getTimeAgo(publishedDate, isInternational);
  
  // Toate știrile se deschid pe platformă
  return (
    <Link to={`/news/${article.id}`}>
      <Card className="hover:shadow-lg transition-all duration-300 overflow-hidden group cursor-pointer">
        <CardContent className="p-0">
          <div className="flex flex-col md:flex-row">
            {article.image_url && (
              <div className="md:w-48 h-48 md:h-auto flex-shrink-0 overflow-hidden">
                <img 
                  src={article.image_url} 
                  alt="" 
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => e.target.parentElement.style.display = 'none'}
                />
              </div>
            )}
            <div className="flex-1 p-4">
              <div className="flex items-center gap-2 mb-2 flex-wrap">
                <Badge variant={isInternational ? "default" : "secondary"} className="text-xs">
                  {isInternational ? <Globe className="w-3 h-3 mr-1" /> : <Flag className="w-3 h-3 mr-1" />}
                  {article.source?.name || 'Unknown'}
                </Badge>
                {isInternational && (
                  <Badge variant="outline" className="text-xs">
                    🌍 EN
                  </Badge>
                )}
                <span className="text-xs text-muted-foreground flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  {timeAgo}
                </span>
              </div>
              <h3 className="font-semibold text-lg mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
                {article.title}
              </h3>
              <p className="text-sm text-muted-foreground line-clamp-3">
                {article.description || article.content}
              </p>
              <p className="text-sm text-blue-600 mt-3 font-medium">
                {isInternational ? 'Read article →' : 'Citește articolul →'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function getTimeAgo(date, isEnglish = false) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (isEnglish) {
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US');
  }
  
  if (diffMins < 60) return `acum ${diffMins} minute`;
  if (diffHours < 24) return `acum ${diffHours} ore`;
  if (diffDays < 7) return `acum ${diffDays} zile`;
  return date.toLocaleDateString('ro-RO');
}

export default function NewsPage() {
  const [roNews, setRoNews] = useState([]);
  const [intlNews, setIntlNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('romania');

  const fetchNews = async () => {
    try {
      const [roRes, intlRes] = await Promise.all([
        fetch(`${API_URL}/api/news/romania?limit=30`),
        fetch(`${API_URL}/api/news/international?limit=30`)
      ]);
      
      const roData = await roRes.json();
      const intlData = await intlRes.json();
      
      setRoNews(Array.isArray(roData) ? roData : []);
      setIntlNews(Array.isArray(intlData) ? intlData : []);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 300000); // 5 min
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/news`, { method: 'POST' }).catch(() => {});
    await fetchNews();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-12 w-full" />
        {[...Array(5)].map((_, i) => (
          <Skeleton key={i} className="h-48" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Newspaper className="w-8 h-8 text-blue-600" />
            Știri Financiare
          </h1>
          <p className="text-muted-foreground">Știri din România și surse internaționale</p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizează
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="romania" className="flex items-center gap-2">
            <span className="text-lg">🇷🇴</span>
            România & BVB
            <Badge variant="secondary" className="ml-1">{roNews.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="international" className="flex items-center gap-2">
            <span className="text-lg">🌍</span>
            Internațional
            <Badge variant="secondary" className="ml-1">{intlNews.length}</Badge>
          </TabsTrigger>
        </TabsList>

        {/* Romanian News Tab */}
        <TabsContent value="romania" className="space-y-4">
          {/* Stats for Romanian */}
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
            <CardContent className="p-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="text-sm text-muted-foreground">
                  {roNews.length} articole din surse românești
                </span>
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="outline">ZF</Badge>
                  <Badge variant="outline">Profit.ro</Badge>
                  <Badge variant="outline">Capital</Badge>
                  <Badge variant="outline">Economica</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Romanian News List */}
          <div className="space-y-4">
            {roNews.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Newspaper className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Nu sunt știri românești disponibile momentan.</p>
                  <Button onClick={handleRefresh} className="mt-4">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Încearcă din nou
                  </Button>
                </CardContent>
              </Card>
            ) : (
              roNews.map((article, idx) => (
                <NewsCard key={article.id || idx} article={article} isInternational={false} />
              ))
            )}
          </div>
        </TabsContent>

        {/* International News Tab */}
        <TabsContent value="international" className="space-y-4">
          {/* Stats for International */}
          <Card className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20">
            <CardContent className="p-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="text-sm text-muted-foreground">
                  {intlNews.length} articole din surse internaționale
                </span>
                <div className="flex gap-2 flex-wrap">
                  <Badge variant="outline">Yahoo Finance</Badge>
                  <Badge variant="outline">CNBC</Badge>
                  <Badge variant="outline">Reuters</Badge>
                  <Badge variant="outline">Bloomberg</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* International News List */}
          <div className="space-y-4">
            {intlNews.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <Globe className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Se încarcă știrile internaționale...</p>
                  <p className="text-xs text-muted-foreground mt-2">Prima încărcare poate dura câteva secunde.</p>
                  <Button onClick={handleRefresh} className="mt-4">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Încarcă știri
                  </Button>
                </CardContent>
              </Card>
            ) : (
              intlNews.map((article, idx) => (
                <NewsCard key={article.id || idx} article={article} isInternational={true} />
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Financial Education CTA */}
      <Card className="bg-gradient-to-r from-green-600 to-emerald-600 text-white border-0">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="text-center sm:text-left">
              <h3 className="font-bold">💰 Vrei Să Înțelegi Mai Bine Ce Citești?</h3>
              <p className="text-green-100 text-sm">15 lecții gratuite de educație financiară - de la bazele bugetării la investiții</p>
            </div>
            <Link to="/financial-education">
              <Button className="bg-white text-green-600 hover:bg-green-50 whitespace-nowrap">
                Începe Gratuit →
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
