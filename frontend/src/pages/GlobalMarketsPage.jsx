import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Globe, TrendingUp, TrendingDown, RefreshCw, Clock, Flame,
  DollarSign, Coins, BarChart3, Zap, Timer,
  ChevronRight, Sparkles, Activity, X, ArrowUp, ArrowDown
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
import TradingCompanion, { TradingReminder, shouldShowReminder, markReminderShown } from '../components/TradingCompanion';
import { useAuth } from '../context/AuthContext';
import UnifiedChart from '../components/UnifiedChart';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// ASSET DETAIL MODAL WITH CHART
// ============================================
const AssetDetailModal = ({ asset, onClose, isPro, token }) => {
  const { t } = useTranslation();
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('1d');
  const [interval, setInterval] = useState('15m');
  const [chartInfo, setChartInfo] = useState(null);

  // Intraday intervals live
  const intervals = [
    { value: '1m', label: '1 min', requiresPeriod: '1d' },
    { value: '5m', label: '5 min', requiresPeriod: '1d' },
    { value: '15m', label: '15 min', requiresPeriod: '1d' },
    { value: '30m', label: '30 min', requiresPeriod: '5d' },
    { value: '1h', label: t('global.interval1h'), requiresPeriod: '5d' },
    { value: '1d', label: t('global.interval1d'), requiresPeriod: '1mo' },
  ];

  const periods = [
    { value: '1d', label: t('global.period1Day') },
    { value: '5d', label: t('global.period5Days') },
    { value: '1mo', label: t('global.period1Month') },
    { value: '3mo', label: t('global.period3Months') },
    { value: '6mo', label: t('global.period6Months') },
    { value: '1y', label: t('global.period1Year') },
  ];

  useEffect(() => {
    const fetchChart = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_URL}/api/global/chart/${encodeURIComponent(asset.symbol)}?period=${period}&interval=${interval}`);
        if (res.ok) {
          const data = await res.json();
          setChartData(data.data || []);
          setChartInfo(data);
        }
      } catch (err) {
        console.error('Error fetching chart:', err);
      } finally {
        setLoading(false);
      }
    };
    
    if (asset?.symbol) {
      fetchChart();
    }
  }, [asset?.symbol, period, interval]);

  if (!asset) return null;

  const isPositive = asset.change_percent >= 0;
  const minPrice = chartData.length > 0 ? Math.min(...chartData.map(d => d.low || d.close)) * 0.995 : 0;
  const maxPrice = chartData.length > 0 ? Math.max(...chartData.map(d => d.high || d.close)) * 1.005 : 0;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white dark:bg-zinc-900 rounded-2xl shadow-2xl w-full max-w-sm sm:max-w-2xl lg:max-w-6xl max-h-[90vh] overflow-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className={`p-6 ${isPositive ? 'bg-gradient-to-r from-green-600 to-emerald-600' : 'bg-gradient-to-r from-red-600 to-orange-600'} text-white`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-4xl">{asset.flag}</span>
                <div>
                  <h2 className="text-2xl font-bold">{asset.name}</h2>
                  <p className="text-white/80 text-sm">{asset.symbol} • {asset.country || asset.category}</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-white/20">
                <X className="w-6 h-6" />
              </Button>
            </div>
            
            <div className="mt-4 flex items-end gap-6">
              <p className="text-4xl font-bold">
                {asset.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
              </p>
              <div className="flex items-center gap-2">
                {isPositive ? <ArrowUp className="w-6 h-6" /> : <ArrowDown className="w-6 h-6" />}
                <span className="text-2xl font-bold">
                  {isPositive ? '+' : ''}{asset.change_percent?.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* PRO Chart Component */}
          <div className="p-6">
            <UnifiedChart
              symbol={asset.symbol}
              type="global"
              isPro={isPro}
              token={token}
            />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

// ============================================
// GLOBAL SENTIMENT GAUGE
// ============================================
const GlobalSentimentGauge = ({ sentiment }) => {
  const { t } = useTranslation();
  const score = useMemo(() => {
    if (!sentiment) return 50;
    const ratio = sentiment.gainers / (sentiment.gainers + sentiment.losers || 1);
    return Math.round(ratio * 100);
  }, [sentiment]);

  const getLabel = (s) => {
    if (s >= 70) return { text: 'BULLISH 🐂', color: 'text-green-500' };
    if (s >= 55) return { text: t('global.slightlyBullish'), color: 'text-green-400' };
    if (s >= 45) return { text: t('global.neutral'), color: 'text-yellow-500' };
    if (s >= 30) return { text: t('global.slightlyBearish'), color: 'text-orange-500' };
    return { text: 'BEARISH 🐻', color: 'text-red-500' };
  };

  const label = getLabel(score);

  return (
    <Card className="bg-gradient-to-br from-zinc-900 via-blue-900 to-zinc-900 text-white border-0">
      <CardContent className="p-6">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-400" />
          {t('global.sentimentGlobal')}
        </h3>

        <div className="flex items-center justify-between">
          <div>
            <p className={`text-3xl font-bold ${label.color}`}>{score}%</p>
            <p className={`font-semibold ${label.color}`}>{label.text}</p>
          </div>

          <div className="text-right text-sm">
            <p className="text-green-400">📈 {sentiment?.gainers || 0} {t('global.gaining')}</p>
            <p className="text-red-400">📉 {sentiment?.losers || 0} {t('global.losing')}</p>
            <p className="text-blue-300 mt-2">
              {t('global.average')}: {sentiment?.avg_change >= 0 ? '+' : ''}{sentiment?.avg_change?.toFixed(2)}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// EXCHANGE MARKET STATUS WITH COUNTDOWN
// ============================================
const EXCHANGES = [
  {
    key: 'us',
    name: 'Wall Street',
    flag: '🇺🇸',
    exchange: 'NYSE / NASDAQ',
    openH: 14, openM: 30,   // 14:30 UTC = 09:30 ET
    closeH: 21, closeM: 0,  // 21:00 UTC = 16:00 ET
    indices: ['S&P 500', 'NASDAQ 100', 'Dow Jones'],
  },
  {
    key: 'lse',
    name: 'Londra (LSE)',
    flag: '🇬🇧',
    exchange: 'London Stock Exchange',
    openH: 8, openM: 0,
    closeH: 16, closeM: 30,
    indices: ['FTSE 100'],
  },
  {
    key: 'xetra',
    name: 'Frankfurt / Paris',
    flag: '🇩🇪',
    exchange: 'XETRA / Euronext',
    openH: 7, openM: 0,
    closeH: 15, closeM: 30,
    indices: ['DAX', 'CAC 40'],
  },
  {
    key: 'tse',
    name: 'Tokyo (TSE)',
    flag: '🇯🇵',
    exchange: 'Tokyo Stock Exchange',
    openH: 0, openM: 0,
    closeH: 6, closeM: 0,
    indices: ['Nikkei 225'],
  },
  {
    key: 'hkex',
    name: 'Hong Kong (HKEX)',
    flag: '🇭🇰',
    exchange: 'HK Stock Exchange',
    openH: 1, openM: 30,
    closeH: 8, closeM: 0,
    indices: ['Hang Seng'],
  },
  {
    key: 'bvb',
    nameKey: 'global.bvbExchangeName',
    flag: '🇷🇴',
    exchangeKey: 'global.bvbExchangeFull',
    // BVB 10:00-18:00 Bucharest. Dynamic UTC offset handled below.
    indices: ['BET', 'BET-FI'],
    isBVB: true,
  },
  {
    key: 'crypto',
    name: 'Crypto',
    flag: '₿',
    exchange: '24/7 Global',
    alwaysOpen: true,
    indices: ['Bitcoin', 'Ethereum'],
  },
];

function getExchangeStatus(ex, nowUTC) {
  if (ex.alwaysOpen) return { isOpen: true, nextEventMin: null, nextEventType: null };

  const weekday = nowUTC.getUTCDay(); // 0=Sun, 6=Sat
  const isWeekday = weekday >= 1 && weekday <= 5;
  const curMin = nowUTC.getUTCHours() * 60 + nowUTC.getUTCMinutes();

  let openMin, closeMin;
  if (ex.isBVB) {
    // BVB 10:00-18:00 Bucharest. Detect DST: April(3)-October(9) = EEST (UTC+3), else EET (UTC+2)
    const month = nowUTC.getUTCMonth(); // 0-indexed
    const utcOffset = (month >= 3 && month <= 9) ? 3 : 2;
    openMin = (10 - utcOffset) * 60;   // e.g. 10-3=7:00 UTC in summer
    closeMin = (18 - utcOffset) * 60;  // e.g. 18-3=15:00 UTC in summer
  } else {
    openMin = ex.openH * 60 + ex.openM;
    closeMin = ex.closeH * 60 + ex.closeM;
  }

  const isOpen = isWeekday && curMin >= openMin && curMin < closeMin;

  let nextEventMin = null;
  let nextEventType = null;
  if (isWeekday) {
    if (curMin < openMin) {
      nextEventMin = openMin - curMin;
      nextEventType = 'opens';
    } else if (curMin < closeMin) {
      nextEventMin = closeMin - curMin;
      nextEventType = 'closes';
    } else {
      const daysAhead = weekday === 5 ? 3 : 1; // Friday -> Monday
      nextEventMin = daysAhead * 1440 - curMin + openMin;
      nextEventType = 'opens';
    }
  } else {
    const daysUntilMon = weekday === 0 ? 1 : (8 - weekday);
    nextEventMin = daysUntilMon * 1440 - curMin + openMin;
    nextEventType = 'opens';
  }

  return { isOpen, nextEventMin, nextEventType };
}

function fmtCountdown(totalMin) {
  if (!totalMin) return '';
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h === 0) return `${m}m`;
  return `${h}h ${m}m`;
}

const ExchangeCard = ({ ex, nowUTC }) => {
  const { t } = useTranslation();
  const { isOpen, nextEventMin, nextEventType } = getExchangeStatus(ex, nowUTC);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl p-3 border transition-all ${
        ex.alwaysOpen
          ? 'bg-gradient-to-br from-blue-500/10 to-blue-500/10 border-blue-500/20'
          : isOpen
          ? 'bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/25'
          : 'bg-gradient-to-br from-slate-500/10 to-slate-600/10 border-slate-500/20'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className="text-base">{ex.flag}</span>
            <span className="font-semibold text-sm truncate">{ex.nameKey ? t(ex.nameKey) : ex.name}</span>
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              ex.alwaysOpen ? 'bg-blue-400 animate-pulse' :
              isOpen ? 'bg-green-400 animate-pulse' : 'bg-slate-400'
            }`} />
          </div>
          <p className="text-xs text-muted-foreground truncate">{ex.exchangeKey ? t(ex.exchangeKey) : ex.exchange}</p>
          <div className="flex flex-wrap gap-1 mt-1">
            {ex.indices.map(idx => (
              <span key={idx} className="text-xs bg-background/60 rounded px-1 py-0.5 text-muted-foreground">{idx}</span>
            ))}
          </div>
        </div>
      </div>

      {/* Status badge */}
      <div className="mt-2 flex items-center justify-between">
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
          ex.alwaysOpen ? 'bg-blue-500/20 text-blue-400' :
          isOpen ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'
        }`}>
          {ex.alwaysOpen ? 'LIVE 24/7' : isOpen ? t('global.open') : t('global.closed')}
        </span>
        {!ex.alwaysOpen && nextEventMin !== null && (
          <span className="text-xs text-muted-foreground">
            {nextEventType === 'opens' ? t('global.opensInLabel') : t('global.closesInLabel')}{' '}
            <span className="font-semibold text-foreground">{fmtCountdown(nextEventMin)}</span>
          </span>
        )}
      </div>

      {/* Data note when closed */}
      {!ex.alwaysOpen && !isOpen && (
        <p className="text-xs text-muted-foreground mt-1 italic">
          {t('global.showingLastClose')}
        </p>
      )}
    </motion.div>
  );
};

const MarketStatusBar = ({ marketStatus }) => {
  const { t } = useTranslation();
  const [nowUTC, setNowUTC] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => setNowUTC(new Date()), 60000); // update every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Clock className="w-4 h-4" />
        <span>{t('global.exchangeScheduleLabel')}: <strong className="text-foreground">{nowUTC.toUTCString().slice(17, 22)}</strong></span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
        {EXCHANGES.map(ex => (
          <ExchangeCard key={ex.key} ex={ex} nowUTC={nowUTC} />
        ))}
      </div>
    </div>
  );
};

// ============================================
// ASSET CARD COMPONENT
// ============================================
const AssetCard = ({ asset, index, onClick }) => {
  const { t } = useTranslation();
  const isPositive = asset.change_percent >= 0;
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ scale: 1.02, y: -5 }}
      className="cursor-pointer"
      onClick={() => onClick && onClick(asset)}
    >
      <Card className={`overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all ${
        isPositive 
          ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20' 
          : 'bg-gradient-to-br from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20'
      }`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">{asset.flag}</span>
            <div className="flex items-center gap-2">
              <Badge variant={isPositive ? "default" : "destructive"} className="text-xs">
                {isPositive ? '+' : ''}{asset.change_percent?.toFixed(2)}%
              </Badge>
              <BarChart3 className="w-4 h-4 text-muted-foreground opacity-50" />
            </div>
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
          
          {/* Click hint */}
          <p className="text-xs text-center text-muted-foreground mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
            {t('global.clickForDetailedChart')}
          </p>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// ============================================
// GLOBAL HEATMAP
// ============================================
const GlobalHeatmap = ({ assets, onAssetClick }) => {
  const { t } = useTranslation();
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
      <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-500 text-white">
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          {t('global.heatmap')}
          <span className="text-xs font-normal ml-2 opacity-80">{t('global.clickForChart')}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 bg-zinc-900">
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
                onClick={() => onAssetClick && onAssetClick(asset)}
                className={`relative cursor-pointer rounded-lg bg-gradient-to-br ${colorClass} shadow-lg flex flex-col items-center justify-center text-white p-3 min-w-0 hover:ring-2 hover:ring-white/50`}
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
        <div className="flex items-center justify-center gap-4 mt-4 pt-4 border-t border-zinc-700">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-red-500 to-red-600" />
            <span>{t('global.decrease')}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-slate-400 to-slate-500" />
            <span>{t('global.neutral')}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <div className="w-4 h-4 rounded bg-gradient-to-br from-green-500 to-green-600" />
            <span>{t('global.increase')}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// ============================================
// TOP MOVERS COMPONENT
// ============================================
const TopMovers = ({ assets, onAssetClick }) => {
  const { t } = useTranslation();
  const sorted = [...assets].sort((a, b) => Math.abs(b.change_percent) - Math.abs(a.change_percent));
  const topMovers = sorted.slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-500" />
          {t('global.mostActive')}
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
              onClick={() => onAssetClick && onAssetClick(asset)}
              className={`flex items-center justify-between p-3 rounded-lg cursor-pointer hover:scale-[1.02] transition-transform ${
                isPositive ? 'bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30' : 'bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-xl">{asset.flag}</span>
                <div>
                  <p className="font-bold">{asset.name}</p>
                  <p className="text-xs text-muted-foreground">{asset.country || asset.category}</p>
                </div>
              </div>
              <div className="text-right flex items-center gap-2">
                <div>
                  <p className={`font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {isPositive ? '+' : ''}{asset.change_percent?.toFixed(2)}%
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {asset.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
                  </p>
                </div>
                <ChevronRight className="w-4 h-4 text-muted-foreground" />
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
  const { t } = useTranslation();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [showReminder, setShowReminder] = useState(false);
  const [companionOpen, setCompanionOpen] = useState(false);
  const { user, token } = useAuth();
  
  // Check subscription for delay badge
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
          console.log('[GlobalMarkets] Subscription:', level, 'isPro:', is_pro);
        })
        .catch((err) => {
          console.error('[GlobalMarkets] Failed to fetch subscription:', err);
          setSubscriptionLevel('free');
          setIsPro(false);
        });
    }
  }, [user, token]);
  
  // Delay info cu update frequency REAL pentru PRO
  // Data update info - fără a menționa delay
  const delayInfo = isPro
    ? { text: 'PRO', color: 'bg-green-500', description: t('global.proDataDesc'), frequency: '30s' }
    : { text: 'Live', color: 'bg-blue-500', description: t('global.liveDataDesc'), frequency: '60s' };

  const fetchData = useCallback(async () => {
    try {
      // CACHE BUSTING - timestamp forțează browser să facă request nou
      const timestamp = Date.now();
      const res = await fetch(`${API_URL}/api/global/overview?_t=${timestamp}`, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      if (res.ok) {
        const result = await res.json();
        setData(result);
        console.log('[GlobalMarkets] Fetched LIVE data at', new Date().toLocaleTimeString(), '- assets:', result.indices?.length || 0);
      }
    } catch (err) {
      console.error('Error fetching global data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    
    // Refresh la 60 secunde - date cu delay 15min
    // Nu are sens să facem refresh mai des
    const interval = setInterval(fetchData, 60000);
    
    console.log('[GlobalMarkets] Auto-refresh every 60s');
    
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = () => {
    setRefreshing(true);
    setData(null); // Clear old data
    fetchData();
  };

  const handleAssetClick = useCallback((asset) => {
    // Check if we should show reminder
    if (shouldShowReminder(!!user)) {
      setSelectedAsset(asset);
      setShowReminder(true);
      // Don't mark as shown here - wait for user to actually close it
    } else {
      setSelectedAsset(asset);
    }
  }, [user]);

  const handleCloseReminder = useCallback(() => {
    setShowReminder(false);
    // Mark as shown when user actually closes the reminder
    if (user) {
      markReminderShown();
    }
  }, [user]);

  const handleOpenCompanion = useCallback(() => {
    setShowReminder(false);
    setSelectedAsset(null); // Clear selected asset so modal doesn't open
    setCompanionOpen(true);
    // Mark as shown when user opens companion
    if (user) {
      markReminderShown();
    }
  }, [user]);

  const handleCloseModal = useCallback(() => {
    setSelectedAsset(null);
    setCompanionOpen(false); // Also close companion when closing modal
  }, []);

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
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={`${t('global.title')} Live | FinRomania`}
        description={t('global.seoDescription')}
        keywords="indici globali, S&P 500, NASDAQ, DAX, bitcoin, petrol, aur, forex"
      />

      {/* Trading Reminder Modal */}
      <TradingReminder 
        isOpen={showReminder}
        onClose={handleCloseReminder}
        onOpenCompanion={handleOpenCompanion}
      />

      {/* Asset Detail Modal cu ProStockChart */}
      {selectedAsset && !showReminder && (
        <AssetDetailModal 
          asset={selectedAsset} 
          onClose={handleCloseModal}
          isPro={isPro}
          token={token}
        />
      )}

      <div className="space-y-6">
        {/* Hero cu Delay Badge */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-4"
        >
          <div className="flex items-center justify-center gap-3 mb-2">
            <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 bg-clip-text text-transparent">
              {t('global.title')}
            </h1>
            <Badge className={`${delayInfo.color} text-white ${isPro ? 'animate-pulse' : ''}`}>
              <Zap className="w-3 h-3 mr-1" />
              {delayInfo.text}
            </Badge>
            {refreshing && (
              <Badge className="bg-blue-500 text-white">
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                {t('global.updating')}
              </Badge>
            )}
          </div>
          <p className="text-muted-foreground">
            {delayInfo.description} • {t('global.autoRefresh')} {delayInfo.frequency}
            {!isPro && (
              <Link to="/pricing" className="text-amber-600 hover:underline ml-2">
                → {t('global.fasterRefresh')}
              </Link>
            )}
          </p>
        </motion.div>

        {/* Market Status - ore burse per exchange cu countdown */}
        <Card className="border border-border/50">
          <CardContent className="p-4">
            <MarketStatusBar marketStatus={data?.market_status} />
          </CardContent>
        </Card>

        {/* Top Section */}
        <div className="grid lg:grid-cols-[1fr,300px] gap-6">
          {/* Heatmap */}
          <GlobalHeatmap assets={allAssets} onAssetClick={handleAssetClick} />
          
          {/* Sidebar */}
          <div className="space-y-6">
            <GlobalSentimentGauge sentiment={data?.sentiment} />
            <TopMovers assets={allAssets} onAssetClick={handleAssetClick} />
          </div>
        </div>

        {/* Tabs for Categories */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="overflow-x-auto">
              <TabsList className="flex-shrink-0 w-full sm:w-auto">
                <TabsTrigger value="all">
                  <span className="hidden sm:inline">🌐 </span>{t('global.all')}
                </TabsTrigger>
                <TabsTrigger value="indices">
                  <span className="hidden sm:inline">📊 </span>{t('global.indices')}
                </TabsTrigger>
                <TabsTrigger value="commodities">
                  <span className="hidden sm:inline">🛢️ </span>{t('global.commodities')}
                </TabsTrigger>
                <TabsTrigger value="crypto">
                  <span className="hidden sm:inline">₿ </span>{t('global.crypto')}
                </TabsTrigger>
                <TabsTrigger value="forex">
                  <span className="hidden sm:inline">💱 </span>{t('global.forex')}
                </TabsTrigger>
              </TabsList>
            </div>
            
            <Button variant="outline" size="sm" onClick={handleRefresh} disabled={refreshing} className="self-end sm:self-auto">
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              {t('common.refresh')}
            </Button>
          </div>

          <TabsContent value="all" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {allAssets.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} onClick={handleAssetClick} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="indices" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.indices?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} onClick={handleAssetClick} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="commodities" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.commodities?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} onClick={handleAssetClick} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="crypto" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.crypto?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} onClick={handleAssetClick} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="forex" className="mt-6">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data?.forex?.map((asset, idx) => (
                <AssetCard key={asset.symbol} asset={asset} index={idx} onClick={handleAssetClick} />
              ))}
            </div>
          </TabsContent>
        </Tabs>

        {/* Info Banner */}
        <Card className="bg-gradient-to-r from-blue-700 to-blue-500 text-white border-0">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold mb-1">{t('global.whyGlobalMatters')}</h3>
                <p className="text-blue-100">
                  {t('global.whyGlobalDesc')}
                </p>
              </div>
              <Link to="/stocks">
                <Button className="bg-white text-blue-600 hover:bg-blue-50">
                  {t('global.seeBVB')} →
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Educational Note */}
        <Card className="bg-gray-50 dark:bg-zinc-800">
          <CardContent className="p-4 text-sm text-muted-foreground">
            <h4 className="font-semibold text-foreground mb-2">ℹ️ {t('global.infoTitle')}</h4>
            <ul className="space-y-1">
              <li>• <strong>{t('global.indices')}:</strong> {t('global.indicesDesc')}</li>
              <li>• <strong>{t('global.commodities')}:</strong> {t('global.commoditiesDesc')}</li>
              <li>• <strong>{t('global.crypto')}:</strong> {t('global.cryptoDesc')}</li>
              <li>• <strong>{t('global.forex')}:</strong> {t('global.forexDesc')}</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Trading Companion - Verifică Înainte */}
      {!selectedAsset && (
        <TradingCompanion 
          stockSymbol={selectedAsset?.symbol || "Global"}
          stockName={selectedAsset?.name || t('global.title')}
          currentPrice={selectedAsset?.price}
          changePercent={selectedAsset?.change_percent || data?.sentiment?.avg_change}
          stockType="global"
          forceOpen={companionOpen}
          onOpenChange={setCompanionOpen}
        />
      )}
    </>
  );
}
