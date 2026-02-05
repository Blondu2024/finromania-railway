import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, RefreshCw, Search, ArrowUpDown, BarChart3, 
  Flame, Activity, Building2, Clock, Zap, Eye, Target, AlertTriangle,
  ChevronRight, Sparkles, Gauge, Timer, ArrowRight
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Skeleton } from '../components/ui/skeleton';
import SEO from '../components/SEO';
import TradingCompanion from '../components/TradingCompanion';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// MARKET PULSE GAUGE COMPONENT
// Fear & Greed Style Indicator
// ============================================
const MarketPulseGauge = ({ gainers, losers, avgChange, totalStocks }) => {
  // Calculate sentiment score (0-100)
  const sentimentScore = useMemo(() => {
    if (totalStocks === 0) return 50;
    const gainRatio = gainers / totalStocks;
    const changeImpact = Math.min(Math.max(avgChange * 10, -25), 25);
    const baseScore = gainRatio * 100;
    return Math.min(Math.max(baseScore + changeImpact, 0), 100);
  }, [gainers, losers, avgChange, totalStocks]);

  const getSentimentLabel = (score) => {
    if (score >= 80) return { text: 'LĂCOMIE EXTREMĂ', color: 'text-green-500', emoji: '🚀' };
    if (score >= 60) return { text: 'LĂCOMIE', color: 'text-green-400', emoji: '📈' };
    if (score >= 40) return { text: 'NEUTRU', color: 'text-yellow-500', emoji: '⚖️' };
    if (score >= 20) return { text: 'FRICĂ', color: 'text-orange-500', emoji: '😰' };
    return { text: 'FRICĂ EXTREMĂ', color: 'text-red-500', emoji: '😱' };
  };

  const sentiment = getSentimentLabel(sentimentScore);
  const rotation = (sentimentScore / 100) * 180 - 90; // -90 to 90 degrees

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative"
    >
      <Card className="overflow-hidden border-0 shadow-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <CardContent className="p-6">
          <div className="text-center mb-4">
            <h3 className="text-lg font-bold text-white flex items-center justify-center gap-2">
              <Gauge className="w-5 h-5 text-blue-400" />
              Market Pulse
            </h3>
            <p className="text-xs text-slate-400">Sentimentul pieței BVB</p>
          </div>

          {/* Gauge Visual */}
          <div className="relative w-48 h-24 mx-auto mb-8">
            {/* Background arc */}
            <svg viewBox="0 0 200 100" className="w-full h-full">
              {/* Gradient definitions */}
              <defs>
                <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#ef4444" />
                  <stop offset="25%" stopColor="#f97316" />
                  <stop offset="50%" stopColor="#eab308" />
                  <stop offset="75%" stopColor="#22c55e" />
                  <stop offset="100%" stopColor="#10b981" />
                </linearGradient>
              </defs>
              
              {/* Background track */}
              <path
                d="M 20 90 A 80 80 0 0 1 180 90"
                fill="none"
                stroke="url(#gaugeGradient)"
                strokeWidth="12"
                strokeLinecap="round"
              />
              
              {/* Needle */}
              <motion.g
                initial={{ rotate: -90 }}
                animate={{ rotate: rotation }}
                transition={{ duration: 1, ease: "easeOut" }}
                style={{ transformOrigin: '100px 90px' }}
              >
                <line
                  x1="100"
                  y1="90"
                  x2="100"
                  y2="25"
                  stroke="white"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
                <circle cx="100" cy="90" r="8" fill="white" />
              </motion.g>
            </svg>

            {/* Labels - positioned below the gauge */}
            <div className="absolute -bottom-6 left-0 text-xs text-red-400 font-bold">FRICĂ</div>
            <div className="absolute -bottom-6 right-0 text-xs text-green-400 font-bold">LĂCOMIE</div>
          </div>

          {/* Score Display */}
          <motion.div 
            className="text-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="flex items-center justify-center gap-2 mb-2">
              <span className="text-4xl">{sentiment.emoji}</span>
              <span className={`text-3xl font-bold ${sentiment.color}`}>
                {Math.round(sentimentScore)}
              </span>
            </div>
            <p className={`text-lg font-bold ${sentiment.color}`}>{sentiment.text}</p>
            <div className="flex justify-center gap-4 mt-3 text-sm">
              <span className="text-green-400">📈 {gainers} creșteri</span>
              <span className="text-red-400">📉 {losers} scăderi</span>
            </div>
          </motion.div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// ============================================
// COUNTDOWN TIMER COMPONENT
// ============================================
const MarketCountdown = () => {
  const [timeLeft, setTimeLeft] = useState({ hours: 0, minutes: 0, seconds: 0, isOpen: false, status: '' });

  useEffect(() => {
    const calculateTime = () => {
      const now = new Date();
      const day = now.getDay();
      const hours = now.getHours();
      const minutes = now.getMinutes();
      
      // BVB: Luni-Vineri, 10:00 - 18:00 (ora României)
      const isWeekday = day >= 1 && day <= 5;
      const currentMinutes = hours * 60 + minutes;
      const openMinutes = 10 * 60; // 10:00
      const closeMinutes = 18 * 60; // 18:00
      
      if (!isWeekday) {
        // Weekend
        const daysUntilMonday = day === 0 ? 1 : 8 - day;
        const msUntilOpen = daysUntilMonday * 24 * 60 * 60 * 1000 - (hours * 60 + minutes) * 60 * 1000 + openMinutes * 60 * 1000;
        const h = Math.floor(msUntilOpen / (1000 * 60 * 60));
        const m = Math.floor((msUntilOpen % (1000 * 60 * 60)) / (1000 * 60));
        setTimeLeft({ hours: h, minutes: m, seconds: 0, isOpen: false, status: 'Weekend - Deschidere Luni' });
      } else if (currentMinutes < openMinutes) {
        // Before market opens
        const diff = openMinutes - currentMinutes;
        setTimeLeft({ hours: Math.floor(diff / 60), minutes: diff % 60, seconds: 0, isOpen: false, status: 'Până la deschidere' });
      } else if (currentMinutes < closeMinutes) {
        // Market is open
        const diff = closeMinutes - currentMinutes;
        setTimeLeft({ hours: Math.floor(diff / 60), minutes: diff % 60, seconds: 60 - now.getSeconds(), isOpen: true, status: 'Până la închidere' });
      } else {
        // After market closes
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const nextOpen = day === 5 ? 3 : 1; // If Friday, next is Monday (3 days)
        setTimeLeft({ hours: nextOpen * 24 - (hours - 10), minutes: 60 - minutes, seconds: 0, isOpen: false, status: 'Închis - Deschidere mâine' });
      }
    };

    calculateTime();
    const interval = setInterval(calculateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl p-4 ${timeLeft.isOpen ? 'bg-gradient-to-r from-green-600 to-emerald-600' : 'bg-gradient-to-r from-slate-700 to-slate-600'}`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.div
            animate={timeLeft.isOpen ? { scale: [1, 1.2, 1] } : {}}
            transition={{ duration: 1, repeat: Infinity }}
          >
            {timeLeft.isOpen ? (
              <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
            ) : (
              <Clock className="w-5 h-5 text-slate-300" />
            )}
          </motion.div>
          <div>
            <p className="text-white font-bold">
              {timeLeft.isOpen ? '🟢 BURSA DESCHISĂ' : '🔴 BURSA ÎNCHISĂ'}
            </p>
            <p className="text-xs text-white/80">{timeLeft.status}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-1 font-mono text-white">
          <div className="bg-black/30 rounded px-2 py-1">
            <span className="text-2xl font-bold">{String(timeLeft.hours).padStart(2, '0')}</span>
          </div>
          <span className="text-xl">:</span>
          <div className="bg-black/30 rounded px-2 py-1">
            <span className="text-2xl font-bold">{String(timeLeft.minutes).padStart(2, '0')}</span>
          </div>
          {timeLeft.isOpen && (
            <>
              <span className="text-xl">:</span>
              <div className="bg-black/30 rounded px-2 py-1">
                <span className="text-2xl font-bold">{String(timeLeft.seconds).padStart(2, '0')}</span>
              </div>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// HEATMAP COMPONENT
// ============================================
const StockHeatmap = ({ stocks }) => {
  const [hoveredStock, setHoveredStock] = useState(null);

  // Calculate sizes based on volume/market presence
  const maxVolume = Math.max(...stocks.map(s => s.volume || 1000));
  
  const getBlockSize = (stock) => {
    const volumeRatio = (stock.volume || 1000) / maxVolume;
    // Size between 60 and 150
    return Math.max(60, Math.min(150, 60 + volumeRatio * 90));
  };

  const getColor = (changePercent) => {
    if (changePercent >= 5) return 'from-green-500 to-green-600';
    if (changePercent >= 2) return 'from-green-400 to-green-500';
    if (changePercent > 0) return 'from-green-300 to-green-400';
    if (changePercent === 0) return 'from-slate-400 to-slate-500';
    if (changePercent > -2) return 'from-red-300 to-red-400';
    if (changePercent > -5) return 'from-red-400 to-red-500';
    return 'from-red-500 to-red-600';
  };

  const sortedStocks = [...stocks].sort((a, b) => (b.volume || 0) - (a.volume || 0)).slice(0, 30);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-blue-600 text-white">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          🗺️ Heatmap BVB
          <Badge variant="secondary" className="ml-auto bg-white/20 text-white">
            Top 30 după volum
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 bg-slate-900">
        <div className="flex flex-wrap gap-2 justify-center">
          {sortedStocks.map((stock, idx) => {
            const size = getBlockSize(stock);
            const colorClass = getColor(stock.change_percent || 0);
            
            return (
              <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                <motion.div
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.02 }}
                  whileHover={{ scale: 1.1, zIndex: 10 }}
                  onMouseEnter={() => setHoveredStock(stock)}
                  onMouseLeave={() => setHoveredStock(null)}
                  className={`relative cursor-pointer rounded-lg bg-gradient-to-br ${colorClass} shadow-lg flex flex-col items-center justify-center text-white transition-all`}
                  style={{ 
                    width: `${size}px`, 
                    height: `${size}px`,
                    minWidth: '60px',
                    minHeight: '60px'
                  }}
                >
                  <span className="font-bold text-sm">{stock.symbol}</span>
                  <span className={`text-xs font-semibold ${stock.change_percent >= 0 ? '' : ''}`}>
                    {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(1)}%
                  </span>
                  {size > 80 && (
                    <span className="text-xs opacity-80">{stock.price?.toFixed(1)}</span>
                  )}
                </motion.div>
              </Link>
            );
          })}
        </div>

        {/* Legend */}
        <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-red-500 to-red-600" />
            <span>Scădere mare</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-slate-400 to-slate-500" />
            <span>Neutru</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-green-500 to-green-600" />
            <span>Creștere mare</span>
          </div>
        </div>

        {/* Hover Info */}
        <AnimatePresence>
          {hoveredStock && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white dark:bg-slate-800 rounded-lg shadow-2xl p-4 z-50"
            >
              <div className="flex items-center gap-4">
                <div>
                  <p className="font-bold text-lg">{hoveredStock.symbol}</p>
                  <p className="text-sm text-muted-foreground">{hoveredStock.name}</p>
                </div>
                <div className="text-right">
                  <p className="font-bold">{hoveredStock.price?.toFixed(2)} RON</p>
                  <p className={`font-semibold ${hoveredStock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {hoveredStock.change_percent >= 0 ? '+' : ''}{hoveredStock.change_percent?.toFixed(2)}%
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  );
};

// ============================================
// ANIMATED TOP MOVERS COMPONENT
// ============================================
const AnimatedTopMovers = ({ gainers, losers, mostTraded }) => {
  const [activeTab, setActiveTab] = useState('gainers');

  const tabs = [
    { id: 'gainers', label: '🚀 Creșteri', data: gainers, color: 'green' },
    { id: 'losers', label: '📉 Scăderi', data: losers, color: 'red' },
    { id: 'volume', label: '📊 Volum', data: mostTraded, color: 'blue' },
  ];

  const currentTab = tabs.find(t => t.id === activeTab);

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-500" />
          Top Movers Live
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {/* Tab Buttons */}
        <div className="flex border-b">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 text-sm font-semibold transition-all ${
                activeTab === tab.id 
                  ? `bg-${tab.color}-50 text-${tab.color}-600 border-b-2 border-${tab.color}-500`
                  : 'text-muted-foreground hover:bg-muted/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="space-y-2"
            >
              {currentTab?.data?.slice(0, 5).map((stock, idx) => (
                <motion.div
                  key={stock.symbol}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                >
                  <Link to={`/stocks/bvb/${stock.symbol}`}>
                    <div className={`flex items-center justify-between p-3 rounded-lg transition-all hover:scale-102 ${
                      currentTab.color === 'green' ? 'bg-green-50 hover:bg-green-100' :
                      currentTab.color === 'red' ? 'bg-red-50 hover:bg-red-100' :
                      'bg-blue-50 hover:bg-blue-100'
                    }`}>
                      <div className="flex items-center gap-3">
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: idx * 0.1 + 0.2, type: "spring" }}
                          className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                            currentTab.color === 'green' ? 'bg-green-500' :
                            currentTab.color === 'red' ? 'bg-red-500' :
                            'bg-blue-500'
                          }`}
                        >
                          {idx + 1}
                        </motion.div>
                        <div>
                          <p className="font-bold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[120px]">
                            {stock.name}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        {activeTab === 'volume' ? (
                          <>
                            <p className="font-bold">{(stock.volume || 0).toLocaleString('ro-RO')}</p>
                            <p className="text-xs text-muted-foreground">volum</p>
                          </>
                        ) : (
                          <>
                            <p className={`font-bold ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                            </p>
                            <p className="text-xs text-muted-foreground">{stock.price?.toFixed(2)} RON</p>
                          </>
                        )}
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// BVB INDICES CAROUSEL
// ============================================
const IndicesCarousel = ({ indices }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
      {indices.map((index, idx) => (
        <motion.div
          key={index.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: idx * 0.1 }}
          whileHover={{ y: -5, scale: 1.02 }}
        >
          <Card className={`overflow-hidden border-0 ${
            index.change_percent >= 0 
              ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20' 
              : 'bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20'
          }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <Badge variant="outline" className="font-bold">{index.id}</Badge>
                {index.is_live && (
                  <motion.div
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="w-2 h-2 bg-green-500 rounded-full"
                  />
                )}
              </div>
              <p className="text-2xl font-bold">{index.value?.toLocaleString('ro-RO')}</p>
              <div className={`flex items-center gap-1 ${index.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {index.change_percent >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                <span className="font-semibold">
                  {index.change_percent >= 0 ? '+' : ''}{index.change_percent?.toFixed(2)}%
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">{index.name}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
};

// ============================================
// SECTOR PERFORMANCE BARS
// ============================================
const SectorPerformance = ({ sectors }) => {
  const maxChange = Math.max(...sectors.map(s => Math.abs(s.average_change_percent || 0)), 1);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Building2 className="w-5 h-5 text-indigo-600" />
          Performanță pe Sectoare
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {sectors.map((sector, idx) => {
          const width = (Math.abs(sector.average_change_percent || 0) / maxChange) * 100;
          const isPositive = (sector.average_change_percent || 0) >= 0;
          
          return (
            <motion.div
              key={sector.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="space-y-1"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{sector.name}</span>
                <span className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? '+' : ''}{sector.average_change_percent?.toFixed(2)}%
                </span>
              </div>
              <div className="h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${width}%` }}
                  transition={{ duration: 0.5, delay: idx * 0.1 }}
                  className={`h-full rounded-full ${isPositive ? 'bg-gradient-to-r from-green-400 to-green-600' : 'bg-gradient-to-r from-red-400 to-red-600'}`}
                />
              </div>
            </motion.div>
          );
        })}
      </CardContent>
    </Card>
  );
};

// ============================================
// MAIN STOCKS PAGE COMPONENT
// ============================================
export default function StocksPage() {
  const { user, token } = useAuth();
  const [stocks, setStocks] = useState([]);
  const [indices, setIndices] = useState([]);
  const [topMovers, setTopMovers] = useState({ gainers: [], losers: [], most_traded: [] });
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'change_percent', direction: 'desc' });
  
  // Check subscription for delay badge și refresh rate
  const [subscriptionLevel, setSubscriptionLevel] = useState('free');
  const [isPro, setIsPro] = useState(false);
  
  useEffect(() => {
    if (user && token) {
      fetch(`${API_URL}/api/subscriptions/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          const level = data?.subscription?.subscription_level || 'free';
          const is_pro = data?.subscription?.is_pro || false;
          setSubscriptionLevel(level);
          setIsPro(is_pro);
          console.log('[StocksPage] Subscription:', level, 'isPro:', is_pro);
        })
        .catch((err) => {
          console.error('[StocksPage] Failed to fetch subscription:', err);
          setSubscriptionLevel('free');
          setIsPro(false);
        });
    }
  }, [user, token]);
  
  // Delay info - BVB data refresh
  const delayInfo = isPro
    ? { text: 'Update 15s', color: 'bg-green-500', description: 'Date BVB actualizate la 15 secunde (PRO)', refresh: 15000 }
    : { text: 'Update 60s', color: 'bg-yellow-500', description: 'Date BVB actualizate la 60 secunde (Gratuit)', refresh: 60000 };

  const fetchAllData = async () => {
    try {
      // CACHE BUSTING pentru date LIVE
      const timestamp = Date.now();
      const fetchOptions = {
        cache: 'no-store',
        headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
      };
      
      const [stocksRes, indicesRes, moversRes, sectorsRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb?_t=${timestamp}`, fetchOptions),
        fetch(`${API_URL}/api/bvb/indices?_t=${timestamp}`, fetchOptions),
        fetch(`${API_URL}/api/bvb/top-movers?_t=${timestamp}`, fetchOptions),
        fetch(`${API_URL}/api/bvb/sectors?_t=${timestamp}`, fetchOptions)
      ]);
      
      const stocksData = await stocksRes.json();
      const indicesData = await indicesRes.json();
      const moversData = await moversRes.json();
      const sectorsData = await sectorsRes.json();
      
      setStocks(stocksData);
      setIndices(indicesData.indices || []);
      setTopMovers(moversData);
      setSectors(sectorsData.sectors || []);
      
      console.log('[StocksPage] Fetched LIVE data at', new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    
    // Interval diferențiat: PRO = 15s, FREE = 60s
    const refreshInterval = delayInfo.refresh;
    const interval = setInterval(fetchAllData, refreshInterval);
    
    console.log(`[StocksPage] Auto-refresh every ${refreshInterval/1000}s (${isPro ? 'PRO' : 'FREE'})`);
    
    return () => clearInterval(interval);
  }, [isPro, delayInfo.refresh]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/bvb`, { method: 'POST' });
    await fetchAllData();
  };

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const filteredStocks = stocks
    .filter(stock => 
      stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortConfig.key] || 0;
      const bVal = b[sortConfig.key] || 0;
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

  const marketStats = {
    gainers: stocks.filter(s => s.change_percent > 0).length,
    losers: stocks.filter(s => s.change_percent < 0).length,
    avgChange: stocks.length > 0 
      ? stocks.reduce((acc, s) => acc + (s.change_percent || 0), 0) / stocks.length
      : 0
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-20 w-full" />
        <div className="grid grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <>
      <SEO 
        title="Bursa de Valori București | Date Live BVB | FinRomania"
        description="Date în timp real de pe Bursa de Valori București. Heatmap BVB, indicatori Market Pulse, top movers și analiză completă a pieței românești."
        keywords="BVB, bursa bucuresti, actiuni romania, TLV, SNP, BRD, indici BVB, market pulse"
      />

      <div className="space-y-6">
        {/* Hero Section cu Delay Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-4"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              🏛️ Bursa de Valori București
            </h1>
            <Badge className={`${delayInfo.color} text-white`}>
              <Clock className="w-3 h-3 mr-1" />
              {delayInfo.text}
            </Badge>
          </div>
          <p className="text-muted-foreground">
            {delayInfo.description}
            {subscriptionLevel === 'free' && (
              <Link to="/pricing" className="text-amber-600 hover:underline ml-2">
                → PRO: 15min delay
              </Link>
            )}
          </p>
        </motion.div>

        {/* Market Status Bar */}
        <MarketCountdown />

        {/* Top Section: Market Pulse + Refresh */}
        <div className="grid lg:grid-cols-[300px,1fr] gap-6">
          {/* Market Pulse */}
          <MarketPulseGauge
            gainers={marketStats.gainers}
            losers={marketStats.losers}
            avgChange={marketStats.avgChange}
            totalStocks={stocks.length}
          />

          {/* Indices */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Activity className="w-5 h-5 text-purple-600" />
                Indicii BVB
              </h2>
              <Button variant="outline" onClick={handleRefresh} disabled={refreshing} size="sm">
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Actualizează
              </Button>
            </div>
            <IndicesCarousel indices={indices} />
          </div>
        </div>

        {/* Heatmap Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <StockHeatmap stocks={stocks} />
        </motion.div>

        {/* Middle Section: Top Movers + Sectors */}
        <div className="grid lg:grid-cols-2 gap-6">
          <AnimatedTopMovers
            gainers={topMovers.gainers}
            losers={topMovers.losers}
            mostTraded={topMovers.most_traded}
          />
          <SectorPerformance sectors={sectors} />
        </div>

        {/* Market Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
              <CardContent className="p-4">
                <p className="text-sm text-blue-100">Total Acțiuni</p>
                <p className="text-3xl font-bold">{stocks.length}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0">
              <CardContent className="p-4">
                <p className="text-sm text-green-100">În Creștere</p>
                <p className="text-3xl font-bold">{marketStats.gainers}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0">
              <CardContent className="p-4">
                <p className="text-sm text-red-100">În Scădere</p>
                <p className="text-3xl font-bold">{marketStats.losers}</p>
              </CardContent>
            </Card>
          </motion.div>
          <motion.div whileHover={{ scale: 1.05 }}>
            <Card className={`bg-gradient-to-br ${marketStats.avgChange >= 0 ? 'from-emerald-500 to-emerald-600' : 'from-orange-500 to-orange-600'} text-white border-0`}>
              <CardContent className="p-4">
                <p className="text-sm opacity-90">Media Piață</p>
                <p className="text-3xl font-bold">{marketStats.avgChange >= 0 ? '+' : ''}{marketStats.avgChange.toFixed(2)}%</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* All Stocks Table */}
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Toate Acțiunile BVB ({filteredStocks.length})
              </CardTitle>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Caută acțiune..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="cursor-pointer" onClick={() => handleSort('symbol')}>
                    <div className="flex items-center gap-1">
                      Simbol <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </TableHead>
                  <TableHead>Companie</TableHead>
                  <TableHead>Sector</TableHead>
                  <TableHead className="text-right cursor-pointer" onClick={() => handleSort('price')}>
                    <div className="flex items-center justify-end gap-1">
                      Preț (RON) <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </TableHead>
                  <TableHead className="text-right cursor-pointer" onClick={() => handleSort('change_percent')}>
                    <div className="flex items-center justify-end gap-1">
                      Variație <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </TableHead>
                  <TableHead className="text-right cursor-pointer" onClick={() => handleSort('volume')}>
                    <div className="flex items-center justify-end gap-1">
                      Volum <ArrowUpDown className="w-4 h-4" />
                    </div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredStocks.map((stock, idx) => (
                  <motion.tr
                    key={stock.symbol}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: idx * 0.02 }}
                    className="hover:bg-muted/50"
                  >
                    <TableCell>
                      <Link to={`/stocks/bvb/${stock.symbol}`} className="font-bold text-blue-600 hover:underline">
                        {stock.symbol}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Link to={`/stocks/bvb/${stock.symbol}`} className="hover:text-blue-600">
                        {stock.name}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{stock.sector || 'N/A'}</Badge>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {stock.price?.toFixed(2)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className={`flex items-center justify-end gap-1 ${
                        stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {stock.change_percent >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                        <span className="font-medium">
                          {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {(stock.volume || 0).toLocaleString('ro-RO')}
                    </TableCell>
                  </motion.tr>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Education CTA */}
        <Card className="bg-gradient-to-r from-green-600 to-blue-600 text-white border-0 overflow-hidden relative">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMwLTkuOTQtOC4wNi0xOC0xOC0xOHY2YzYuNjMgMCAxMiA1LjM3IDEyIDEyaC02bDkgOSA5LTloLTZ6IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9Ii4wNSIvPjwvZz48L3N2Zz4=')] opacity-50" />
          <CardContent className="relative p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="text-center md:text-left">
                <h3 className="text-xl font-bold mb-1">💰 Vrei Să Înțelegi Mai Bine Piața?</h3>
                <p className="text-green-100">Învață bazele investițiilor în 15 lecții gratuite</p>
              </div>
              <Link to="/financial-education">
                <Button className="bg-white text-green-600 hover:bg-green-50">
                  Începe Educația Financiară →
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trading Companion - Verifică Înainte */}
      <TradingCompanion 
        stockSymbol="BVB"
        stockName="Bursa de Valori București"
        currentPrice={null}
        changePercent={marketStats.avgChange}
        stockType="bvb"
      />
    </>
  );
}
