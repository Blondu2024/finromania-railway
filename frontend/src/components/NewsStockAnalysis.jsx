import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  TrendingUp, TrendingDown, Sparkles, BarChart3, AlertTriangle,
  Loader2, ChevronDown, ChevronUp, Globe, Zap, RefreshCw
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Category icons
const CATEGORY_ICONS = {
  indices: '📊',
  commodities: '🛢️',
  currencies: '💱',
  sectors_etf: '🏭',
  popular_stocks: '📈',
  bonds_rates: '📉',
  other: '📌'
};

// Category colors
const CATEGORY_COLORS = {
  indices: 'bg-blue-100 text-blue-800',
  commodities: 'bg-amber-100 text-amber-800',
  currencies: 'bg-green-100 text-green-800',
  sectors_etf: 'bg-blue-100 text-blue-800',
  popular_stocks: 'bg-pink-100 text-pink-800',
  bonds_rates: 'bg-gray-100 text-gray-800',
  other: 'bg-gray-100 text-zinc-800'
};

// Mini Chart component
const MiniChart = ({ data, positive }) => {
  if (!data || data.length === 0) return null;
  
  const color = positive ? '#22c55e' : '#ef4444';
  
  return (
    <div className="h-[100px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <defs>
            <linearGradient id={`mini-gradient-${positive ? 'up' : 'down'}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <Area 
            type="monotone" 
            dataKey="close" 
            stroke={color} 
            fill={`url(#mini-gradient-${positive ? 'up' : 'down'})`}
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

// Custom tooltip
const ChartTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;
  const data = payload[0]?.payload;
  if (!data) return null;
  
  return (
    <div className="bg-white border rounded shadow-lg p-2 text-xs">
      <p className="font-semibold">{data.date}</p>
      <p>Preț: <span className="font-bold">{data.close?.toFixed(2)}</span></p>
    </div>
  );
};

export default function SmartNewsAnalysis({ article }) {
  const { t } = useTranslation();
  const [recommendations, setRecommendations] = useState([]);
  const [assetsData, setAssetsData] = useState({});
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  useEffect(() => {
    if (!article) return;
    analyzeNews();
  }, [article]);

  const analyzeNews = async () => {
    setLoading(true);
    try {
      // Get AI recommendations for relevant assets
      const recRes = await fetch(`${API_URL}/api/smart-analysis/recommend-assets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: article.title,
          description: article.description,
          content: article.content
        })
      });
      
      if (recRes.ok) {
        const recData = await recRes.json();
        setRecommendations(recData.recommendations || []);
        setKeywords(recData.keywords_found || []);
        
        // Fetch data for each recommended asset
        if (recData.recommendations?.length > 0) {
          await fetchAssetsData(recData.recommendations);
        }
      }
    } catch (error) {
      console.error('Error analyzing news:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssetsData = async (assets) => {
    try {
      const dataPromises = assets.map(async (asset) => {
        try {
          const res = await fetch(`${API_URL}/api/smart-analysis/asset/${encodeURIComponent(asset.symbol)}?period=1m`);
          if (res.ok) {
            const data = await res.json();
            return { symbol: asset.symbol, data };
          }
        } catch (e) {
          console.error(`Error fetching ${asset.symbol}:`, e);
        }
        return null;
      });
      
      const results = await Promise.all(dataPromises);
      const dataMap = {};
      
      results.forEach(result => {
        if (result) {
          dataMap[result.symbol] = result.data;
        }
      });
      
      setAssetsData(dataMap);
    } catch (error) {
      console.error('Error fetching assets data:', error);
    }
  };

  const generateAiAnalysis = async () => {
    if (aiLoading) return;
    
    setAiLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/smart-analysis/generate-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: article.title,
          description: article.description,
          content: article.content
        })
      });

      if (res.ok) {
        const data = await res.json();
        setAiAnalysis(data.analysis);
      }
    } catch (error) {
      console.error('Error generating AI analysis:', error);
      setAiAnalysis(t('analysis.generateError'));
    } finally {
      setAiLoading(false);
    }
  };

  if (loading) {
    return (
      <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-50">
        <CardContent className="p-6 text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-600" />
          <p className="font-medium">{t('analysis.analyzing')}</p>
          <p className="text-sm text-muted-foreground mt-1">{t('analysis.identifyingAssets')}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-50 dark:from-blue-950 dark:to-blue-950">
      <CardHeader className="pb-2">
        <div 
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          <CardTitle className="text-lg flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            {t('analysis.smartAnalysis')}
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-blue-100 text-blue-800">
              <Globe className="w-3 h-3 mr-1" />
              {recommendations.length} {t('analysis.relevantAssets')}
            </Badge>
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>
        
        {/* Keywords found */}
        {keywords.length > 0 && expanded && (
          <div className="flex flex-wrap gap-1 mt-2">
            <span className="text-xs text-muted-foreground">{t('analysis.keywords')}:</span>
            {keywords.map((kw, idx) => (
              <Badge key={idx} variant="outline" className="text-xs">
                {kw}
              </Badge>
            ))}
          </div>
        )}
      </CardHeader>
      
      {expanded && (
        <CardContent className="space-y-4">
          {/* Recommended Assets Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((rec) => {
              const data = assetsData[rec.symbol];
              const isPositive = data?.change_percent >= 0;
              
              return (
                <Card key={rec.symbol} className="overflow-hidden bg-white">
                  <CardContent className="p-4">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xl">{CATEGORY_ICONS[rec.category] || '📌'}</span>
                          <div>
                            <p className="font-bold">{data?.name || rec.name}</p>
                            <p className="text-xs text-muted-foreground">{rec.symbol}</p>
                          </div>
                        </div>
                      </div>
                      <Badge className={`text-xs ${CATEGORY_COLORS[rec.category] || CATEGORY_COLORS.other}`}>
                        {rec.category}
                      </Badge>
                    </div>
                    
                    {/* Price & Change */}
                    {data && (
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl font-bold">
                          {data.current_price?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          <span className="text-sm font-normal text-muted-foreground ml-1">{data.currency}</span>
                        </span>
                        <span className={`flex items-center font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                          {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                          {isPositive ? '+' : ''}{data.change_percent?.toFixed(2)}%
                        </span>
                      </div>
                    )}
                    
                    {/* Mini Chart */}
                    {data?.history && (
                      <MiniChart data={data.history} positive={isPositive} />
                    )}
                    
                    {/* Matched keyword */}
                    <div className="flex items-center justify-between mt-2 pt-2 border-t">
                      <span className="text-xs text-muted-foreground">
                        <Zap className="w-3 h-3 inline mr-1" />
                        {t('analysis.detected')}: "{rec.matched_keyword}"
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {data?.data_points} zile
                      </span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {/* AI Analysis Section */}
          <Card className="bg-white/80">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-yellow-500" />
                  {t('analysis.detailedAnalysis')}
                </CardTitle>
                {aiAnalysis && (
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={generateAiAnalysis}
                    disabled={aiLoading}
                  >
                    <RefreshCw className={`w-3 h-3 mr-1 ${aiLoading ? 'animate-spin' : ''}`} />
                    {t('analysis.regenerate')}
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {!aiAnalysis && !aiLoading && (
                <div className="text-center py-6">
                  <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                    <Sparkles className="w-8 h-8 text-blue-600" />
                  </div>
                  <p className="font-medium mb-2">{t('analysis.getDetailed')}</p>
                  <p className="text-sm text-muted-foreground mb-4 max-w-md mx-auto">
                    {t('analysis.aiWillAnalyze')}
                  </p>
                  <Button onClick={generateAiAnalysis} className="bg-blue-600 hover:bg-blue-700">
                    <Sparkles className="w-4 h-4 mr-2" />
                    {t('analysis.generateAnalysis')}
                  </Button>
                </div>
              )}
              
              {aiLoading && (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-600" />
                  <p className="font-medium">{t('analysis.aiAnalyzing')}</p>
                  <p className="text-sm text-muted-foreground">{t('analysis.processDuration')}</p>
                </div>
              )}
              
              {aiAnalysis && (
                <div className="space-y-3">
                  <div className={`prose prose-sm max-w-none ${!showFullAnalysis && aiAnalysis.length > 600 ? 'line-clamp-8' : ''}`}>
                    {aiAnalysis.split('\n').map((line, idx) => (
                      <p key={idx} className="mb-2 text-sm leading-relaxed">{line}</p>
                    ))}
                  </div>
                  
                  {aiAnalysis.length > 600 && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                    >
                      {showFullAnalysis ? t('common.showLess') : t('common.showMore')}
                    </Button>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
          
          {/* Disclaimer */}
          <div className="flex items-start gap-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
            <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-yellow-800">
              <strong>{t('analysis.disclaimer')}:</strong> {t('analysis.disclaimerText')}
            </p>
          </div>
        </CardContent>
      )}
    </Card>
  );
}
