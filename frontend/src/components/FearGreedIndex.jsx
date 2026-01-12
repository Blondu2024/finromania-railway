import React, { useState, useEffect, useCallback } from 'react';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Info, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Gauge component for the fear & greed meter
const FearGreedGauge = ({ score, label, color }) => {
  const rotation = (score / 100) * 180 - 90; // -90 to 90 degrees
  
  return (
    <div className="relative w-64 h-32 mx-auto">
      {/* Background arc */}
      <svg viewBox="0 0 200 100" className="w-full h-full">
        {/* Gradient background */}
        <defs>
          <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#dc2626" />
            <stop offset="25%" stopColor="#ea580c" />
            <stop offset="50%" stopColor="#ca8a04" />
            <stop offset="75%" stopColor="#65a30d" />
            <stop offset="100%" stopColor="#16a34a" />
          </linearGradient>
        </defs>
        
        {/* Background arc */}
        <path
          d="M 20 90 A 80 80 0 0 1 180 90"
          fill="none"
          stroke="url(#gaugeGradient)"
          strokeWidth="12"
          strokeLinecap="round"
        />
        
        {/* Tick marks */}
        {[0, 25, 50, 75, 100].map((tick) => {
          const angle = ((tick / 100) * 180 - 180) * (Math.PI / 180);
          const x1 = 100 + 70 * Math.cos(angle);
          const y1 = 90 + 70 * Math.sin(angle);
          const x2 = 100 + 80 * Math.cos(angle);
          const y2 = 90 + 80 * Math.sin(angle);
          return (
            <line
              key={tick}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke="#374151"
              strokeWidth="2"
            />
          );
        })}
        
        {/* Labels */}
        <text x="15" y="95" className="text-[8px] fill-gray-500">Frică</text>
        <text x="165" y="95" className="text-[8px] fill-gray-500">Lăcomie</text>
      </svg>
      
      {/* Needle */}
      <div 
        className="absolute bottom-0 left-1/2 w-1 h-20 -ml-0.5 origin-bottom transition-transform duration-1000 ease-out"
        style={{ transform: `rotate(${rotation}deg)` }}
      >
        <div className="w-2 h-2 bg-white rounded-full -ml-0.5 shadow-lg" />
        <div className="w-1 h-16 bg-gradient-to-t from-gray-800 to-gray-600 mx-auto rounded-full shadow-lg" />
      </div>
      
      {/* Center circle */}
      <div className="absolute bottom-0 left-1/2 w-6 h-6 -ml-3 -mb-3 bg-gray-800 rounded-full border-2 border-gray-600" />
    </div>
  );
};

const FearGreedIndex = ({ compact = false }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/market/fear-greed`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch Fear & Greed data');
      }
      
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      console.error('Error fetching Fear & Greed:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />;
      default:
        return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  if (loading && !data) {
    return (
      <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
        <CardContent className="p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-slate-700 rounded w-1/2 mx-auto mb-4" />
            <div className="h-32 bg-slate-700 rounded-full w-32 mx-auto mb-4" />
            <div className="h-4 bg-slate-700 rounded w-3/4 mx-auto" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
        <CardContent className="p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
          <p className="text-gray-400">Nu am putut încărca indicele</p>
          <button 
            onClick={fetchData}
            className="mt-2 text-blue-400 hover:text-blue-300 text-sm"
          >
            Încearcă din nou
          </button>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-slate-800/50 rounded-lg px-4 py-2">
        <div 
          className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
          style={{ backgroundColor: data?.color || '#64748b' }}
        >
          {data?.score || 0}
        </div>
        <div>
          <p className="text-sm text-gray-400">Fear & Greed</p>
          <p className="font-semibold text-white">{data?.label || 'Loading...'}</p>
        </div>
        {data?.trend && getTrendIcon(data.trend)}
      </div>
    );
  }

  return (
    <Card className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-slate-700 overflow-hidden">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white">Fear & Greed Index</h3>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="w-4 h-4 text-gray-400 hover:text-gray-300" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>Indicatorul Fear & Greed măsoară sentimentul general al pieței BVB bazat pe RSI, momentum, volatilitate și volum.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <button 
            onClick={fetchData}
            className="p-1.5 hover:bg-slate-700 rounded-full transition-colors"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Main Score Display */}
        <div className="text-center mb-4">
          <FearGreedGauge 
            score={data?.score || 50} 
            label={data?.label || 'Neutru'} 
            color={data?.color || '#ca8a04'} 
          />
          
          <div className="mt-4">
            <div className="flex items-center justify-center gap-2">
              <span 
                className="text-5xl font-bold"
                style={{ color: data?.color || '#64748b' }}
              >
                {data?.score || 0}
              </span>
              {data?.trend && getTrendIcon(data.trend)}
            </div>
            <p 
              className="text-xl font-semibold mt-1"
              style={{ color: data?.color || '#64748b' }}
            >
              {data?.label || 'Loading...'}
            </p>
            <p className="text-sm text-gray-400 mt-2 max-w-xs mx-auto">
              {data?.description || ''}
            </p>
          </div>
        </div>

        {/* Components Breakdown */}
        {data?.components && (
          <div className="mt-6">
            <button 
              onClick={() => setShowDetails(!showDetails)}
              className="w-full text-sm text-gray-400 hover:text-gray-300 flex items-center justify-center gap-1 mb-3"
            >
              {showDetails ? 'Ascunde detalii' : 'Vezi componentele'}
              <svg 
                className={`w-4 h-4 transition-transform ${showDetails ? 'rotate-180' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {showDetails && (
              <div className="space-y-3 animate-in fade-in duration-200">
                {Object.entries(data.components).map(([key, component]) => (
                  <div key={key} className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-300 capitalize text-sm">
                        {key === 'rsi' ? 'RSI' : 
                         key === 'momentum' ? 'Momentum' :
                         key === 'volatility' ? 'Volatilitate' : 'Volum'}
                      </span>
                      <span className="text-xs text-gray-500">({component.weight})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full transition-all duration-500"
                          style={{ 
                            width: `${component.score}%`,
                            backgroundColor: component.score < 30 ? '#dc2626' : 
                                           component.score < 50 ? '#ea580c' :
                                           component.score < 70 ? '#ca8a04' : '#16a34a'
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-300 w-8 text-right">
                        {component.score}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Last Updated */}
        <p className="text-xs text-gray-500 text-center mt-4">
          Actualizat: {data?.last_updated ? new Date(data.last_updated).toLocaleString('ro-RO') : 'N/A'}
        </p>
      </CardContent>
    </Card>
  );
};

export default FearGreedIndex;
