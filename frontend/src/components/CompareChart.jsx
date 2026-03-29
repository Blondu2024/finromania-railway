import React, { useState, useEffect, useMemo } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { TrendingUp, BarChart3 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const COLORS = ['#2196F3', '#FF9800', '#4CAF50', '#E91E63'];

const TIMEFRAMES = [
  { label: '1L', value: '1mo', days: 30 },
  { label: '3L', value: '3mo', days: 90 },
  { label: '6L', value: '6mo', days: 180 },
  { label: '1A', value: '1y', days: 365 },
];

const MODES = [
  { label: 'Performanță %', value: 'percent', icon: TrendingUp },
  { label: 'Volum', value: 'volume', icon: BarChart3 },
];

const CompareTooltip = ({ active, payload, label, mode, symbols }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-white dark:bg-zinc-800 border rounded-lg shadow-lg p-3 text-sm">
      <p className="font-bold mb-2 text-muted-foreground">{label}</p>
      {payload.map((entry, idx) => {
        if (!entry.value && entry.value !== 0) return null;
        const suffix = mode === 'percent' ? '%' : mode === 'rsi' ? '' : '';
        return (
          <p key={idx} style={{ color: entry.color }} className="flex items-center gap-2">
            <span className="font-semibold">{entry.name}:</span>
            <span>
              {mode === 'percent' && entry.value >= 0 ? '+' : ''}
              {mode === 'volume'
                ? entry.value.toLocaleString('ro-RO')
                : entry.value.toFixed(2)}{suffix}
            </span>
          </p>
        );
      })}
    </div>
  );
};

export default function CompareChart({ symbols = [] }) {
  const [mode, setMode] = useState('percent');
  const [timeframe, setTimeframe] = useState('3mo');
  const [historyData, setHistoryData] = useState({});
  const [loading, setLoading] = useState(false);
  const [hiddenSymbols, setHiddenSymbols] = useState(new Set());

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

  // Process and align data
  const chartData = useMemo(() => {
    if (symbols.length < 2 || Object.keys(historyData).length < 2) return [];

    // Collect all dates
    const dateMap = {};

    symbols.forEach(symbol => {
      const data = historyData[symbol] || [];
      const sorted = [...data].sort((a, b) => new Date(a.date) - new Date(b.date));
      const baseClose = sorted[0]?.close;

      sorted.forEach(point => {
        const dateKey = point.date?.split('T')[0];
        if (!dateKey) return;
        if (!dateMap[dateKey]) dateMap[dateKey] = { date: dateKey };

        if (mode === 'percent' && baseClose) {
          dateMap[dateKey][symbol] = ((point.close - baseClose) / baseClose * 100);
        } else if (mode === 'volume') {
          dateMap[dateKey][symbol] = point.volume || 0;
        }
      });
    });

    return Object.values(dateMap).sort((a, b) => new Date(a.date) - new Date(b.date));
  }, [historyData, symbols, mode]);

  const toggleSymbol = (symbol) => {
    setHiddenSymbols(prev => {
      const next = new Set(prev);
      if (next.has(symbol)) next.delete(symbol); else next.add(symbol);
      // Don't hide all
      if (next.size >= symbols.length) return prev;
      return next;
    });
  };

  if (symbols.length < 2) return null;

  return (
    <div className="mb-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {/* Mode selector */}
        <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
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

        {/* Timeframe selector */}
        <div className="flex items-center gap-1 bg-muted rounded-lg p-1">
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

        {/* Symbol toggles */}
        <div className="flex items-center gap-1 ml-auto">
          {symbols.map((symbol, idx) => (
            <button
              key={symbol}
              onClick={() => toggleSymbol(symbol)}
              className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-all ${
                hiddenSymbols.has(symbol)
                  ? 'opacity-40 line-through'
                  : 'opacity-100'
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
          <div className="text-sm text-muted-foreground animate-pulse">Se încarcă graficele...</div>
        </div>
      ) : chartData.length > 0 ? (
        <div className="h-[280px]">
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" opacity={0.5} />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  const d = new Date(value);
                  return `${d.getDate()}/${d.getMonth() + 1}`;
                }}
              />
              <YAxis
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => {
                  if (mode === 'percent') return `${value >= 0 ? '+' : ''}${value.toFixed(0)}%`;
                  if (mode === 'volume') {
                    if (value >= 1e6) return `${(value/1e6).toFixed(1)}M`;
                    if (value >= 1e3) return `${(value/1e3).toFixed(0)}K`;
                    return value;
                  }
                  return value.toFixed(0);
                }}
                orientation="right"
              />
              <Tooltip content={<CompareTooltip mode={mode} symbols={symbols} />} />

              {/* Reference line at 0% for percent mode */}
              {mode === 'percent' && (
                <Line
                  dataKey={() => 0}
                  stroke="#999"
                  strokeDasharray="4 4"
                  strokeWidth={1}
                  dot={false}
                  legendType="none"
                  isAnimationActive={false}
                />
              )}

              {symbols.map((symbol, idx) => {
                if (hiddenSymbols.has(symbol)) return null;

                if (mode === 'volume') {
                  return (
                    <Bar
                      key={symbol}
                      dataKey={symbol}
                      fill={COLORS[idx % COLORS.length]}
                      opacity={0.7}
                      name={symbol}
                    />
                  );
                }

                return (
                  <Line
                    key={symbol}
                    type="monotone"
                    dataKey={symbol}
                    stroke={COLORS[idx % COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                    name={symbol}
                    connectNulls
                  />
                );
              })}
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-[280px] flex items-center justify-center bg-muted/30 rounded-lg">
          <p className="text-sm text-muted-foreground">Nu sunt date disponibile</p>
        </div>
      )}

      {/* Performance summary */}
      {mode === 'percent' && chartData.length > 0 && (
        <div className="flex flex-wrap gap-3 mt-2">
          {symbols.map((symbol, idx) => {
            if (hiddenSymbols.has(symbol)) return null;
            const lastPoint = chartData[chartData.length - 1];
            const value = lastPoint?.[symbol];
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
