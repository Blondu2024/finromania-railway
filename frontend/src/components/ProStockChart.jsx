import React, { useState, useEffect, useMemo } from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  Area, ReferenceLine, Cell
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  BarChart3, Eye, EyeOff, Maximize2, X, Lock, Crown, Zap, Activity, TrendingUp
} from 'lucide-react';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Daily timeframes (FREE + PRO)
const TIMEFRAMES_DAILY = [
  { label: '1D', value: '1d', days: 1 },
  { label: '1S', value: '1w', days: 7 },
  { label: '1L', value: '1m', days: 30 },
  { label: '3L', value: '3m', days: 90 },
  { label: '6L', value: '6m', days: 180 },
  { label: '1A', value: '1y', days: 365 },
];

// Intraday (PRO only!)
const TIMEFRAMES_INTRADAY = [
  { label: '1min', value: '1m', interval: '1m' },
  { label: '5min', value: '5m', interval: '5m' },
  { label: '15min', value: '15m', interval: '15m' },
  { label: '30min', value: '30m', interval: '30m' },
  { label: '1H', value: '1h', interval: '1h' },
];

// Calculate RSI
const calculateRSI = (data, period = 14) => {
  if (data.length < period + 1) return [];
  const rsi = [];
  let gains = 0, losses = 0;
  
  for (let i = 1; i <= period; i++) {
    const change = data[i].close - data[i - 1].close;
    if (change > 0) gains += change;
    else losses += Math.abs(change);
  }
  
  let avgGain = gains / period;
  let avgLoss = losses / period;
  rsi.push(100 - (100 / (1 + avgGain / (avgLoss || 1))));
  
  for (let i = period + 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    avgGain = (avgGain * (period - 1) + (change > 0 ? change : 0)) / period;
    avgLoss = (avgLoss * (period - 1) + (change < 0 ? Math.abs(change) : 0)) / period;
    rsi.push(100 - (100 / (1 + avgGain / (avgLoss || 1))));
  }
  return rsi;
};

// Candlestick Component
const Candlestick = (props) => {
  const { x, y, width, height, payload } = props;
  if (!payload) return null;
  
  const { open, close, high, low } = payload;
  const isGreen = close >= open;
  const color = isGreen ? '#10b981' : '#ef4444';
  const candleWidth = Math.max(width * 0.7, 2);
  const wickX = x + width / 2;
  
  return (
    <g>
      <line x1={wickX} y1={y} x2={wickX} y2={y + height} stroke={color} strokeWidth={1.5} />
      <rect
        x={x + (width - candleWidth) / 2}
        y={isGreen ? y : y + height * 0.3}
        width={candleWidth}
        height={height * 0.7}
        fill={color}
      />
    </g>
  );
};

