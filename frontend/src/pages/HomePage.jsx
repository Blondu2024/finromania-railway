import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function StockCard({ stock }) {
  const isPositive = stock.change_percent >= 0;
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <div>
            <p className="font-bold text-lg">{stock.symbol}</p>
            <p className="text-sm text-muted-foreground truncate max-w-[120px]">{stock.name}</p>
          </div>
          {stock.is_mock && <Badge variant="outline" className="text-xs">MOCK</Badge>}
        </div>
        <div className="flex justify-between items-end">
          <p className="text-2xl font-bold">{stock.price?.toFixed(2)} <span className="text-sm font-normal text-muted-foreground">{stock.currency || 'RON'}</span></p>
          <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            <span className="font-medium">{isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function IndexCard({ index }) {
  const isPositive = index.change_percent >= 0;
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <p className="font-bold text-lg">{index.name}</p>
          <Badge variant="secondary" className="text-xs">{index.symbol}</Badge>
        </div>
        <div className="flex justify-between items-end">
          <p className="text-xl font-bold">{index.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}</p>
          <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
            <span className="font-medium">{isPositive ? '+' : ''}{index.change_percent?.toFixed(2)}%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function NewsCard({ article }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
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
        <div className="grid grid-cols-2 gap-4">
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
        fetch(`${API_URL}/api/news?limit=5`),
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
    const interval = setInterval(fetchData, 60000); // Refresh every minute
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
            <StockCard key={stock.symbol} stock={stock} />
          ))}
        </div>
      </section>

      {/* Global Indices & Currencies */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Indici Globali</h2>
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            {globalIndices.map(index => (
              <IndexCard key={index.symbol} index={index} />
            ))}
          </div>
        </div>
        <div>
          <CurrencyWidget currencies={currencies} />
        </div>
      </div>

      {/* News */}
      <section>
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
            <a key={idx} href={article.url} target="_blank" rel="noopener noreferrer">
              <NewsCard article={article} />
            </a>
          ))}
        </div>
      </section>
    </div>
  );
}
