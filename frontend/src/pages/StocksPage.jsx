import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, RefreshCw, Search, ArrowUpDown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StocksPage() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'symbol', direction: 'asc' });

  const fetchStocks = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stocks/bvb`);
      const data = await res.json();
      setStocks(data);
    } catch (error) {
      console.error('Error fetching stocks:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStocks();
    const interval = setInterval(fetchStocks, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/bvb`, { method: 'POST' });
    await fetchStocks();
  };

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const filteredStocks = stocks
    .filter(stock => 
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name.toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];
      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

  const marketStats = {
    gainers: stocks.filter(s => s.change_percent > 0).length,
    losers: stocks.filter(s => s.change_percent < 0).length,
    unchanged: stocks.filter(s => s.change_percent === 0).length,
    avgChange: stocks.length > 0 
      ? (stocks.reduce((acc, s) => acc + s.change_percent, 0) / stocks.length).toFixed(2)
      : 0
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold">Acțiuni BVB</h1>
          <p className="text-muted-foreground">Bursa de Valori București - Top 10 Companii</p>
        </div>
        <div className="flex gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Caută acțiune..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 w-64"
            />
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizează
          </Button>
        </div>
      </div>

      {/* Market Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Total Acțiuni</p>
            <p className="text-2xl font-bold">{stocks.length}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">În Creștere</p>
            <p className="text-2xl font-bold text-green-600">{marketStats.gainers}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">În Scădere</p>
            <p className="text-2xl font-bold text-red-600">{marketStats.losers}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <p className="text-sm text-muted-foreground">Variație Medie</p>
            <p className={`text-2xl font-bold ${parseFloat(marketStats.avgChange) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {marketStats.avgChange}%
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Stocks Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Lista Acțiuni</span>
            <Badge variant="outline">Date MOCK pentru MVP</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="cursor-pointer" onClick={() => handleSort('symbol')}>
                  <div className="flex items-center">
                    Simbol <ArrowUpDown className="ml-1 h-4 w-4" />
                  </div>
                </TableHead>
                <TableHead>Companie</TableHead>
                <TableHead className="text-right cursor-pointer" onClick={() => handleSort('price')}>
                  <div className="flex items-center justify-end">
                    Preț <ArrowUpDown className="ml-1 h-4 w-4" />
                  </div>
                </TableHead>
                <TableHead className="text-right cursor-pointer" onClick={() => handleSort('change_percent')}>
                  <div className="flex items-center justify-end">
                    Variație <ArrowUpDown className="ml-1 h-4 w-4" />
                  </div>
                </TableHead>
                <TableHead className="text-right">Volum</TableHead>
                <TableHead className="text-right">Acțiune</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredStocks.map(stock => {
                const isPositive = stock.change_percent >= 0;
                return (
                  <TableRow key={stock.symbol} className="hover:bg-muted/50">
                    <TableCell className="font-bold">{stock.symbol}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="truncate max-w-[200px]">{stock.name}</span>
                        {stock.is_mock && <Badge variant="outline" className="text-xs">MOCK</Badge>}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {stock.price?.toFixed(2)} {stock.currency}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className={`flex items-center justify-end ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                        {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                        <span className="font-medium">{isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono">
                      {stock.volume?.toLocaleString('ro-RO')}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link to={`/stocks/bvb/${stock.symbol}`}>
                        <Button variant="ghost" size="sm">Detalii</Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Financial Education CTA */}
      <Card className="bg-gradient-to-r from-green-600 to-blue-600 text-white border-0 mt-6">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h3 className="text-xl font-bold mb-1">💰 Nu Înțelegi Bine Cifrele?</h3>
              <p className="text-green-100">Învață bazele investițiilor în 15 lecții gratuite - de la bugete la ETF-uri</p>
            </div>
            <div className="flex gap-3">
              <Link to="/financial-education">
                <Button className="bg-white text-green-600 hover:bg-green-50">
                  Începe Educația Financiară →
                </Button>
              </Link>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
