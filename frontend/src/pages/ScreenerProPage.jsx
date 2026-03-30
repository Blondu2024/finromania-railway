import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  TrendingUp, TrendingDown, Activity, Filter, Zap, Target, Crown,
  RefreshCw, ChevronDown, ChevronUp, Gem, Rocket, Coins, Trophy,
  RotateCcw, ArrowUpDown, Eye, Download, BarChart3, PieChart
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Slider } from '../components/ui/slider';
import { Switch } from '../components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../components/ui/tooltip';
import { toast } from 'sonner';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';
import StockLogo from '../components/StockLogo';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// SIGNAL BADGE COMPONENT
// ============================================
const SignalBadge = ({ signal, score, t }) => {
  const configs = {
    STRONG_BUY: { bg: 'bg-green-600', text: t('screener.strongBuy'), icon: '🚀' },
    BUY: { bg: 'bg-green-500', text: t('screener.buy'), icon: '📈' },
    HOLD: { bg: 'bg-gray-500', text: t('screener.hold'), icon: '⏸️' },
    SELL: { bg: 'bg-orange-500', text: t('screener.sell'), icon: '📉' },
    STRONG_SELL: { bg: 'bg-red-600', text: t('screener.strongSell'), icon: '🔻' },
  };

  const config = configs[signal] || configs.HOLD;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <Badge className={`${config.bg} text-white font-bold px-2 py-1`}>
            {config.icon} {config.text}
          </Badge>
        </TooltipTrigger>
        <TooltipContent>
          <p>{t('screener.score')}: {score}/100</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// ============================================
// INDICATOR CELL COMPONENT
// ============================================
const IndicatorCell = ({ value, type, thresholds }) => {
  if (value === null || value === undefined) {
    return <span className="text-gray-400">-</span>;
  }

  let color = 'text-gray-600';
  let icon = null;

  if (type === 'rsi') {
    if (value < 30) {
      color = 'text-green-600 font-bold';
      icon = <TrendingUp className="w-3 h-3 inline ml-1" />;
    } else if (value > 70) {
      color = 'text-red-600 font-bold';
      icon = <TrendingDown className="w-3 h-3 inline ml-1" />;
    }
  } else if (type === 'pe') {
    if (value > 0 && value < 10) {
      color = 'text-green-600 font-bold';
    } else if (value > 25) {
      color = 'text-orange-500';
    }
  } else if (type === 'roe') {
    if (value > 15) {
      color = 'text-green-600 font-bold';
    } else if (value < 5) {
      color = 'text-red-500';
    }
  } else if (type === 'change') {
    color = value >= 0 ? 'text-green-600' : 'text-red-600';
  }

  return (
    <span className={color}>
      {typeof value === 'number' ? value.toFixed(type === 'macd' ? 4 : 2) : value}
      {icon}
    </span>
  );
};

// ============================================
// PRESET CARD COMPONENT
// ============================================
const PresetCard = ({ preset, onClick, isActive }) => {
  const icons = {
    gem: <Gem className="w-5 h-5" />,
    rocket: <Rocket className="w-5 h-5" />,
    coins: <Coins className="w-5 h-5" />,
    target: <Target className="w-5 h-5" />,
    trophy: <Trophy className="w-5 h-5" />,
    refresh: <RotateCcw className="w-5 h-5" />,
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${
        isActive
          ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20'
          : 'border-gray-200 hover:border-amber-300 dark:border-gray-700'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
          isActive ? 'bg-amber-500 text-white' : 'bg-gray-100 text-gray-600 dark:bg-gray-800'
        }`}>
          {icons[preset.icon] || <Filter className="w-5 h-5" />}
        </div>
        <div className="flex-1">
          <p className="font-semibold">{preset.name}</p>
          <p className="text-xs text-muted-foreground">{preset.description}</p>
        </div>
      </div>
    </motion.div>
  );
};

// ============================================
// SIGNAL SUMMARY COMPONENT
// ============================================
const SignalSummary = ({ summary, t }) => {
  const signals = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL'];
  const colors = {
    STRONG_BUY: 'bg-green-600',
    BUY: 'bg-green-400',
    HOLD: 'bg-gray-400',
    SELL: 'bg-orange-400',
    STRONG_SELL: 'bg-red-600',
  };
  const labels = {
    STRONG_BUY: t('screener.strongBuy'),
    BUY: t('screener.buy'),
    HOLD: t('screener.hold'),
    SELL: t('screener.sell'),
    STRONG_SELL: t('screener.strongSell'),
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
      {signals.map(signal => (
        <div key={signal} className="text-center">
          <div className={`${colors[signal]} text-white rounded-lg p-3 mb-1`}>
            <p className="text-2xl font-bold">{summary[signal]?.count || 0}</p>
          </div>
          <p className="text-xs text-muted-foreground">{labels[signal]}</p>
        </div>
      ))}
    </div>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================
export default function ScreenerProPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [stocks, setStocks] = useState([]);
  const [presets, setPresets] = useState([]);
  const [signalSummary, setSignalSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scanTime, setScanTime] = useState(null);
  const [activePreset, setActivePreset] = useState(null);
  const [sortConfig, setSortConfig] = useState({ key: 'signal_score', direction: 'desc' });
  const [expandedStock, setExpandedStock] = useState(null);
  const [isRefreshingBackground, setIsRefreshingBackground] = useState(false);
  const [cacheAge, setCacheAge] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const pollingRef = useRef(null);

  // Filters state
  const [filters, setFilters] = useState({
    min_rsi: null,
    max_rsi: null,
    macd_signal: null,
    above_sma20: null,
    min_pe: null,
    max_pe: null,
    min_roe: null,
    signal_filter: null,
  });

  // Fetch subscription status live (avoid stale context after PRO activation)
  useEffect(() => {
    if (!token) return;
    fetch(`${API_URL}/api/subscriptions/status`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(data => setSubscriptionStatus(data))
      .catch(console.error);
  }, [token]);

  const isPro = subscriptionStatus?.subscription?.is_pro
    || user?.subscription_level === 'pro'
    || user?.subscription_level === 'premium';

  // Funcție de polling — verifică la fiecare 8s dacă cache-ul e gata
  const startPolling = useCallback((currentToken) => {
    if (pollingRef.current) return; // deja în polling
    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_URL}/api/screener-pro/scan`, {
          headers: { 'Authorization': `Bearer ${currentToken}` }
        });
        if (res.ok) {
          const data = await res.json();
          if ((data.stocks || []).length > 0 && !data.cache_refreshing) {
            setStocks(data.stocks || []);
            setScanTime('0.3');
            setCacheAge(data.scanned_at);
            setIsRefreshingBackground(false);
            clearInterval(pollingRef.current);
            pollingRef.current = null;
            toast.success(`${data.count} ${t('screener.stocksUpdated')}`);
          }
        }
      } catch (err) {
        // ignore polling errors
      }
    }, 8000);
  }, [t]);

  // Cleanup polling la unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  // Fetch presets
  useEffect(() => {
    fetch(`${API_URL}/api/screener-pro/presets`)
      .then(r => r.json())
      .then(data => setPresets(data.presets || []))
      .catch(console.error);
  }, []);

  // Full scan
  const runFullScan = useCallback(async () => {
    if (!isPro) {
      toast.error(t('screener.proRequired'));
      return;
    }

    setLoading(true);
    const startTime = Date.now();

    try {
      const [scanRes, summaryRes] = await Promise.all([
        fetch(`${API_URL}/api/screener-pro/scan`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_URL}/api/screener-pro/signals/summary`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (scanRes.ok) {
        const data = await scanRes.json();
        setStocks(data.stocks || []);
        setScanTime(((Date.now() - startTime) / 1000).toFixed(1));
        setCacheAge(data.scanned_at);

        if (data.cache_refreshing && (data.stocks || []).length === 0) {
          // Cache gol — pornim polling automat, userul nu trebuie să facă nimic
          setIsRefreshingBackground(true);
          startPolling(token);
          toast.info(t('screener.preparingData'));
        } else if (data.cache_refreshing) {
          // Date vechi disponibile, refresh în background
          setIsRefreshingBackground(true);
          startPolling(token);
          toast.success(t('screener.stocksAutoUpdate', { count: data.count }));
        } else if (data.from_cache) {
          const timeStr = data.scanned_at
            ? new Date(data.scanned_at).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' })
            : '';
          toast.success(t('screener.stocksFromCache', { count: data.count, time: timeStr }));
        } else {
          toast.success(t('screener.scanComplete', { count: data.count }));
        }
      } else {
        const err = await scanRes.json();
        toast.error(err.detail || t('screener.scanError'));
      }

      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSignalSummary(summaryData.summary);
      }
    } catch (err) {
      console.error(err);
      toast.error(t('screener.connectionError'));
    } finally {
      setLoading(false);
      setActivePreset(null);
    }
  }, [token, isPro, startPolling]);

  // Apply preset
  const applyPreset = async (preset) => {
    if (!isPro) {
      toast.error(t('screener.proRequired'));
      return;
    }

    setLoading(true);
    setActivePreset(preset.id);

    try {
      const res = await fetch(`${API_URL}/api/screener-pro/filter`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(preset.filters)
      });

      if (res.ok) {
        const data = await res.json();
        setStocks(data.stocks || []);
        toast.success(t('screener.presetFound', { name: preset.name, count: data.count }));
      }
    } catch (err) {
      console.error(err);
      toast.error(t('screener.filterError'));
    } finally {
      setLoading(false);
    }
  };

  // Sort handler
  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  // Sorted stocks
  const sortedStocks = [...stocks].sort((a, b) => {
    const aVal = a[sortConfig.key] ?? 0;
    const bVal = b[sortConfig.key] ?? 0;
    return sortConfig.direction === 'desc' ? bVal - aVal : aVal - bVal;
  });

  // Export to CSV
  const exportCSV = () => {
    const headers = [t('common.symbol'), t('common.name'), `${t('common.price')} (RON)`, `${t('common.change')} %`, 'RSI', 'MACD', 'P/E', 'ROE %', 'Div Yield % (BVB.ro)', 'D/E', t('screener.signal'), t('screener.score')];
    const rows = sortedStocks.map(s => [
      s.symbol,
      `"${(s.name || '').replace(/"/g, '""')}"`,
      s.price ?? '',
      s.change_percent ?? '',
      s.rsi ?? '',
      s.macd ?? '',
      s.pe_ratio ?? '',
      s.roe ?? '',
      s.dividend_yield ?? 'N/A',
      s.debt_equity ?? 'N/A',
      s.signal_text ?? '',
      s.signal_score ?? ''
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `screener_pro_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // If not PRO, show upgrade prompt
  if (!isPro) {
    return (
      <>
        <SEO title="Screener PRO | FinRomania" />
        <div className="max-w-4xl mx-auto py-12">
          <Card className="border-2 border-amber-400 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20">
            <CardContent className="p-8 text-center">
              <Crown className="w-16 h-16 mx-auto text-amber-500 mb-4" />
              <h1 className="text-3xl font-bold mb-4">{t('screener.proTitle')}</h1>
              <p className="text-lg text-muted-foreground mb-6">
                {t('screener.proSubtitle')}
              </p>
              <div className="grid md:grid-cols-3 gap-4 mb-8 text-left">
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                  <BarChart3 className="w-8 h-8 text-blue-500 mb-2" />
                  <h3 className="font-bold">{t('screener.technicals')}</h3>
                  <p className="text-sm text-muted-foreground">{t('screener.techDesc')}</p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                  <PieChart className="w-8 h-8 text-green-500 mb-2" />
                  <h3 className="font-bold">{t('screener.fundamentals')}</h3>
                  <p className="text-sm text-muted-foreground">P/E, ROE, EPS, Dividend Yield, Market Cap</p>
                </div>
                <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
                  <Target className="w-8 h-8 text-blue-500 mb-2" />
                  <h3 className="font-bold">{t('screener.aiSignals')}</h3>
                  <p className="text-sm text-muted-foreground">{t('screener.signalDesc')}</p>
                </div>
              </div>
              <Link to="/pricing">
                <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                  <Crown className="w-5 h-5 mr-2" />
                  {t('screener.upgradeProPrice')}
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <SEO title="Screener PRO | FinRomania" description={t('screener.proSubtitle')} />

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Crown className="w-8 h-8 text-amber-500" />
              {t('screener.proTitle')}
              <Badge className="bg-amber-500 text-white">LIVE DATA</Badge>
            </h1>
            <p className="text-muted-foreground">
              {t('screener.proSubtitle')}
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={runFullScan} disabled={loading} className="bg-gradient-to-r from-amber-500 to-orange-500" data-testid="screener-scan-btn">
              {loading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Zap className="w-4 h-4 mr-2" />
              )}
              {t('screener.scanAll')}
            </Button>
            {stocks.length > 0 && (
              <Button variant="outline" onClick={exportCSV} data-testid="export-screener-csv">
                <Download className="w-4 h-4 mr-2" />
                {t('screener.exportCSV')}
              </Button>
            )}
          </div>
        </div>

        {/* Banner refresh background */}
        {isRefreshingBackground && (
          <div className="flex items-center gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg text-sm text-blue-700 dark:text-blue-300" data-testid="screener-refresh-banner">
            <RefreshCw className="w-4 h-4 animate-spin flex-shrink-0" />
            <span>{t('screener.refreshing')}</span>
          </div>
        )}

        {/* Signal Summary */}
        {signalSummary && (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">{t('screener.signalSummary')}</CardTitle>
            </CardHeader>
            <CardContent>
              <SignalSummary summary={signalSummary} t={t} />
            </CardContent>
          </Card>
        )}

        {/* Presets */}
        <div>
          <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            {t('screener.presets')}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {presets.map(preset => (
              <PresetCard
                key={preset.id}
                preset={preset}
                isActive={activePreset === preset.id}
                onClick={() => applyPreset(preset)}
              />
            ))}
          </div>
        </div>

        {/* Results */}
        {loading ? (
          <Card>
            <CardContent className="p-8">
              <div className="flex flex-col items-center justify-center gap-4">
                <RefreshCw className="w-12 h-12 text-amber-500 animate-spin" />
                <p className="text-lg font-semibold">{t('screener.scanning')}</p>
                <p className="text-sm text-muted-foreground">{t('screener.scanningDetail')}</p>
              </div>
            </CardContent>
          </Card>
        ) : stocks.length > 0 ? (
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <CardTitle>
                  {t('screener.results')} ({stocks.length} {t('screener.stocks')})
                  {scanTime && <span className="text-sm font-normal text-muted-foreground ml-2">{t('screener.inSeconds', { time: scanTime })}</span>}
                </CardTitle>
                {cacheAge && (
                  <span className="text-xs text-muted-foreground flex items-center gap-1">
                    {isRefreshingBackground && <RefreshCw className="w-3 h-3 animate-spin" />}
                    {t('screener.updatedAt', { time: new Date(cacheAge).toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' }) })}
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="p-3 text-left">{t('screener.stock')}</th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('price')}>
                        {t('screener.price')} <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('change_percent')}>
                        {t('screener.varPercent')} <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('rsi')}>
                        RSI <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right">MACD</th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('pe_ratio')}>
                        P/E <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('roe')}>
                        ROE% <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('dividend_yield')}>
                        Div Yield <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('debt_equity')}>
                        D/E <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-right cursor-pointer hover:bg-muted" onClick={() => handleSort('signal_score')}>
                        {t('screener.signal')} <ArrowUpDown className="w-3 h-3 inline" />
                      </th>
                      <th className="p-3 text-center">{t('screener.detailsLabel')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedStocks.map((stock, idx) => (
                      <React.Fragment key={stock.symbol}>
                        <motion.tr
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: idx * 0.02 }}
                          className="border-b hover:bg-muted/30"
                        >
                          <td className="p-3">
                            <div className="flex items-center gap-2">
                              <StockLogo symbol={stock.symbol} logoUrl={stock.logo_url} />
                              <div>
                                <Link to={`/stocks/bvb/${stock.symbol}`} className="font-bold text-blue-600 hover:underline">
                                  {stock.symbol}
                                </Link>
                                <p className="text-xs text-muted-foreground">{stock.name}</p>
                              </div>
                            </div>
                          </td>
                          <td className="p-3 text-right font-medium">{stock.price?.toFixed(2)} RON</td>
                          <td className="p-3 text-right">
                            <IndicatorCell value={stock.change_percent} type="change" />
                          </td>
                          <td className="p-3 text-right">
                            <IndicatorCell value={stock.rsi} type="rsi" />
                          </td>
                          <td className="p-3 text-right">
                            <IndicatorCell value={stock.macd} type="macd" />
                          </td>
                          <td className="p-3 text-right">
                            <IndicatorCell value={stock.pe_ratio} type="pe" />
                          </td>
                          <td className="p-3 text-right">
                            <IndicatorCell value={stock.roe} type="roe" />
                          </td>
                          <td className="p-3 text-right">
                            {stock.dividend_yield !== null && stock.dividend_yield !== undefined ? (
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger>
                                    <span className="text-green-600 font-medium">{stock.dividend_yield.toFixed(2)}%</span>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p className="text-xs">{t('screener.confirmedBVB')}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            ) : (
                              <span className="text-gray-400 text-xs">N/A</span>
                            )}
                          </td>
                          <td className="p-3 text-right">
                            {stock.debt_equity !== null && stock.debt_equity !== undefined ? (
                              <span className={stock.debt_equity > 2 ? 'text-orange-500' : stock.debt_equity > 1 ? 'text-yellow-600' : 'text-gray-700 dark:text-gray-300'}>
                                {stock.debt_equity.toFixed(2)}
                              </span>
                            ) : (
                              <span className="text-gray-400 text-xs">N/A</span>
                            )}
                          </td>
                          <td className="p-3 text-right">
                            <SignalBadge signal={stock.signal} score={stock.signal_score} t={t} />
                          </td>
                          <td className="p-3 text-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setExpandedStock(expandedStock === stock.symbol ? null : stock.symbol)}
                            >
                              {expandedStock === stock.symbol ? <ChevronUp className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            </Button>
                          </td>
                        </motion.tr>

                        {/* Expanded Details */}
                        <AnimatePresence>
                          {expandedStock === stock.symbol && (
                            <motion.tr
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: 'auto' }}
                              exit={{ opacity: 0, height: 0 }}
                            >
                              <td colSpan={11} className="p-4 bg-muted/20">
                                <div className="grid md:grid-cols-3 gap-4">
                                  {/* Technicals */}
                                  <div className="space-y-2">
                                    <h4 className="font-bold text-sm flex items-center gap-1">
                                      <BarChart3 className="w-4 h-4" /> {t('screener.technicals')}
                                    </h4>
                                    <div className="text-sm space-y-1">
                                      <p>RSI(14): <span className="font-mono">{stock.rsi?.toFixed(2) || '-'}</span></p>
                                      <p>MACD: <span className="font-mono">{stock.macd?.toFixed(4) || '-'}</span></p>
                                      <p>MACD Signal: <span className="font-mono">{stock.macd_signal?.toFixed(4) || '-'}</span></p>
                                      <p>SMA20: <span className="font-mono">{stock.sma20?.toFixed(2) || '-'}</span></p>
                                      <p>SMA50: <span className="font-mono">{stock.sma50?.toFixed(2) || '-'}</span></p>
                                      <p>BB Upper: <span className="font-mono">{stock.bb_upper?.toFixed(2) || '-'}</span></p>
                                      <p>BB Lower: <span className="font-mono">{stock.bb_lower?.toFixed(2) || '-'}</span></p>
                                    </div>
                                  </div>

                                  {/* Fundamentals */}
                                  <div className="space-y-2">
                                    <h4 className="font-bold text-sm flex items-center gap-1">
                                      <PieChart className="w-4 h-4" /> {t('screener.fundamentals')}
                                    </h4>
                                    <div className="text-sm space-y-1">
                                      <p>P/E Ratio: <span className="font-mono">{stock.pe_ratio?.toFixed(2) || <span className="text-gray-400">N/A</span>}</span></p>
                                      <p>P/B Ratio: <span className="font-mono">{stock.pb_ratio?.toFixed(2) || <span className="text-gray-400">N/A</span>}</span></p>
                                      <p>ROE: <span className="font-mono">{stock.roe !== null && stock.roe !== undefined ? `${stock.roe.toFixed(2)}%` : <span className="text-gray-400">N/A</span>}</span></p>
                                      <p>EPS: <span className="font-mono">{stock.eps !== null && stock.eps !== undefined ? stock.eps.toFixed(2) : <span className="text-gray-400">N/A</span>}</span></p>
                                      <p>
                                        Div Yield:{' '}
                                        {stock.dividend_yield !== null && stock.dividend_yield !== undefined ? (
                                          <span>
                                            <span className="font-mono text-green-600">{stock.dividend_yield.toFixed(2)}%</span>
                                            <span className="ml-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-1.5 py-0.5 rounded font-normal">BVB.ro</span>
                                          </span>
                                        ) : (
                                          <span className="text-gray-400 font-mono">N/A</span>
                                        )}
                                      </p>
                                      <p>
                                        Dat/Cap (D/E):{' '}
                                        {stock.debt_equity !== null && stock.debt_equity !== undefined ? (
                                          <span className={`font-mono ${stock.debt_equity > 2 ? 'text-orange-500' : ''}`}>
                                            {stock.debt_equity.toFixed(2)}
                                          </span>
                                        ) : (
                                          <span className="text-gray-400 font-mono">N/A</span>
                                        )}
                                      </p>
                                      <p>Market Cap: <span className="font-mono">{stock.market_cap ? (stock.market_cap/1e9).toFixed(2) + 'B' : <span className="text-gray-400">N/A</span>}</span></p>
                                    </div>
                                  </div>

                                  {/* Signal Reasons */}
                                  <div className="space-y-2">
                                    <h4 className="font-bold text-sm flex items-center gap-1">
                                      <Target className="w-4 h-4" /> {t('screener.signalReasons')}
                                    </h4>
                                    <div className="space-y-1">
                                      {stock.signal_reasons?.map((reason, i) => (
                                        <div key={i} className="flex items-center gap-2 text-sm">
                                          <Badge variant={reason[1] === 'bullish' ? 'default' : 'destructive'} className="text-xs">
                                            {reason[1] === 'bullish' ? '↑' : '↓'}
                                          </Badge>
                                          <span>{reason[0]}</span>
                                          <span className="text-muted-foreground text-xs">({reason[2]})</span>
                                        </div>
                                      ))}
                                      {stock.warnings?.length > 0 && (
                                        <div className="mt-2 text-orange-600 text-xs">
                                          ⚠️ {stock.warnings.join(', ')}
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              </td>
                            </motion.tr>
                          )}
                        </AnimatePresence>
                      </React.Fragment>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-dashed">
            <CardContent className="p-12 text-center">
              <Activity className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">{t('screener.readyToScan')}</h3>
              <p className="text-muted-foreground mb-4">
                {t('screener.readyToScanDesc')}
              </p>
              <Button onClick={runFullScan} className="bg-gradient-to-r from-amber-500 to-orange-500">
                <Zap className="w-4 h-4 mr-2" />
                {t('screener.startScan')}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Disclaimer */}
        <p className="text-xs text-center text-muted-foreground">
          {t('screener.disclaimer')}
        </p>
      </div>
    </>
  );
}
