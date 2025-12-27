import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Settings, 
  TrendingUp, 
  BarChart3, 
  Layers, 
  Eye, 
  EyeOff,
  Maximize2,
  ChevronDown 
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
  { label: 'Candlestick', value: 'candlestick', icon: '📊' },
  { label: 'Linie', value: 'line', icon: '📈' },
  { label: 'Area', value: 'area', icon: '📉' },
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
  const result = [];
  for (let i = period - 1; i < data.length; i++) {
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    result.push({
      time: data[i].time,
      value: sum / period
    });
  }
  return result;
};

// Calculate EMA
const calculateEMA = (data, period) => {
  const result = [];
  const multiplier = 2 / (period + 1);
  
  // First EMA is SMA
  let sum = 0;
  for (let i = 0; i < period; i++) {
    sum += data[i].close;
  }
  let ema = sum / period;
  result.push({ time: data[period - 1].time, value: ema });
  
  // Calculate rest of EMAs
  for (let i = period; i < data.length; i++) {
    ema = (data[i].close - ema) * multiplier + ema;
    result.push({ time: data[i].time, value: ema });
  }
  return result;
};

export default function AdvancedStockChart({ 
  symbol, 
  data = [], 
  currency = 'RON',
  onTimeframeChange,
  currentTimeframe = '1m'
}) {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const mainSeriesRef = useRef();
  const volumeSeriesRef = useRef();
  const indicatorSeriesRef = useRef({});
  
  const [chartType, setChartType] = useState('candlestick');
  const [showVolume, setShowVolume] = useState(true);
  const [activeIndicators, setActiveIndicators] = useState(['sma20']);
  const [showSettings, setShowSettings] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Format data for the chart
  const formatChartData = (rawData) => {
    return rawData.map(item => ({
      time: item.date,
      open: item.open,
      high: item.high,
      low: item.low,
      close: item.close,
      value: item.close, // For line/area charts
    })).sort((a, b) => new Date(a.time) - new Date(b.time));
  };

  const formatVolumeData = (rawData) => {
    return rawData.map(item => ({
      time: item.date,
      value: item.volume || 0,
      color: item.close >= item.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
    })).sort((a, b) => new Date(a.time) - new Date(b.time));
  };

  useEffect(() => {
    if (!chartContainerRef.current || !data.length) return;

    // Clear previous chart
    if (chartRef.current) {
      chartRef.current.remove();
    }

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#e1e3e6' },
        horzLines: { color: '#e1e3e6' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#e1e3e6',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: '#e1e3e6',
        timeVisible: true,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: isFullscreen ? 600 : 400,
    });

    chartRef.current = chart;
    const formattedData = formatChartData(data);

    // Create main series based on chart type
    let mainSeries;
    switch (chartType) {
      case 'line':
        mainSeries = chart.addLineSeries({
          color: '#2196F3',
          lineWidth: 2,
        });
        mainSeries.setData(formattedData.map(d => ({ time: d.time, value: d.close })));
        break;
      case 'area':
        mainSeries = chart.addAreaSeries({
          topColor: 'rgba(33, 150, 243, 0.4)',
          bottomColor: 'rgba(33, 150, 243, 0.0)',
          lineColor: '#2196F3',
          lineWidth: 2,
        });
        mainSeries.setData(formattedData.map(d => ({ time: d.time, value: d.close })));
        break;
      case 'bar':
        mainSeries = chart.addBarSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
        });
        mainSeries.setData(formattedData);
        break;
      default: // candlestick
        mainSeries = chart.addCandlestickSeries({
          upColor: '#26a69a',
          downColor: '#ef5350',
          borderUpColor: '#26a69a',
          borderDownColor: '#ef5350',
          wickUpColor: '#26a69a',
          wickDownColor: '#ef5350',
        });
        mainSeries.setData(formattedData);
    }
    mainSeriesRef.current = mainSeries;

    // Add volume
    if (showVolume) {
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
      volumeSeries.setData(formatVolumeData(data));
      volumeSeriesRef.current = volumeSeries;
    }

    // Add indicators
    indicatorSeriesRef.current = {};
    activeIndicators.forEach(indicatorId => {
      const indicator = INDICATORS.find(i => i.value === indicatorId);
      if (!indicator) return;

      let indicatorData;
      if (indicatorId.startsWith('sma')) {
        indicatorData = calculateSMA(formattedData, indicator.period);
      } else if (indicatorId.startsWith('ema')) {
        indicatorData = calculateEMA(formattedData, indicator.period);
      }

      if (indicatorData && indicatorData.length > 0) {
        const lineSeries = chart.addLineSeries({
          color: indicator.color,
          lineWidth: 1,
          title: indicator.label,
        });
        lineSeries.setData(indicatorData);
        indicatorSeriesRef.current[indicatorId] = lineSeries;
      }
    });

    // Fit content
    chart.timeScale().fitContent();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ 
          width: chartContainerRef.current.clientWidth,
          height: isFullscreen ? 600 : 400,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data, chartType, showVolume, activeIndicators, isFullscreen]);

  const toggleIndicator = (indicatorId) => {
    setActiveIndicators(prev => 
      prev.includes(indicatorId) 
        ? prev.filter(i => i !== indicatorId)
        : [...prev, indicatorId]
    );
  };

  const stats = data.length > 0 ? {
    high: Math.max(...data.map(d => d.high)),
    low: Math.min(...data.map(d => d.low)),
    avgVolume: Math.round(data.reduce((acc, d) => acc + (d.volume || 0), 0) / data.length),
    change: ((data[data.length - 1]?.close - data[0]?.close) / data[0]?.close * 100).toFixed(2)
  } : {};

  return (
    <Card className={`${isFullscreen ? 'fixed inset-4 z-50 overflow-auto' : ''}`}>
      <CardHeader className="pb-2">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-center gap-2">
            <CardTitle className="text-lg">Grafic {symbol}</CardTitle>
            <Badge variant="outline" className="text-xs">
              {TIMEFRAMES.find(t => t.value === currentTimeframe)?.label || '1L'}
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
                {type.icon}
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
              <div className="absolute top-full left-0 mt-1 bg-white border rounded-lg shadow-lg p-2 z-10 min-w-[160px]">
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
        {/* Chart Container */}
        <div 
          ref={chartContainerRef} 
          className={`w-full ${isFullscreen ? 'h-[600px]' : 'h-[400px]'}`}
        />
        
        {/* Stats Bar */}
        {data.length > 0 && (
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
        )}
        
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
