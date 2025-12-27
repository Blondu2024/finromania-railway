import React, { useState, useMemo } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ReferenceLine,
  Legend
} from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  Layers, 
  Eye, 
  EyeOff,
  Maximize2,
  ChevronDown,
  X
} from 'lucide-react';

// Timeframe options
const TIMEFRAMES = [
  { label: '1Z', value: '1d', days: 1 },
  { label: '1S', value: '1w', days: 7 },
  { label: '1L', value: '1m', days: 30 },
  { label: '3L', value: '3m', days: 90 },
  { label: '6L', value: '6m', days: 180 },
  { label: '1A', value: '1y', days: 365 },
  { label: '5A', value: '5y', days: 1825 },
];

// Chart type options
const CHART_TYPES = [
  { label: 'Linie', value: 'line', icon: '📈' },
  { label: 'Area', value: 'area', icon: '📊' },
  { label: 'Bare', value: 'bar', icon: '📶' },
];

// Indicator options
const INDICATORS = [
  { label: 'SMA 20', value: 'sma20', color: '#2196F3', period: 20 },
  { label: 'SMA 50', value: 'sma50', color: '#FF9800', period: 50 },
  { label: 'SMA 200', value: 'sma200', color: '#9C27B0', period: 200 },
  { label: 'EMA 12', value: 'ema12', color: '#4CAF50', period: 12 },
  { label: 'EMA 26', value: 'ema26', color: '#F44336', period: 26 },
];

// Calculate SMA
const calculateSMA = (data, period) => {
  return data.map((item, index) => {
    if (index < period - 1) return null;
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += data[index - i].close;
    }
    return sum / period;
  });
};

// Calculate EMA
const calculateEMA = (data, period) => {
  const multiplier = 2 / (period + 1);
  const result = [];
  
  // First EMA is SMA
  let sum = 0;
  for (let i = 0; i < period && i < data.length; i++) {
    sum += data[i].close;
  }
  let ema = sum / Math.min(period, data.length);
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else if (i === period - 1) {
      result.push(ema);
    } else {
      ema = (data[i].close - ema) * multiplier + ema;
      result.push(ema);
    }
  }
  return result;
};

// Custom Candlestick component
const CandlestickBar = (props) => {
  const { x, y, width, height, payload } = props;
  if (!payload) return null;
  
  const { open, close, high, low } = payload;
  const isGreen = close >= open;
  const color = isGreen ? '#26a69a' : '#ef5350';
  
  const bodyTop = Math.max(open, close);
  const bodyBottom = Math.min(open, close);
  const yScale = height / (high - low || 1);
  
  const candleWidth = Math.max(width * 0.6, 4);
  const wickX = x + width / 2;
  
  return (
    <g>
      {/* Wick */}
      <line
        x1={wickX}
        y1={y + (high - Math.max(open, close)) * yScale}
        x2={wickX}
        y2={y + (high - Math.min(open, close)) * yScale}
        stroke={color}
        strokeWidth={1}
      />
      {/* Body */}
      <rect
        x={x + (width - candleWidth) / 2}
        y={y + (high - bodyTop) * yScale}
        width={candleWidth}
        height={Math.max((bodyTop - bodyBottom) * yScale, 1)}
        fill={isGreen ? color : color}
        stroke={color}
      />
    </g>
  );
};

