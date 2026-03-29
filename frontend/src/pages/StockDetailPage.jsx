import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, TrendingUp, TrendingDown, RefreshCw, Building2, Calendar, DollarSign, BarChart3, Activity } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import AddToWatchlistButton from '../components/AddToWatchlistButton';
import SocialShare from '../components/SocialShare';
import UnifiedChart from '../components/UnifiedChart';
import AITechnicalAnalysis from '../components/AITechnicalAnalysis';
import TradingCompanion, { TradingReminder, shouldShowReminder, markReminderShown } from '../components/TradingCompanion';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StockDetailPage() {
  const { type, symbol } = useParams();
  const { user, token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPeriod, setCurrentPeriod] = useState('1m');
  const [refreshing, setRefreshing] = useState(false);
  const [showReminder, setShowReminder] = useState(false);
  const [companionOpen, setCompanionOpen] = useState(false);
  
  // Check PRO status
  const [isPro, setIsPro] = useState(false);
  
  useEffect(() => {
    if (user && token) {
      fetch(`${API_URL}/api/subscriptions/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          const is_pro = data?.subscription?.is_pro || false;
          setIsPro(is_pro);
          console.log('[StockDetail] isPro:', is_pro);
        })
        .catch((err) => {
          console.error('[StockDetail] Failed to fetch subscription:', err);
          setIsPro(false);
        });
    }
  }, [user, token]);

  // Show reminder on first load (check only, don't mark as shown yet)
  useEffect(() => {
    if (shouldShowReminder(!!user)) {
      setShowReminder(true);
    }
  }, [user]);

  const handleCloseReminder = () => {
    setShowReminder(false);
    // Mark as shown only when user actually sees and closes it
    if (user) {
      markReminderShown();
    }
  };

  const handleOpenCompanion = () => {
    setShowReminder(false);
    setCompanionOpen(true);
    // Mark as shown when user opens companion
    if (user) {
      markReminderShown();
    }
  };

  const fetchDetails = useCallback(async (period = '1m', days = null) => {
    try {
      setRefreshing(true);
      
      // Pentru global, convertim perioada în formatul yfinance (1m -> 1mo, etc.)
      let apiPeriod = period;
      if (type === 'global') {
        const periodMapping = {
          '1d': '1d',
          '1w': '5d',
          '1m': '1mo',
          '3m': '3mo',
          '6m': '6mo',
          '1y': '1y',
          '5y': '5y'
        };
        apiPeriod = periodMapping[period] || '1mo';
      }
      
      const endpoint = type === 'global' 
        ? `${API_URL}/api/stocks/global/${encodeURIComponent(symbol)}/details?period=${apiPeriod}`
        : `${API_URL}/api/stocks/bvb/${symbol}/details?period=${period}${days ? `&days=${days}` : ''}`;
      
      const res = await fetch(endpoint);
      if (!res.ok) throw new Error('Failed to fetch');
      
      const result = await res.json();
      setData(result);
      setCurrentPeriod(period);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [type, symbol]);

  useEffect(() => {
    fetchDetails('1m');
  }, [fetchDetails]);

  const handleTimeframeChange = (period, days) => {
    fetchDetails(period, days);
  };

  const handleRefresh = () => {
    fetchDetails(currentPeriod);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-[500px]" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Nu s-au putut încărca datele pentru {symbol}</p>
        <Link to="/stocks">
          <Button className="mt-4"><ArrowLeft className="w-4 h-4 mr-2" /> Înapoi</Button>
        </Link>
      </div>
    );
  }

  const history = data.history || [];
  const lastPrice = history[history.length - 1]?.close || 0;
  const firstPrice = history[0]?.close || lastPrice;
  const priceChange = lastPrice - firstPrice;
  const percentChange = firstPrice > 0 ? ((priceChange / firstPrice) * 100) : 0;
  const isPositive = percentChange >= 0;

  // Calculate additional stats
  const highPrice = history.length > 0 ? Math.max(...history.map(h => h.high)) : 0;
  const lowPrice = history.length > 0 ? Math.min(...history.map(h => h.low)) : 0;
  const avgVolume = history.length > 0 ? Math.round(history.reduce((acc, h) => acc + (h.volume || 0), 0) / history.length) : 0;
  const totalVolume = history.reduce((acc, h) => acc + (h.volume || 0), 0);

  // Structured data pentru Google Rich Results
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "FinancialProduct",
    "name": `${data.name} (${data.symbol})`,
    "description": `Preț live ${data.name} - ${data.symbol} la ${data.exchange || 'BVB'}. Urmărește cotația în timp real, grafice istorice, volum de tranzacționare.`,
    "provider": {
      "@type": "Organization",
      "name": "FinRomania"
    },
    "offers": {
      "@type": "Offer",
      "price": data.price || lastPrice,
      "priceCurrency": data.currency || "RON"
    }
  };

  return (
    <div className="space-y-6">
      <SEO 
        title={`${data.name} (${data.symbol}) - Preț Live ${(data.price || lastPrice)?.toFixed(2)} ${data.currency || 'RON'}`}
        description={`Preț live ${data.name} (${data.symbol}) la ${data.exchange || 'BVB'}: ${(data.price || lastPrice)?.toFixed(2)} ${data.currency || 'RON'} (${isPositive ? '+' : ''}${(data.change_percent || percentChange)?.toFixed(2)}%). Grafice profesionale, analiză tehnică, date istorice.`}
        keywords={`${data.symbol} preț, ${data.name} cotație, ${data.symbol} live, ${data.symbol} grafic, acțiune ${data.symbol}, ${data.exchange || 'BVB'} ${data.symbol}`}
        structuredData={structuredData}
      />
      
      {/* Back Button */}
      <Link to="/stocks">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi la BVB
        </Button>
      </Link>

      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-bold">{data.name}</h1>
            <Badge variant="secondary" className="text-lg">{data.symbol}</Badge>
            {data.is_mock && <Badge variant="outline" className="bg-yellow-100">Demo</Badge>}
            {!data.is_mock && <Badge className="bg-green-100 text-green-800">Date Reale</Badge>}
          </div>
          <div className="flex items-center gap-4 text-muted-foreground">
            <span className="flex items-center gap-1">
              <Building2 className="w-4 h-4" />
              {data.exchange || 'BVB'}
            </span>
            <span className="flex items-center gap-1">
              <DollarSign className="w-4 h-4" />
              {data.currency || 'RON'}
            </span>
          </div>
        </div>
        
        <div className="text-left lg:text-right space-y-1">
          <p className="text-2xl sm:text-4xl font-bold">
            {lastPrice.toLocaleString('ro-RO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span className="text-lg font-normal text-muted-foreground ml-2">{data.currency || 'RON'}</span>
          </p>
          <p className={`flex items-center lg:justify-end text-lg ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
            {isPositive ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
            {isPositive ? '+' : ''}{priceChange.toFixed(2)} ({isPositive ? '+' : ''}{percentChange.toFixed(2)}%)
            <span className="text-muted-foreground text-sm ml-2">
              ({currentPeriod === '1d' ? '1 zi' : 
                currentPeriod === '1w' ? '1 săptămână' :
                currentPeriod === '1m' ? '30 zile' :
                currentPeriod === '3m' ? '3 luni' :
                currentPeriod === '6m' ? '6 luni' :
                currentPeriod === '1y' ? '1 an' : '5 ani'})
            </span>
          </p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4 flex-wrap">
        <AddToWatchlistButton symbol={data.symbol} type={type} name={data.name} />
        <SocialShare title={`${data.name} (${data.symbol})`} />
        <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizează
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <TrendingUp className="w-4 h-4 text-green-600" />
              <span className="text-sm">Maxim Perioadă</span>
            </div>
            <p className="text-2xl font-bold text-green-600">
              {highPrice.toLocaleString('ro-RO', { minimumFractionDigits: 2 })} {data.currency}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <TrendingDown className="w-4 h-4 text-red-600" />
              <span className="text-sm">Minim Perioadă</span>
            </div>
            <p className="text-2xl font-bold text-red-600">
              {lowPrice.toLocaleString('ro-RO', { minimumFractionDigits: 2 })} {data.currency}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <span className="text-sm">Volum Mediu</span>
            </div>
            <p className="text-2xl font-bold">
              {avgVolume.toLocaleString('ro-RO')}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-muted-foreground mb-1">
              <Activity className="w-4 h-4 text-blue-600" />
              <span className="text-sm">Volum Total</span>
            </div>
            <p className="text-2xl font-bold">
              {totalVolume.toLocaleString('ro-RO')}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Unified Chart (lightweight-charts) */}
      <UnifiedChart
        symbol={symbol}
        type={type}
        isPro={isPro}
        token={token}
      />

      {/* AI Technical Analysis - Only for BVB stocks */}
      {type === 'bvb' && (
        <AITechnicalAnalysis
          symbol={symbol}
          isPro={isPro}
          token={token}
        />
      )}

      {/* Price Info */}
      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Informații Preț
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
              <div>
                <p className="text-sm text-muted-foreground">Deschidere</p>
                <p className="text-xl font-bold">{history[history.length - 1]?.open?.toFixed(2)} {data.currency}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Închidere</p>
                <p className="text-xl font-bold">{history[history.length - 1]?.close?.toFixed(2)} {data.currency}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Max Zi</p>
                <p className="text-xl font-bold text-green-600">{history[history.length - 1]?.high?.toFixed(2)} {data.currency}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Min Zi</p>
                <p className="text-xl font-bold text-red-600">{history[history.length - 1]?.low?.toFixed(2)} {data.currency}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

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
            <CardTitle>Știri Legate de {data.symbol}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {data.related_news.map((article, idx) => (
                <Link 
                  key={article.id || idx} 
                  to={`/news/${article.id}`}
                  className="block p-3 rounded-lg hover:bg-muted/50 transition-colors border"
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

      {/* Financial Education CTA */}
      <Card className="bg-gradient-to-r from-green-600 to-blue-600 text-white border-0">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h3 className="text-lg font-bold mb-1">💰 Vrei Să Înveți Analiza Tehnică?</h3>
              <p className="text-green-100 text-sm">Află cum să citești graficele și indicatorii în cursul nostru gratuit de trading</p>
            </div>
            <div className="flex gap-3">
              <Link to="/trading-school">
                <Button className="bg-white text-green-600 hover:bg-green-50">
                  Școala de Trading →
                </Button>
              </Link>
              <Link to="/financial-education">
                <Button variant="outline" className="border-white text-white hover:bg-white/10">
                  Educație Financiară
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trading Reminder Modal */}
      <TradingReminder 
        isOpen={showReminder}
        onClose={handleCloseReminder}
        onOpenCompanion={handleOpenCompanion}
      />

      {/* Trading Companion */}
      <TradingCompanion 
        stockSymbol={symbol}
        stockName={data?.name || symbol}
        currentPrice={data?.price}
        changePercent={data?.change_percent}
        stockType={type}
        forceOpen={companionOpen}
        onOpenChange={setCompanionOpen}
      />
    </div>
  );
}
