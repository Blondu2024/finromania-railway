import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart3, TrendingUp, TrendingDown, X, Plus, Search, 
  ArrowUpDown, Target, Activity, DollarSign, Percent
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Skeleton } from './ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StockCompare({ initialSymbols = [], onClose }) {
  const [symbols, setSymbols] = useState(initialSymbols);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [allStocks, setAllStocks] = useState([]);

  // Fetch all stocks for search
  useEffect(() => {
    fetch(`${API_URL}/api/stocks/bvb`)
      .then(res => res.json())
      .then(data => setAllStocks(data))
      .catch(err => console.error('Error fetching stocks:', err));
  }, []);

  // Search stocks
  useEffect(() => {
    if (searchTerm.length >= 1) {
      const results = allStocks.filter(s => 
        s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.name?.toLowerCase().includes(searchTerm.toLowerCase())
      ).slice(0, 5);
      setSearchResults(results);
    } else {
      setSearchResults([]);
    }
  }, [searchTerm, allStocks]);

  // Fetch comparison data
  useEffect(() => {
    if (symbols.length >= 2) {
      setLoading(true);
      fetch(`${API_URL}/api/stocks/compare?symbols=${symbols.join(',')}`)
        .then(res => res.json())
        .then(data => {
          setComparisonData(data.comparison || []);
          setLoading(false);
        })
        .catch(err => {
          console.error('Error fetching comparison:', err);
          setLoading(false);
        });
    } else {
      setComparisonData([]);
    }
  }, [symbols]);

  const addSymbol = (symbol) => {
    if (symbols.length < 4 && !symbols.includes(symbol)) {
      setSymbols([...symbols, symbol]);
    }
    setSearchTerm('');
    setSearchResults([]);
  };

  const removeSymbol = (symbol) => {
    setSymbols(symbols.filter(s => s !== symbol));
  };

  const formatValue = (value, type) => {
    if (value === null || value === undefined) return '-';
    
    switch (type) {
      case 'price':
        return `${value.toFixed(2)} RON`;
      case 'percent':
        return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
      case 'ratio':
        return value.toFixed(2);
      case 'marketCap':
        if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
        if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
        return value.toLocaleString();
      default:
        return value;
    }
  };

  const getColorClass = (value, type) => {
    if (value === null || value === undefined) return 'text-muted-foreground';
    
    if (type === 'percent' || type === 'change') {
      return value >= 0 ? 'text-green-600' : 'text-red-600';
    }
    return '';
  };

  const metrics = [
    { key: 'price', label: 'Preț', type: 'price', icon: DollarSign },
    { key: 'change_percent', label: 'Variație Azi', type: 'percent', icon: TrendingUp },
    { key: 'volume', label: 'Volum', type: 'number', icon: BarChart3 },
    { key: 'pe_ratio', label: 'P/E Ratio', type: 'ratio', icon: Target },
    { key: 'dividend_yield', label: 'Dividend Yield', type: 'percent', icon: Percent },
    { key: 'roe', label: 'ROE', type: 'percent', icon: Activity },
    { key: 'rsi', label: 'RSI (14)', type: 'ratio', icon: Activity },
    { key: '52_week_high', label: '52W High', type: 'price', icon: TrendingUp },
    { key: '52_week_low', label: '52W Low', type: 'price', icon: TrendingDown },
    { key: 'pct_from_52w_high', label: 'vs 52W High', type: 'percent', icon: ArrowUpDown },
    { key: 'pct_from_52w_low', label: 'vs 52W Low', type: 'percent', icon: ArrowUpDown },
  ];

  return (
    <Card className="w-full">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Comparație Acțiuni BVB
          </CardTitle>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose} className="text-white hover:bg-white/20">
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="p-4">
        {/* Search & Add */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Caută și adaugă acțiuni (max 4)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
              disabled={symbols.length >= 4}
            />
            
            {/* Search Results Dropdown */}
            {searchResults.length > 0 && (
              <div className="absolute z-10 w-full bg-white dark:bg-slate-800 border rounded-lg mt-1 shadow-lg">
                {searchResults.map(stock => (
                  <button
                    key={stock.symbol}
                    onClick={() => addSymbol(stock.symbol)}
                    disabled={symbols.includes(stock.symbol)}
                    className="w-full flex items-center justify-between p-3 hover:bg-muted/50 transition-colors disabled:opacity-50"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-bold">{stock.symbol}</span>
                      <span className="text-sm text-muted-foreground">{stock.name}</span>
                    </div>
                    <Plus className="w-4 h-4" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Selected Symbols */}
          <div className="flex flex-wrap gap-2 mt-3">
            {symbols.map(symbol => (
              <Badge key={symbol} variant="secondary" className="flex items-center gap-1 py-1 px-3">
                {symbol}
                <button onClick={() => removeSymbol(symbol)} className="ml-1 hover:text-red-600">
                  <X className="w-3 h-3" />
                </button>
              </Badge>
            ))}
            {symbols.length < 2 && (
              <span className="text-sm text-muted-foreground">
                Adaugă minim 2 acțiuni pentru comparație
              </span>
            )}
          </div>
        </div>

        {/* Comparison Table */}
        {loading ? (
          <div className="space-y-2">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : comparisonData.length >= 2 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2 font-semibold">Metric</th>
                  {comparisonData.map(stock => (
                    <th key={stock.symbol} className="text-center p-2">
                      <Link to={`/stocks/bvb/${stock.symbol}`} className="hover:text-blue-600">
                        <div className="font-bold">{stock.symbol}</div>
                        <div className="text-xs text-muted-foreground font-normal truncate max-w-[100px]">
                          {stock.name}
                        </div>
                      </Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {metrics.map(metric => (
                  <tr key={metric.key} className="border-b hover:bg-muted/50">
                    <td className="p-2">
                      <div className="flex items-center gap-2">
                        <metric.icon className="w-4 h-4 text-muted-foreground" />
                        <span className="font-medium text-sm">{metric.label}</span>
                      </div>
                    </td>
                    {comparisonData.map(stock => {
                      const value = stock[metric.key];
                      const colorClass = getColorClass(value, metric.type);
                      
                      // Find best value for highlighting
                      const allValues = comparisonData.map(s => s[metric.key]).filter(v => v !== null && v !== undefined);
                      const isBest = metric.key === 'pe_ratio' 
                        ? value === Math.min(...allValues) 
                        : value === Math.max(...allValues);
                      
                      return (
                        <td 
                          key={`${stock.symbol}-${metric.key}`} 
                          className={`text-center p-2 ${colorClass} ${isBest && allValues.length > 1 ? 'bg-green-50 dark:bg-green-900/20 font-bold' : ''}`}
                        >
                          {formatValue(value, metric.type)}
                        </td>
                      );
                    })}
                  </tr>
                ))}
                
                {/* Sector Row */}
                <tr className="border-b bg-slate-50 dark:bg-slate-800/50">
                  <td className="p-2 font-medium text-sm">Sector</td>
                  {comparisonData.map(stock => (
                    <td key={`${stock.symbol}-sector`} className="text-center p-2">
                      <Badge variant="outline">{stock.sector || 'N/A'}</Badge>
                    </td>
                  ))}
                </tr>
                
                {/* Above SMA 50 Row */}
                <tr className="border-b">
                  <td className="p-2">
                    <div className="flex items-center gap-2">
                      <Activity className="w-4 h-4 text-muted-foreground" />
                      <span className="font-medium text-sm">Peste SMA 50</span>
                    </div>
                  </td>
                  {comparisonData.map(stock => (
                    <td key={`${stock.symbol}-sma`} className="text-center p-2">
                      {stock.above_sma_50 === true ? (
                        <Badge className="bg-green-100 text-green-700">DA</Badge>
                      ) : stock.above_sma_50 === false ? (
                        <Badge className="bg-red-100 text-red-700">NU</Badge>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        ) : null}

        {/* Legend */}
        {comparisonData.length >= 2 && (
          <div className="mt-4 text-xs text-muted-foreground flex items-center gap-4">
            <span className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-100 rounded" /> Cea mai bună valoare
            </span>
            <span className="flex items-center gap-1">
              <span className="text-green-600 font-bold">+</span> Creștere
            </span>
            <span className="flex items-center gap-1">
              <span className="text-red-600 font-bold">-</span> Scădere
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
