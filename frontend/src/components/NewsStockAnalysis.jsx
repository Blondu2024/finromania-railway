import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Sparkles, BarChart3, AlertTriangle, Loader2, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import {
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// BVB stocks mapping for detection
const BVB_STOCKS = {
  // Banks
  'banca transilvania': 'TLV',
  'bancatransilvania': 'TLV',
  'brd groupe societe': 'BRD',
  'brd-groupe': 'BRD',
  // Energy
  'electrica sa': 'EL',
  'electrica s.a': 'EL',
  'hidroelectrica': 'H2O',
  'omv petrom': 'SNP',
  'petrom sa': 'SNP',
  'romgaz': 'SNG',
  'transgaz': 'TGN',
  'nuclearelectrica': 'SNN',
  // Telecom
  'digi communications': 'DIGI',
  'digi romania': 'DIGI',
  'rcs & rds': 'DIGI',
  // Others
  'fondul proprietatea': 'FP',
  'purcari wineries': 'WINE',
  'medlife': 'M',
  'sphera franchise': 'SFG',
  'conpet': 'COTE',
  'transelectrica': 'TEL',
  'aquila part prod': 'AQ',
  // Direct symbols (more reliable)
  ' tlv ': 'TLV',
  ' brd ': 'BRD',
  ' snp ': 'SNP',
  ' sng ': 'SNG',
  ' tgn ': 'TGN',
  ' snn ': 'SNN',
  ' digi ': 'DIGI',
  ' fp ': 'FP',
};

// Detect stocks mentioned in article
const detectMentionedStocks = (title, content, description) => {
  const fullText = `${title} ${content || ''} ${description || ''}`.toLowerCase();
  const detected = new Set();
  
  for (const [keyword, symbol] of Object.entries(BVB_STOCKS)) {
    if (fullText.includes(keyword)) {
      detected.add(symbol);
    }
  }
  
  return Array.from(detected);
};

// Mini Chart component
const MiniStockChart = ({ data }) => {
  if (!data || data.length === 0) return null;
  
  const isPositive = data[data.length - 1]?.close >= data[0]?.close;
  const color = isPositive ? '#22c55e' : '#ef4444';
  
  return (
    <div className="h-[120px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <defs>
            <linearGradient id={`gradient-${isPositive ? 'green' : 'red'}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <Area 
            type="monotone" 
            dataKey="close" 
            stroke={color} 
            fill={`url(#gradient-${isPositive ? 'green' : 'red'})`}
            strokeWidth={2}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default function NewsStockAnalysis({ article }) {
  const [detectedStocks, setDetectedStocks] = useState([]);
  const [stocksData, setStocksData] = useState({});
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [expanded, setExpanded] = useState(true);
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);

  useEffect(() => {
    if (!article) return;
    
    // Detect mentioned stocks
    const stocks = detectMentionedStocks(article.title, article.content, article.description);
    setDetectedStocks(stocks);
    
    if (stocks.length > 0) {
      fetchStocksData(stocks);
    } else {
      setLoading(false);
    }
  }, [article]);

  const fetchStocksData = async (symbols) => {
    try {
      const dataPromises = symbols.map(async (symbol) => {
        const res = await fetch(`${API_URL}/api/stocks/bvb/${symbol}/details?period=1m`);
        if (res.ok) {
          const data = await res.json();
          return { symbol, data };
        }
        return null;
      });
      
      const results = await Promise.all(dataPromises);
      const stocksMap = {};
      
      results.forEach(result => {
        if (result) {
          stocksMap[result.symbol] = result.data;
        }
      });
      
      setStocksData(stocksMap);
    } catch (error) {
      console.error('Error fetching stocks data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAiAnalysis = async () => {
    if (detectedStocks.length === 0 || aiLoading) return;
    
    setAiLoading(true);
    try {
      // Build context about the stocks
      const stocksInfo = detectedStocks.map(symbol => {
        const data = stocksData[symbol];
        if (!data) return null;
        
        const history = data.history || [];
        const lastPrice = history[history.length - 1]?.close || 0;
        const firstPrice = history[0]?.close || lastPrice;
        const change = ((lastPrice - firstPrice) / firstPrice * 100).toFixed(2);
        
        return `${symbol} (${data.name}): preț ${lastPrice.toFixed(2)} RON, variație 30 zile: ${change}%`;
      }).filter(Boolean).join('; ');

      const prompt = `Analizează această știre financiară și oferă o perspectivă scurtă (max 150 cuvinte) despre potențialul impact asupra acțiunilor menționate.

ȘTIRE: "${article.title}"
${article.description ? `DESCRIERE: "${article.description}"` : ''}

ACȚIUNI MENȚIONATE: ${stocksInfo}

Răspunde în română cu:
1. 📊 Sentiment general (Bullish/Bearish/Neutru)
2. 📈 Impact potențial pe termen scurt
3. ⚠️ Riscuri de luat în considerare
4. 💡 Concluzie pentru investitori

IMPORTANT: Aceasta este doar o analiză educațională, NU sfat de investiții.`;

      const res = await fetch(`${API_URL}/api/ai-advisor/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: prompt })
      });

      if (res.ok) {
        const data = await res.json();
        setAiAnalysis(data.response);
      }
    } catch (error) {
      console.error('Error generating AI analysis:', error);
      setAiAnalysis('Nu s-a putut genera analiza. Încearcă din nou mai târziu.');
    } finally {
      setAiLoading(false);
    }
  };

  // Don't render if no stocks detected
  if (!loading && detectedStocks.length === 0) {
    return null;
  }

  if (loading) {
    return (
      <Card className="border-2 border-blue-200">
        <CardContent className="p-6 text-center">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Se analizează știrea...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950 dark:to-blue-950">
      <CardHeader className="pb-2">
        <div 
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setExpanded(!expanded)}
        >
          <CardTitle className="text-lg flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-600" />
            🔍 Analiză Acțiuni Menționate
          </CardTitle>
          <div className="flex items-center gap-2">
            <Badge variant="secondary" className="bg-purple-100 text-purple-800">
              {detectedStocks.length} {detectedStocks.length === 1 ? 'acțiune' : 'acțiuni'} detectată
            </Badge>
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </div>
      </CardHeader>
      
      {expanded && (
        <CardContent className="space-y-4">
          {/* Detected Stocks Cards */}
          <div className="grid gap-4">
            {detectedStocks.map(symbol => {
              const data = stocksData[symbol];
              if (!data) return null;
              
              const history = data.history || [];
              const lastPrice = history[history.length - 1]?.close || 0;
              const firstPrice = history[0]?.close || lastPrice;
              const change = lastPrice - firstPrice;
              const changePercent = firstPrice > 0 ? ((change / firstPrice) * 100) : 0;
              const isPositive = changePercent >= 0;
              
              return (
                <Card key={symbol} className="overflow-hidden">
                  <div className="flex flex-col md:flex-row">
                    {/* Stock Info */}
                    <div className="flex-1 p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <Link 
                            to={`/stocks/bvb/${symbol}`}
                            className="font-bold text-lg hover:text-blue-600 transition-colors"
                          >
                            {symbol}
                          </Link>
                          <p className="text-sm text-muted-foreground">{data.name}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold">{lastPrice.toFixed(2)} RON</p>
                          <p className={`flex items-center justify-end ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                            {isPositive ? '+' : ''}{changePercent.toFixed(2)}% (30 zile)
                          </p>
                        </div>
                      </div>
                      
                      {/* Quick Stats */}
                      <div className="flex gap-4 text-xs text-muted-foreground mt-3">
                        <span>Max: <span className="text-green-600 font-medium">{Math.max(...history.map(h => h.high)).toFixed(2)}</span></span>
                        <span>Min: <span className="text-red-600 font-medium">{Math.min(...history.map(h => h.low)).toFixed(2)}</span></span>
                        <span>Vol: <span className="font-medium">{(history.reduce((a, h) => a + (h.volume || 0), 0) / 1000000).toFixed(1)}M</span></span>
                      </div>
                      
                      <Link to={`/stocks/bvb/${symbol}`}>
                        <Button size="sm" variant="outline" className="mt-3">
                          <BarChart3 className="w-3 h-3 mr-1" />
                          Vezi Grafic Complet
                        </Button>
                      </Link>
                    </div>
                    
                    {/* Mini Chart */}
                    <div className="w-full md:w-48 bg-white/50 p-2">
                      <MiniStockChart data={history} />
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* AI Analysis Section */}
          <Card className="bg-white/80">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-yellow-500" />
                🤖 Analiză AI a Știrii
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!aiAnalysis && !aiLoading && (
                <div className="text-center py-4">
                  <p className="text-sm text-muted-foreground mb-3">
                    Generează o analiză AI despre impactul potențial al acestei știri asupra acțiunilor menționate
                  </p>
                  <Button onClick={generateAiAnalysis} className="bg-purple-600 hover:bg-purple-700">
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generează Analiză AI
                  </Button>
                </div>
              )}
              
              {aiLoading && (
                <div className="text-center py-6">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-purple-600" />
                  <p className="text-sm text-muted-foreground">AI-ul analizează știrea...</p>
                </div>
              )}
              
              {aiAnalysis && (
                <div className="space-y-3">
                  <div className={`prose prose-sm max-w-none ${!showFullAnalysis && aiAnalysis.length > 500 ? 'line-clamp-6' : ''}`}>
                    {aiAnalysis.split('\n').map((line, idx) => (
                      <p key={idx} className="mb-2 text-sm">{line}</p>
                    ))}
                  </div>
                  
                  {aiAnalysis.length > 500 && (
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={() => setShowFullAnalysis(!showFullAnalysis)}
                    >
                      {showFullAnalysis ? 'Arată mai puțin' : 'Arată mai mult'}
                    </Button>
                  )}
                  
                  {/* Disclaimer */}
                  <div className="flex items-start gap-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                    <AlertTriangle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-yellow-800">
                      <strong>Disclaimer:</strong> Aceasta este o analiză generată de AI în scop educațional. 
                      NU reprezintă sfat de investiții. Deciziile de investiții sunt responsabilitatea ta. 
                      Consultă un consilier financiar autorizat înainte de a investi.
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </CardContent>
      )}
    </Card>
  );
}
