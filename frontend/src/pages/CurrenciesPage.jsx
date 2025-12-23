import React, { useState, useEffect } from 'react';
import { DollarSign, RefreshCw, TrendingUp, TrendingDown, Search } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CURRENCY_INFO = {
  EUR: { name: 'Euro', flag: '🇪🇺' },
  USD: { name: 'Dolar American', flag: '🇺🇸' },
  GBP: { name: 'Liră Sterlină', flag: '🇬🇧' },
  CHF: { name: 'Franc Elvețian', flag: '🇨🇭' },
  JPY: { name: 'Yen Japonez', flag: '🇯🇵' },
  CAD: { name: 'Dolar Canadian', flag: '🇨🇦' },
  AUD: { name: 'Dolar Australian', flag: '🇦🇺' },
  PLN: { name: 'Zlot Polonez', flag: '🇵🇱' },
  HUF: { name: 'Forint Maghiar', flag: '🇭🇺' },
  CZK: { name: 'Coroană Cehă', flag: '🇨🇿' },
  SEK: { name: 'Coroană Suedeză', flag: '🇸🇪' },
  NOK: { name: 'Coroană Norvegiană', flag: '🇳🇴' },
  DKK: { name: 'Coroană Daneză', flag: '🇩🇰' },
  BGN: { name: 'Leva Bulgărească', flag: '🇧🇬' },
  RSD: { name: 'Dinar Sârbesc', flag: '🇷🇸' },
  MDL: { name: 'Leu Moldovenesc', flag: '🇲🇩' },
  UAH: { name: 'Hryvna Ucraineană', flag: '🇺🇦' },
  TRY: { name: 'Liră Turcească', flag: '🇹🇷' },
  CNY: { name: 'Yuan Chinezesc', flag: '🇨🇳' },
  INR: { name: 'Rupie Indiană', flag: '🇮🇳' },
  BRL: { name: 'Real Brazilian', flag: '🇧🇷' },
  MXN: { name: 'Peso Mexican', flag: '🇲🇽' },
  ZAR: { name: 'Rand Sud-African', flag: '🇿🇦' },
  SGD: { name: 'Dolar Singaporean', flag: '🇸🇬' },
  HKD: { name: 'Dolar Hong Kong', flag: '🇭🇰' },
  NZD: { name: 'Dolar Neo-Zeelandez', flag: '🇳🇿' },
  KRW: { name: 'Won Sud-Coreean', flag: '🇰🇷' },
  THB: { name: 'Baht Thailandez', flag: '🇹🇭' },
  MYR: { name: 'Ringgit Malaysian', flag: '🇲🇾' },
  PHP: { name: 'Peso Filipinez', flag: '🇵🇭' },
  IDR: { name: 'Rupie Indoneziană', flag: '🇮🇩' },
  XAU: { name: 'Aur (1 gram)', flag: '🥇' },
  XDR: { name: 'DST (FMI)', flag: '🌐' },
};

function MainCurrencyCard({ code, data }) {
  const info = CURRENCY_INFO[code] || { name: code, flag: '💱' };
  
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{info.flag}</span>
            <div>
              <p className="font-bold text-lg">{code}</p>
              <p className="text-sm text-muted-foreground">{info.name}</p>
            </div>
          </div>
        </div>
        <div className="text-center">
          <p className="text-3xl font-bold">{data.rate.toFixed(4)}</p>
          <p className="text-sm text-muted-foreground">RON</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default function CurrenciesPage() {
  const [currencies, setCurrencies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchCurrencies = async () => {
    try {
      const res = await fetch(`${API_URL}/api/currencies`);
      const data = await res.json();
      setCurrencies(data);
    } catch (error) {
      console.error('Error fetching currencies:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchCurrencies();
    const interval = setInterval(fetchCurrencies, 3600000); // Refresh every hour
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetch(`${API_URL}/api/refresh/currencies`, { method: 'POST' });
    await fetchCurrencies();
  };

  const mainCurrencies = ['EUR', 'USD', 'GBP', 'CHF'];
  
  const allCurrencies = currencies?.rates ? Object.entries(currencies.rates)
    .filter(([code]) => 
      code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (CURRENCY_INFO[code]?.name || '').toLowerCase().includes(searchTerm.toLowerCase())
    )
    .sort((a, b) => a[0].localeCompare(b[0]))
    : [];

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-40" />)}
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
            <DollarSign className="w-8 h-8 text-blue-600" />
            Curs Valutar BNR
          </h1>
          <p className="text-muted-foreground">
            Cursuri oficiale de la Banca Națională a României
            {currencies?.date && ` - ${currencies.date}`}
          </p>
        </div>
        <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
          <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
          Actualizează
        </Button>
      </div>

      {/* Main Currencies */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {mainCurrencies.map(code => currencies?.rates?.[code] && (
          <MainCurrencyCard key={code} code={code} data={currencies.rates[code]} />
        ))}
      </div>

      {/* All Currencies Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <CardTitle>Toate Valutele ({allCurrencies.length})</CardTitle>
            <div className="relative w-full md:w-64">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Caută valută..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Valută</TableHead>
                <TableHead>Denumire</TableHead>
                <TableHead className="text-right">Curs (RON)</TableHead>
                <TableHead className="text-right">Multiplicator</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allCurrencies.map(([code, data]) => {
                const info = CURRENCY_INFO[code] || { name: code, flag: '💱' };
                return (
                  <TableRow key={code} className="hover:bg-muted/50">
                    <TableCell className="font-bold">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{info.flag}</span>
                        <span>{code}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{info.name}</TableCell>
                    <TableCell className="text-right font-mono font-bold">
                      {data.rate.toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {data.multiplier > 1 ? `pentru ${data.multiplier} unități` : '-'}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Badge variant="outline">Info</Badge>
            <span>Cursurile valutare sunt furnizate de Banca Națională a României și se actualizează zilnic în jurul orei 13:00.</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
