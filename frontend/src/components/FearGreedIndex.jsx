import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { TrendingUp, TrendingDown, Minus, RefreshCw, Info, AlertTriangle } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './ui/tooltip';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Gauge component for the fear & greed meter
const FearGreedGauge = ({ score, label, color, fearLabel, greedLabel }) => {
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
        <text x="15" y="95" className="text-[8px] fill-gray-500">{fearLabel}</text>
        <text x="165" y="95" className="text-[8px] fill-gray-500">{greedLabel}</text>
      </svg>
      
      {/* Needle */}
      <div 
        className="absolute bottom-0 left-1/2 w-1 h-20 -ml-0.5 origin-bottom transition-transform duration-1000 ease-out"
        style={{ transform: `rotate(${rotation}deg)` }}
      >
        <div className="w-2 h-2 bg-foreground rounded-full -ml-0.5 shadow-lg" />
        <div className="w-1 h-16 bg-foreground/70 mx-auto rounded-full shadow-lg" />
      </div>
      
      {/* Center circle */}
      <div className="absolute bottom-0 left-1/2 w-6 h-6 -ml-3 -mb-3 bg-muted rounded-full border-2 border-border" />
    </div>
  );
};

const FearGreedIndex = ({ compact = false }) => {
  const { t } = useTranslation();
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
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse">
            <div className="h-6 bg-muted rounded w-1/2 mx-auto mb-4" />
            <div className="h-32 bg-muted rounded-full w-32 mx-auto mb-4" />
            <div className="h-4 bg-muted rounded w-3/4 mx-auto" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
          <p className="text-muted-foreground">{t('fearGreed.error')}</p>
          <button
            onClick={fetchData}
            className="mt-2 text-blue-500 hover:text-blue-400 text-sm"
          >
            {t('common.tryAgain')}
          </button>
        </CardContent>
      </Card>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center gap-3 bg-muted/50 rounded-lg px-4 py-2">
        <div
          className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
          style={{ backgroundColor: data?.color || '#64748b' }}
        >
          {data?.score || 0}
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Fear & Greed</p>
          <p className="font-semibold">{data?.label || 'Loading...'}</p>
        </div>
        {data?.trend && getTrendIcon(data.trend)}
      </div>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold">Fear & Greed Index</h3>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Info className="w-4 h-4 text-muted-foreground hover:text-foreground" />
                </TooltipTrigger>
                <TooltipContent className="max-w-xs">
                  <p>Indicatorul Fear & Greed măsoară sentimentul general al pieței BVB bazat pe RSI, momentum, volatilitate și volum.</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
          <button
            onClick={fetchData}
            className="p-1.5 hover:bg-muted rounded-full transition-colors"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 text-muted-foreground ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Main Score Display */}
        <div className="text-center mb-4">
          <FearGreedGauge
            score={data?.score || 50}
            label={data?.label || 'Neutru'}
            color={data?.color || '#ca8a04'}
            fearLabel={t('fearGreed.fear')}
            greedLabel={t('fearGreed.greed')}
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
            <p className="text-sm text-muted-foreground mt-2 max-w-xs mx-auto">
              {data?.description || ''}
            </p>
          </div>
        </div>

        {/* Components Breakdown */}
        {data?.components && (
          <div className="mt-6">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="w-full text-sm text-muted-foreground hover:text-foreground flex items-center justify-center gap-1 mb-3"
            >
              {showDetails ? t('fearGreed.hideDetails') : t('fearGreed.showComponents')}
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
                  <div key={key} className="flex items-center justify-between bg-muted/50 rounded-lg px-3 py-2">
                    <div className="flex items-center gap-2">
                      <span className="text-foreground capitalize text-sm">
                        {key === 'rsi' ? 'RSI' :
                         key === 'momentum' ? 'Momentum' :
                         key === 'volatility' ? t('fearGreed.volatility') : t('fearGreed.volume')}
                      </span>
                      <span className="text-xs text-muted-foreground">({component.weight})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
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
                      <span className="text-sm font-medium text-foreground w-8 text-right">
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
        <p className="text-xs text-muted-foreground text-center mt-4">
          {t('converter.updated')}: {data?.last_updated ? new Date(data.last_updated).toLocaleString('ro-RO') : 'N/A'}
        </p>
      </CardContent>
    </Card>
  );
};

export default FearGreedIndex;
