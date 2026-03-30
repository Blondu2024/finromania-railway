import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRightLeft, RefreshCw, TrendingUp, TrendingDown, Loader2,
  Globe, Zap, DollarSign, Euro, Coins, Sparkles, ArrowRight,
  Clock, ChevronDown, Calculator, Wallet
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Flag emoji map for popular currencies
const CURRENCY_FLAGS = {
  RON: '🇷🇴', EUR: '🇪🇺', USD: '🇺🇸', GBP: '🇬🇧', CHF: '🇨🇭',
  BGN: '🇧🇬', HUF: '🇭🇺', PLN: '🇵🇱', CZK: '🇨🇿', JPY: '🇯🇵',
  CNY: '🇨🇳', AUD: '🇦🇺', CAD: '🇨🇦', SEK: '🇸🇪', NOK: '🇳🇴',
  DKK: '🇩🇰', INR: '🇮🇳', BRL: '🇧🇷', MXN: '🇲🇽', TRY: '🇹🇷',
  UAH: '🇺🇦', MDL: '🇲🇩', RUB: '🇷🇺', ZAR: '🇿🇦', KRW: '🇰🇷',
  SGD: '🇸🇬', HKD: '🇭🇰', NZD: '🇳🇿', AED: '🇦🇪', SAR: '🇸🇦'
};

// Animated background shapes
const FloatingShape = ({ delay, duration, className }) => (
  <motion.div
    className={`absolute rounded-full opacity-10 ${className}`}
    animate={{
      y: [0, -20, 0],
      x: [0, 10, 0],
      scale: [1, 1.1, 1],
    }}
    transition={{
      duration,
      delay,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  />
);

// Live Ticker Component
const LiveTicker = ({ rates, isLoading }) => {
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setOffset(prev => prev - 1);
    }, 30);
    return () => clearInterval(interval);
  }, []);

  const tickerItems = Object.entries(rates).slice(0, 15);
  const duplicatedItems = [...tickerItems, ...tickerItems, ...tickerItems];

  return (
    <div className="relative overflow-hidden bg-gradient-to-r from-zinc-900 via-blue-900 to-zinc-900 py-3">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjEiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIi8+PC9nPjwvc3ZnPg==')] opacity-30" />

      <motion.div
        className="flex gap-8 whitespace-nowrap"
        animate={{ x: offset }}
        transition={{ duration: 0, ease: "linear" }}
        style={{ width: 'fit-content' }}
      >
        {duplicatedItems.map(([code, data], idx) => (
          <div key={`${code}-${idx}`} className="flex items-center gap-2 text-white">
            <span className="text-lg">{CURRENCY_FLAGS[code] || '💱'}</span>
            <span className="font-bold">{code}</span>
            <span className="text-blue-300">{data.rate?.toFixed(4) || '-'}</span>
            <span className="text-slate-500">|</span>
          </div>
        ))}
      </motion.div>
    </div>
  );
};

