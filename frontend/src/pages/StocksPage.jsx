import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, RefreshCw, Search, ArrowUpDown, BarChart3, Flame, Activity, Building2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Skeleton } from '../components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function StocksPage() {
  const [stocks, setStocks] = useState([]);
  const [indices, setIndices] = useState([]);
  const [topMovers, setTopMovers] = useState({ gainers: [], losers: [], most_traded: [] });
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState({ key: 'symbol', direction: 'asc' });

  const fetchAllData = async () => {
    try {
      const [stocksRes, indicesRes, moversRes, sectorsRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb`),
        fetch(`${API_URL}/api/bvb/indices`),
        fetch(`${API_URL}/api/bvb/top-movers`),
        fetch(`${API_URL}/api/bvb/sectors`)
      ]);
      
      const stocksData = await stocksRes.json();
      const indicesData = await indicesRes.json();
      const moversData = await moversRes.json();
      const sectorsData = await sectorsRes.json();
      
      setStocks(stocksData);
      setIndices(indicesData.indices || []);
      setTopMovers(moversData);
      setSectors(sectorsData.sectors || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/bvb`, { method: 'POST' });
    await fetchAllData();
  };

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  const filteredStocks = stocks
    .filter(stock => 
      stock.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.name?.toLowerCase().includes(searchTerm.toLowerCase())
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
    avgChange: stocks.length > 0 
      ? (stocks.reduce((acc, s) => acc + (s.change_percent || 0), 0) / stocks.length).toFixed(2)
      : 0
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-5 gap-4">
          {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-24" />)}
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
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <BarChart3 className="w-8 h-8 text-blue-600" />
            Bursa de Valori București
          </h1>
          <p className="text-muted-foreground">Date în timp real • Actualizare automată</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Actualizează
          </Button>
        </div>
      </div>

      {/* BVB Indices Section */}
      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-purple-600" />
          Indicii BVB
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {indices.map((index) => (
            <Card key={index.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-bold text-lg">{index.id}</p>
                    <p className="text-xs text-muted-foreground truncate">{index.name}</p>
                  </div>
                  {!index.is_live && (
                    <Badge variant="outline" className="text-xs">Estimat</Badge>
                  )}
                </div>
                <p className="text-2xl font-bold">{index.value?.toLocaleString('ro-RO')}</p>
                <div className={`flex items-center mt-1 ${index.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {index.change_percent >= 0 ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
                  <span className="font-medium">{index.change_percent >= 0 ? '+' : ''}{index.change_percent?.toFixed(2)}%</span>
                </div>
                <p className="text-xs text-muted-foreground mt-2">{index.components} componente</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Top Movers Section */}
      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Flame className="w-5 h-5 text-orange-600" />
          Top Movers Azi
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          {/* Top Gainers */}
          <Card className="border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                🚀 Top Creșteri
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {topMovers.gainers?.slice(0, 5).map((stock, idx) => (
                  <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                    <div className="flex justify-between items-center p-2 rounded-lg hover:bg-green-50 transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-green-600">#{idx + 1}</span>
                        <div>
                          <p className="font-semibold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[100px]">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-green-600">+{stock.change_percent?.toFixed(2)}%</p>
                        <p className="text-xs">{stock.price?.toFixed(2)} RON</p>
                      </div>
                    </div>
                  </Link>
                ))}
                {topMovers.gainers?.length === 0 && (
                  <p className="text-muted-foreground text-center py-4">Nicio acțiune în creștere</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Top Losers */}
          <Card className="border-red-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingDown className="w-5 h-5 text-red-600" />
                📉 Top Scăderi
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {topMovers.losers?.slice(0, 5).map((stock, idx) => (
                  <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                    <div className="flex justify-between items-center p-2 rounded-lg hover:bg-red-50 transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-red-600">#{idx + 1}</span>
                        <div>
                          <p className="font-semibold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[100px]">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-red-600">{stock.change_percent?.toFixed(2)}%</p>
                        <p className="text-xs">{stock.price?.toFixed(2)} RON</p>
                      </div>
                    </div>
                  </Link>
                ))}
                {topMovers.losers?.length === 0 && (
                  <p className="text-muted-foreground text-center py-4">Nicio acțiune în scădere</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Most Traded */}
          <Card className="border-blue-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                📊 Cel Mai Mare Volum
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {topMovers.most_traded?.slice(0, 5).map((stock, idx) => (
                  <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                    <div className="flex justify-between items-center p-2 rounded-lg hover:bg-blue-50 transition-colors">
                      <div className="flex items-center gap-2">
                        <span className="text-lg font-bold text-blue-600">#{idx + 1}</span>
                        <div>
                          <p className="font-semibold">{stock.symbol}</p>
                          <p className="text-xs text-muted-foreground truncate max-w-[100px]">{stock.name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">{(stock.volume || 0).toLocaleString('ro-RO')}</p>
                        <p className="text-xs text-muted-foreground">volum</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Sector Performance */}
      <section>
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          <Building2 className="w-5 h-5 text-indigo-600" />
          Performanță pe Sectoare
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {sectors.map((sector) => (
            <Card key={sector.name} className={`${
              sector.average_change_percent > 0 ? 'border-green-200 bg-green-50/50' : 
              sector.average_change_percent < 0 ? 'border-red-200 bg-red-50/50' : 
              'border-gray-200'
            }`}>
              <CardContent className="p-3 text-center">
                <p className="font-semibold text-sm">{sector.name}</p>
                <p className={`text-lg font-bold ${
                  sector.average_change_percent > 0 ? 'text-green-600' : 
                  sector.average_change_percent < 0 ? 'text-red-600' : ''
                }`}>
                  {sector.average_change_percent > 0 ? '+' : ''}{sector.average_change_percent?.toFixed(2)}%
                </p>
                <p className="text-xs text-muted-foreground">{sector.stock_count} acțiuni</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Market Stats Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm text-blue-100">Total Acțiuni</p>
            <p className="text-3xl font-bold">{stocks.length}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm text-green-100">În Creștere</p>
            <p className="text-3xl font-bold">{marketStats.gainers}</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white">
          <CardContent className="p-4">
            <p className="text-sm text-red-100">În Scădere</p>
            <p className="text-3xl font-bold">{marketStats.losers}</p>
          </CardContent>
        </Card>
        <Card className={`bg-gradient-to-br ${parseFloat(marketStats.avgChange) >= 0 ? 'from-emerald-500 to-emerald-600' : 'from-orange-500 to-orange-600'} text-white`}>
          <CardContent className="p-4">
            <p className="text-sm opacity-90">Media Piață</p>
            <p className="text-3xl font-bold">{parseFloat(marketStats.avgChange) >= 0 ? '+' : ''}{marketStats.avgChange}%</p>
          </CardContent>
        </Card>
      </div>

      {/* All Stocks Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
            <CardTitle>Toate Acțiunile BVB</CardTitle>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Caută acțiune..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="cursor-pointer" onClick={() => handleSort('symbol')}>
                  <div className="flex items-center gap-1">
                    Simbol <ArrowUpDown className="w-4 h-4" />
                  </div>
                </TableHead>
                <TableHead>Companie</TableHead>
                <TableHead>Sector</TableHead>
                <TableHead className="text-right cursor-pointer" onClick={() => handleSort('price')}>
                  <div className="flex items-center justify-end gap-1">
                    Preț (RON) <ArrowUpDown className="w-4 h-4" />
                  </div>
                </TableHead>
                <TableHead className="text-right cursor-pointer" onClick={() => handleSort('change_percent')}>
                  <div className="flex items-center justify-end gap-1">
                    Variație <ArrowUpDown className="w-4 h-4" />
                  </div>
                </TableHead>
                <TableHead className="text-right cursor-pointer" onClick={() => handleSort('volume')}>
                  <div className="flex items-center justify-end gap-1">
                    Volum <ArrowUpDown className="w-4 h-4" />
                  </div>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredStocks.map((stock) => (
                <TableRow key={stock.symbol} className="hover:bg-muted/50">
                  <TableCell>
                    <Link to={`/stocks/bvb/${stock.symbol}`} className="font-bold text-blue-600 hover:underline">
                      {stock.symbol}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Link to={`/stocks/bvb/${stock.symbol}`} className="hover:text-blue-600">
                      {stock.name}
                    </Link>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{stock.sector || 'N/A'}</Badge>
                  </TableCell>
                  <TableCell className="text-right font-medium">
                    {stock.price?.toFixed(2)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className={`flex items-center justify-end gap-1 ${
                      stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stock.change_percent >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                      <span className="font-medium">
                        {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right text-muted-foreground">
                    {(stock.volume || 0).toLocaleString('ro-RO')}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Financial Education CTA */}
      <Card className="bg-gradient-to-r from-green-600 to-blue-600 text-white border-0">
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h3 className="text-xl font-bold mb-1">💰 Vrei Să Înțelegi Mai Bine Piața?</h3>
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
