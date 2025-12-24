import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { RefreshCw } from 'lucide-react';

export default function LiveChart({ 
  symbol, 
  marketType = 'bvb',
  height = 400,
  showVolume = true,
  positions = []  // Array of open positions to mark on chart
}) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [currentPrice, setCurrentPrice] = useState(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { color: '#ffffff' },
        textColor: '#333',
      },
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#cccccc',
      },
      timeScale: {
        borderColor: '#cccccc',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    chartRef.current = chart;

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    seriesRef.current = candlestickSeries;

    // Fetch and load data
    loadChartData();

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    // Live updates every 5 seconds
    const interval = setInterval(() => {
      updateLivePrice();
    }, 5000);

    return () => {
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
      if (chartRef.current) {
        chartRef.current.remove();
      }
    };
  }, [symbol, marketType]);

  const loadChartData = async () => {
    try {
      setLoading(true);
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      // Fetch simulated intraday candles
      const res = await fetch(
        `${API_URL}/api/live/candles/${symbol}?market_type=${marketType}&interval=5m&limit=100`
      );
      
      if (res.ok) {
        const data = await res.json();
        if (seriesRef.current && data.candles) {
          seriesRef.current.setData(data.candles);
          
          // Set current price
          if (data.candles.length > 0) {
            const lastCandle = data.candles[data.candles.length - 1];
            setCurrentPrice(lastCandle.close);
          }
        }
      }
    } catch (error) {
      console.error('Error loading chart data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateLivePrice = async () => {
    try {
      const API_URL = process.env.REACT_APP_BACKEND_URL;
      
      // Fetch live quote
      const res = await fetch(
        `${API_URL}/api/live/quote/${symbol}?market_type=${marketType}`
      );
      
      if (res.ok) {
        const quote = await res.json();
        setCurrentPrice(quote.price);
        
        // Update last candle (simulate live update)
        if (seriesRef.current) {
          const now = Math.floor(Date.now() / 1000);
          seriesRef.current.update({
            time: now,
            open: quote.price * 0.999,
            high: quote.price * 1.001,
            low: quote.price * 0.998,
            close: quote.price
          });
        }
      }
    } catch (error) {
      console.error('Error updating live price:', error);
    }
  };

  return (
    <div className="relative">
      {loading && (
        <div className=\"absolute inset-0 flex items-center justify-center bg-white/80 z-10\">\n          <RefreshCw className=\"w-6 h-6 animate-spin text-blue-600\" />\n        </div>\n      )}\n      \n      {/* Live Price Ticker */}\n      {currentPrice && (\n        <div className=\"absolute top-2 left-2 z-20 bg-black/80 text-white px-3 py-1 rounded text-sm font-mono\">\n          {currentPrice.toFixed(4)} RON\n        </div>\n      )}\n      \n      <div ref={chartContainerRef} className=\"w-full\" />\n      \n      {/* Position Markers */}\n      {positions.length > 0 && (\n        <div className=\"absolute top-2 right-2 z-20 space-y-1\">\n          {positions.map((pos, idx) => (\n            <div \n              key={idx}\n              className={`text-xs px-2 py-1 rounded ${\n                pos.position_type === 'long' ? 'bg-green-600' : 'bg-red-600'\n              } text-white`}\n            >\n              {pos.position_type.toUpperCase()} @ {pos.entry_price.toFixed(2)}\n            </div>\n          ))}\n        </div>\n      )}\n    </div>\n  );\n}