// Animated Currency Card
const CurrencyCard = ({ code, data, onClick, isSelected, delay = 0 }) => {
  const flag = CURRENCY_FLAGS[code] || '💱';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.05, duration: 0.3 }}
      whileHover={{ scale: 1.05, y: -5 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onClick(code)}
      className={`relative cursor-pointer group ${isSelected ? 'ring-2 ring-blue-500' : ''}`}
    >
      <Card className="overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all">
        <div className={`absolute inset-0 bg-gradient-to-br ${
          isSelected
            ? 'from-blue-500/20 to-blue-500/20'
            : 'from-gray-100 to-gray-50 dark:from-zinc-800 dark:to-zinc-900'
        }`} />
        <CardContent className="relative p-4 text-center">
          <motion.span
            className="text-3xl block mb-2"
            animate={{ rotate: isSelected ? [0, -10, 10, 0] : 0 }}
            transition={{ duration: 0.5 }}
          >
            {flag}
          </motion.span>
          <p className="font-bold text-lg">{code}</p>
          <p className="text-sm text-muted-foreground truncate">{data.name}</p>
          <div className="mt-2 pt-2 border-t">
            <p className="text-xl font-bold bg-gradient-to-r from-blue-700 to-blue-500 bg-clip-text text-transparent">
              {data.rate?.toFixed(4)}
            </p>
            <p className="text-xs text-muted-foreground">RON</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Popular Pair Button
const PopularPairButton = ({ pair, onClick, delay }) => (
  <motion.button
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay: delay * 0.1 }}
    whileHover={{ scale: 1.05 }}
    whileTap={{ scale: 0.95 }}
    onClick={onClick}
    className="relative group overflow-hidden rounded-xl"
  >
    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
    <div className="relative p-4 bg-white dark:bg-zinc-800 group-hover:bg-transparent border rounded-xl transition-all">
      <div className="flex items-center justify-center gap-2 mb-2">
        <span className="text-2xl">{pair.from_flag}</span>
        <motion.div
          animate={{ x: [0, 5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <ArrowRight className="w-4 h-4 text-blue-500 group-hover:text-white" />
        </motion.div>
        <span className="text-2xl">{pair.to_flag}</span>
      </div>
      <p className="font-bold text-lg group-hover:text-white transition-colors">{pair.from}/{pair.to}</p>
      <p className="text-sm text-muted-foreground group-hover:text-white/80 transition-colors">
        {pair.rate?.toFixed(4)}
      </p>
    </div>
  </motion.button>
);

// Main Converter Component
const MainConverter = ({
  currencies, amount, setAmount, fromCurrency, setFromCurrency,
  toCurrency, setToCurrency, result, loading, onSwap, t
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
    >
      <Card className="overflow-hidden border-0 shadow-2xl">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-700 via-blue-600 to-blue-800" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMwLTkuOTQtOC4wNi0xOC0xOC0xOHY2YzYuNjMgMCAxMiA1LjM3IDEyIDEyaC02bDkgOSA5LTloLTZ6IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9Ii4wNSIvPjwvZz48L3N2Zz4=')] opacity-50" />

        <CardContent className="relative p-8 text-white">
          <div className="flex items-center justify-center gap-2 mb-6">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Coins className="w-6 h-6" />
            </motion.div>
            <h2 className="text-2xl font-bold">{t('converter.instantConverter')}</h2>
          </div>

          <div className="grid md:grid-cols-[1fr,auto,1fr] gap-6 items-center">
            {/* From */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-100 flex items-center gap-2">
                <Wallet className="w-4 h-4" />
                {t('converter.from')}
              </label>
              <div className="flex gap-2">
                <Input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="bg-white/10 border-white/20 text-white placeholder:text-white/50 text-xl font-bold"
                  placeholder={t('converter.amount')}
                />
                <Select value={fromCurrency} onValueChange={setFromCurrency}>
                  <SelectTrigger className="w-36 bg-white/10 border-white/20 text-white">
                    <SelectValue>
                      {CURRENCY_FLAGS[fromCurrency]} {fromCurrency}
                    </SelectValue>
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
            <motion.div
              whileHover={{ scale: 1.2, rotate: 180 }}
              whileTap={{ scale: 0.9 }}
            >
              <Button
                variant="outline"
                size="icon"
                onClick={onSwap}
                className="rounded-full bg-white/20 border-white/30 hover:bg-white/30 text-white h-14 w-14"
              >
                <ArrowRightLeft className="w-6 h-6" />
              </Button>
            </motion.div>

            {/* To */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-blue-100 flex items-center gap-2">
                <Calculator className="w-4 h-4" />
                {t('converter.to')}
              </label>
              <div className="flex gap-2">
                <div className="flex-1 bg-white/10 rounded-md border border-white/20 flex items-center justify-center min-h-[48px] px-4">
                  {loading ? (
                    <Loader2 className="w-6 h-6 animate-spin" />
                  ) : result ? (
                    <motion.span
                      key={result.result}
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="text-xl font-bold"
                    >
                      {result.result.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
                    </motion.span>
                  ) : (
                    <span className="text-white/50">-</span>
                  )}
                </div>
                <Select value={toCurrency} onValueChange={setToCurrency}>
                  <SelectTrigger className="w-36 bg-white/10 border-white/20 text-white">
                    <SelectValue>
                      {CURRENCY_FLAGS[toCurrency]} {toCurrency}
                    </SelectValue>
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

          {/* Result Display */}
          <AnimatePresence mode="wait">
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="mt-6 p-6 bg-white/10 backdrop-blur rounded-xl text-center"
              >
                <p className="text-4xl font-bold mb-2">
                  {parseFloat(amount).toLocaleString('ro-RO')} {fromCurrency} = {' '}
                  <span className="text-yellow-300">
                    {result.result.toLocaleString('ro-RO', { maximumFractionDigits: 2 })} {toCurrency}
                  </span>
                </p>
                <div className="flex items-center justify-center gap-4 text-sm text-blue-100">
                  <span className="flex items-center gap-1">
                    <Zap className="w-4 h-4" />
                    {t('converter.rate')}: 1 {fromCurrency} = {result.rate.toFixed(6)} {toCurrency}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    Live
                  </span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Vertical Auto-Scroll Rate List
const AutoScrollRates = ({ rates }) => {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setScrollY(prev => {
        const maxScroll = Object.keys(rates).length * 60;
        return prev >= maxScroll ? 0 : prev + 1;
      });
    }, 50);
    return () => clearInterval(interval);
  }, [rates]);

  const ratesList = Object.entries(rates);
  const duplicatedRates = [...ratesList, ...ratesList];

  return (
    <div className="h-[400px] overflow-hidden relative">
      <div className="absolute inset-x-0 top-0 h-12 bg-gradient-to-b from-background to-transparent z-10" />
      <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-background to-transparent z-10" />

      <motion.div
        animate={{ y: -scrollY }}
        className="space-y-2"
      >
        {duplicatedRates.map(([code, data], idx) => (
          <motion.div
            key={`${code}-${idx}`}
            className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-white dark:from-zinc-800 dark:to-zinc-900 rounded-lg border hover:shadow-md transition-all"
            whileHover={{ x: 5, scale: 1.02 }}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">{CURRENCY_FLAGS[code] || '💱'}</span>
              <div>
                <p className="font-bold">{code}</p>
                <p className="text-xs text-muted-foreground">{data.name}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-lg">{data.rate?.toFixed(4)}</p>
              <p className="text-xs text-muted-foreground">RON</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

// Main Page Component
export default function CurrencyConverterPage() {
  const { t } = useTranslation();
  const [currencies, setCurrencies] = useState([]);
  const [rates, setRates] = useState({});
  const [popularPairs, setPopularPairs] = useState([]);
  const [amount, setAmount] = useState('100');
  const [fromCurrency, setFromCurrency] = useState('EUR');
  const [toCurrency, setToCurrency] = useState('RON');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch data
  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [currRes, ratesRes, pairsRes] = await Promise.all([
          fetch(`${API_URL}/api/currency/currencies`),
          fetch(`${API_URL}/api/currency/rates?base=RON`),
          fetch(`${API_URL}/api/currency/popular-pairs`)
        ]);

        if (currRes.ok) {
          const data = await currRes.json();
          setCurrencies(data.currencies || []);
        }
        if (ratesRes.ok) {
          const data = await ratesRes.json();
          setRates(data.rates || {});
          setLastUpdated(data.last_updated);
        }
        if (pairsRes.ok) {
          const data = await pairsRes.json();
          setPopularPairs(data.pairs || []);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setPageLoading(false);
      }
    };

    fetchAll();
    const interval = setInterval(fetchAll, 300000); // 5 min
    return () => clearInterval(interval);
  }, []);

  // Convert currency
  const convertCurrency = useCallback(async () => {
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
      }
    } catch (error) {
      console.error('Conversion error:', error);
    } finally {
      setLoading(false);
    }
  }, [amount, fromCurrency, toCurrency]);

  useEffect(() => {
    if (amount && fromCurrency && toCurrency) {
      const timer = setTimeout(convertCurrency, 300);
      return () => clearTimeout(timer);
    }
  }, [amount, fromCurrency, toCurrency, convertCurrency]);

  const swapCurrencies = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const handlePairClick = (from, to) => {
    setFromCurrency(from);
    setToCurrency(to);
    setAmount('100');
  };

  const handleCurrencySelect = (code) => {
    setFromCurrency(code);
  };

  if (pageLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <Loader2 className="w-12 h-12 text-blue-600" />
        </motion.div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="Convertor Valutar Live | FinRomania"
        description="Convertor valutar în timp real cu rate BNR. Convertește EUR, USD, GBP și alte 30+ valute. Rate actualizate automat."
        keywords="convertor valutar, curs valutar, EUR RON, USD RON, rate de schimb, BNR"
      />

      <div className="min-h-screen">
        {/* Live Ticker */}
        <LiveTicker rates={rates} />

        {/* Hero Section */}
        <section className="relative overflow-hidden py-12 bg-gradient-to-br from-gray-50 via-blue-50 to-blue-50 dark:from-zinc-900 dark:via-zinc-800 dark:to-zinc-900">
          {/* Floating shapes */}
          <FloatingShape delay={0} duration={4} className="w-64 h-64 bg-blue-400 -top-32 -left-32" />
          <FloatingShape delay={1} duration={5} className="w-48 h-48 bg-blue-400 top-20 right-10" />
          <FloatingShape delay={2} duration={6} className="w-32 h-32 bg-green-400 bottom-10 left-1/4" />

          <div className="container mx-auto px-4 relative z-10">
            {/* Header */}
            <motion.div
              className="text-center mb-10"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-center gap-3 mb-4">
                <motion.div
                  animate={{
                    rotate: [0, 360],
                    scale: [1, 1.2, 1]
                  }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  <Globe className="w-12 h-12 text-blue-600" />
                </motion.div>
                <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-700 to-blue-500 bg-clip-text text-transparent">
                  {t('converter.title')}
                </h1>
              </div>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                {t('converter.subtitle')}
                <motion.span
                  className="inline-block ml-2"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  ⚡
                </motion.span>
              </p>
              {lastUpdated && (
                <Badge variant="outline" className="mt-3">
                  <Clock className="w-3 h-3 mr-1" />
                  {t('converter.lastUpdated')}: {new Date(lastUpdated).toLocaleString('ro-RO')}
                </Badge>
              )}
            </motion.div>

            {/* Main Converter */}
            <div className="max-w-4xl mx-auto">
              <MainConverter
                currencies={currencies}
                amount={amount}
                setAmount={setAmount}
                fromCurrency={fromCurrency}
                setFromCurrency={setFromCurrency}
                toCurrency={toCurrency}
                setToCurrency={setToCurrency}
                result={result}
                loading={loading}
                onSwap={swapCurrencies}
                t={t}
              />
            </div>
          </div>
        </section>

        {/* Popular Pairs Section */}
        <section className="py-12 bg-background">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-center mb-8"
            >
              <h2 className="text-2xl md:text-3xl font-bold flex items-center justify-center gap-2">
                <Sparkles className="w-6 h-6 text-yellow-500" />
                {t('converter.popularPairs')}
              </h2>
              <p className="text-muted-foreground mt-2">{t('converter.clickForConversion')}</p>
            </motion.div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {popularPairs.map((pair, idx) => (
                <PopularPairButton
                  key={idx}
                  pair={pair}
                  delay={idx}
                  onClick={() => handlePairClick(pair.from, pair.to)}
                />
              ))}
            </div>
          </div>
        </section>

        {/* Two Column Layout: Currency Grid + Auto Scroll */}
        <section className="py-12 bg-gradient-to-b from-gray-50 to-white dark:from-zinc-900 dark:to-zinc-800">
          <div className="container mx-auto px-4">
            <div className="grid lg:grid-cols-[2fr,1fr] gap-8">
              {/* Currency Grid */}
              <div>
                <motion.h2
                  className="text-2xl font-bold mb-6 flex items-center gap-2"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                >
                  <Coins className="w-6 h-6 text-blue-600" />
                  {t('converter.allCurrencies')} ({Object.keys(rates).length})
                </motion.h2>
                <p className="text-muted-foreground mb-6">Click pe o valută pentru a o selecta ca sursă</p>

                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {Object.entries(rates).map(([code, data], idx) => (
                    <CurrencyCard
                      key={code}
                      code={code}
                      data={data}
                      onClick={handleCurrencySelect}
                      isSelected={fromCurrency === code}
                      delay={idx}
                    />
                  ))}
                </div>
              </div>

              {/* Auto Scroll Sidebar */}
              <div className="hidden lg:block">
                <Card className="sticky top-4 overflow-hidden">
                  <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-500 text-white">
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      {t('converter.liveRates')}
                      <motion.div
                        animate={{ opacity: [1, 0.5, 1] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="w-2 h-2 bg-green-400 rounded-full ml-auto"
                      />
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4">
                    <AutoScrollRates rates={rates} />
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        </section>

        {/* Info Footer */}
        <section className="py-8 bg-gray-100 dark:bg-zinc-800">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <Badge variant="outline">
                  <DollarSign className="w-3 h-3 mr-1" />
                  BNR
                </Badge>
                <span>{t('converter.bnrSource')}</span>
              </div>
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                >
                  <RefreshCw className="w-4 h-4" />
                </motion.div>
                <span>{t('converter.autoUpdate')}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
