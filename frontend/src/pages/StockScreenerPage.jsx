import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Filter, TrendingUp, TrendingDown, BarChart3, Zap, Search,
  ChevronRight, Sliders, Rocket, Target, Building2, DollarSign, Activity
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Slider } from '../components/ui/slider';
import SEO from '../components/SEO';

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

export default function StockScreenerPage() {
  const [screeners, setScreeners] = useState([]);
  const [activeScreener, setActiveScreener] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [stats, setStats] = useState(null);

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
              {(results.length > 0 || resultsLoading) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                >
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>📊 Rezultate ({results.length} acțiuni)</span>
                        {activeScreener && activeScreener !== 'custom' && (
                          <Badge>{screeners.find(s => s.id === activeScreener)?.name}</Badge>
                        )}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      {resultsLoading ? (
                        <div className="space-y-2">
                          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12" />)}
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
          <div>
            <CustomFilterPanel onApply={runCustomScreener} />
          </div>
        </div>
      </div>
    </>
  );
}
