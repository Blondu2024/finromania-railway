import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Globe, TrendingUp, TrendingDown, RefreshCw, Clock, Flame,
  DollarSign, Coins, BarChart3, Zap, Building2, Timer,
  ChevronRight, Sparkles, Activity, X, Calendar, ArrowUp, ArrowDown
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Skeleton } from '../components/ui/skeleton';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Area, AreaChart,
  CartesianGrid, ReferenceLine
} from 'recharts';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// GLOBAL SENTIMENT GAUGE
// ============================================
const GlobalSentimentGauge = ({ sentiment }) => {
  const score = useMemo(() => {
    if (!sentiment) return 50;
    const ratio = sentiment.gainers / (sentiment.gainers + sentiment.losers || 1);
    return Math.round(ratio * 100);
  }, [sentiment]);

  const getLabel = (s) => {
    if (s >= 70) return { text: 'BULLISH 🐂', color: 'text-green-500' };
    if (s >= 55) return { text: 'UȘOR BULLISH', color: 'text-green-400' };
    if (s >= 45) return { text: 'NEUTRU', color: 'text-yellow-500' };
    if (s >= 30) return { text: 'UȘOR BEARISH', color: 'text-orange-500' };
    return { text: 'BEARISH 🐻', color: 'text-red-500' };
  };

  const label = getLabel(score);

  return (
    <Card className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white border-0">
      <CardContent className="p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          Sentiment Global
        </h3>
        
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-3xl font-bold ${label.color}`}>{score}%</p>
            <p className={`font-semibold ${label.color}`}>{label.text}</p>
          </div>
          
          <div className="text-right text-sm">
            <p className="text-green-400">📈 {sentiment?.gainers || 0} în creștere</p>
            <p className="text-red-400">📉 {sentiment?.losers || 0} în scădere</p>
            <p className="text-blue-300 mt-2">
              Media: {sentiment?.avg_change >= 0 ? '+' : ''}{sentiment?.avg_change?.toFixed(2)}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// MARKET STATUS COMPONENT
// ============================================
const MarketStatusBar = ({ marketStatus }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {Object.entries(marketStatus || {}).map(([key, market]) => (
        <motion.div
          key={key}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`rounded-xl p-3 ${
            market.open 
              ? 'bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30' 
              : 'bg-gradient-to-r from-slate-500/20 to-slate-600/20 border border-slate-500/30'
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-bold text-sm">{market.name}</p>
              <p className="text-xs text-muted-foreground">{market.hours}</p>
            </div>
            <div className={`w-3 h-3 rounded-full ${market.open ? 'bg-green-500 animate-pulse' : 'bg-slate-500'}`} />
          </div>
        </motion.div>
      ))}
    </div>
  );
};

