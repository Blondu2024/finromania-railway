import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Filter, TrendingUp, TrendingDown, BarChart3, Zap, Search,
  ChevronRight, Sliders, Rocket, Target, Building2, DollarSign, Activity,
  Crown, Lock, PieChart
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Slider } from '../components/ui/slider';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Predefined Screener Card
const ScreenerCard = ({ screener, onClick, isActive }) => {
  const getIcon = (id) => {
    const icons = {
      'top_gainers': <Rocket className="w-5 h-5" />,
      'top_losers': <TrendingDown className="w-5 h-5" />,
      'most_active': <Activity className="w-5 h-5" />,
      'penny_stocks': <DollarSign className="w-5 h-5" />,
      'blue_chips': <Target className="w-5 h-5" />,
      'high_volume_gainers': <Zap className="w-5 h-5" />,
      'banking_sector': <Building2 className="w-5 h-5" />,
      'energy_sector': <Zap className="w-5 h-5" />
    };
    return icons[id] || <Filter className="w-5 h-5" />;
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <Card
        className={`cursor-pointer transition-all hover:shadow-lg ${
          isActive ? 'ring-2 ring-blue-500 bg-blue-50' : ''
        }`}
        onClick={onClick}
      >
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              isActive ? 'bg-blue-500 text-white' : 'bg-slate-100 text-slate-600'
            }`}>
              {getIcon(screener.id)}
            </div>
            <div className="flex-1">
              <p className="font-semibold">{screener.name}</p>
              <p className="text-xs text-muted-foreground">{screener.description}</p>
            </div>
            <ChevronRight className={`w-5 h-5 transition-transform ${
              isActive ? 'rotate-90 text-blue-500' : 'text-muted-foreground'
            }`} />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Result Stock Row
const StockRow = ({ stock, index }) => {
  const isPositive = (stock.change_percent || 0) >= 0;
  
  return (
    <motion.tr
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      className="hover:bg-muted/50"
    >
      <td className="p-3">
        <Link to={`/stocks/bvb/${stock.symbol}`} className="font-bold text-blue-600 hover:underline">
          {stock.symbol}
        </Link>
      </td>
      <td className="p-3">
        <Link to={`/stocks/bvb/${stock.symbol}`} className="hover:text-blue-600">
          {stock.name}
        </Link>
      </td>
      <td className="p-3">
        <Badge variant="outline">{stock.sector || 'N/A'}</Badge>
      </td>
      <td className="p-3 text-right font-medium">
        {stock.price?.toFixed(2)} RON
      </td>
      <td className="p-3 text-right">
        <div className={`flex items-center justify-end gap-1 ${
          isPositive ? 'text-green-600' : 'text-red-600'
        }`}>
          {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span className="font-medium">
            {isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%
          </span>
        </div>
      </td>
      <td className="p-3 text-right text-muted-foreground">
        {(stock.volume || 0).toLocaleString('ro-RO')}
      </td>
    </motion.tr>
  );
};

// Custom Filter Panel
const CustomFilterPanel = ({ onApply }) => {
  const [priceRange, setPriceRange] = useState([0, 200]);
  const [changeRange, setChangeRange] = useState([-10, 10]);
  const [minVolume, setMinVolume] = useState('');

  const handleApply = () => {
    onApply({
      min_price: priceRange[0] > 0 ? priceRange[0] : null,
      max_price: priceRange[1] < 200 ? priceRange[1] : null,
      min_change: changeRange[0] > -10 ? changeRange[0] : null,
      max_change: changeRange[1] < 10 ? changeRange[1] : null,
      min_volume: minVolume ? parseInt(minVolume) : null,
      sort_by: 'change_percent',
      sort_order: 'desc',
      limit: 50
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Sliders className="w-5 h-5" />
          Filtre Personalizate
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Price Range */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Preț: {priceRange[0]} - {priceRange[1]} RON
          </label>
          <Slider
            value={priceRange}
            onValueChange={setPriceRange}
            min={0}
            max={200}
            step={1}
            className="mt-2"
          />
        </div>

        {/* Change Range */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            Variație: {changeRange[0]}% - {changeRange[1]}%
          </label>
          <Slider
            value={changeRange}
            onValueChange={setChangeRange}
            min={-10}
            max={10}
            step={0.5}
            className="mt-2"
          />
        </div>

        {/* Volume */}
        <div>
          <label className="text-sm font-medium mb-2 block">Volum Minim</label>
          <Input
            type="number"
            value={minVolume}
            onChange={(e) => setMinVolume(e.target.value)}
            placeholder="Ex: 10000"
          />
        </div>

        <Button onClick={handleApply} className="w-full">
          <Filter className="w-4 h-4 mr-2" />
          Aplică Filtre
        </Button>
      </CardContent>
    </Card>
  );
};

// PRO Filter Panel - Fundamental Indicators
const ProFilterPanel = ({ onApply, isPro, onUpgrade }) => {
  const [peRange, setPeRange] = useState([0, 30]);
  const [roeRange, setRoeRange] = useState([0, 30]);
  const [minDividend, setMinDividend] = useState('');
  const [maxDebt, setMaxDebt] = useState('');

  const handleApply = () => {
    onApply({
      min_pe: peRange[0] > 0 ? peRange[0] : null,
      max_pe: peRange[1] < 30 ? peRange[1] : null,
      min_roe: roeRange[0] > 0 ? roeRange[0] : null,
      max_roe: roeRange[1] < 30 ? roeRange[1] : null,
      min_dividend_yield: minDividend ? parseFloat(minDividend) : null,
      max_debt_equity: maxDebt ? parseFloat(maxDebt) : null,
      sort_by: 'roe',
      sort_order: 'desc',
      limit: 50
    });
  };

  if (!isPro) {
    return (
      <Card className="border-2 border-dashed border-amber-300 bg-gradient-to-br from-amber-50 to-orange-50">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Crown className="w-5 h-5 text-amber-500" />
            Screener PRO
            <Badge className="bg-amber-500">PRO</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center py-4">
            <Lock className="w-12 h-12 mx-auto text-amber-400 mb-3" />
            <p className="font-semibold mb-2">Indicatori Fundamentali</p>
            <p className="text-sm text-muted-foreground mb-4">
              Accesează P/E, ROE, EPS, Marjă Profit, Grad Îndatorare și multe altele
            </p>
            <ul className="text-sm text-left space-y-2 mb-4">
              <li className="flex items-center gap-2">
                <PieChart className="w-4 h-4 text-amber-500" />
                P/E Ratio, P/Book Value
              </li>
              <li className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                ROE, ROI, EPS
              </li>
              <li className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-blue-500" />
                Randament Dividend
              </li>
              <li className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-purple-500" />
                Marjă Profit, Grad Îndatorare
              </li>
            </ul>
            <Button onClick={onUpgrade} className="w-full bg-gradient-to-r from-amber-500 to-orange-500">
              <Crown className="w-4 h-4 mr-2" />
              Upgrade la PRO - 49 lei/lună
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-amber-400 bg-gradient-to-br from-amber-50 to-orange-50">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Crown className="w-5 h-5 text-amber-500" />
          Screener PRO
          <Badge className="bg-amber-500">ACTIV</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* P/E Range */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            P/E Ratio: {peRange[0]} - {peRange[1]}
          </label>
          <Slider
            value={peRange}
            onValueChange={setPeRange}
            min={0}
            max={30}
            step={0.5}
            className="mt-2"
          />
        </div>

        {/* ROE Range */}
        <div>
          <label className="text-sm font-medium mb-2 block">
            ROE (%): {roeRange[0]} - {roeRange[1]}
          </label>
          <Slider
            value={roeRange}
            onValueChange={setRoeRange}
            min={0}
            max={30}
            step={1}
            className="mt-2"
          />
        </div>

        {/* Dividend Yield */}
        <div>
          <label className="text-sm font-medium mb-2 block">Randament Dividend Min (%)</label>
          <Input
            type="number"
            value={minDividend}
            onChange={(e) => setMinDividend(e.target.value)}
            placeholder="Ex: 5"
          />
        </div>

        {/* Debt/Equity */}
        <div>
          <label className="text-sm font-medium mb-2 block">Îndatorare Max (Debt/Equity)</label>
          <Input
            type="number"
            value={maxDebt}
            onChange={(e) => setMaxDebt(e.target.value)}
            placeholder="Ex: 0.5"
            step="0.1"
          />
        </div>

        <Button onClick={handleApply} className="w-full bg-gradient-to-r from-amber-500 to-orange-500">
          <Filter className="w-4 h-4 mr-2" />
          Aplică Filtre PRO
        </Button>
      </CardContent>
    </Card>
  );
};

// PRO Stock Row with fundamental data
const ProStockRow = ({ stock, index }) => {
  const isPositive = (stock.change_percent || 0) >= 0;
  
  return (
    <motion.tr
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.03 }}
      className="hover:bg-muted/50"
    >
      <td className="p-3">
        <Link to={`/stocks/bvb/${stock.symbol}`} className="font-bold text-blue-600 hover:underline">
          {stock.symbol}
        </Link>
      </td>
      <td className="p-3 text-right font-medium">
        {stock.price?.toFixed(2)} RON
      </td>
      <td className="p-3 text-right">
        <span className={isPositive ? 'text-green-600' : 'text-red-600'}>
          {isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%
        </span>
      </td>
      <td className="p-3 text-right font-medium text-purple-600">
        {stock.pe_ratio?.toFixed(1) || '-'}
      </td>
      <td className="p-3 text-right text-blue-600">
        {stock.pb_ratio?.toFixed(2) || '-'}
      </td>
      <td className="p-3 text-right text-green-600 font-medium">
        {stock.roe ? `${stock.roe.toFixed(1)}%` : '-'}
      </td>
      <td className="p-3 text-right">
        {stock.eps?.toFixed(2) || '-'}
      </td>
      <td className="p-3 text-right text-amber-600">
        {stock.dividend_yield ? `${stock.dividend_yield.toFixed(1)}%` : '-'}
      </td>
      <td className="p-3 text-right text-red-600">
        {stock.debt_equity?.toFixed(2) || '-'}
      </td>
    </motion.tr>
  );
};

export default function StockScreenerPage() {
  const { user, token } = useAuth();
  const [screeners, setScreeners] = useState([]);
  const [activeScreener, setActiveScreener] = useState(null);
  const [results, setResults] = useState([]);
  const [proResults, setProResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [showProResults, setShowProResults] = useState(false);
  
  const isPro = user?.subscription_level === 'pro' || user?.subscription_level === 'premium';

  // Fetch predefined screeners
  useEffect(() => {
    const fetchScreeners = async () => {
      try {
        const [screenersRes, statsRes] = await Promise.all([
          fetch(`${API_URL}/api/screener/predefined`),
          fetch(`${API_URL}/api/screener/stats`)
        ]);

        if (screenersRes.ok) {
          const data = await screenersRes.json();
          setScreeners(data.screeners || []);
        }
        if (statsRes.ok) {
          const data = await statsRes.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Error fetching screeners:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchScreeners();
  }, []);

  // Run screener
  const runScreener = async (screenerId) => {
    setResultsLoading(true);
    setActiveScreener(screenerId);
    setShowProResults(false);
    
    try {
      const res = await fetch(`${API_URL}/api/screener/run/${screenerId}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      }
    } catch (err) {
      console.error('Error running screener:', err);
    } finally {
      setResultsLoading(false);
    }
  };

  // Run custom screener
  const runCustomScreener = async (filters) => {
    setResultsLoading(true);
    setActiveScreener('custom');
    setShowProResults(false);
    
    try {
      const res = await fetch(`${API_URL}/api/screener/custom`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filters)
      });
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      }
    } catch (err) {
      console.error('Error running custom screener:', err);
    } finally {
      setResultsLoading(false);
    }
  };

  // Run PRO screener
  const runProScreener = async (filters) => {
    if (!isPro) return;
    
    setResultsLoading(true);
    setActiveScreener('pro');
    setShowProResults(true);
    
    try {
      const res = await fetch(`${API_URL}/api/screener/pro/filter`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(filters)
      });
      if (res.ok) {
        const data = await res.json();
        setProResults(data.results || []);
      }
    } catch (err) {
      console.error('Error running PRO screener:', err);
    } finally {
      setResultsLoading(false);
    }
  };

  const handleUpgrade = () => {
    window.location.href = '/pricing';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <div className="grid md:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => <Skeleton key={i} className="h-20" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="Stock Screener BVB | FinRomania"
        description="Filtrează și găsește cele mai bune acțiuni de pe Bursa București. Screener-e predefinite și filtre personalizate."
      />

      <div className="space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-4"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
            🔍 Stock Screener BVB
          </h1>
          <p className="text-muted-foreground">Găsește oportunitățile de investiție potrivite pentru tine</p>
        </motion.div>

        {/* Market Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
              <CardContent className="p-4">
                <p className="text-sm text-blue-100">Total Acțiuni</p>
                <p className="text-2xl font-bold">{stats.total_stocks}</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
              <CardContent className="p-4">
                <p className="text-sm text-green-100">Creșteri</p>
                <p className="text-2xl font-bold">{stats.gainers}</p>
              </CardContent>
            </Card>
            <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
              <CardContent className="p-4">
                <p className="text-sm text-red-100">Scăderi</p>
                <p className="text-2xl font-bold">{stats.losers}</p>
              </CardContent>
            </Card>
            <Card className={`bg-gradient-to-br ${
              stats.market_sentiment === 'bullish' ? 'from-emerald-500 to-emerald-600' : 'from-orange-500 to-orange-600'
            } text-white`}>
              <CardContent className="p-4">
                <p className="text-sm opacity-90">Sentiment</p>
                <p className="text-2xl font-bold capitalize">
                  {stats.market_sentiment === 'bullish' ? '🐂 Bullish' : '🐻 Bearish'}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Content */}
        <div className="grid lg:grid-cols-[1fr,300px] gap-6">
          {/* Left - Screeners & Results */}
          <div className="space-y-6">
            {/* Predefined Screeners */}
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                Screener-e Rapide
              </h2>
              <div className="grid md:grid-cols-2 gap-3">
                {screeners.map(screener => (
                  <ScreenerCard
                    key={screener.id}
                    screener={screener}
                    isActive={activeScreener === screener.id}
                    onClick={() => runScreener(screener.id)}
                  />
                ))}
              </div>
            </div>

            {/* Results */}
            <AnimatePresence mode="wait">
              {(results.length > 0 || proResults.length > 0 || resultsLoading) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>
                          {showProResults ? (
                            <span className="flex items-center gap-2">
                              <Crown className="w-5 h-5 text-amber-500" />
                              Rezultate PRO ({proResults.length} acțiuni)
                            </span>
                          ) : (
                            `📊 Rezultate (${results.length} acțiuni)`
                          )}
                        </span>
                        {activeScreener && activeScreener !== 'custom' && activeScreener !== 'pro' && (
                          <Badge>{screeners.find(s => s.id === activeScreener)?.name}</Badge>
                        )}
                        {activeScreener === 'pro' && (
                          <Badge className="bg-amber-500">PRO</Badge>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {resultsLoading ? (
                        <div className="space-y-2">
                          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12" />)}
                        </div>
                      ) : showProResults ? (
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="border-b text-sm text-muted-foreground">
                                <th className="p-3 text-left">Simbol</th>
                                <th className="p-3 text-right">Preț</th>
                                <th className="p-3 text-right">Var %</th>
                                <th className="p-3 text-right">P/E</th>
                                <th className="p-3 text-right">P/B</th>
                                <th className="p-3 text-right">ROE</th>
                                <th className="p-3 text-right">EPS</th>
                                <th className="p-3 text-right">Div %</th>
                                <th className="p-3 text-right">D/E</th>
                              </tr>
                            </thead>
                            <tbody>
                              {proResults.map((stock, idx) => (
                                <ProStockRow key={stock.symbol} stock={stock} index={idx} />
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div className="overflow-x-auto">
                          <table className="w-full">
                            <thead>
                              <tr className="border-b text-sm text-muted-foreground">
                                <th className="p-3 text-left">Simbol</th>
                                <th className="p-3 text-left">Companie</th>
                                <th className="p-3 text-left">Sector</th>
                                <th className="p-3 text-right">Preț</th>
                                <th className="p-3 text-right">Variație</th>
                                <th className="p-3 text-right">Volum</th>
                              </tr>
                            </thead>
                            <tbody>
                              {results.map((stock, idx) => (
                                <StockRow key={stock.symbol} stock={stock} index={idx} />
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Sidebar - Custom Filters */}
          <div className="space-y-6">
            <CustomFilterPanel onApply={runCustomScreener} />
            <ProFilterPanel onApply={runProScreener} isPro={isPro} onUpgrade={handleUpgrade} />
          </div>
        </div>
      </div>
    </>
  );
}
