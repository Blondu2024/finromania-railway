import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  TrendingUp, TrendingDown, Activity, AlertTriangle, 
  Flame, RefreshCw, ArrowUp, ArrowDown 
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Skeleton } from './ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// 52 Week Extremes Component
export function Week52Extremes() {
  const [data, setData] = useState({ near_52w_high: [], near_52w_low: [] });
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('high');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/stocks/52-week-extremes`);
        if (res.ok) {
          const result = await res.json();
          setData(result);
        }
      } catch (err) {
        console.error('Error fetching 52 week extremes:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full mb-2" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
        <CardTitle className="flex items-center gap-2">
          <Target className="w-5 h-5" />
          52 Week High/Low
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="w-full rounded-none">
            <TabsTrigger value="high" className="flex-1">
              <ArrowUp className="w-4 h-4 mr-1 text-green-600" />
              Aproape de Maxim ({data.near_52w_high?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="low" className="flex-1">
              <ArrowDown className="w-4 h-4 mr-1 text-red-600" />
              Aproape de Minim ({data.near_52w_low?.length || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="high" className="p-4 m-0">
            {data.near_52w_high?.length > 0 ? (
              <div className="space-y-2">
                {data.near_52w_high.map((stock, idx) => (
                  <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-green-50 hover:bg-green-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {idx + 1}
                        </div>
                        <div>
                          <p className="font-bold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">{stock.price?.toFixed(2)} RON</p>
                        <p className="text-xs text-green-600 font-semibold">
                          {stock.pct_from_high >= 0 ? '+' : ''}{stock.pct_from_high}% de la maxim
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Max: {stock['52_week_high']?.toFixed(2)} RON
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">
                Nicio acțiune aproape de maximul pe 52 săptămâni
              </p>
            )}
          </TabsContent>

          <TabsContent value="low" className="p-4 m-0">
            {data.near_52w_low?.length > 0 ? (
              <div className="space-y-2">
                {data.near_52w_low.map((stock, idx) => (
                  <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                    <div className="flex items-center justify-between p-3 rounded-lg bg-red-50 hover:bg-red-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                          {idx + 1}
                        </div>
                        <div>
                          <p className="font-bold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">{stock.price?.toFixed(2)} RON</p>
                        <p className="text-xs text-red-600 font-semibold">
                          +{stock.pct_from_low}% de la minim
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Min: {stock['52_week_low']?.toFixed(2)} RON
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-8">
                Nicio acțiune aproape de minimul pe 52 săptămâni
              </p>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

// Import Target since it's used above
import { Target } from 'lucide-react';

// Unusual Volume Component
export function UnusualVolume() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(`${API_URL}/api/stocks/unusual-volume`);
        if (res.ok) {
          const result = await res.json();
          setData(result.unusual_volume || []);
        }
      } catch (err) {
        console.error('Error fetching unusual volume:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-48" />
        </CardHeader>
        <CardContent>
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full mb-2" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-orange-500 to-red-500 text-white">
        <CardTitle className="flex items-center gap-2">
          <Flame className="w-5 h-5" />
          Volum Neobișnuit
          <Badge className="bg-white/20 ml-2">{data.length} acțiuni</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {data.length > 0 ? (
          <div className="space-y-2">
            {data.slice(0, 10).map((stock, idx) => (
              <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                <div className={`flex items-center justify-between p-3 rounded-lg transition-colors ${
                  stock.volume_ratio >= 5 ? 'bg-red-100 hover:bg-red-200' :
                  stock.volume_ratio >= 3 ? 'bg-orange-100 hover:bg-orange-200' :
                  'bg-yellow-100 hover:bg-yellow-200'
                }`}>
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold ${
                      stock.volume_ratio >= 5 ? 'bg-red-600' :
                      stock.volume_ratio >= 3 ? 'bg-orange-600' :
                      'bg-yellow-600'
                    }`}>
                      {stock.volume_ratio}x
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-bold">{stock.symbol}</p>
                        <Badge variant="outline" className="text-xs">
                          {stock.alert_level}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{stock.name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-sm">{stock.volume?.toLocaleString('ro-RO')}</p>
                    <p className="text-xs text-muted-foreground">
                      vs medie: {stock.avg_volume?.toLocaleString('ro-RO')}
                    </p>
                    <p className={`text-xs font-semibold ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-8">
            Nicio acțiune cu volum neobișnuit azi
          </p>
        )}
        
        <p className="text-xs text-muted-foreground mt-4 text-center">
          ⚡ Volumul neobișnuit poate indica interes crescut sau știri importante
        </p>
      </CardContent>
    </Card>
  );
}

// Combined Widget for Homepage
export default function MarketSignals() {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      <Week52Extremes />
      <UnusualVolume />
    </div>
  );
}
