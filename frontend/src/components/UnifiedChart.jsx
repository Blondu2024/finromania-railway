import React, { useEffect, useRef, useState, useCallback } from 'react';
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { BarChart3, Crown, Lock } from 'lucide-react';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TIMEFRAMES_DAILY = [
  { label: '1S', value: '1w', period: '5d' },
  { label: '1L', value: '1m', period: '1mo' },
  { label: '3L', value: '3m', period: '3mo' },
  { label: '6L', value: '6m', period: '6mo' },
  { label: '1A', value: '1y', period: '1y' },
];

const TIMEFRAMES_INTRADAY = [
  { label: '1min', interval: '1m' },
  { label: '5min', interval: '5m' },
  { label: '15min', interval: '15m' },
  { label: '30min', interval: '30m' },
  { label: '1H', interval: '1h' },
];

const SMA_CONFIGS = [
  { period: 20, color: '#2196F3', label: 'SMA 20' },
  { period: 50, color: '#FF9800', label: 'SMA 50' },
];

function calculateSMA(data, period) {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) continue;
    let sum = 0;
    for (let j = 0; j < period; j++) sum += data[i - j].close;
    result.push({ time: data[i].time, value: sum / period });
  }
  return result;
}

function calculateRSI(data, period = 14) {
  const result = [];
  if (data.length < period + 1) return result;
  let gains = 0, losses = 0;
  for (let i = 1; i <= period; i++) {
    const d = data[i].close - data[i - 1].close;
    if (d > 0) gains += d; else losses -= d;
  }
  let avgGain = gains / period;
  let avgLoss = losses / period;
  result.push({ time: data[period].time, value: 100 - 100 / (1 + avgGain / (avgLoss || 0.001)) });
  for (let i = period + 1; i < data.length; i++) {
    const d = data[i].close - data[i - 1].close;
    avgGain = (avgGain * (period - 1) + (d > 0 ? d : 0)) / period;
    avgLoss = (avgLoss * (period - 1) + (d < 0 ? -d : 0)) / period;
    result.push({ time: data[i].time, value: 100 - 100 / (1 + avgGain / (avgLoss || 0.001)) });
  }
  return result;
}

function parseDate(dateStr) {
  if (!dateStr) return 0;
  const d = dateStr.split('T')[0];
  return d;
}

