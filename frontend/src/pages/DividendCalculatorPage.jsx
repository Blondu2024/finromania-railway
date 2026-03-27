import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Coins, TrendingUp, Calendar, Calculator, Plus, Trash2, Download,
  PiggyBank, Percent, Clock, DollarSign, BarChart3, RefreshCw, Info
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
import { toast } from 'sonner';
import SEO from '../components/SEO';

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
        
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200">
          <CardContent className="pt-4">
            <div className="text-sm text-muted-foreground">Randament Portofoliu</div>
            <div className="text-2xl font-bold text-purple-600">{summary.portfolio_yield?.toFixed(2)}%</div>
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
// MAIN COMPONENT
// ============================================
export default function DividendCalculatorPage() {
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
