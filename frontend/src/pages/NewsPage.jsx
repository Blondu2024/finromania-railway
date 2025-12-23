import React, { useState, useEffect } from 'react';
import { Newspaper, RefreshCw, ExternalLink, Clock, Building2 } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function NewsCard({ article }) {
  const publishedDate = new Date(article.published_at);
  const timeAgo = getTimeAgo(publishedDate);
  
  return (
    <Card className="hover:shadow-lg transition-all duration-300 overflow-hidden group">
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
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary" className="text-xs">
                <Building2 className="w-3 h-3 mr-1" />
                {article.source?.name || 'Unknown'}
              </Badge>
              <span className="text-xs text-muted-foreground flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {timeAgo}
              </span>
            </div>
            <h3 className="font-semibold text-lg mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
              {article.title}
            </h3>
            <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
              {article.description || article.content}
            </p>
            <a 
              href={article.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
            >
              Citește mai mult <ExternalLink className="w-3 h-3 ml-1" />
            </a>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function getTimeAgo(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 60) return `acum ${diffMins} minute`;
  if (diffHours < 24) return `acum ${diffHours} ore`;
  if (diffDays < 7) return `acum ${diffDays} zile`;
  return date.toLocaleDateString('ro-RO');
}

export default function NewsPage() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNews = async () => {
    try {
      const res = await fetch(`${API_URL}/api/news?limit=50`);
      const data = await res.json();
      setNews(data);
    } catch (error) {
      console.error('Error fetching news:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/news`, { method: 'POST' });
    await fetchNews();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
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
          <p className="text-muted-foreground">Ultimele știri din lumea financiară</p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizează Știrile
        </Button>
      </div>

      {/* Stats */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {news.length} articole disponibile
            </span>
            <Badge variant="outline">Actualizare automată la 15 minute</Badge>
          </div>
        </CardContent>
      </Card>

      {/* News List */}
      <div className="space-y-4">
        {news.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <Newspaper className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nu sunt știri disponibile momentan.</p>
              <Button onClick={handleRefresh} className="mt-4">
                <RefreshCw className="w-4 h-4 mr-2" />
                Încearcă din nou
              </Button>
            </CardContent>
          </Card>
        ) : (
          news.map((article, idx) => (
            <NewsCard key={article.url || idx} article={article} />
          ))
        )}
      </div>
    </div>
  );
}
