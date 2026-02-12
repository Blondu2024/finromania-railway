import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TickerBar() {
  const [indices, setIndices] = useState([]);
  const [bvbStocks, setBvbStocks] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // CACHE BUSTING - timestamp forțează request nou
        const timestamp = Date.now();
        const fetchOptions = {
          cache: 'no-store',
          headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
        };
        
        const [globalRes, bvbRes] = await Promise.all([
          fetch(`${API_URL}/api/stocks/global?_t=${timestamp}`, fetchOptions),
          fetch(`${API_URL}/api/stocks/bvb?_t=${timestamp}`, fetchOptions)
        ]);
        const [global, bvb] = await Promise.all([globalRes.json(), bvbRes.json()]);
        setIndices(global);
        setBvbStocks(bvb.slice(0, 5)); // Top 5 BVB
        console.log('[TickerBar] Updated at', new Date().toLocaleTimeString());
      } catch (error) {
        console.error('Error fetching ticker data:', error);
      }
    };

    fetchData();
    // Update la 30 secunde - datele EODHD au 15min delay oricum
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const allItems = [
    ...indices.map(i => ({ ...i, type: 'global' })),
    ...bvbStocks.map(s => ({ ...s, type: 'bvb', name: s.symbol }))
  ];

  // Duplicate for seamless loop
  const tickerItems = [...allItems, ...allItems];

  return (
    <div className="bg-slate-900 dark:bg-slate-950 text-white overflow-hidden border-b">
      <div className="ticker-container">
        <div className="ticker-track">
          {tickerItems.map((item, idx) => {
            const isPositive = item.change_percent >= 0;
            const linkPath = item.type === 'global' 
              ? `/stocks/global/${encodeURIComponent(item.symbol)}`
              : `/stocks/bvb/${item.symbol}`;
            
            return (
              <Link
                key={`${item.symbol}-${idx}`}
                to={linkPath}
                className="ticker-item inline-flex items-center px-4 py-2 hover:bg-slate-800 transition-colors"
              >
                <span className="font-semibold mr-2 text-white">{item.name}</span>
                <span className="font-mono mr-2">
                  {typeof item.price === 'number' 
                    ? item.price.toLocaleString('ro-RO', { maximumFractionDigits: 2 })
                    : item.price}
                </span>
                <span className={`flex items-center text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                  {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                  {isPositive ? '+' : ''}{item.change_percent?.toFixed(2)}%
                </span>
                <span className="mx-4 text-slate-600">|</span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
