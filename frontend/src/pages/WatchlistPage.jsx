import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Star, TrendingUp, TrendingDown, Trash2, Bell, RefreshCw, Plus } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function WatchlistPage() {
  const { user } = useAuth();
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stockPrices, setStockPrices] = useState({});

  useEffect(() => {
    if (user) {
      fetchWatchlist();
      fetchPrices();
    }
  }, [user]);

  const fetchWatchlist = async () => {
    try {
      const res = await fetch(`${API_URL}/api/watchlist`, { credentials: 'include' });
      if (res.ok) {
        const data = await res.json();
        setWatchlist(data);
      }
    } catch (error) {
      console.error('Error fetching watchlist:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrices = async () => {
    try {
      const [bvbRes, globalRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb`),
        fetch(`${API_URL}/api/stocks/global`)
      ]);
      const [bvb, global] = await Promise.all([bvbRes.json(), globalRes.json()]);
      
      const prices = {};
      bvb.forEach(s => { prices[`bvb_${s.symbol}`] = s; });
      global.forEach(s => { prices[`global_${s.symbol}`] = s; });
      setStockPrices(prices);
    } catch (error) {
      console.error('Error fetching prices:', error);
    }
  };

  const removeFromWatchlist = async (itemId) => {
    try {
      await fetch(`${API_URL}/api/watchlist/${itemId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      setWatchlist(watchlist.filter(item => item.id !== itemId));
    } catch (error) {
      console.error('Error removing from watchlist:', error);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <Star className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Conectează-te pentru Watchlist</h2>
        <p className="text-muted-foreground mb-4">Trebuie să fii conectat pentru a salva acțiuni în watchlist.</p>
        <Link to="/login"><Button>Conectează-te</Button></Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-24" />)}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Star className="w-8 h-8 text-yellow-500" />
            Watchlist
          </h1>
          <p className="text-muted-foreground">Acțiunile tale preferate</p>
        </div>
        <Button variant="outline" onClick={() => { fetchWatchlist(); fetchPrices(); }}>
          <RefreshCw className="w-4 h-4 mr-2" /> Actualizează
        </Button>
      </div>

      {watchlist.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <Star className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-semibold mb-2">Watchlist-ul tău este gol</h3>
            <p className="text-muted-foreground mb-4">
              Adaugă acțiuni din pagina Acțiuni BVB sau Indici Globali
            </p>
            <Link to="/stocks"><Button><Plus className="w-4 h-4 mr-2" /> Explorează Acțiuni</Button></Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {watchlist.map(item => {
            const priceKey = `${item.type}_${item.symbol}`;
            const priceData = stockPrices[priceKey];
            const isPositive = priceData?.change_percent >= 0;
            
            return (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <Link 
                            to={`/stocks/${item.type}/${encodeURIComponent(item.symbol)}`}
                            className="font-bold text-lg hover:text-blue-600"
                          >
                            {item.symbol}
                          </Link>
                          <Badge variant="outline">{item.type === 'bvb' ? 'BVB' : 'Global'}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.name || priceData?.name}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      {priceData && (
                        <div className="text-right">
                          <p className="font-bold text-lg">
                            {priceData.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
                          </p>
                          <p className={`text-sm flex items-center justify-end ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                            {isPositive ? '+' : ''}{priceData.change_percent?.toFixed(2)}%
                          </p>
                        </div>
                      )}
                      
                      <div className="flex gap-2">
                        {item.alert_enabled && (
                          <Badge variant="secondary">
                            <Bell className="w-3 h-3 mr-1" />
                            {item.target_price}
                          </Badge>
                        )}
                        <Button 
                          variant="ghost" 
                          size="icon"
                          onClick={() => removeFromWatchlist(item.id)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
