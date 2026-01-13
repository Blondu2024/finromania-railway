import React, { useState, useEffect, useMemo } from 'react';
import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  Area, ReferenceLine, Legend, Cell
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  BarChart3, TrendingUp, Eye, EyeOff, Maximize2, X, Lock, Crown, Zap, Activity
} from 'lucide-react';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Timeframes - Separare FREE vs PRO
const TIMEFRAMES_DAILY = [
  { label: '1D', value: '1d', days: 1 },
  { label: '1S', value: '1w', days: 7 },
  { label: '1L', value: '1m', days: 30 },
  { label: '3L', value: '3m', days: 90 },
  { label: '6L', value: '6m', days: 180 },
  { label: '1A', value: '1y', days: 365 },
];

const TIMEFRAMES_INTRADAY = [
  { label: '1min', value: '1m', interval: '1m', pro: true },
  { label: '5min', value: '5m', interval: '5m', pro: true },
  { label: '15min', value: '15m', interval: '15m', pro: true },
  { label: '30min', value: '30m', interval: '30m', pro: true },
  { label: '1H', value: '1h', interval: '1h', pro: true },
];

// Candlestick Component - PROFESSIONAL
const Candlestick = (props) => {
  const { x, y, width, height, payload, index } = props;
  if (!payload || !payload.open) return null;
  
  const { open, close, high, low } = payload;
  const isGreen = close >= open;
  const color = isGreen ? '#10b981' : '#ef4444';
  
  const yScale = height / (Math.max(high, low, open, close) - Math.min(high, low, open, close) || 1);
  const bodyTop = Math.max(open, close);
  const bodyBottom = Math.min(open, close);
  
  const candleWidth = Math.max(width * 0.7, 2);
  const wickX = x + width / 2;
  
  return (
    <g>
      {/* Wick (fitil) */}
      <line
        x1={wickX}
        y1={y}
        x2={wickX}
        y2={y + height}
        stroke={color}
        strokeWidth={1.5}
      />
      {/* Body (corp lumânare) */}
      <rect
        x={x + (width - candleWidth) / 2}
        y={isGreen ? y + height - (close - bodyBottom) * yScale : y + height - (bodyTop - low) * yScale}
        width={candleWidth}
        height={Math.max(Math.abs(close - open) * yScale, 1)}
        fill={color}
        stroke={color}
        strokeWidth={1}
      />
    </g>
  );
};

// Calculate RSI
const calculateRSI = (data, period = 14) => {
  if (data.length < period + 1) return [];
  
  const rsi = [];
  let gains = 0;
  let losses = 0;
  
  // First RSI (SMA)
  for (let i = 1; i <= period; i++) {
    const change = data[i].close - data[i - 1].close;
    if (change > 0) gains += change;
    else losses += Math.abs(change);
  }
  
  let avgGain = gains / period;
  let avgLoss = losses / period;
  let rs = avgGain / (avgLoss || 1);
  rsi.push(100 - (100 / (1 + rs)));
  
  // Rest of RSI (EMA)
  for (let i = period + 1; i < data.length; i++) {
    const change = data[i].close - data[i - 1].close;
    const gain = change > 0 ? change : 0;
    const loss = change < 0 ? Math.abs(change) : 0;
    
    avgGain = (avgGain * (period - 1) + gain) / period;
    avgLoss = (avgLoss * (period - 1) + loss) / period;
    rs = avgGain / (avgLoss || 1);
    rsi.push(100 - (100 / (1 + rs)));
  }
  
  return rsi;
};

// Calculate MACD
const calculateMACD = (data, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) => {
  const closes = data.map(d => d.close);
  
  // Calculate EMAs
  const fastEMA = calculateEMA(closes, fastPeriod);
  const slowEMA = calculateEMA(closes, slowPeriod);
  
  const macdLine = fastEMA.map((fast, i) => fast - slowEMA[i]);
  const signalLine = calculateEMA(macdLine, signalPeriod);
  const histogram = macdLine.map((macd, i) => macd - signalLine[i]);
  
  return { macdLine, signalLine, histogram };
};

const calculateEMA = (data, period) => {
  const multiplier = 2 / (period + 1);
  const ema = [data[0]];
  
  for (let i = 1; i < data.length; i++) {
    ema.push((data[i] - ema[i - 1]) * multiplier + ema[i - 1]);
  }
  return ema;
};

