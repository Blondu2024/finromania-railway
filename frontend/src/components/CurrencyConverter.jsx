import React, { useState, useEffect } from 'react';
import { ArrowRightLeft, RefreshCw, TrendingUp, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function CurrencyConverter({ variant = "full" }) {
  const [currencies, setCurrencies] = useState([]);
  const [popularPairs, setPopularPairs] = useState([]);
  const [amount, setAmount] = useState('100');
  const [fromCurrency, setFromCurrency] = useState('EUR');
  const [toCurrency, setToCurrency] = useState('RON');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    fetchCurrencies();
    fetchPopularPairs();
  }, []);

  useEffect(() => {
    if (amount && fromCurrency && toCurrency) {
      convertCurrency();
    }
  }, [amount, fromCurrency, toCurrency]);

  const fetchCurrencies = async () => {
    try {
      const res = await fetch(`${API_URL}/api/currency/currencies`);
      if (res.ok) {
        const data = await res.json();
        setCurrencies(data.currencies || []);
      }
    } catch (error) {
      console.error('Error fetching currencies:', error);
    }
  };

  const fetchPopularPairs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/currency/popular-pairs`);
      if (res.ok) {
        const data = await res.json();
        setPopularPairs(data.pairs || []);
      }
    } catch (error) {
      console.error('Error fetching pairs:', error);
    }
  };

  const convertCurrency = async () => {
    if (!amount || isNaN(parseFloat(amount))) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/currency/convert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount: parseFloat(amount),
          from_currency: fromCurrency,
          to_currency: toCurrency
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        setLastUpdated(new Date().toLocaleTimeString('ro-RO'));
      }
    } catch (error) {
      console.error('Conversion error:', error);
    } finally {
      setLoading(false);
    }
  };

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const handlePairClick = (from, to) => {
    setFromCurrency(from);
    setToCurrency(to);
    setAmount('100');
  };

  // Compact variant for homepage
  if (variant === "compact") {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <ArrowRightLeft className="w-5 h-5 text-blue-600" />
            Convertor Valutar
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-24"
            />
            <Select value={fromCurrency} onValueChange={setFromCurrency}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {currencies.slice(0, 10).map(c => (
                  <SelectItem key={c.code} value={c.code}>
                    {c.flag} {c.code}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="ghost" size="icon" onClick={swapCurrencies}>
              <ArrowRightLeft className="w-4 h-4" />
            </Button>
            <Select value={toCurrency} onValueChange={setToCurrency}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {currencies.slice(0, 10).map(c => (
                  <SelectItem key={c.code} value={c.code}>
                    {c.flag} {c.code}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {result && (
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">
                {result.result.toLocaleString('ro-RO', { maximumFractionDigits: 2 })} {toCurrency}
              </p>
              <p className="text-xs text-muted-foreground">
                1 {fromCurrency} = {result.rate.toFixed(4)} {toCurrency}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    );
  }

  // Full variant
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Convertor Valutar</h1>
        <p className="text-muted-foreground">Rate de schimb actualizate în timp real</p>
      </div>

      <Card>
        <CardContent className="p-6">
          <div className="grid md:grid-cols-[1fr,auto,1fr] gap-4 items-end">
            {/* From */}
            <div className="space-y-2">
              <label className="text-sm font-medium">De la</label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="text-lg"
                  placeholder="Sumă"
                />
                <Select value={fromCurrency} onValueChange={setFromCurrency}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map(c => (
                      <SelectItem key={c.code} value={c.code}>
                        {c.flag} {c.code} - {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Swap Button */}
            <Button variant="outline" size="icon" onClick={swapCurrencies} className="mb-0.5">
              <ArrowRightLeft className="w-4 h-4" />
            </Button>

            {/* To */}
            <div className="space-y-2">
              <label className="text-sm font-medium">La</label>
              <div className="flex gap-2">
                <div className="flex-1 text-lg font-semibold p-2 bg-muted rounded-md flex items-center justify-center min-h-[40px]">
                  {loading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : result ? (
                    result.result.toLocaleString('ro-RO', { maximumFractionDigits: 2 })
                  ) : '-'}
                </div>
                <Select value={toCurrency} onValueChange={setToCurrency}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {currencies.map(c => (
                      <SelectItem key={c.code} value={c.code}>
                        {c.flag} {c.code} - {c.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {result && (
            <div className="mt-4 p-4 bg-muted/50 rounded-lg text-center">
              <p className="text-3xl font-bold text-blue-600">
                {parseFloat(amount).toLocaleString('ro-RO')} {fromCurrency} = {result.result.toLocaleString('ro-RO', { maximumFractionDigits: 2 })} {toCurrency}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Rată: 1 {fromCurrency} = {result.rate.toFixed(6)} {toCurrency}
              </p>
              {lastUpdated && (
                <p className="text-xs text-muted-foreground mt-1">
                  Actualizat: {lastUpdated}
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Popular Pairs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            Perechi Populare
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {popularPairs.map((pair, idx) => (
              <button
                key={idx}
                onClick={() => handlePairClick(pair.from, pair.to)}
                className="p-3 rounded-lg border hover:bg-muted/50 transition-colors text-left"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{pair.from_flag}</span>
                  <span className="text-muted-foreground">→</span>
                  <span>{pair.to_flag}</span>
                </div>
                <p className="font-semibold">{pair.from}/{pair.to}</p>
                <p className="text-sm text-muted-foreground">{pair.rate.toFixed(4)}</p>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* All Currencies */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Toate Valutele ({currencies.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-2">
            {currencies.map(c => (
              <div
                key={c.code}
                className="p-2 rounded border text-sm flex items-center gap-2 cursor-pointer hover:bg-muted/50"
                onClick={() => setFromCurrency(c.code)}
              >
                <span className="text-lg">{c.flag}</span>
                <div>
                  <p className="font-medium">{c.code}</p>
                  <p className="text-xs text-muted-foreground truncate">{c.name}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