// ============================================
// ASSET CARD COMPONENT
// ============================================
const AssetCard = ({ asset, index }) => {
  const isPositive = asset.change_percent >= 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.02, y: -5 }}
      className="cursor-pointer"
    >
      <Card className={`overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all ${
        isPositive 
          ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20' 
          : 'bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20'
      }`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">{asset.flag}</span>
            <Badge variant={isPositive ? "default" : "destructive"} className="text-xs">
              {isPositive ? '+' : ''}{asset.change_percent?.toFixed(2)}%
            </Badge>
          </div>
          
          <p className="font-bold text-lg">{asset.name}</p>
          {asset.country && (
            <p className="text-xs text-muted-foreground">{asset.country}</p>
          )}
          
          <div className="mt-3 flex items-end justify-between">
            <div>
              <p className="text-2xl font-bold">
                {asset.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
              </p>
              {asset.unit && <p className="text-xs text-muted-foreground">{asset.unit}</p>}
            </div>
            
            {/* Mini Sparkline */}
            {asset.sparkline && asset.sparkline.length > 0 && (
              <div className="w-20 h-10">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={asset.sparkline.map((v, i) => ({ value: v }))}>
                    <Area 
                      type="monotone" 
                      dataKey="value" 
                      stroke={isPositive ? '#22c55e' : '#ef4444'} 
                      fill={isPositive ? '#22c55e20' : '#ef444420'}
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// ============================================
// GLOBAL HEATMAP
// ============================================
const GlobalHeatmap = ({ assets }) => {
  const getColor = (changePercent) => {
    if (changePercent >= 3) return 'from-green-500 to-green-600';
    if (changePercent >= 1) return 'from-green-400 to-green-500';
    if (changePercent > 0) return 'from-green-300 to-green-400';
    if (changePercent === 0) return 'from-slate-400 to-slate-500';
    if (changePercent > -1) return 'from-red-300 to-red-400';
    if (changePercent > -3) return 'from-red-400 to-red-500';
    return 'from-red-500 to-red-600';
  };

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          🗺️ Heatmap Global
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 bg-slate-900">
        <div className="flex flex-wrap gap-2 justify-center">
          {assets.map((asset, idx) => {
            const colorClass = getColor(asset.change_percent || 0);
            
            return (
              <motion.div
                key={asset.symbol}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: idx * 0.03 }}
                whileHover={{ scale: 1.1, zIndex: 10 }}
                className={`relative cursor-pointer rounded-lg bg-gradient-to-br ${colorClass} shadow-lg flex flex-col items-center justify-center text-white p-3 min-w-[100px]`}
              >
                <span className="text-xl mb-1">{asset.flag}</span>
                <span className="font-bold text-sm">{asset.name}</span>
                <span className="text-xs">
                  {asset.change_percent >= 0 ? '+' : ''}{asset.change_percent?.toFixed(2)}%
                </span>
              </motion.div>
            );
          })}
        </div>
        
        {/* Legend */}
        <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-red-500 to-red-600" />
            <span>Scădere</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-slate-400 to-slate-500" />
            <span>Neutru</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-green-500 to-green-600" />
            <span>Creștere</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// TOP MOVERS COMPONENT
// ============================================
const TopMovers = ({ assets }) => {
  const sorted = [...assets].sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent));
  const topMovers = sorted.slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-500" />
          🔥 Cele Mai Active
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {topMovers.map((asset, idx) => {
          const isPositive = asset.change_percent >= 0;
          return (
            <motion.div
              key={asset.symbol}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className={`flex items-center justify-between p-3 rounded-lg ${
                isPositive ? 'bg-green-50 dark:bg-green-900/20' : 'bg-red-50 dark:bg-red-900/20'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{asset.flag}</span>
                <div>
                  <p className="font-bold">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">{asset.country || asset.category}</p>
                </div>
              </div>
              <div className="text-right">
                <p className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? '+' : ''}{asset.change_percent?.toFixed(2)}%
                </p>
                <p className="text-sm text-muted-foreground">
                  {asset.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
                </p>
              </div>
            </motion.div>
          );
        })}
      </CardContent>
    </Card>
  );
};

// ============================================
// MAIN PAGE COMPONENT
// ============================================
export default function GlobalMarketsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  const fetchData = async () => {
    try {
      const res = await fetch(`${API_URL}/api/global/overview`);
      if (res.ok) {
        const result = await res.json();
        setData(result);
      }
    } catch (err) {
      console.error('Error fetching global data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000); // 1 min refresh
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  const allAssets = useMemo(() => {
    if (!data) return [];
    return [
      ...(data.indices || []),
      ...(data.commodities || []),
      ...(data.crypto || []),
      ...(data.forex || [])
    ];
  }, [data]);

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="Piețe Globale Live | FinRomania"
        description="Date în timp real de pe piețele globale. Indici S&P 500, NASDAQ, DAX, comodități, crypto și forex."
        keywords="indici globali, S&P 500, NASDAQ, DAX, bitcoin, petrol, aur, forex"
      />

      <div className="space-y-6">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-4"
        >
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            🌍 Piețe Globale
          </h1>
          <p className="text-muted-foreground">
            Indici, Comodități, Crypto & Forex • Live
          </p>
        </motion.div>

        {/* Market Status */}
        <MarketStatusBar marketStatus={data?.market_status} />

        {/* Top Section */}
        <div className="grid lg:grid-cols-[1fr,300px] gap-6">
          {/* Heatmap */}
          <GlobalHeatmap assets={allAssets} />
          
          {/* Sidebar */}
          <div className="space-y-6">
            <GlobalSentimentGauge sentiment={data?.sentiment} />
            <TopMovers assets={allAssets} />
          </div>
        </div>

        {/* Tabs for Categories */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="all">🌐 Toate</TabsTrigger>
              <TabsTrigger value="indices">📊 Indici</TabsTrigger>
              <TabsTrigger value="commodities">🛢️ Comodități</TabsTrigger>
              <TabsTrigger value="crypto">₿ Crypto</TabsTrigger>
              <TabsTrigger value="forex">💱 Forex</TabsTrigger>
            </TabsList>
            
            <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Actualizează
            </Button>
          </div>

          <TabsContent value="all" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {allAssets.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="indices" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.indices?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="commodities" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.commodities?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="crypto" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.crypto?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="forex" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.forex?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} />
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Info Banner */}
        <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold mb-1">💡 De Ce Contează Piețele Globale?</h3>
                <p className="text-blue-100">
                  BVB este influențată de piețele internaționale. Când S&P 500 scade, de obicei și BET scade.
                </p>
              </div>
              <Link to="/stocks">
                <Button className="bg-white text-blue-600 hover:bg-blue-50">
                  Vezi Bursa București →
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Educational Note */}
        <Card className="bg-slate-50 dark:bg-slate-800">
          <CardContent className="p-4 text-sm text-muted-foreground">
            <h4 className="font-semibold text-foreground mb-2">ℹ️ Informații</h4>
            <ul className="space-y-1">
              <li>• <strong>Indici:</strong> Reprezintă performanța unui grup de acțiuni (ex: S&P 500 = top 500 companii SUA)</li>
              <li>• <strong>Comodități:</strong> Materii prime tranzacționate (petrol, aur, gaze)</li>
              <li>• <strong>Crypto:</strong> Monede digitale descentralizate</li>
              <li>• <strong>Forex:</strong> Piața valutară - schimb între valute</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
