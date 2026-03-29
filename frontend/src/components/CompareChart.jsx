import React, { useEffect, useRef, useState, useMemo } from 'react';
import { createChart, ColorType } from 'lightweight-charts';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { TrendingUp, BarChart3 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const COLORS = ['#3b82f6', '#f59e0b', '#10b981', '#ec4899'];

const TIMEFRAMES = [
  { label: '1L', value: '1mo' },
  { label: '3L', value: '3mo' },
  { label: '6L', value: '6mo' },
  { label: '1A', value: '1y' },
];

const MODES = [
  { label: 'Performanță %', value: 'percent', icon: TrendingUp },
  { label: 'Volum', value: 'volume', icon: BarChart3 },
];

export default function CompareChart({ symbols = [] }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const [mode, setMode] = useState('percent');
  const [timeframe, setTimeframe] = useState('3mo');
  const [historyData, setHistoryData] = useState({});
  const [loading, setLoading] = useState(false);
  const [hiddenSymbols, setHiddenSymbols] = useState(new Set());

  const isDark = typeof window !== 'undefined' &&
    document.documentElement.classList.contains('dark');

  // Fetch history for all symbols
  useEffect(() => {
    if (symbols.length < 2) return;
    setLoading(true);
    Promise.all(
      symbols.map(symbol =>
        fetch(`${API_URL}/api/bvb/chart/${symbol}?period=${timeframe}`)
          .then(res => res.json())
          .then(resp => ({ symbol, data: resp.data || [] }))
          .catch(() => ({ symbol, data: [] }))
      )
    ).then(results => {
      const newData = {};
      results.forEach(r => { newData[r.symbol] = r.data; });
      setHistoryData(newData);
      setLoading(false);
    });
  }, [symbols, timeframe]);

  // Process data
  const processedData = useMemo(() => {
    if (symbols.length < 2 || Object.keys(historyData).length < 2) return {};

    const result = {};
    symbols.forEach(symbol => {
      const data = historyData[symbol] || [];
      const sorted = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
      const baseClose = sorted[0]?.close;

      result[symbol] = sorted.map(point => {
        const dateKey = point.date?.split('T')[0];
        if (mode === 'percent' && baseClose) {
          return { time: dateKey, value: ((point.close - baseClose) / baseClose * 100) };
        } else if (mode === 'volume') {
          return { time: dateKey, value: point.volume || 0 };
        }
        return { time: dateKey, value: point.close };
      }).filter(d => d.time);
    });
    return result;
  }, [historyData, symbols, mode]);

  // Create chart
  useEffect(() => {
    if (!chartContainerRef.current || Object.keys(processedData).length < 2) return;

    if (chartRef.current) { chartRef.current.remove(); chartRef.current = null; }

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 280,
      layout: {
        background: { type: ColorType.Solid, color: isDark ? '#18181b' : '#ffffff' },
        textColor: isDark ? '#a1a1aa' : '#71717a',
        fontFamily: "'Inter', system-ui, sans-serif",
      },
      grid: {
        vertLines: { color: isDark ? '#27272a' : '#f4f4f5' },
        horzLines: { color: isDark ? '#27272a' : '#f4f4f5' },
      },
      rightPriceScale: {
        borderColor: isDark ? '#3f3f46' : '#e4e4e7',
      },
      timeScale: {
        borderColor: isDark ? '#3f3f46' : '#e4e4e7',
      },
      crosshair: { mode: 0 },
    });
    chartRef.current = chart;

    // Add series for each symbol
    symbols.forEach((symbol, idx) => {
      if (hiddenSymbols.has(symbol)) return;
      const data = processedData[symbol];
      if (!data || data.length === 0) return;

      if (mode === 'volume') {
        const series = chart.addHistogramSeries({
          color: COLORS[idx % COLORS.length],
          priceFormat: { type: 'volume' },
        });
        series.setData(data);
      } else {
        const series = chart.addLineSeries({
          color: COLORS[idx % COLORS.length],
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: true,
        });
        series.setData(data);
      }
    });

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth });
      }
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(container);

    return () => { observer.disconnect(); chart.remove(); chartRef.current = null; };
  }, [processedData, hiddenSymbols, isDark, mode]);

  const toggleSymbol = (symbol) => {
    setHiddenSymbols(prev => {
      const next = new Set(prev);
      if (next.has(symbol)) next.delete(symbol); else next.add(symbol);
      if (next.size >= symbols.length) return prev;
      return next;
    });
  };

  if (symbols.length < 2) return null;

  // Get last values for performance badges
  const lastValues = {};
  if (mode === 'percent') {
    symbols.forEach(symbol => {
      const data = processedData[symbol];
      if (data && data.length > 0) {
        lastValues[symbol] = data[data.length - 1].value;
      }
    });
  }

  return (
    <div className="mb-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <div className="flex gap-0.5 p-1 bg-muted rounded-lg">
          {MODES.map(m => (
            <Button
              key={m.value}
              variant={mode === m.value ? 'default' : 'ghost'}
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={() => setMode(m.value)}
            >
              <m.icon className="w-3 h-3 mr-1" />
              {m.label}
            </Button>
          ))}
        </div>

        <div className="flex gap-0.5 p-1 bg-muted rounded-lg">
          {TIMEFRAMES.map(tf => (
            <Button
              key={tf.value}
              variant={timeframe === tf.value ? 'default' : 'ghost'}
              size="sm"
              className="h-7 px-2 text-xs"
              onClick={() => setTimeframe(tf.value)}
            >
              {tf.label}
            </Button>
          ))}
        </div>

        <div className="flex items-center gap-1 ml-auto">
          {symbols.map((symbol, idx) => (
            <button
              key={symbol}
              onClick={() => toggleSymbol(symbol)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-all ${
                hiddenSymbols.has(symbol) ? 'opacity-40 line-through' : 'opacity-100'
              }`}
              style={{
                borderWidth: 2,
                borderStyle: 'solid',
                borderColor: COLORS[idx % COLORS.length],
                color: hiddenSymbols.has(symbol) ? '#999' : COLORS[idx % COLORS.length]
              }}
            >
              <div
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: hiddenSymbols.has(symbol) ? '#ccc' : COLORS[idx % COLORS.length] }}
              />
              {symbol}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      {loading ? (
        <div className="h-[280px] flex items-center justify-center bg-muted/30 rounded-lg">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 rounded-full border-t-transparent" />
        </div>
      ) : Object.keys(processedData).length >= 2 ? (
        <div ref={chartContainerRef} className="w-full rounded-lg overflow-hidden" />
      ) : (
        <div className="h-[280px] flex items-center justify-center bg-muted/30 rounded-lg">
          <p className="text-sm text-muted-foreground">Nu sunt date disponibile</p>
        </div>
      )}

      {/* Performance badges */}
      {mode === 'percent' && Object.keys(lastValues).length > 0 && (
        <div className="flex flex-wrap gap-2 mt-2">
          {symbols.map((symbol, idx) => {
            if (hiddenSymbols.has(symbol)) return null;
            const value = lastValues[symbol];
            if (value === undefined) return null;
            return (
              <Badge
                key={symbol}
                variant="outline"
                className="text-xs"
                style={{
                  borderColor: COLORS[idx % COLORS.length],
                  color: value >= 0 ? '#16a34a' : '#dc2626'
                }}
              >
                {symbol}: {value >= 0 ? '+' : ''}{value.toFixed(2)}%
              </Badge>
            );
          })}
        </div>
      )}
    </div>
  );
}