// Custom tooltip
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;
  
  const data = payload[0]?.payload;
  if (!data) return null;
  
  return (
    <div className="bg-white border rounded-lg shadow-lg p-3 text-sm">
      <p className="font-bold mb-2">{data.date}</p>
      <div className="space-y-1">
        <p>Deschidere: <span className="font-semibold">{data.open?.toFixed(2)}</span></p>
        <p>Maxim: <span className="font-semibold text-green-600">{data.high?.toFixed(2)}</span></p>
        <p>Minim: <span className="font-semibold text-red-600">{data.low?.toFixed(2)}</span></p>
        <p>Închidere: <span className="font-semibold">{data.close?.toFixed(2)}</span></p>
        {data.volume && (
          <p>Volum: <span className="font-semibold">{data.volume.toLocaleString('ro-RO')}</span></p>
        )}
        {payload.map((entry, idx) => {
          if (entry.name && !['close', 'volume', 'high', 'low', 'open'].includes(entry.name)) {
            return (
              <p key={idx} style={{ color: entry.color }}>
                {entry.name}: <span className="font-semibold">{entry.value?.toFixed(2)}</span>
              </p>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
};

export default function AdvancedStockChart({ 
  symbol, 
  data = [], 
  currency = 'RON',
  onTimeframeChange,
  currentTimeframe = '1m'
}) {
  const [chartType, setChartType] = useState('area');
  const [showVolume, setShowVolume] = useState(true);
  const [activeIndicators, setActiveIndicators] = useState(['sma20']);
  const [showSettings, setShowSettings] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Process data with indicators
  const processedData = useMemo(() => {
    if (!data || data.length === 0) return [];
    
    const sortedData = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    // Calculate indicators
    const sma20 = calculateSMA(sortedData, 20);
    const sma50 = calculateSMA(sortedData, 50);
    const sma200 = calculateSMA(sortedData, 200);
    const ema12 = calculateEMA(sortedData, 12);
    const ema26 = calculateEMA(sortedData, 26);
    
    return sortedData.map((item, index) => ({
      ...item,
      sma20: sma20[index],
      sma50: sma50[index],
      sma200: sma200[index],
      ema12: ema12[index],
      ema26: ema26[index],
      volumeColor: item.close >= item.open ? 'rgba(38, 166, 154, 0.6)' : 'rgba(239, 83, 80, 0.6)'
    }));
  }, [data]);

  const toggleIndicator = (indicatorId) => {
    setActiveIndicators(prev => 
      prev.includes(indicatorId) 
        ? prev.filter(i => i !== indicatorId)
        : [...prev, indicatorId]
    );
  };

  // Calculate min/max for Y axis
  const { minPrice, maxPrice, minVolume, maxVolume } = useMemo(() => {
    if (processedData.length === 0) return { minPrice: 0, maxPrice: 100, minVolume: 0, maxVolume: 1000 };
    
    const prices = processedData.flatMap(d => [d.high, d.low].filter(Boolean));
    const volumes = processedData.map(d => d.volume || 0);
    
    return {
      minPrice: Math.min(...prices) * 0.98,
      maxPrice: Math.max(...prices) * 1.02,
      minVolume: 0,
      maxVolume: Math.max(...volumes) * 1.2
    };
  }, [processedData]);

  const stats = processedData.length > 0 ? {
    high: Math.max(...processedData.map(d => d.high)),
    low: Math.min(...processedData.map(d => d.low)),
    avgVolume: Math.round(processedData.reduce((acc, d) => acc + (d.volume || 0), 0) / processedData.length),
    change: ((processedData[processedData.length - 1]?.close - processedData[0]?.close) / processedData[0]?.close * 100).toFixed(2)
  } : {};

  if (processedData.length === 0) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <p className="text-muted-foreground">Nu există date pentru grafic</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${isFullscreen ? 'fixed inset-4 z-50 overflow-auto bg-white' : ''}`}>
      {isFullscreen && (
        <Button 
          variant="ghost" 
          size="sm" 
          className="absolute top-2 right-2 z-10"
          onClick={() => setIsFullscreen(false)}
        >
          <X className="w-4 h-4" />
        </Button>
      )}
      
      <CardHeader className="pb-2">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">📈 Grafic {symbol}</CardTitle>
            <Badge variant="outline" className="text-xs">
              {TIMEFRAMES.find(t => t.value === currentTimeframe)?.label || '1L'}
            </Badge>
            <Badge className="text-xs bg-green-100 text-green-800">
              {processedData.length} puncte date
            </Badge>
          </div>
          
          {/* Timeframe Buttons */}
          <div className="flex flex-wrap items-center gap-1">
            {TIMEFRAMES.map((tf) => (
              <Button
                key={tf.value}
                variant={currentTimeframe === tf.value ? 'default' : 'ghost'}
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={() => onTimeframeChange?.(tf.value, tf.days)}
              >
                {tf.label}
              </Button>
            ))}
          </div>
        </div>
        
        {/* Chart Controls */}
        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t">
          {/* Chart Type */}
          <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
            {CHART_TYPES.map((type) => (
              <Button
                key={type.value}
                variant={chartType === type.value ? 'default' : 'ghost'}
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={() => setChartType(type.value)}
                title={type.label}
              >
                {type.icon} {type.label}
              </Button>
            ))}
          </div>

          {/* Volume Toggle */}
          <Button
            variant={showVolume ? 'default' : 'outline'}
            size="sm"
            className="h-7 text-xs"
            onClick={() => setShowVolume(!showVolume)}
          >
            <BarChart3 className="w-3 h-3 mr-1" />
            Volum
          </Button>

          {/* Indicators Dropdown */}
          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs"
              onClick={() => setShowSettings(!showSettings)}
            >
              <Layers className="w-3 h-3 mr-1" />
              Indicatori ({activeIndicators.length})
              <ChevronDown className="w-3 h-3 ml-1" />
            </Button>
            
            {showSettings && (
              <div className="absolute top-full left-0 mt-1 bg-white border rounded-lg shadow-lg p-2 z-20 min-w-[160px]">
                {INDICATORS.map((indicator) => (
                  <button
                    key={indicator.value}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded hover:bg-muted ${
                      activeIndicators.includes(indicator.value) ? 'bg-muted' : ''
                    }`}
                    onClick={() => toggleIndicator(indicator.value)}
                  >
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: indicator.color }}
                    />
                    <span className="flex-1 text-left">{indicator.label}</span>
                    {activeIndicators.includes(indicator.value) ? (
                      <Eye className="w-4 h-4 text-green-600" />
                    ) : (
                      <EyeOff className="w-4 h-4 text-muted-foreground" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Fullscreen Toggle */}
          <Button
            variant="outline"
            size="sm"
            className="h-7 text-xs ml-auto"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            <Maximize2 className="w-3 h-3 mr-1" />
            {isFullscreen ? 'Închide' : 'Ecran Complet'}
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        {/* Main Chart */}
        <div className={`w-full ${isFullscreen ? 'h-[500px]' : 'h-[350px]'}`}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={processedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
              <XAxis 
                dataKey="date" 
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getDate()}/${date.getMonth() + 1}`;
                }}
              />
              <YAxis 
                yAxisId="price"
                domain={[minPrice, maxPrice]} 
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => value.toFixed(0)}
                orientation="right"
              />
              {showVolume && (
                <YAxis 
                  yAxisId="volume"
                  domain={[0, maxVolume * 4]}
                  orientation="left"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(value) => value >= 1000000 ? `${(value/1000000).toFixed(1)}M` : value >= 1000 ? `${(value/1000).toFixed(0)}K` : value}
                />
              )}
              <Tooltip content={<CustomTooltip />} />
              
              {/* Volume Bars */}
              {showVolume && (
                <Bar 
                  yAxisId="volume"
                  dataKey="volume" 
                  fill="#93c5fd"
                  opacity={0.4}
                />
              )}
              
              {/* Main Price Chart */}
              {chartType === 'line' && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="close" 
                  stroke="#2196F3" 
                  strokeWidth={2}
                  dot={false}
                  name="Preț"
                />
              )}
              
              {chartType === 'area' && (
                <Area 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="close" 
                  stroke="#2196F3" 
                  fill="url(#colorPrice)"
                  strokeWidth={2}
                  name="Preț"
                />
              )}
              
              {chartType === 'bar' && (
                <Bar 
                  yAxisId="price"
                  dataKey="close" 
                  fill="#2196F3"
                  name="Preț"
                />
              )}
              
              {/* Indicators */}
              {activeIndicators.includes('sma20') && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="sma20" 
                  stroke="#2196F3" 
                  strokeWidth={1}
                  dot={false}
                  name="SMA 20"
                  strokeDasharray="5 5"
                />
              )}
              {activeIndicators.includes('sma50') && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="sma50" 
                  stroke="#FF9800" 
                  strokeWidth={1}
                  dot={false}
                  name="SMA 50"
                  strokeDasharray="5 5"
                />
              )}
              {activeIndicators.includes('sma200') && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="sma200" 
                  stroke="#9C27B0" 
                  strokeWidth={1}
                  dot={false}
                  name="SMA 200"
                  strokeDasharray="5 5"
                />
              )}
              {activeIndicators.includes('ema12') && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="ema12" 
                  stroke="#4CAF50" 
                  strokeWidth={1}
                  dot={false}
                  name="EMA 12"
                />
              )}
              {activeIndicators.includes('ema26') && (
                <Line 
                  yAxisId="price"
                  type="monotone" 
                  dataKey="ema26" 
                  stroke="#F44336" 
                  strokeWidth={1}
                  dot={false}
                  name="EMA 26"
                />
              )}
              
              {/* Gradient Definition */}
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2196F3" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#2196F3" stopOpacity={0}/>
                </linearGradient>
              </defs>
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        
        {/* Stats Bar */}
        <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t text-sm">
          <div>
            <span className="text-muted-foreground">Maxim: </span>
            <span className="font-semibold text-green-600">{stats.high?.toFixed(2)} {currency}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Minim: </span>
            <span className="font-semibold text-red-600">{stats.low?.toFixed(2)} {currency}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Vol. Mediu: </span>
            <span className="font-semibold">{stats.avgVolume?.toLocaleString('ro-RO')}</span>
          </div>
          <div>
            <span className="text-muted-foreground">Variație: </span>
            <span className={`font-semibold ${parseFloat(stats.change) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {parseFloat(stats.change) >= 0 ? '+' : ''}{stats.change}%
            </span>
          </div>
        </div>
        
        {/* Indicator Legend */}
        {activeIndicators.length > 0 && (
          <div className="flex flex-wrap gap-3 mt-3 pt-3 border-t">
            {activeIndicators.map(indicatorId => {
              const indicator = INDICATORS.find(i => i.value === indicatorId);
              return indicator ? (
                <div key={indicatorId} className="flex items-center gap-1 text-xs">
                  <div 
                    className="w-4 h-0.5 rounded" 
                    style={{ backgroundColor: indicator.color }}
                  />
                  <span>{indicator.label}</span>
                </div>
              ) : null;
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
