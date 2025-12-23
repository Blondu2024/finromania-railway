import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, RefreshCw, ExternalLink } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StockDetailPage() {
  const { type, symbol } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        setLoading(true);
        const endpoint = type === 'global' 
          ? `${API_URL}/api/stocks/global/${encodeURIComponent(symbol)}/details`
          : `${API_URL}/api/stocks/bvb/${symbol}/details`;
        
        const res = await fetch(endpoint);
        if (!res.ok) throw new Error('Failed to fetch');
        
        const result = await res.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [type, symbol]);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-96" />
        <Skeleton className="h-48" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Nu s-au putut încărca datele pentru {symbol}</p>
        <Link to="/">
          <Button className="mt-4"><ArrowLeft className="w-4 h-4 mr-2" /> Înapoi</Button>
        </Link>
      </div>
    );
  }

  const lastPrice = data.history?.[data.history.length - 1]?.close || 0;
  const firstPrice = data.history?.[0]?.close || lastPrice;
  const priceChange = lastPrice - firstPrice;
  const percentChange = firstPrice > 0 ? ((priceChange / firstPrice) * 100) : 0;
  const isPositive = percentChange >= 0;

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link to={type === 'bvb' ? '/stocks' : '/'}>
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
        </Button>
      </Link>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-bold">{data.name}</h1>
            <Badge variant="secondary">{data.symbol}</Badge>
            {data.is_mock && <Badge variant="outline">MOCK</Badge>}
          </div>
          <p className="text-muted-foreground">{data.exchange} • {data.currency}</p>
        </div>
        <div className="text-right">
          <p className="text-4xl font-bold">
            {lastPrice.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
            <span className="text-lg font-normal text-muted-foreground ml-2">{data.currency}</span>
          </p>
          <p className={`flex items-center justify-end text-lg ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
            {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({isPositive ? '+' : ''}{percentChange.toFixed(2)}%)
            <span className="text-muted-foreground text-sm ml-2">30 zile</span>
          </p>
        </div>
      </div>

      {/* Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Grafic Preț - Ultimele 30 Zile</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  tickFormatter={(val) => new Date(val).toLocaleDateString('ro-RO', { day: 'numeric', month: 'short' })}
                />
                <YAxis 
                  domain={['auto', 'auto']}
                  tick={{ fontSize: 12 }}
                  tickFormatter={(val) => val.toLocaleString('ro-RO')}
                />
                <Tooltip 
                  formatter={(val) => [val.toLocaleString('ro-RO', { maximumFractionDigits: 2 }) + ' ' + data.currency, 'Preț']}
                  labelFormatter={(label) => new Date(label).toLocaleDateString('ro-RO', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                />
                <Line 
                  type="monotone" 
                  dataKey="close" 
                  stroke={isPositive ? '#16a34a' : '#dc2626'}
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Description */}
      {data.description && (
        <Card>
          <CardHeader>
            <CardTitle>Despre {data.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{data.description}</p>
          </CardContent>
        </Card>
      )}

      {/* Related News */}
      {data.related_news && data.related_news.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Știri Legate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.related_news.map((article, idx) => (
                <Link 
                  key={article.id || idx} 
                  to={`/news/${article.id}`}
                  className="block p-3 rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <h4 className="font-semibold line-clamp-2">{article.title}</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    {article.source?.name} • {new Date(article.published_at).toLocaleDateString('ro-RO')}
                  </p>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