export default function UnifiedChart({ symbol, type = 'bvb', isPro = false, token = null }) {
  const chartContainerRef = useRef(null);
  const rsiContainerRef = useRef(null);
  const chartRef = useRef(null);
  const rsiChartRef = useRef(null);
  const seriesRef = useRef({});

  const [timeframe, setTimeframe] = useState('1m');
  const [intradayInterval, setIntradayInterval] = useState(null);
  const [chartType, setChartType] = useState('candlestick');
  const [showVolume, setShowVolume] = useState(true);
  const [showSMA, setShowSMA] = useState([20]);
  const [showRSI, setShowRSI] = useState(false);
  const [loading, setLoading] = useState(true);
  const [noData, setNoData] = useState(false);
  const [rawData, setRawData] = useState([]);

  const isDark = typeof window !== 'undefined' &&
    document.documentElement.classList.contains('dark');

  const colors = {
    bg: isDark ? '#18181b' : '#ffffff',
    text: isDark ? '#a1a1aa' : '#71717a',
    grid: isDark ? '#27272a' : '#f4f4f5',
    border: isDark ? '#3f3f46' : '#e4e4e7',
    up: '#10b981',
    down: '#ef4444',
    line: '#3b82f6',
    volume: isDark ? 'rgba(59,130,246,0.3)' : 'rgba(59,130,246,0.2)',
  };

  const fetchData = useCallback(async (tf, intv) => {
    setLoading(true);
    setNoData(false);
    try {
      let url;
      if (intv && isPro) {
        url = type === 'bvb'
          ? `${API_URL}/api/bvb/intraday/${encodeURIComponent(symbol)}?interval=${intv}`
          : `${API_URL}/api/global/chart/${encodeURIComponent(symbol)}?period=5d&interval=${intv}`;
      } else {
        const tfObj = TIMEFRAMES_DAILY.find(t => t.value === tf);
        const period = tfObj?.period || '1mo';
        url = type === 'bvb'
          ? `${API_URL}/api/bvb/chart/${encodeURIComponent(symbol)}?period=${period}`
          : `${API_URL}/api/global/chart/${encodeURIComponent(symbol)}?period=${period}&interval=1d`;
      }
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const res = await fetch(url, { headers });
      if (res.ok) {
        const result = await res.json();
        const d = result.data || result.history || [];
        if (d.length === 0) { setNoData(true); setRawData([]); }
        else setRawData(d);
      } else {
        setNoData(true); setRawData([]);
      }
    } catch {
      setNoData(true); setRawData([]);
    }
    setLoading(false);
  }, [symbol, type, isPro, token]);

  useEffect(() => {
    if (symbol) fetchData(timeframe, intradayInterval);
  }, [symbol, fetchData, timeframe, intradayInterval]);

  // Create/update main chart
  useEffect(() => {
    if (!chartContainerRef.current || rawData.length === 0) return;

    // Clear previous
    if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }
    seriesRef.current = {};

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 420,
      layout: {
        background: { type: ColorType.Solid, color: colors.bg },
        textColor: colors.text,
        fontFamily: "'Inter', system-ui, sans-serif",
      },
      grid: {
        vertLines: { color: colors.grid },
        horzLines: { color: colors.grid },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: {
        borderColor: colors.border,
        scaleMargins: { top: 0.05, bottom: showVolume ? 0.25 : 0.05 },
      },
      timeScale: {
        borderColor: colors.border,
        timeVisible: !!intradayInterval,
        secondsVisible: false,
      },
      handleScroll: true,
      handleScale: true,
    });
    chartRef.current = chart;

    // Process data
    const sorted = [...rawData].sort((a, b) => new Date(a.date) - new Date(b.date));
    const ohlc = sorted.map(d => ({
      time: parseDate(d.date),
      open: d.open || d.close,
      high: d.high || d.close,
      low: d.low || d.close,
      close: d.close,
    }));
    const volumes = sorted.map(d => ({
      time: parseDate(d.date),
      value: d.volume || 0,
      color: (d.close >= (d.open || d.close)) ? 'rgba(16,185,129,0.4)' : 'rgba(239,68,68,0.4)',
    }));

    // Main series
    if (chartType === 'candlestick') {
      const cs = chart.addCandlestickSeries({
        upColor: colors.up,
        downColor: colors.down,
        borderDownColor: colors.down,
        borderUpColor: colors.up,
        wickDownColor: colors.down,
        wickUpColor: colors.up,
      });
      cs.setData(ohlc);
      seriesRef.current.main = cs;
    } else {
      const ls = chart.addAreaSeries({
        lineColor: colors.line,
        topColor: isDark ? 'rgba(59,130,246,0.3)' : 'rgba(59,130,246,0.15)',
        bottomColor: isDark ? 'rgba(59,130,246,0.02)' : 'rgba(59,130,246,0.01)',
        lineWidth: 2,
      });
      ls.setData(ohlc.map(d => ({ time: d.time, value: d.close })));
      seriesRef.current.main = ls;
    }

    // Volume
    if (showVolume) {
      const vs = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: 'volume',
      });
      chart.priceScale('volume').applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 },
      });
      vs.setData(volumes);
      seriesRef.current.volume = vs;
    }

    // SMA overlays
    const smaData = ohlc.map(d => ({ ...d, close: d.close }));
    showSMA.forEach((period, idx) => {
      const cfg = SMA_CONFIGS.find(c => c.period === period);
      if (!cfg) return;
      const smaValues = calculateSMA(smaData, period);
      if (smaValues.length > 0) {
        const sma = chart.addLineSeries({
          color: cfg.color,
          lineWidth: 1,
          lineStyle: 2,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        sma.setData(smaValues);
        seriesRef.current[`sma${period}`] = sma;
      }
    });

    chart.timeScale().fitContent();

    // Resize handler
    const handleResize = () => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth });
      }
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(container);

    return () => { observer.disconnect(); chart.remove(); chartRef.current = null; };
  }, [rawData, chartType, showVolume, showSMA, isDark, intradayInterval]);

  // RSI chart
  useEffect(() => {
    if (!rsiContainerRef.current || !showRSI || rawData.length === 0) {
      if (rsiChartRef.current) { rsiChartRef.current.remove(); rsiChartRef.current = null; }
      return;
    }
    if (rsiChartRef.current) { rsiChartRef.current.remove(); rsiChartRef.current = null; }

    const container = rsiContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 120,
      layout: {
        background: { type: ColorType.Solid, color: colors.bg },
        textColor: colors.text,
        fontFamily: "'Inter', system-ui, sans-serif",
      },
      grid: {
        vertLines: { color: colors.grid },
        horzLines: { color: colors.grid },
      },
      rightPriceScale: { borderColor: colors.border },
      timeScale: { borderColor: colors.border, visible: false },
      handleScroll: false,
      handleScale: false,
    });
    rsiChartRef.current = chart;

    const sorted = [...rawData].sort((a, b) => new Date(a.date) - new Date(b.date));
    const dataForRSI = sorted.map(d => ({ time: parseDate(d.date), close: d.close }));
    const rsiValues = calculateRSI(dataForRSI);

    const rsiSeries = chart.addLineSeries({
      color: '#8b5cf6',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
    });
    rsiSeries.setData(rsiValues);

    // Overbought/oversold lines
    const ob = chart.addLineSeries({ color: '#ef444480', lineWidth: 1, lineStyle: 2, priceLineVisible: false, lastValueVisible: false });
    const os = chart.addLineSeries({ color: '#22c55e80', lineWidth: 1, lineStyle: 2, priceLineVisible: false, lastValueVisible: false });
    const mid = chart.addLineSeries({ color: '#a1a1aa40', lineWidth: 1, lineStyle: 2, priceLineVisible: false, lastValueVisible: false });
    if (rsiValues.length >= 2) {
      const times = [rsiValues[0].time, rsiValues[rsiValues.length - 1].time];
      ob.setData(times.map(t => ({ time: t, value: 70 })));
      os.setData(times.map(t => ({ time: t, value: 30 })));
      mid.setData(times.map(t => ({ time: t, value: 50 })));
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (rsiChartRef.current && container) rsiChartRef.current.applyOptions({ width: container.clientWidth });
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(container);

    return () => { observer.disconnect(); chart.remove(); rsiChartRef.current = null; };
  }, [rawData, showRSI, isDark]);

  const toggleSMA = (period) => {
    setShowSMA(prev => prev.includes(period) ? prev.filter(p => p !== period) : [...prev, period]);
  };

  const handleIntraday = (intv) => {
    if (!isPro) return;
    setIntradayInterval(intv);
    setTimeframe('1m');
  };

  if (noData && !loading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
          <p className="font-medium mb-1">Date istorice indisponibile pentru {symbol}</p>
          <p className="text-sm text-muted-foreground">
            Verifică direct pe{' '}
            <a href={`https://bvb.ro/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s=${symbol}`} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">BVB.ro</a>
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <BarChart3 className="w-5 h-5" />
            {symbol}
          </CardTitle>
          {isPro && <Badge className="bg-amber-500 text-white"><Crown className="w-3 h-3 mr-1" />PRO</Badge>}
        </div>

        {/* Timeframes */}
        <div className="flex flex-wrap items-center gap-2 pt-2">
          <div className="flex gap-0.5 p-1 bg-muted rounded-lg">
            {TIMEFRAMES_DAILY.map(tf => (
              <Button
                key={tf.value}
                variant={timeframe === tf.value && !intradayInterval ? 'default' : 'ghost'}
                size="sm"
                className="h-7 px-2.5 text-xs"
                onClick={() => { setIntradayInterval(null); setTimeframe(tf.value); }}
              >
                {tf.label}
              </Button>
            ))}
          </div>
          {isPro && (
            <div className="flex gap-0.5 p-1 bg-amber-500/10 rounded-lg border border-amber-500/30">
              {TIMEFRAMES_INTRADAY.map(tf => (
                <Button
                  key={tf.interval}
                  variant={intradayInterval === tf.interval ? 'default' : 'ghost'}
                  size="sm"
                  className="h-7 px-2.5 text-xs"
                  onClick={() => handleIntraday(tf.interval)}
                >
                  {tf.label}
                </Button>
              ))}
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1">
          <Button
            variant={chartType === 'candlestick' ? 'default' : 'outline'}
            size="sm" className="h-7 text-xs"
            onClick={() => setChartType('candlestick')}
          >Candles</Button>
          <Button
            variant={chartType === 'line' ? 'default' : 'outline'}
            size="sm" className="h-7 text-xs"
            onClick={() => setChartType('line')}
          >Line</Button>

          <div className="w-px h-5 bg-border mx-1" />

          <Button
            variant={showVolume ? 'default' : 'outline'}
            size="sm" className="h-7 text-xs"
            onClick={() => setShowVolume(!showVolume)}
          >Vol</Button>

          {SMA_CONFIGS.map(cfg => (
            <Button
              key={cfg.period}
              variant={showSMA.includes(cfg.period) ? 'default' : 'outline'}
              size="sm" className="h-7 text-xs"
              onClick={() => toggleSMA(cfg.period)}
              style={showSMA.includes(cfg.period) ? { backgroundColor: cfg.color, borderColor: cfg.color } : {}}
            >
              {cfg.label}
            </Button>
          ))}

          {isPro && (
            <Button
              variant={showRSI ? 'default' : 'outline'}
              size="sm" className="h-7 text-xs"
              onClick={() => setShowRSI(!showRSI)}
              style={showRSI ? { backgroundColor: '#8b5cf6', borderColor: '#8b5cf6' } : {}}
            >RSI</Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0 space-y-1">
        {loading ? (
          <div className="h-[420px] flex items-center justify-center">
            <div className="animate-spin h-10 w-10 border-2 border-blue-500 rounded-full border-t-transparent" />
          </div>
        ) : (
          <>
            <div ref={chartContainerRef} className="w-full" />
            {showRSI && isPro && (
              <div>
                <p className="text-xs font-medium text-muted-foreground mb-1 pl-1">RSI (14)</p>
                <div ref={rsiContainerRef} className="w-full" />
              </div>
            )}
          </>
        )}

        {/* PRO upsell */}
        {!isPro && (
          <div className="flex items-center gap-3 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
            <Crown className="w-8 h-8 text-amber-600 shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-sm">Grafice PRO: Intraday + RSI + Volume</p>
              <p className="text-xs text-muted-foreground">Candlestick profesionale, intervale 1-30min, indicatori tehnici</p>
            </div>
            <Link to="/pricing">
              <Button size="sm" className="bg-amber-500 hover:bg-amber-600 text-xs">
                <Crown className="w-3 h-3 mr-1" />PRO
              </Button>
            </Link>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