// Calculate Bollinger Bands
const calculateBollingerBands = (data, period = 20, stdDev = 2) => {
  const sma = [];
  const upper = [];
  const lower = [];
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      sma.push(null);
      upper.push(null);
      lower.push(null);
      continue;
    }
    
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    const avg = sum / period;
    
    let variance = 0;
    for (let j = 0; j < period; j++) {
      variance += Math.pow(data[i - j].close - avg, 2);
    }
    const std = Math.sqrt(variance / period);
    
    sma.push(avg);
    upper.push(avg + stdDev * std);
    lower.push(avg - stdDev * std);
  }
  
  return { sma, upper, lower };
};

export default function ProStockChart({ 
  symbol,
  type = 'bvb', // 'bvb' or 'global'
  isPro = false,
  token = null
}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentTimeframe, setCurrentTimeframe] = useState('1m');
  const [currentInterval, setCurrentInterval] = useState(null); // For intraday
  const [chartType, setChartType] = useState('candlestick');
  const [showIndicators, setShowIndicators] = useState({
    rsi: true,
    macd: true,
    bollinger: true,
    volume: true,
    sma20: false,
    sma50: true,
    sma200: false
  });
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Fetch data (daily sau intraday)
  const fetchChartData = async (timeframe, interval = null) => {
    setLoading(true);
    try {
      let url;
      
      if (interval && isPro) {
        // Intraday data (PRO only!)
        url = `${API_URL}/api/intraday/${type}/${symbol}?interval=${interval}`;
      } else {
        // Daily data (FREE + PRO)
        const days = TIMEFRAMES_DAILY.find(t => t.value === timeframe)?.days || 30;
        url = type === 'bvb'
          ? `${API_URL}/api/stocks/bvb/${symbol}/details?period=${timeframe}&days=${days}`
          : `${API_URL}/api/stocks/global/${encodeURIComponent(symbol)}/details?period=${timeframe}`;
      }
      
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(url, { headers });
      
      if (res.ok) {
        const result = await res.json();
        setData(result.data || result.history || []);
      } else if (res.status === 403) {
        alert('⏱️ Grafice INTRADAY sunt disponibile doar pentru utilizatorii PRO!\\n\\nUpgrade la PRO pentru: 1min, 5min, 15min, 30min, 1H\\n\\nVezi /pricing');
      }
    } catch (err) {
      console.error('Chart data error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchChartData(currentTimeframe, currentInterval);
  }, [symbol, type]);
  
  // Process data cu TOȚI indicatorii
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const rsi = calculateRSI(data);
    const macd = calculateMACD(data);
    const bollinger = calculateBollingerBands(data);
    
    return data.map((item, index) => ({
      ...item,
      rsi: rsi[index - (data.length - rsi.length)] || null,
      macd: macd.macdLine[index] || null,
      macdSignal: macd.signalLine[index] || null,
      macdHistogram: macd.histogram[index] || null,
      bollingerUpper: bollinger.upper[index],
      bollingerMiddle: bollinger.sma[index],
      bollingerLower: bollinger.lower[index],
      volumeColor: item.close >= item.open ? 'rgba(16, 185, 129, 0.6)' : 'rgba(239, 68, 68, 0.6)'
    }));
  }, [data]);
  
  const handleTimeframeClick = (timeframe, interval = null) => {
    if (interval && !isPro) {
      alert([
        '⏱️ Grafice INTRADAY (1min, 5min, 15min, 30min, 1H) sunt DOAR PRO!',
        '',
        'Upgrade la PRO: 49 RON/lună',
        '',
        'Beneficii PRO:',
        '✓ Grafice intraday complete',
        '✓ Indicatori tehnici avansați',
        '✓ Update la 3 secunde',
        '✓ Calculator Fiscal',
        '',
        'Vezi /pricing'
      ].join('\n'));
      return;
    }
    
    setCurrentTimeframe(timeframe);
    setCurrentInterval(interval);
    fetchChartData(timeframe, interval);
  };
  
  if (loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Se încarcă grafic PRO...</p>
        </CardContent>
      </Card>
    );
  }
  
  if (!processedData || processedData.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">Nu există date pentru acest simbol</p>
        </CardContent>
      </Card>
    );
  }
  
  const stats = {
    high: Math.max(...processedData.map(d => d.high)),
    low: Math.min(...processedData.map(d => d.low)),
    avgVolume: Math.round(processedData.reduce((acc, d) => acc + (d.volume || 0), 0) / processedData.length),
    change: ((processedData[processedData.length - 1]?.close - processedData[0]?.close) / processedData[0]?.close * 100).toFixed(2)
  };
  
  return (
    <Card className={`${isFullscreen ? 'fixed inset-4 z-50 overflow-auto bg-white dark:bg-slate-900' : ''}`}>
      {isFullscreen && (
        <Button variant=\"ghost\" size=\"sm\" className=\"absolute top-2 right-2 z-10\" onClick={() => setIsFullscreen(false)}>
          <X className=\"w-4 h-4\" />
        </Button>
      )}
      
      <CardHeader className=\"pb-3 space-y-4\">
        {/* Header cu PRO Badge */}
        <div className=\"flex items-center justify-between\">
          <div className=\"flex items-center gap-3\">
            <CardTitle className=\"text-xl font-bold flex items-center gap-2\">
              <BarChart3 className=\"w-6 h-6 text-blue-600\" />
              {symbol}
            </CardTitle>
            {isPro && (
              <Badge className=\"bg-gradient-to-r from-amber-500 to-orange-500 text-white\">
                <Crown className=\"w-3 h-3 mr-1\" />
                PRO Charts
              </Badge>
            )}
            <Badge variant=\"outline\">{processedData.length} candles</Badge>
          </div>
          
          <div className=\"flex gap-2\">
            <Button variant=\"outline\" size=\"sm\" onClick={() => setIsFullscreen(!isFullscreen)}>
              <Maximize2 className=\"w-4 h-4\" />
            </Button>
          </div>
        </div>
        
        {/* Stats Bar */}
        <div className=\"grid grid-cols-4 gap-4 text-sm\">
          <div>
            <span className=\"text-muted-foreground\">H:</span>
            <span className=\"font-bold text-green-600 ml-1\">{stats.high.toFixed(2)}</span>
          </div>
          <div>
            <span className=\"text-muted-foreground\">L:</span>
            <span className=\"font-bold text-red-600 ml-1\">{stats.low.toFixed(2)}</span>
          </div>
          <div>
            <span className=\"text-muted-foreground\">Vol:</span>
            <span className=\"font-bold ml-1\">{(stats.avgVolume / 1000).toFixed(0)}K</span>
          </div>
          <div>
            <span className=\"text-muted-foreground\">Chg:</span>
            <span className={`font-bold ml-1 ${parseFloat(stats.change) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {stats.change}%
            </span>
          </div>
        </div>
        
        {/* Timeframe Selector */}
        <div className=\"flex flex-wrap gap-2\">
          {/* Daily (FREE + PRO) */}
          <div className=\"flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg\">
            {TIMEFRAMES_DAILY.map((tf) => (
              <Button
                key={tf.value}
                variant={currentTimeframe === tf.value && !currentInterval ? 'default' : 'ghost'}
                size=\"sm\"
                onClick={() => handleTimeframeClick(tf.value)}
                className=\"text-xs px-3 h-8\"
              >
                {tf.label}
              </Button>
            ))}
          </div>
          
          {/* Intraday (PRO only!) */}
          <div className={`flex gap-1 p-1 rounded-lg border-2 ${isPro ? 'bg-amber-500/10 border-amber-500/30' : 'bg-slate-200 dark:bg-slate-700 border-slate-300 dark:border-slate-600'}`}>
            {TIMEFRAMES_INTRADAY.map((tf) => (
              <Button
                key={tf.value}
                variant={currentInterval === tf.interval ? 'default' : 'ghost'}
                size=\"sm\"
                onClick={() => handleTimeframeClick(tf.value, tf.interval)}
                className={`text-xs px-3 h-8 ${!isPro ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={!isPro}
              >
                {tf.label}
                {!isPro && ' 🔒'}
              </Button>
            ))}
            {!isPro && (
              <Link to=\"/pricing\">
                <Badge className=\"bg-amber-500 text-white ml-1\">
                  <Crown className=\"w-3 h-3 mr-1\" />
                  PRO
                </Badge>
              </Link>
            )}
          </div>
        </div>
        
        {/* Chart Type & Indicators Toggle */}
        <div className=\"flex flex-wrap gap-3 items-center text-sm\">
          <div className=\"flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg\">
            <Button
              variant={chartType === 'candlestick' ? 'default' : 'ghost'}
              size=\"sm\"
              onClick={() => setChartType('candlestick')}
              className=\"text-xs\"
            >
              🕯️ Candlestick
            </Button>
            <Button
              variant={chartType === 'line' ? 'default' : 'ghost'}
              size=\"sm\"
              onClick={() => setChartType('line')}
              className=\"text-xs\"
            >
              📈 Line
            </Button>
            <Button
              variant={chartType === 'area' ? 'default' : 'ghost'}
              size=\"sm\"
              onClick={() => setChartType('area')}
              className=\"text-xs\"
            >
              📊 Area
            </Button>
          </div>
          
          {/* Indicators - PRO only */}
          {isPro && (
            <div className=\"flex gap-2 flex-wrap\">
              <Button
                variant={showIndicators.rsi ? 'default' : 'outline'}
                size=\"sm\"
                onClick={() => setShowIndicators(prev => ({ ...prev, rsi: !prev.rsi }))}
                className=\"text-xs\"
              >
                RSI
              </Button>
              <Button
                variant={showIndicators.macd ? 'default' : 'outline'}
                size=\"sm\"
                onClick={() => setShowIndicators(prev => ({ ...prev, macd: !prev.macd }))}
                className=\"text-xs\"
              >
                MACD
              </Button>
              <Button
                variant={showIndicators.bollinger ? 'default' : 'outline'}
                size=\"sm\"
                onClick={() => setShowIndicators(prev => ({ ...prev, bollinger: !prev.bollinger }))}
                className=\"text-xs\"
              >
                Bollinger
              </Button>
              <Button
                variant={showIndicators.volume ? 'default' : 'outline'}
                size=\"sm\"
                onClick={() => setShowIndicators(prev => ({ ...prev, volume: !prev.volume }))}
                className=\"text-xs\"
              >
                Volume
              </Button>
            </div>
          )}
          {!isPro && (
            <div className=\"text-xs text-muted-foreground flex items-center gap-1\">
              <Lock className=\"w-3 h-3\" />
              Indicatori disponibili în PRO
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className=\"space-y-4\">
        {/* Main Price Chart */}
        <div className=\"h-[400px]\">
          <ResponsiveContainer width=\"100%\" height=\"100%\">
            <ComposedChart data={processedData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#e0e0e0\" />
              <XAxis 
                dataKey=\"date\" 
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => {
                  try {
                    const date = new Date(value);
                    if (currentInterval) {
                      return date.toLocaleTimeString('ro-RO', { hour: '2-digit', minute: '2-digit' });
                    }
                    return date.toLocaleDateString('ro-RO', { month: 'short', day: 'numeric' });
                  } catch {
                    return value;
                  }
                }}
              />
              <YAxis 
                yAxisId=\"price\"
                domain={['auto', 'auto']}
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => value.toFixed(2)}
              />
              
              <Tooltip 
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px' }}
                labelFormatter={(value) => {
                  try {
                    const date = new Date(value);
                    if (currentInterval) {
                      return date.toLocaleString('ro-RO', { 
                        month: 'short', day: 'numeric', 
                        hour: '2-digit', minute: '2-digit' 
                      });
                    }
                    return date.toLocaleDateString('ro-RO', { 
                      year: 'numeric', month: 'long', day: 'numeric' 
                    });
                  } catch {
                    return value;
                  }
                }}
                formatter={(value, name) => {
                  if (name === 'volume') return [value.toLocaleString(), 'Volume'];
                  return [value?.toFixed(2), name];
                }}
              />
              
              {/* Bollinger Bands (PRO) */}
              {isPro && showIndicators.bollinger && (
                <>
                  <Line yAxisId=\"price\" type=\"monotone\" dataKey=\"bollingerUpper\" stroke=\"#9333ea\" strokeWidth={1} dot={false} strokeDasharray=\"3 3\" />
                  <Line yAxisId=\"price\" type=\"monotone\" dataKey=\"bollingerMiddle\" stroke=\"#3b82f6\" strokeWidth={1} dot={false} />
                  <Line yAxisId=\"price\" type=\"monotone\" dataKey=\"bollingerLower\" stroke=\"#9333ea\" strokeWidth={1} dot={false} strokeDasharray=\"3 3\" />
                </>
              )}
              
              {/* Price Chart - Candlestick sau Line */}
              {chartType === 'candlestick' ? (
                <Bar yAxisId=\"price\" dataKey=\"close\" shape={<Candlestick />} />
              ) : chartType === 'line' ? (
                <Line yAxisId=\"price\" type=\"monotone\" dataKey=\"close\" stroke=\"#2563eb\" strokeWidth={2} dot={false} />
              ) : (
                <Area yAxisId=\"price\" type=\"monotone\" dataKey=\"close\" fill=\"#3b82f680\" stroke=\"#2563eb\" />
              )}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        
        {/* Volume Chart (PRO) */}
        {isPro && showIndicators.volume && (
          <div className=\"h-[100px]\">
            <ResponsiveContainer width=\"100%\" height=\"100%\">
              <ComposedChart data={processedData} margin={{ top: 0, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#e0e0e0\" />
                <XAxis dataKey=\"date\" hide />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey=\"volume\">
                  {processedData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.volumeColor} />
                  ))}
                </Bar>
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {/* RSI Indicator (PRO) */}
        {isPro && showIndicators.rsi && (
          <div className=\"h-[120px]\">
            <div className=\"flex items-center gap-2 mb-2\">
              <Activity className=\"w-4 h-4 text-purple-600\" />
              <span className=\"text-sm font-semibold\">RSI (14)</span>
              <Badge variant=\"outline\" className=\"text-xs\">PRO</Badge>
            </div>
            <ResponsiveContainer width=\"100%\" height=\"100%\">
              <ComposedChart data={processedData} margin={{ top: 0, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#e0e0e0\" />
                <XAxis dataKey=\"date\" hide />
                <YAxis domain={[0, 100]} ticks={[30, 50, 70]} tick={{ fontSize: 10 }} />
                <Tooltip />
                <ReferenceLine y={70} stroke=\"#ef4444\" strokeDasharray=\"3 3\" label={{ value: 'Supracumpărat', fontSize: 10 }} />
                <ReferenceLine y={30} stroke=\"#22c55e\" strokeDasharray=\"3 3\" label={{ value: 'Supravândut', fontSize: 10 }} />
                <Line type=\"monotone\" dataKey=\"rsi\" stroke=\"#9333ea\" strokeWidth={2} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {/* MACD Indicator (PRO) */}
        {isPro && showIndicators.macd && (
          <div className=\"h-[120px]\">
            <div className=\"flex items-center gap-2 mb-2\">
              <TrendingUp className=\"w-4 h-4 text-blue-600\" />
              <span className=\"text-sm font-semibold\">MACD</span>
              <Badge variant=\"outline\" className=\"text-xs\">PRO</Badge>
            </div>
            <ResponsiveContainer width=\"100%\" height=\"100%\">
              <ComposedChart data={processedData} margin={{ top: 0, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#e0e0e0\" />
                <XAxis dataKey=\"date\" hide />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey=\"macdHistogram\">
                  {processedData.map((entry, index) => (
                    <Cell key={`macd-${index}`} fill={entry.macdHistogram >= 0 ? '#22c55e' : '#ef4444'} />
                  ))}
                </Bar>
                <Line type=\"monotone\" dataKey=\"macd\" stroke=\"#2563eb\" strokeWidth={2} dot={false} />
                <Line type=\"monotone\" dataKey=\"macdSignal\" stroke=\"#dc2626\" strokeWidth={2} dot={false} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {/* Upgrade Prompt pentru FREE */}
        {!isPro && (
          <Card className=\"bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-2 border-amber-500/30\">
            <CardContent className=\"p-6\">
              <div className=\"flex items-start gap-4\">
                <div className=\"p-3 bg-amber-500/20 rounded-xl\">
                  <Crown className=\"w-8 h-8 text-amber-600\" />
                </div>
                <div className=\"flex-1\">
                  <h3 className=\"font-bold text-lg mb-2\">Deblochează Grafice PRO</h3>
                  <ul className=\"text-sm space-y-1 text-muted-foreground mb-4\">
                    <li>✓ Candlestick charts (lumânări japoneze)</li>
                    <li>✓ Grafice intraday: 1min, 5min, 15min, 30min, 1H</li>
                    <li>✓ Indicatori tehnici: RSI, MACD, Bollinger Bands</li>
                    <li>✓ Volume analysis</li>
                    <li>✓ Update la 3 secunde (aproape real-time)</li>
                  </ul>
                  <Link to=\"/pricing\">
                    <Button className=\"bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600\">
                      <Crown className=\"w-4 h-4 mr-2\" />
                      Upgrade la PRO - 49 RON/lună
                      <Zap className=\"w-4 h-4 ml-2\" />
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
