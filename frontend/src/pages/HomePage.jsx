import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function StockCard({ stock, type = 'bvb' }) {
  const isPositive = stock.change_percent >= 0;
  const linkPath = type === 'global' 
    ? `/stocks/global/${encodeURIComponent(stock.symbol)}`
    : `/stocks/bvb/${stock.symbol}`;
  
  return (
    <Link to={linkPath}>
      <Card className="hover:shadow-lg transition-all hover:scale-[1.02] cursor-pointer h-full">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-2">
            <div>
              <p className="font-bold text-lg">{stock.symbol || stock.name}</p>
              <p className="text-sm text-muted-foreground truncate max-w-[120px]">{stock.name}</p>
            </div>
            {stock.is_mock && <Badge variant="outline" className="text-xs">MOCK</Badge>}
          </div>
          <div className="flex justify-between items-end">
            <p className="text-2xl font-bold">
              {stock.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
              <span className="text-sm font-normal text-muted-foreground ml-1">{stock.currency || ''}</span>
            </p>
            <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              <span className="font-medium">{isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function NewsCard({ article }) {
  return (
    <Link to={`/news/${article.id}`}>
      <Card className="hover:shadow-lg transition-all hover:scale-[1.01] cursor-pointer h-full">
        <CardContent className="p-4">
          <div className="flex gap-4">
            {article.image_url && (
              <img 
                src={article.image_url} 
                alt="" 
                className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                onError={(e) => e.target.style.display = 'none'}
              />
            )}
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold line-clamp-2 mb-1">{article.title}</h3>
              <p className="text-sm text-muted-foreground line-clamp-2">{article.description}</p>
              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                <span>{article.source?.name}</span>
                <span className="mx-2">•</span>
                <span>{new Date(article.published_at).toLocaleDateString('ro-RO')}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}

function CurrencyWidget({ currencies }) {
  const mainCurrencies = ['EUR', 'USD', 'GBP', 'CHF'];
  
  if (!currencies?.rates) return null;
  
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Curs Valutar BNR</CardTitle>
        <p className="text-xs text-muted-foreground">Data: {currencies.date}</p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {mainCurrencies.map(code => currencies.rates[code] && (
            <div key={code} className="flex justify-between items-center p-2 bg-muted/50 rounded">
              <span className="font-medium">{code}</span>
              <span className="font-bold">{currencies.rates[code].rate?.toFixed(4)} RON</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export default function HomePage() {
  const [bvbStocks, setBvbStocks] = useState([]);
  const [globalIndices, setGlobalIndices] = useState([]);
  const [news, setNews] = useState([]);
  const [currencies, setCurrencies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [bvbRes, globalRes, newsRes, currRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb`),
        fetch(`${API_URL}/api/stocks/global`),
        fetch(`${API_URL}/api/news?limit=6`),
        fetch(`${API_URL}/api/currencies`)
      ]);
      
      const [bvb, global, newsData, curr] = await Promise.all([
        bvbRes.json(),
        globalRes.json(),
        newsRes.json(),
        currRes.json()
      ]);
      
      setBvbStocks(bvb);
      setGlobalIndices(global);
      setNews(newsData);
      setCurrencies(curr);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex justify-between items-center">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Piața Financiară România</h1>
          <p className="text-muted-foreground">Acțiuni, indici și știri financiare în timp real</p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizează
        </Button>
      </div>

      {/* BVB Stocks */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            Bursa de Valori București
          </h2>
          <Link to="/stocks">
            <Button variant="ghost" size="sm">
              Vezi toate <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {bvbStocks.slice(0, 5).map(stock => (
            <StockCard key={stock.symbol} stock={stock} type="bvb" />
          ))}
        </div>
      </section>

      {/* Main Content Grid */}
      <div className="grid lg:grid-cols-4 gap-6">
        {/* News - Left side */}
        <div className="lg:col-span-3">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Newspaper className="w-5 h-5 text-blue-600" />
              Ultimele Știri Financiare
            </h2>
            <Link to="/news">
              <Button variant="ghost" size="sm">
                Vezi toate <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            {news.map((article, idx) => (
              <NewsCard key={article.id || idx} article={article} />
            ))}
          </div>
        </div>

        {/* Sidebar - Right side */}
        <div className="space-y-6">
          <CurrencyWidget currencies={currencies} />
          
          {/* Global Indices Compact */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">Indici Globali</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {globalIndices.slice(0, 4).map(index => {
                const isPositive = index.change_percent >= 0;
                return (
                  <Link 
                    key={index.symbol} 
                    to={`/stocks/global/${encodeURIComponent(index.symbol)}`}
                    className="flex justify-between items-center p-2 rounded hover:bg-muted/50 transition-colors"
                  >
                    <span className="font-medium text-sm">{index.name}</span>
                    <span className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                      {isPositive ? '+' : ''}{index.change_percent?.toFixed(2)}%
                    </span>
                  </Link>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
