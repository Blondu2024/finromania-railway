import React, { useState, useEffect } from 'react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import { TrendingUp, TrendingDown, BarChart3, Clock, Lock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function DailySummaryPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await fetch(`${API_URL}/api/daily-summary/preview`);
        if (!res.ok) throw new Error('Nu s-au putut încărca datele');
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchSummary();
  }, []);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-4" data-testid="daily-summary-loading">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto text-center py-16" data-testid="daily-summary-error">
        <p className="text-muted-foreground">Nu s-a putut încărca rezumatul zilei.</p>
      </div>
    );
  }

  const md = data.market_data || {};
  const gainers = md.top_gainers || [];
  const losers = md.top_losers || [];
  const sentiment = md.sentiment || {};

  return (
    <div className="max-w-3xl mx-auto space-y-6" data-testid="daily-summary-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            Rezumatul Zilei BVB
          </h1>
          <p className="text-muted-foreground text-sm flex items-center gap-1 mt-1">
            <Clock className="w-3.5 h-3.5" />
            {data.date}
          </p>
        </div>
        <Badge variant={md.avg_change >= 0 ? 'default' : 'destructive'} className="text-lg px-3 py-1">
          {md.avg_change >= 0 ? '+' : ''}{md.avg_change?.toFixed(2)}%
        </Badge>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3">
        <Card data-testid="stat-positive">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Creșteri</p>
            <p className="text-2xl font-bold text-green-600">{sentiment.positive || 0}</p>
          </CardContent>
        </Card>
        <Card data-testid="stat-negative">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Scăderi</p>
            <p className="text-2xl font-bold text-red-600">{sentiment.negative || 0}</p>
          </CardContent>
        </Card>
        <Card data-testid="stat-neutral">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground">Neutre</p>
            <p className="text-2xl font-bold text-gray-500">{sentiment.neutral || 0}</p>
          </CardContent>
        </Card>
      </div>

      {/* AI Analysis */}
      <Card data-testid="ai-summary-card">
        <CardContent className="p-5">
          <h2 className="text-sm font-semibold text-muted-foreground mb-3 uppercase tracking-wide">Analiza Zilei</h2>
          <p className="text-foreground leading-relaxed">{data.ai_summary}</p>
        </CardContent>
      </Card>

      {/* Top Gainers & Losers */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card data-testid="top-gainers">
          <CardContent className="p-4">
            <h3 className="text-sm font-semibold text-green-600 mb-3 flex items-center gap-1">
              <TrendingUp className="w-4 h-4" /> Top Creșteri
            </h3>
            <div className="space-y-2">
              {gainers.map((s, i) => (
                <Link key={i} to={`/stocks/bvb/${s.symbol}`} className="flex items-center justify-between hover:bg-accent rounded px-2 py-1.5 transition-colors">
                  <div>
                    <span className="font-semibold text-sm">{s.symbol}</span>
                    <span className="text-xs text-muted-foreground ml-2">{s.name?.substring(0, 18)}</span>
                  </div>
                  <span className="text-green-600 font-bold text-sm">+{s.change_percent?.toFixed(2)}%</span>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card data-testid="top-losers">
          <CardContent className="p-4">
            <h3 className="text-sm font-semibold text-red-600 mb-3 flex items-center gap-1">
              <TrendingDown className="w-4 h-4" /> Top Scăderi
            </h3>
            <div className="space-y-2">
              {losers.map((s, i) => (
                <Link key={i} to={`/stocks/bvb/${s.symbol}`} className="flex items-center justify-between hover:bg-accent rounded px-2 py-1.5 transition-colors">
                  <div>
                    <span className="font-semibold text-sm">{s.symbol}</span>
                    <span className="text-xs text-muted-foreground ml-2">{s.name?.substring(0, 18)}</span>
                  </div>
                  <span className="text-red-600 font-bold text-sm">{s.change_percent?.toFixed(2)}%</span>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Email Subscribe CTA */}
      {!user && (
        <Card className="border-blue-200 dark:border-blue-800" data-testid="subscribe-cta">
          <CardContent className="p-5 text-center">
            <Lock className="w-5 h-5 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground mb-3">Primește rezumatul zilnic pe email la 18:10</p>
            <Link to="/login">
              <Button size="sm">Conectează-te pentru abonare</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground text-center">
        Informații educative, NU sfaturi de investiții. Datele pot conține erori.
      </p>
    </div>
  );
}