export default function ProStockChart({ symbol, type = 'bvb', isPro = false, token = null }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState('1m');
  const [interval, setInterval] = useState(null);
  const [chartType, setChartType] = useState('candlestick');
  const [showRSI, setShowRSI] = useState(true);
  const [showVolume, setShowVolume] = useState(true);
  
  // Map frontend periods to yfinance periods
  const mapPeriodToYFinance = (period) => {
    const mapping = {
      '1d': '1d',
      '1w': '5d',
      '1m': '1mo',
      '3m': '3mo',
      '6m': '6mo',
      '1y': '1y'
    };
    return mapping[period] || '1mo';
  };

  const fetchData = async (tf, intv = null) => {
    setLoading(true);
    try {
      let url;
      if (intv && isPro) {
        // Intraday data (PRO only) - date live cu interval
        url = type === 'bvb'
          ? `${API_URL}/api/bvb/intraday/${encodeURIComponent(symbol)}?interval=${intv}`
          : `${API_URL}/api/global/chart/${encodeURIComponent(symbol)}?period=5d&interval=${intv}`;
      } else {
        // Daily/historical data
        const mappedPeriod = mapPeriodToYFinance(tf);
        url = type === 'bvb'
          ? `${API_URL}/api/bvb/chart/${encodeURIComponent(symbol)}?period=${mappedPeriod}`
          : `${API_URL}/api/global/chart/${encodeURIComponent(symbol)}?period=${mappedPeriod}&interval=1d`;
      }
      
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(url, { headers });
      
      if (res.ok) {
        const result = await res.json();
        setData(result.data || result.history || []);
      } else {
        console.error('Failed to fetch chart data:', res.status, res.statusText);
        setData([]);
      }
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setData([]);
    }
    setLoading(false);
  };
  
  useEffect(() => {
    if (symbol) {
      fetchData(timeframe, interval);
    }
  }, [symbol, timeframe, interval]);
  
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    const rsi = calculateRSI(data);
    return data.map((item, i) => ({
      ...item,
      rsi: rsi[i - (data.length - rsi.length)] || null,
      volumeColor: item.close >= item.open ? 'rgba(16,185,129,0.6)' : 'rgba(239,68,68,0.6)'
    }));
  }, [data]);
  
  const handleClick = (tf, intv = null) => {
    if (intv && !isPro) {
      alert('Grafice INTRADAY doar pentru PRO!\n\nUpgrade: 49 RON/lună\n\nVezi /pricing');
      return;
    }
    setTimeframe(tf);
    setInterval(intv);
    fetchData(tf, intv);
  };
  
  if (loading) return <Card><CardContent className="p-8 text-center"><div className="animate-spin h-12 w-12 border-2 border-blue-500 rounded-full border-t-transparent mx-auto"></div></CardContent></Card>;
  if (!loading && processedData.length === 0) return (
    <Card>
      <CardContent className="p-8 text-center">
        <BarChart3 className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
        <p className="font-medium mb-1">Date istorice indisponibile pentru {symbol}</p>
        <p className="text-sm text-muted-foreground">
          Acest simbol nu are încă date istorice suficiente pe BVB. Verifică direct pe{' '}
          <a href={`https://bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s=${symbol}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">BVB.ro ↗</a>
        </p>
      </CardContent>
    </Card>
  );
  
  return (
    <Card>
      <CardHeader className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              {symbol}
            </CardTitle>
            {isPro && <Badge className="bg-amber-500 text-white"><Crown className="w-3 h-3 mr-1" />PRO Charts</Badge>}
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <div className="flex gap-1 p-1 bg-gray-100 dark:bg-zinc-800 rounded-lg">
            {TIMEFRAMES_DAILY.map(tf => (
              <Button
                key={tf.value}
                variant={timeframe === tf.value && !interval ? 'default' : 'ghost'}
                size="sm"
                onClick={() => handleClick(tf.value)}
                className="text-xs px-3"
              >
                {tf.label}
              </Button>
            ))}
          </div>
          
          <div className="flex gap-1 p-1 bg-amber-500/10 rounded-lg border-2 border-amber-500/30">
            {TIMEFRAMES_INTRADAY.map(tf => (
              <Button
                key={tf.value}
                variant={interval === tf.interval ? 'default' : 'ghost'}
                size="sm"
                onClick={() => handleClick(tf.value, tf.interval)}
                className="text-xs px-3"
                disabled={!isPro}
              >
                {tf.label} {!isPro && '🔒'}
              </Button>
            ))}
            {!isPro && <Link to="/pricing"><Badge className="bg-amber-500 text-white text-xs ml-1">PRO</Badge></Link>}
          </div>
        </div>
        
        <div className="flex gap-2">
          <Button variant={chartType === 'candlestick' ? 'default' : 'outline'} size="sm" onClick={() => setChartType('candlestick')}>🕯️ Candles</Button>
          <Button variant={chartType === 'line' ? 'default' : 'outline'} size="sm" onClick={() => setChartType('line')}>📈 Line</Button>
          {isPro && <Button variant={showRSI ? 'default' : 'outline'} size="sm" onClick={() => setShowRSI(!showRSI)}>RSI</Button>}
          {isPro && <Button variant={showVolume ? 'default' : 'outline'} size="sm" onClick={() => setShowVolume(!showVolume)}>Volume</Button>}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
              <Tooltip />
              {chartType === 'candlestick' ? (
                <Bar dataKey="close" shape={<Candlestick />} />
              ) : chartType === 'line' ? (
                <Line type="monotone" dataKey="close" stroke="#2563eb" strokeWidth={2} dot={false} />
              ) : (
                <Area type="monotone" dataKey="close" fill="#3b82f680" stroke="#2563eb" />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        
        {isPro && showVolume && (
          <div className="h-[100px]">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis tick={{ fontSize: 10 }} />
                <Bar dataKey="volume">
                  {processedData.map((entry, i) => <Cell key={i} fill={entry.volumeColor} />)}
                </Bar>
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {isPro && showRSI && (
          <div className="h-[120px]">
            <p className="text-sm font-semibold mb-2 flex items-center gap-2">
              <Activity className="w-4 h-4" />
              RSI (14)
            </p>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={processedData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" hide />
                <YAxis domain={[0, 100]} ticks={[30, 50, 70]} />
                <Tooltip />
                <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" />
                <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="3 3" />
                <Line type="monotone" dataKey="rsi" stroke="#9333ea" strokeWidth={2} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {!isPro && (
          <Card className="bg-amber-500/10 border-2 border-amber-500/30">
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                <Crown className="w-12 h-12 text-amber-600" />
                <div>
                  <h3 className="font-bold text-lg mb-2">Deblochează Grafice PRO</h3>
                  <ul className="text-sm space-y-1 mb-4">
                    <li>✓ Candlestick charts</li>
                    <li>✓ Intraday: 1min, 5min, 15min, 30min, 1H</li>
                    <li>✓ RSI, MACD, Bollinger Bands</li>
                    <li>✓ Volume analysis</li>
                  </ul>
                  <Link to="/pricing">
                    <Button className="bg-amber-500 hover:bg-amber-600">
                      <Crown className="w-4 h-4 mr-2" />
                      PRO: 49 RON/lună
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </CardContent>
    </Card>
  );
}
