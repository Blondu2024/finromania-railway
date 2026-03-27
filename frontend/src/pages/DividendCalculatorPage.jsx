import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Coins, TrendingUp, Calendar, Calculator, Plus, Trash2, Download,
  PiggyBank, Percent, Clock, DollarSign, BarChart3, RefreshCw, Info,
  Lock, Award, Shield, History, ChevronRight, Star
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Slider } from '../components/ui/slider';
import { Label } from '../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '../components/ui/tooltip';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell } from 'recharts';
import { toast } from 'sonner';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ============================================
// DIVIDEND STOCKS TABLE
// ============================================
const DividendStocksTable = ({ stocks, onAddToPortfolio }) => {
  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Acțiune</TableHead>
            <TableHead className="text-right">Preț</TableHead>
            <TableHead className="text-right">Dividend/Acț</TableHead>
            <TableHead className="text-right">Yield</TableHead>
            <TableHead className="text-right">Payout</TableHead>
            <TableHead className="text-right">Ex-Date</TableHead>
            <TableHead className="text-center">Acțiune</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {stocks.map((stock) => (
            <TableRow key={stock.symbol} className="hover:bg-muted/50">
              <TableCell>
                <div>
                  <span className="font-bold text-blue-600">{stock.symbol}</span>
                  <p className="text-xs text-muted-foreground">{stock.name}</p>
                  {stock.data_source?.includes('BVB') && (
                    <span className="text-[10px] text-green-600 font-medium">BVB.ro</span>
                  )}
                </div>
              </TableCell>
              <TableCell className="text-right font-mono">{stock.price?.toFixed(2)} RON</TableCell>
              <TableCell className="text-right font-mono text-green-600">{stock.dividend_per_share?.toFixed(3)} RON</TableCell>
              <TableCell className="text-right">
                <Badge variant={stock.dividend_yield >= 5 ? "default" : "secondary"} className={stock.dividend_yield >= 5 ? "bg-green-600" : ""}>
                  {stock.dividend_yield?.toFixed(2)}%
                </Badge>
              </TableCell>
              <TableCell className="text-right text-sm">{stock.payout_ratio}%</TableCell>
              <TableCell className="text-right text-sm text-muted-foreground">{stock.ex_date}</TableCell>
              <TableCell className="text-center">
                <Button size="sm" variant="outline" onClick={() => onAddToPortfolio(stock)}>
                  <Plus className="w-4 h-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

// ============================================
// PORTFOLIO BUILDER
// ============================================
const PortfolioBuilder = ({ portfolio, setPortfolio, stocks }) => {
  const addHolding = (symbol) => {
    if (portfolio.find(h => h.symbol === symbol)) {
      toast.error('Acțiunea există deja în portofoliu');
      return;
    }
    setPortfolio([...portfolio, { symbol, shares: 100 }]);
    toast.success(`${symbol} adăugat în portofoliu`);
  };

  const removeHolding = (symbol) => {
    setPortfolio(portfolio.filter(h => h.symbol !== symbol));
  };

  const updateShares = (symbol, shares) => {
    setPortfolio(portfolio.map(h => 
      h.symbol === symbol ? { ...h, shares: parseInt(shares) || 0 } : h
    ));
  };

  const stocksMap = stocks.reduce((acc, s) => ({ ...acc, [s.symbol]: s }), {});

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <PiggyBank className="w-5 h-5 text-amber-500" />
          Portofoliul Tău
        </CardTitle>
        <CardDescription>Adaugă acțiuni și specifică numărul de unități</CardDescription>
      </CardHeader>
      <CardContent>
        {portfolio.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Coins className="w-12 h-12 mx-auto mb-2 opacity-30" />
            <p>Adaugă acțiuni din tabelul de mai jos</p>
          </div>
        ) : (
          <div className="space-y-3">
            {portfolio.map((holding) => {
              const stock = stocksMap[holding.symbol];
              const dividendValue = stock ? holding.shares * stock.dividend_per_share : 0;
              
              return (
                <motion.div
                  key={holding.symbol}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/30"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">{holding.symbol}</span>
                      <span className="text-sm text-muted-foreground">{stock?.name}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Investiție: {(holding.shares * (stock?.price || 0)).toFixed(0)} RON
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      value={holding.shares}
                      onChange={(e) => updateShares(holding.symbol, e.target.value)}
                      className="w-24 text-right"
                      min="1"
                    />
                    <span className="text-sm text-muted-foreground">acț.</span>
                  </div>
                  <div className="text-right min-w-[80px]">
                    <div className="text-green-600 font-bold">{dividendValue.toFixed(2)} RON</div>
                    <div className="text-xs text-muted-foreground">/an brut</div>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => removeHolding(holding.symbol)}>
                    <Trash2 className="w-4 h-4 text-red-500" />
                  </Button>
                </motion.div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// ============================================
// RESULTS DISPLAY
// ============================================
const ResultsDisplay = ({ results }) => {
  if (!results) return null;

  const { summary, holdings, projections, settings, tax_info } = results;
  const cass = summary.cass || {};

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200">
          <CardContent className="pt-4">
            <div className="text-sm text-muted-foreground">Investiție Totală</div>
            <div className="text-2xl font-bold text-blue-600">{summary.total_investment.toLocaleString('ro-RO', {minimumFractionDigits: 0})} RON</div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200">
          <CardContent className="pt-4">
            <div className="text-sm text-muted-foreground">Dividend Brut/An</div>
            <div className="text-2xl font-bold text-green-600">{summary.total_annual_dividend_gross?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</div>
            <div className="text-xs text-muted-foreground">Randament: {summary.portfolio_yield?.toFixed(2)}%</div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 dark:from-amber-900/20 dark:to-amber-800/20 border-amber-200">
          <CardContent className="pt-4">
            <div className="text-sm text-muted-foreground">Net după Impozit + CASS</div>
            <div className="text-2xl font-bold text-amber-600">{(summary.total_net_dupa_cass ?? summary.total_annual_dividend_net)?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</div>
            <div className="text-xs text-muted-foreground">~{((summary.total_net_dupa_cass ?? summary.total_annual_dividend_net) / 12).toFixed(0)} RON/lună</div>
          </CardContent>
        </Card>
        
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200">
          <CardContent className="pt-4">
            <div className="text-sm text-muted-foreground">Randament Portofoliu</div>
            <div className="text-2xl font-bold text-blue-600">{summary.portfolio_yield?.toFixed(2)}%</div>
            <div className="text-xs text-muted-foreground">brut/an</div>
          </CardContent>
        </Card>
      </div>

      {/* Fiscal breakdown box */}
      <Card className="border-orange-200 dark:border-orange-800/40">
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <Calculator className="w-4 h-4 text-orange-500" />
            Calcul Fiscal 2026
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-1.5">
              <div className="flex justify-between"><span>Dividend brut total:</span><span className="font-mono font-semibold">{summary.total_annual_dividend_gross?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</span></div>
              <div className="flex justify-between text-red-500"><span>Impozit 16% (reținut la sursă):</span><span className="font-mono">-{summary.impozit_dividende_16pct?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</span></div>
              <div className="flex justify-between font-semibold border-t pt-1"><span>Net după impozit:</span><span className="font-mono">{summary.total_annual_dividend_net?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</span></div>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between">
                <span>CASS ({cass.plafon || 'sub 6 SMB'}):</span>
                <span className={`font-mono ${cass.datorat ? 'text-red-500' : 'text-green-500'}`}>
                  {cass.datorat ? `-${cass.suma?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON` : '0 RON (sub prag)'}
                </span>
              </div>
              {cass.detaliu && <div className="text-xs text-muted-foreground">{cass.detaliu}</div>}
              <div className="flex justify-between font-bold text-green-600 border-t pt-1">
                <span>NET FINAL (după impozit + CASS):</span>
                <span className="font-mono">{(summary.total_net_dupa_cass ?? summary.total_annual_dividend_net)?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</span>
              </div>
            </div>
          </div>
          {tax_info && (
            <div className="mt-3 text-xs text-muted-foreground border-t pt-2">
              <p>📋 {tax_info.impozit_dividende}</p>
              <p>🏥 CASS: {tax_info.cass}</p>
              <p className="text-xs opacity-60">{tax_info.baza_legala}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Holdings Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Detalii pe Acțiuni
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Acțiune</TableHead>
                  <TableHead className="text-right">Acțiuni</TableHead>
                  <TableHead className="text-right">Investiție</TableHead>
                  <TableHead className="text-right">Div/Acț</TableHead>
                  <TableHead className="text-right">Dividend Brut</TableHead>
                  <TableHead className="text-right">Impozit 16%</TableHead>
                  <TableHead className="text-right">Dividend NET</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {holdings.map((h) => (
                  <TableRow key={h.symbol}>
                    <TableCell>
                      <span className="font-bold">{h.symbol}</span>
                      <span className="text-xs text-muted-foreground ml-2">{h.name}</span>
                      {h.data_source && <span className="text-xs ml-1 text-blue-500">●</span>}
                    </TableCell>
                    <TableCell className="text-right font-mono">{h.shares.toLocaleString()}</TableCell>
                    <TableCell className="text-right font-mono">{h.investment_value?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono">{h.dividend_per_share} RON</TableCell>
                    <TableCell className="text-right font-mono">{h.annual_dividend_gross?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono text-red-500">-{h.tax_16_percent?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono font-bold text-green-600">{h.annual_dividend_net?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      {/* Projections */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5" />
            Proiecții pe {settings.years_projected} ani
            {settings.reinvest_dividends && (
              <Badge variant="secondary" className="ml-2">Cu reinvestire</Badge>
            )}
          </CardTitle>
          <CardDescription>
            Rata de creștere dividende: {settings.dividend_growth_rate}%/an • Impozit 16% + CASS incluse
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>An</TableHead>
                  <TableHead className="text-right">Dividend Brut</TableHead>
                  <TableHead className="text-right">Impozit 16%</TableHead>
                  <TableHead className="text-right">CASS</TableHead>
                  <TableHead className="text-right">NET Final</TableHead>
                  <TableHead className="text-right">Cumulat NET</TableHead>
                  <TableHead className="text-right">Yield/Cost</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {projections.map((p) => (
                  <TableRow key={p.year}>
                    <TableCell className="font-bold">{p.year}</TableCell>
                    <TableCell className="text-right font-mono">{p.gross_dividend?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono text-red-400">-{p.impozit_16pct?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono text-orange-400">{p.cass > 0 ? `-${p.cass?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON` : '—'}</TableCell>
                    <TableCell className="text-right font-mono font-bold text-green-600">{(p.net_final_dupa_cass ?? p.net_dividend)?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right font-mono text-blue-500">{p.cumulative_net?.toLocaleString('ro-RO', {minimumFractionDigits: 2})} RON</TableCell>
                    <TableCell className="text-right">
                      <Badge variant="outline">{p.yield_on_cost?.toFixed(2)}%</Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// SCORE BADGE COMPONENT
// ============================================
const ScoreBadge = ({ score, rating, size = 'md' }) => {
  const colors = {
    'Excelent': 'from-emerald-500 to-green-600 text-white',
    'Foarte Bun': 'from-blue-600 to-blue-500 text-white',
    'Bun': 'from-amber-400 to-yellow-500 text-black',
    'Mediu': 'from-orange-400 to-orange-500 text-white',
    'Slab': 'from-red-400 to-red-500 text-white',
  };

  const sizeClasses = size === 'lg'
    ? 'w-16 h-16 text-xl'
    : 'w-10 h-10 text-sm';

  return (
    <div className="flex flex-col items-center gap-0.5">
      <div className={`${sizeClasses} rounded-full bg-gradient-to-br ${colors[rating] || colors['Mediu']} flex items-center justify-center font-bold shadow-lg`}>
        {score}
      </div>
      <span className="text-[10px] font-medium text-muted-foreground">{rating}</span>
    </div>
  );
};

// ============================================
// DIVIDEND HISTORY TAB (PRO)
// ============================================
const DividendHistoryTab = ({ isPro }) => {
  const [rankings, setRankings] = useState([]);
  const [loadingRankings, setLoadingRankings] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  // Compare state
  const [compareSymbols, setCompareSymbols] = useState([]);
  const [compareData, setCompareData] = useState(null);
  const [loadingCompare, setLoadingCompare] = useState(false);

  useEffect(() => {
    if (!isPro) return;
    const fetchRankings = async () => {
      setLoadingRankings(true);
      try {
        const res = await fetch(`${API_URL}/api/bvb-dividends/rankings`);
        if (res.ok) {
          const data = await res.json();
          setRankings(data.rankings || []);
          // If cache is refreshing, poll every 5 seconds
          if (data.cache_refreshing && (!data.rankings || data.rankings.length === 0)) {
            setTimeout(fetchRankings, 5000);
          }
        }
      } catch (err) {
        console.error('Error fetching rankings:', err);
      } finally {
        setLoadingRankings(false);
      }
    };
    fetchRankings();
  }, [isPro]);

  const fetchAnalysis = async (symbol) => {
    setSelectedSymbol(symbol);
    setLoadingAnalysis(true);
    try {
      const res = await fetch(`${API_URL}/api/bvb-dividends/analysis/${symbol}`);
      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
      }
    } catch (err) {
      console.error('Error fetching analysis:', err);
      toast.error('Eroare la încărcarea analizei');
    } finally {
      setLoadingAnalysis(false);
    }
  };

  const toggleCompare = (symbol) => {
    setCompareSymbols(prev => {
      if (prev.includes(symbol)) return prev.filter(s => s !== symbol);
      if (prev.length >= 4) { toast.error('Maxim 4 acțiuni pentru comparație'); return prev; }
      return [...prev, symbol];
    });
  };

  const runCompare = async () => {
    if (compareSymbols.length < 2) { toast.error('Selectează minim 2 acțiuni'); return; }
    setLoadingCompare(true);
    try {
      const res = await fetch(`${API_URL}/api/bvb-dividends/compare?symbols=${compareSymbols.join(',')}`);
      if (res.ok) {
        const data = await res.json();
        setCompareData(data);
        setAnalysis(null);
        setSelectedSymbol(null);
      }
    } catch (err) {
      console.error('Error comparing:', err);
      toast.error('Eroare la comparație');
    } finally {
      setLoadingCompare(false);
    }
  };

  if (!isPro) {
    return (
      <Card className="border-amber-200">
        <CardContent className="py-16 text-center">
          <Lock className="w-12 h-12 mx-auto mb-4 text-amber-500 opacity-60" />
          <h3 className="text-xl font-bold mb-2">Istoric Dividende PRO</h3>
          <p className="text-muted-foreground mb-4 max-w-md mx-auto">
            Acces la analiza avansată: Dividend Score, CAGR, stabilitate, grafice pe ani și clasamentul complet BVB.
          </p>
          <Button onClick={() => window.location.href = '/pricing'} className="bg-gradient-to-r from-amber-500 to-orange-500">
            <Award className="w-4 h-4 mr-2" />
            Upgrade la PRO
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Analysis Panel */}
      <AnimatePresence>
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Card className="border-2 border-blue-200 bg-gradient-to-br from-slate-50 to-blue-50/30">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl flex items-center gap-2">
                      <History className="w-5 h-5 text-blue-600" />
                      {analysis.symbol} — {analysis.company}
                    </CardTitle>
                    <CardDescription>
                      {analysis.current_price} RON • {analysis.data_years} ani de date • Sursa: BVB.ro + EODHD
                    </CardDescription>
                  </div>
                  <ScoreBadge score={analysis.dividend_score.score} rating={analysis.dividend_score.rating} size="lg" />
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Metrics Grid */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="text-xs text-muted-foreground">Yield Actual</div>
                    <div className="text-lg font-bold text-green-600">{analysis.current_yield}%</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="text-xs text-muted-foreground">CAGR</div>
                    <div className={`text-lg font-bold ${analysis.metrics.cagr >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                      {analysis.metrics.cagr != null ? `${analysis.metrics.cagr}%` : 'N/A'}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="text-xs text-muted-foreground">Ani Consecutivi</div>
                    <div className="text-lg font-bold">{analysis.metrics.consecutive_years}</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="text-xs text-muted-foreground">Total Ani cu Div.</div>
                    <div className="text-lg font-bold">{analysis.metrics.total_paying_years}</div>
                  </div>
                  <div className="bg-white rounded-lg p-3 shadow-sm border">
                    <div className="text-xs text-muted-foreground">Consistență</div>
                    <div className={`text-lg font-bold ${analysis.metrics.consistency_cv < 50 ? 'text-green-600' : analysis.metrics.consistency_cv < 80 ? 'text-amber-500' : 'text-red-500'}`}>
                      {analysis.metrics.consistency_cv < 30 ? 'Stabil' : analysis.metrics.consistency_cv < 60 ? 'Moderat' : 'Variabil'}
                    </div>
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="bg-white rounded-lg p-4 shadow-sm border">
                  <h4 className="text-sm font-semibold mb-3 flex items-center gap-1.5">
                    <Shield className="w-4 h-4 text-blue-500" />
                    Dividend Score — Detalii
                  </h4>
                  <div className="grid grid-cols-3 gap-4">
                    {[
                      { label: 'Stabilitate', value: analysis.dividend_score.breakdown.stability, max: 40, color: 'bg-emerald-500' },
                      { label: 'Creștere', value: analysis.dividend_score.breakdown.growth, max: 30, color: 'bg-blue-500' },
                      { label: 'Randament', value: analysis.dividend_score.breakdown.yield_score, max: 30, color: 'bg-amber-500' },
                    ].map((item) => (
                      <div key={item.label}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-muted-foreground">{item.label}</span>
                          <span className="font-bold">{item.value}/{item.max}</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${item.color} rounded-full transition-all`}
                            style={{ width: `${(item.value / item.max) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Yearly Dividend Chart */}
                {analysis.yearly_dividends.length > 0 && (
                  <div className="bg-white rounded-lg p-4 shadow-sm border">
                    <h4 className="text-sm font-semibold mb-3">Dividend per An (RON/acțiune)</h4>
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={analysis.yearly_dividends} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <RechartsTooltip
                          formatter={(value) => [`${Number(value).toFixed(4)} RON`, 'Dividend']}
                          contentStyle={{ borderRadius: '8px', fontSize: '13px' }}
                        />
                        <Bar dataKey="dividend" radius={[4, 4, 0, 0]}>
                          {analysis.yearly_dividends.map((entry, idx) => (
                            <Cell key={idx} fill={idx === analysis.yearly_dividends.length - 1 ? '#10b981' : '#3b82f6'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Payment History Table */}
                <details className="bg-white rounded-lg shadow-sm border">
                  <summary className="px-4 py-3 cursor-pointer text-sm font-semibold hover:bg-gray-50">
                    Toate plățile ({analysis.payments.length})
                  </summary>
                  <div className="px-4 pb-3 overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Data</TableHead>
                          <TableHead className="text-right">Dividend</TableHead>
                          <TableHead className="text-right">Sursă</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {analysis.payments.map((p, idx) => (
                          <TableRow key={idx}>
                            <TableCell className="font-mono text-sm">{p.date}</TableCell>
                            <TableCell className="text-right font-mono font-semibold text-green-600">{p.dividend.toFixed(4)} RON</TableCell>
                            <TableCell className="text-right text-xs text-muted-foreground">{p.source}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </details>

                <Button variant="ghost" size="sm" onClick={() => { setAnalysis(null); setSelectedSymbol(null); }}>
                  Închide analiza
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Comparison Panel */}
      <AnimatePresence>
        {compareData && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Card className="border-2 border-blue-200 bg-gradient-to-br from-slate-50 to-blue-50/30">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      Comparație Dividende — {compareData.symbols.join(' vs ')}
                    </CardTitle>
                    <CardDescription>Dividend per an (RON/acțiune) • Sursa: BVB.ro + EODHD</CardDescription>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => setCompareData(null)}>Închide</Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {/* Stocks Summary Cards */}
                <div className={`grid gap-3 ${compareData.symbols.length <= 2 ? 'grid-cols-2' : compareData.symbols.length === 3 ? 'grid-cols-3' : 'grid-cols-4'}`}>
                  {compareData.symbols.map((sym, idx) => {
                    const s = compareData.stocks[sym];
                    const colors = ['bg-blue-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500'];
                    return (
                      <div key={sym} className="bg-white rounded-lg p-3 shadow-sm border">
                        <div className="flex items-center gap-2 mb-2">
                          <div className={`w-3 h-3 rounded-full ${colors[idx]}`} />
                          <span className="font-bold">{sym}</span>
                          <ScoreBadge score={s.dividend_score.score} rating={s.dividend_score.rating} />
                        </div>
                        <p className="text-xs text-muted-foreground truncate">{s.company}</p>
                        <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                          <div><span className="text-muted-foreground">Yield:</span> <span className="font-bold text-green-600">{s.current_yield}%</span></div>
                          <div><span className="text-muted-foreground">CAGR:</span> <span className={`font-bold ${s.cagr >= 0 ? 'text-green-600' : 'text-red-500'}`}>{s.cagr != null ? `${s.cagr}%` : '—'}</span></div>
                          <div><span className="text-muted-foreground">Consec.:</span> <span className="font-bold">{s.consecutive_years} ani</span></div>
                          <div><span className="text-muted-foreground">Preț:</span> <span className="font-bold">{s.price} RON</span></div>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Grouped Bar Chart */}
                <div className="bg-white rounded-lg p-4 shadow-sm border" data-testid="compare-chart">
                  <h4 className="text-sm font-semibold mb-3">Dividend per An (RON/acțiune)</h4>
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={compareData.chart_data} margin={{ top: 5, right: 10, left: 10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="year" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <RechartsTooltip
                        formatter={(value, name) => [`${Number(value).toFixed(4)} RON`, name]}
                        contentStyle={{ borderRadius: '8px', fontSize: '13px' }}
                      />
                      {compareData.symbols.map((sym, idx) => {
                        const fills = ['#3b82f6', '#10b981', '#f59e0b', '#f43f5e'];
                        return <Bar key={sym} dataKey={sym} fill={fills[idx]} radius={[3, 3, 0, 0]} />;
                      })}
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Year-by-Year Table */}
                <details className="bg-white rounded-lg shadow-sm border">
                  <summary className="px-4 py-3 cursor-pointer text-sm font-semibold hover:bg-gray-50">
                    Tabel comparativ pe ani ({compareData.years.length} ani)
                  </summary>
                  <div className="px-4 pb-3 overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>An</TableHead>
                          {compareData.symbols.map(sym => (
                            <TableHead key={sym} className="text-right">{sym}</TableHead>
                          ))}
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {compareData.chart_data.map(row => (
                          <TableRow key={row.year}>
                            <TableCell className="font-bold">{row.year}</TableCell>
                            {compareData.symbols.map(sym => (
                              <TableCell key={sym} className="text-right font-mono">
                                {row[sym] > 0 ? `${row[sym].toFixed(4)} RON` : '—'}
                              </TableCell>
                            ))}
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </details>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Compare Selection Bar */}
      {compareSymbols.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky top-20 z-10"
        >
          <Card className="bg-blue-50 border-blue-200 shadow-lg">
            <CardContent className="py-3 flex items-center justify-between">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium text-blue-700">Compară:</span>
                {compareSymbols.map(sym => (
                  <Badge key={sym} variant="secondary" className="bg-blue-100 text-blue-700 cursor-pointer" onClick={() => toggleCompare(sym)}>
                    {sym} ✕
                  </Badge>
                ))}
                <span className="text-xs text-muted-foreground">({compareSymbols.length}/4)</span>
              </div>
              <div className="flex gap-2">
                <Button size="sm" variant="ghost" onClick={() => { setCompareSymbols([]); setCompareData(null); }}>Anulează</Button>
                <Button
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-700"
                  onClick={runCompare}
                  disabled={compareSymbols.length < 2 || loadingCompare}
                  data-testid="compare-btn"
                >
                  {loadingCompare ? <RefreshCw className="w-4 h-4 animate-spin mr-1" /> : <BarChart3 className="w-4 h-4 mr-1" />}
                  Compară ({compareSymbols.length})
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Rankings Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2" data-testid="dividend-history-title">
            <Award className="w-5 h-5 text-amber-500" />
            Clasament Dividend Score BVB
          </CardTitle>
          <CardDescription>
            Scor calculat din: Stabilitate (40%) + Creștere (30%) + Randament (30%) • Sursa: BVB.ro + EODHD
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingRankings ? (
            <div className="text-center py-8">
              <RefreshCw className="w-8 h-8 mx-auto animate-spin text-muted-foreground" />
              <p className="text-sm text-muted-foreground mt-2">Se calculează scorurile...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-10">#</TableHead>
                    <TableHead className="w-10">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger><BarChart3 className="w-4 h-4 text-blue-500" /></TooltipTrigger>
                          <TooltipContent>Selectează 2-4 acțiuni pentru comparație</TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </TableHead>
                    <TableHead>Acțiune</TableHead>
                    <TableHead className="text-center">Score</TableHead>
                    <TableHead className="text-right">Yield</TableHead>
                    <TableHead className="text-right">CAGR</TableHead>
                    <TableHead className="text-right">Ani Consec.</TableHead>
                    <TableHead className="text-center">Detalii</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rankings.map((r, idx) => (
                    <TableRow
                      key={r.symbol}
                      className={`hover:bg-muted/50 ${selectedSymbol === r.symbol ? 'bg-blue-50' : ''} ${compareSymbols.includes(r.symbol) ? 'bg-blue-50/50' : ''}`}
                      data-testid={`ranking-row-${r.symbol}`}
                    >
                      <TableCell className="font-bold text-muted-foreground">{idx + 1}</TableCell>
                      <TableCell>
                        <input
                          type="checkbox"
                          checked={compareSymbols.includes(r.symbol)}
                          onChange={() => toggleCompare(r.symbol)}
                          className="w-4 h-4 rounded border-blue-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                          data-testid={`compare-check-${r.symbol}`}
                        />
                      </TableCell>
                      <TableCell className="cursor-pointer" onClick={() => fetchAnalysis(r.symbol)}>
                        <div>
                          <span className="font-bold text-blue-600">{r.symbol}</span>
                          <p className="text-xs text-muted-foreground truncate max-w-[200px]">{r.company}</p>
                        </div>
                      </TableCell>
                      <TableCell className="text-center">
                        <ScoreBadge score={r.dividend_score} rating={r.rating} />
                      </TableCell>
                      <TableCell className="text-right">
                        <Badge variant={r.current_yield >= 5 ? 'default' : 'secondary'} className={r.current_yield >= 5 ? 'bg-green-600' : ''}>
                          {r.current_yield}%
                        </Badge>
                      </TableCell>
                      <TableCell className={`text-right font-mono ${r.cagr != null && r.cagr >= 0 ? 'text-green-600' : 'text-red-500'}`}>
                        {r.cagr != null ? `${r.cagr}%` : '—'}
                      </TableCell>
                      <TableCell className="text-right font-mono">{r.consecutive_years}</TableCell>
                      <TableCell className="text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => fetchAnalysis(r.symbol)}
                          disabled={loadingAnalysis && selectedSymbol === r.symbol}
                        >
                          {loadingAnalysis && selectedSymbol === r.symbol ? (
                            <RefreshCw className="w-4 h-4 animate-spin" />
                          ) : (
                            <ChevronRight className="w-4 h-4" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ============================================
// MAIN COMPONENT
// ============================================
export default function DividendCalculatorPage() {
  const { user } = useAuth();
  const isPro = user?.subscription_level === 'pro' || user?.subscription_level === 'premium';
  const [stocks, setStocks] = useState([]);
  const [portfolio, setPortfolio] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingStocks, setLoadingStocks] = useState(true);
  
  // Settings
  const [reinvest, setReinvest] = useState(false);
  const [yearsProjection, setYearsProjection] = useState(5);
  const [growthRate, setGrowthRate] = useState(5);

  // Fetch dividend stocks
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const res = await fetch(`${API_URL}/api/dividend-calculator/stocks`);
        if (res.ok) {
          const data = await res.json();
          setStocks(data.stocks || []);
        }
      } catch (err) {
        console.error('Error fetching stocks:', err);
        toast.error('Eroare la încărcarea acțiunilor');
      } finally {
        setLoadingStocks(false);
      }
    };
    fetchStocks();
  }, []);

  const addToPortfolio = (stock) => {
    if (portfolio.find(h => h.symbol === stock.symbol)) {
      toast.error('Acțiunea există deja în portofoliu');
      return;
    }
    setPortfolio([...portfolio, { symbol: stock.symbol, shares: 100 }]);
    toast.success(`${stock.symbol} adăugat în portofoliu`);
  };

  const calculateDividends = async () => {
    if (portfolio.length === 0) {
      toast.error('Adaugă cel puțin o acțiune în portofoliu');
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/dividend-calculator/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          holdings: portfolio,
          reinvest_dividends: reinvest,
          years_projection: yearsProjection,
          dividend_growth_rate: growthRate,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setResults(data);
        toast.success('Calcul finalizat!');
      }
    } catch (err) {
      console.error('Error calculating:', err);
      toast.error('Eroare la calcul');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SEO 
        title="Calculator Dividende BVB | FinRomania" 
        description="Calculează-ți veniturile din dividende pe BVB. Proiecții pe mai mulți ani cu reinvestire automată."
      />

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Coins className="w-8 h-8 text-amber-500" />
              Calculator Dividende BVB
            </h1>
            <p className="text-muted-foreground">
              Calculează-ți veniturile pasive din dividende • Date oficiale BVB.ro
            </p>
          </div>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="calculator" className="space-y-4">
          <TabsList>
            <TabsTrigger value="calculator">
              <Calculator className="w-4 h-4 mr-2" />
              Calculator
            </TabsTrigger>
            <TabsTrigger value="stocks">
              <BarChart3 className="w-4 h-4 mr-2" />
              Acțiuni cu Dividende
            </TabsTrigger>
            <TabsTrigger value="history" data-testid="tab-istoric-dividende">
              <History className="w-4 h-4 mr-2" />
              Istoric Dividende
              {!isPro && <Lock className="w-3 h-3 ml-1 opacity-50" />}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="calculator" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              {/* Portfolio Builder */}
              <div className="lg:col-span-2">
                <PortfolioBuilder 
                  portfolio={portfolio} 
                  setPortfolio={setPortfolio} 
                  stocks={stocks}
                />
              </div>

              {/* Settings & Calculate */}
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Setări Calcul</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <Label className="flex items-center gap-2">
                        <RefreshCw className="w-4 h-4" />
                        Reinvestire dividende
                      </Label>
                      <Switch checked={reinvest} onCheckedChange={setReinvest} />
                    </div>

                    <div className="space-y-2">
                      <Label>Ani proiecție: {yearsProjection}</Label>
                      <Slider
                        value={[yearsProjection]}
                        onValueChange={([v]) => setYearsProjection(v)}
                        min={1}
                        max={20}
                        step={1}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label>Creștere dividende/an: {growthRate}%</Label>
                      <Slider
                        value={[growthRate]}
                        onValueChange={([v]) => setGrowthRate(v)}
                        min={0}
                        max={15}
                        step={0.5}
                      />
                    </div>

                    <Button 
                      onClick={calculateDividends} 
                      disabled={loading || portfolio.length === 0}
                      className="w-full bg-gradient-to-r from-amber-500 to-orange-500"
                    >
                      {loading ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Calculator className="w-4 h-4 mr-2" />
                      )}
                      Calculează Dividendele
                    </Button>
                  </CardContent>
                </Card>

                <Card className="border-amber-200 bg-amber-50 dark:bg-amber-900/10">
                  <CardContent className="pt-4">
                    <div className="flex gap-2">
                      <Info className="w-5 h-5 text-amber-600 flex-shrink-0" />
                      <div className="text-sm text-amber-800 dark:text-amber-200">
                        <p className="font-medium">Impozit dividende: 16%</p>
                        <p className="text-xs mt-1">
                          În România, dividendele sunt impozitate cu 16% la sursă. 
                          Calculatorul include automat această deducere.
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Quick Add Buttons */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Adaugă Rapid</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {stocks.slice(0, 10).map(stock => (
                    <Button
                      key={stock.symbol}
                      variant="outline"
                      size="sm"
                      onClick={() => addToPortfolio(stock)}
                      disabled={portfolio.some(h => h.symbol === stock.symbol)}
                    >
                      {stock.symbol}
                      <Badge variant="secondary" className="ml-1 text-xs">
                        {stock.dividend_yield?.toFixed(1)}%
                      </Badge>
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Results */}
            <AnimatePresence>
              {results && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <ResultsDisplay results={results} />
                </motion.div>
              )}
            </AnimatePresence>
          </TabsContent>

          <TabsContent value="stocks">
            <Card>
              <CardHeader>
                <CardTitle>Acțiuni BVB cu Dividende</CardTitle>
                <CardDescription>
                  Sursa: BVB.ro (oficial) • Sortate după Dividend Yield
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loadingStocks ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-8 h-8 mx-auto animate-spin text-muted-foreground" />
                  </div>
                ) : (
                  <DividendStocksTable stocks={stocks} onAddToPortfolio={addToPortfolio} />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <DividendHistoryTab isPro={isPro} />
          </TabsContent>
        </Tabs>

        {/* Disclaimer */}
        <p className="text-xs text-center text-muted-foreground">
          Datele despre dividende provin de pe BVB.ro (sursa oficială). 
          Dividendele viitoare pot varia. Aceasta nu constituie sfat de investiții.
        </p>
      </div>
    </>
  );
}
