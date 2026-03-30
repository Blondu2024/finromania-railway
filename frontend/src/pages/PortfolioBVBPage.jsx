import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Plus, Trash2, Download, RefreshCw, Crown, Edit2, Upload,
  TrendingUp, TrendingDown, Info, BarChart3, Brain, Banknote, Newspaper,
  ExternalLink, ChevronDown, ChevronUp, HelpCircle, BookOpen,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../components/ui/tooltip';
import { toast } from 'sonner';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

// ── Portfolio sub-components ──────────────────────────────────────────────────
import { API_URL, fmt, fmtRON } from '../components/portfolio/shared';
import { PLCell, RSIBadge } from '../components/portfolio/PortfolioUtils';
import ProPaywall from '../components/portfolio/ProPaywall';
import MetricCard from '../components/portfolio/MetricCard';
import PositionDialog from '../components/portfolio/PositionDialog';
import AnalysisSection from '../components/portfolio/AnalysisSection';
import AIAdvisorSection from '../components/portfolio/AIAdvisorSection';
import PortfolioNewsSection from '../components/portfolio/PortfolioNewsSection';
import CSVImportDialog from '../components/portfolio/CSVImportDialog';
import StockLogo from '../components/StockLogo';

// ── Methodology collapsible section ─────────────────────────────────────────
function SourcesSection({ items }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-4 border rounded-lg bg-muted/20">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full px-4 py-2.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5" />
          {t('portfolio.sourcesMethodology')}
        </span>
        {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>
      {open && (
        <div className="px-4 pb-3 space-y-2 text-xs text-muted-foreground border-t">
          {items.map((item, i) => (
            <div key={i} className="pt-2">
              <p className="font-medium text-foreground">{item.label}</p>
              <p>{item.description}</p>
              {item.formula && (
                <code className="block mt-1 px-2 py-1 bg-muted rounded text-[11px] font-mono">{item.formula}</code>
              )}
              {item.link && (
                <a href={item.link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 mt-1 text-blue-600 hover:underline">
                  {t('portfolio.checkSource')} <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Info tooltip helper ─────────────────────────────────────────────────────
function InfoTip({ children }) {
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger className="cursor-help">
          <HelpCircle className="w-3 h-3 text-muted-foreground inline ml-0.5" />
        </TooltipTrigger>
        <TooltipContent className="max-w-xs text-xs">{children}</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

export default function PortfolioBVBPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();

  // Subscription check
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [subscriptionLoading, setSubscriptionLoading] = useState(true);

  // Portfolio data
  const [portfolio, setPortfolio] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [aiAdvice, setAiAdvice] = useState(null);
  const [dividends, setDividends] = useState(null);
  const [news, setNews] = useState(null);

  // Loading states
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);

  // Dialogs
  const [showAdd, setShowAdd] = useState(false);
  const [showCSVImport, setShowCSVImport] = useState(false);
  const [editPos, setEditPos] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // Active tab
  const [activeTab, setActiveTab] = useState('positions');

  // ── Subscription check ───────────────────────────────────────────────────
  useEffect(() => {
    if (!token) { setSubscriptionLoading(false); return; }
    fetch(`${API_URL}/api/subscriptions/status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(r => r.json())
      .then(data => { setSubscriptionStatus(data); setSubscriptionLoading(false); })
      .catch(() => setSubscriptionLoading(false));
  }, [token]);

  const isPro =
    subscriptionStatus?.subscription?.is_pro ||
    user?.subscription_level === 'pro' ||
    user?.subscription_level === 'premium';

  // ── Data fetchers ────────────────────────────────────────────────────────
  const fetchAnalysis = useCallback(async () => {
    if (!token) return;
    setLoadingAnalysis(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/analysis`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) setAnalysis(await r.json());
    } catch (e) {
      console.error('Analysis fetch error:', e);
    } finally {
      setLoadingAnalysis(false);
    }
  }, [token]);

  const fetchDividends = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/dividends`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) setDividends(await r.json());
    } catch (e) {
      console.error('Dividends fetch error:', e);
    }
  }, [token]);

  const fetchNews = useCallback(async () => {
    if (!token) return;
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/news`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) setNews(await r.json());
    } catch (e) {
      console.error('News fetch error:', e);
    }
  }, [token]);

  const fetchAIAdvice = useCallback(async () => {
    if (!token) return;
    setLoadingAI(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/ai-analysis`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) setAiAdvice(await r.json());
      else toast.error((await r.json()).detail || t('portfolio.errorAIAdvisor'));
    } catch { toast.error(t('portfolio.errorConnection')); }
    finally { setLoadingAI(false); }
  }, [token]);

  const fetchPortfolio = useCallback(async (quiet = false) => {
    if (!token) return;
    if (!quiet) setLoading(true);
    else setRefreshing(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        const data = await r.json();
        setPortfolio(data);
        // Fetch dividends with positions (needed for table)
        if ((data.positions || []).length > 0) {
          fetchDividends();
        }
      } else if (r.status === 403) {
        setPortfolio(null);
      }
    } catch { toast.error(t('portfolio.errorLoading')); }
    finally { setLoading(false); setRefreshing(false); }
  }, [token, fetchDividends]);

  useEffect(() => {
    if (user && isPro) fetchPortfolio();
    else setLoading(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, isPro]);

  // Lazy-load tab data on tab change
  useEffect(() => {
    if (!portfolio || (portfolio.positions || []).length === 0) return;
    if (activeTab === 'analysis' && !analysis && !loadingAnalysis) fetchAnalysis();
    if (activeTab === 'ai' && !aiAdvice && !loadingAI) fetchAIAdvice();
    if (activeTab === 'news' && !news) fetchNews();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, portfolio]);

  // ── CRUD handlers ────────────────────────────────────────────────────────
  const handleAdd = async (data) => {
    setSaving(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      });
      const res = await r.json();
      if (r.ok) { toast.success(res.message || `${data.symbol} ${t('portfolio.added')}`); setShowAdd(false); fetchPortfolio(true); }
      else toast.error(res.detail || t('portfolio.errorAdding'));
    } catch { toast.error(t('portfolio.errorConnection')); }
    finally { setSaving(false); }
  };

  const handleUpdate = async (data) => {
    if (!editPos) return;
    setSaving(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position/${editPos.symbol}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      });
      const res = await r.json();
      if (r.ok) { toast.success(res.message || `${editPos.symbol} ${t('portfolio.updated')}`); setEditPos(null); fetchPortfolio(true); }
      else toast.error(res.detail || t('portfolio.errorUpdating'));
    } catch { toast.error(t('portfolio.errorConnection')); }
    finally { setSaving(false); }
  };

  const handleDelete = async (symbol) => {
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const res = await r.json();
      if (r.ok) { toast.success(res.message || `${symbol} ${t('portfolio.removed')}`); fetchPortfolio(true); }
      else toast.error(res.detail || t('portfolio.errorGeneric'));
    } catch { toast.error(t('portfolio.errorConnection')); }
    finally { setDeleteConfirm(null); }
  };

  const handleExport = async () => {
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/export`, { headers: { Authorization: `Bearer ${token}` } });
      if (r.ok) {
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `portofoliu_bvb_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch { toast.error(t('portfolio.errorExport')); }
  };

  // ── Guards ───────────────────────────────────────────────────────────────
  if (!user) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center">
          <Crown className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">{t('portfolio.authRequired')}</h2>
          <Link to="/login"><Button className="bg-blue-600 hover:bg-blue-700 text-white">{t('common.login')}</Button></Link>
        </div>
      </div>
    );
  }
  if (subscriptionLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Crown className="w-10 h-10 text-amber-500 mx-auto mb-3 animate-pulse" />
        <p className="text-muted-foreground text-sm">{t('portfolio.checkingSubscription')}</p>
      </div>
    );
  }
  if (!isPro) return <ProPaywall />;
  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => <div key={i} className="h-24 rounded-xl bg-muted" />)}
        </div>
        <div className="h-96 rounded-xl bg-muted" />
      </div>
    );
  }

  const positions = portfolio?.positions || [];
  const summary = portfolio?.summary || {};
  const isEmpty = positions.length === 0;
  const plPos = (summary.pl_ron || 0) >= 0;
  const todayPos = (summary.today_pl || 0) >= 0;

  // Dividend map per symbol
  const divMap = {};
  (dividends?.dividends || []).forEach(d => { divMap[d.symbol] = d; });

  return (
    <>
      <SEO title={`${t('portfolio.title')} | FinRomania`} />

      {/* ── HEADER ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Crown className="w-6 h-6 text-amber-500" />
            {t('portfolio.title')}
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">{t('portfolio.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={() => fetchPortfolio(true)} disabled={refreshing}>
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          {!isEmpty && (
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="w-4 h-4 mr-1.5" /> Export
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => setShowCSVImport(true)}>
            <Upload className="w-4 h-4 mr-1.5" /> {t('portfolio.importCSV')}
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowAdd(true)}>
            <Plus className="w-4 h-4 mr-1.5" /> {t('portfolio.addManual')}
          </Button>
        </div>
      </div>

      {/* ── SUMMARY METRICS ── */}
      {!isEmpty && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
          <MetricCard label={t('portfolio.totalValue')} value={fmtRON(summary.total_value)} sub={`${t('portfolio.invested')}: ${fmtRON(summary.total_invested)}`} highlight={plPos} />
          <MetricCard
            label={t('portfolio.pnlTotal')}
            value={<PLCell value={summary.pl_ron} percent={summary.pl_percent} size="lg" />}
            sub={summary.pl_ron != null ? (plPos ? `▲ ${t('portfolio.profit')}` : `▼ ${t('portfolio.loss')}`) : '—'}
          />
          <MetricCard
            label={t('portfolio.pnlToday')}
            value={<PLCell value={summary.today_pl} size="lg" />}
            sub={t('portfolio.intradayChange')}
            icon={todayPos ? TrendingUp : TrendingDown}
          />
          <MetricCard label={t('portfolio.activePositions')} value={summary.positions_count ?? '—'} sub={t('portfolio.bvbStocks')} />
          {dividends?.total_annual_income > 0 && (
            <MetricCard
              label={t('portfolio.dividendIncome')}
              value={<span className="text-emerald-600 dark:text-emerald-400">{fmtRON(dividends.total_annual_income)}</span>}
              sub={t('portfolio.confirmedBVB')}
              icon={TrendingUp}
            />
          )}
        </div>
      )}

      {/* ── EMPTY STATE ── */}
      {isEmpty ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <TrendingUp className="w-14 h-14 text-muted-foreground mx-auto mb-4 opacity-40" />
            <h3 className="text-lg font-semibold mb-2">{t('portfolio.emptyTitle')}</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-sm mx-auto">
              {t('portfolio.emptyDesc')}
            </p>
            <div className="flex gap-3 justify-center">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowAdd(true)}>
                <Plus className="w-4 h-4 mr-2" /> {t('portfolio.addManual')}
              </Button>
              <Button variant="outline" onClick={() => setShowCSVImport(true)}>
                <Upload className="w-4 h-4 mr-2" /> {t('portfolio.importCSV')}
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* ── TAB NAVIGATION ── */
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="w-full justify-start mb-4 h-auto flex-wrap gap-1 bg-muted/50 p-1">
            <TabsTrigger value="positions" className="flex items-center gap-1.5 data-[state=active]:bg-background">
              <TrendingUp className="w-4 h-4" />
              <span className="hidden sm:inline">{t('portfolio.positions')}</span>
              <Badge variant="secondary" className="text-[10px] px-1.5 py-0">{positions.length}</Badge>
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-1.5 data-[state=active]:bg-background">
              <BarChart3 className="w-4 h-4" />
              <span className="hidden sm:inline">{t('portfolio.analysis')}</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center gap-1.5 data-[state=active]:bg-background">
              <Brain className="w-4 h-4" />
              <span className="hidden sm:inline">{t('portfolio.aiAdvisor')}</span>
            </TabsTrigger>
            <TabsTrigger value="dividends" className="flex items-center gap-1.5 data-[state=active]:bg-background">
              <Banknote className="w-4 h-4" />
              <span className="hidden sm:inline">{t('portfolio.dividendsTab')}</span>
              {dividends?.total_annual_income > 0 && (
                <Badge className="bg-emerald-500 text-white text-[10px] px-1.5 py-0">{fmtRON(dividends.total_annual_income)}{t('common.perYear')}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="news" className="flex items-center gap-1.5 data-[state=active]:bg-background">
              <Newspaper className="w-4 h-4" />
              <span className="hidden sm:inline">{t('portfolio.newsTab')}</span>
            </TabsTrigger>
          </TabsList>

          {/* ── TAB: POSITIONS ── */}
          <TabsContent value="positions">
            <Card>
              <CardHeader className="py-3 px-4 border-b">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  {t('portfolio.activePositions')} — {positions.length}
                </CardTitle>
              </CardHeader>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/40">
                      <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.symbolHeader')}</th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.qtyHeader')}</th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.entryPrice')}</th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                        {t('portfolio.currentPriceHeader')}
                        <InfoTip>{t('portfolio.currentPriceTooltip')}</InfoTip>
                      </th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                        {t('portfolio.valueHeader')}
                        <InfoTip>{t('portfolio.valueTooltip')}</InfoTip>
                      </th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                        P&L
                        <InfoTip>{t('portfolio.plTooltip')}</InfoTip>
                      </th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.todayHeader')}</th>
                      <th className="text-center px-4 py-2.5 font-medium text-muted-foreground">
                        RSI
                        <InfoTip>{t('portfolio.rsiTooltip')}</InfoTip>
                      </th>
                      <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                        Div Yield
                        <InfoTip>{t('portfolio.divYieldTooltip')}</InfoTip>
                      </th>
                      <th className="px-4 py-2.5"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {positions.map((pos) => {
                      const todayPlus = (pos.price_change_percent || 0) >= 0;
                      return (
                        <tr key={pos.symbol} className="hover:bg-muted/30 transition-colors group">
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <StockLogo symbol={pos.symbol} logoUrl={pos.logo_url} />
                              <Link to={`/stocks/bvb/${pos.symbol}`} className="font-bold text-blue-600 hover:underline">{pos.symbol}</Link>
                              {pos.notes && (
                                <TooltipProvider><Tooltip><TooltipTrigger><Info className="w-3 h-3 text-muted-foreground" /></TooltipTrigger><TooltipContent>{pos.notes}</TooltipContent></Tooltip></TooltipProvider>
                              )}
                            </div>
                            <p className="text-xs text-muted-foreground truncate max-w-[140px]">{pos.name}</p>
                          </td>
                          <td className="px-4 py-3 text-right font-mono">{fmt(pos.shares, 0)}</td>
                          <td className="px-4 py-3 text-right font-mono text-muted-foreground">{fmt(pos.purchase_price)} RON</td>
                          <td className="px-4 py-3 text-right font-mono font-medium">
                            {pos.current_price != null ? <span>{fmt(pos.current_price)} RON</span> : <span className="text-muted-foreground text-xs">N/A</span>}
                          </td>
                          <td className="px-4 py-3 text-right font-mono font-medium">{pos.current_value != null ? fmtRON(pos.current_value) : '—'}</td>
                          <td className="px-4 py-3 text-right"><PLCell value={pos.pl_ron} percent={pos.pl_percent} /></td>
                          <td className="px-4 py-3 text-right">
                            {pos.price_change_percent != null ? (
                              <span className={`font-mono text-xs ${todayPlus ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'}`}>
                                {todayPlus ? '+' : ''}{fmt(pos.price_change_percent)}%
                              </span>
                            ) : <span className="text-muted-foreground text-xs">—</span>}
                          </td>
                          <td className="px-4 py-3 text-center"><RSIBadge signal={pos.rsi_signal} rsi={pos.rsi} /></td>
                          <td className="px-4 py-3 text-right">
                            {divMap[pos.symbol]?.dividend_yield_pct != null ? (
                              <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                                {fmt(divMap[pos.symbol].dividend_yield_pct)}%
                              </span>
                            ) : <span className="text-muted-foreground text-xs">—</span>}
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEditPos(pos)}>
                                <Edit2 className="w-3.5 h-3.5" />
                              </Button>
                              <Button variant="ghost" size="icon" className="h-7 w-7 text-red-500 hover:text-red-600" onClick={() => setDeleteConfirm(pos.symbol)}>
                                <Trash2 className="w-3.5 h-3.5" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                  <tfoot>
                    <tr className="border-t-2 bg-muted/20">
                      <td className="px-4 py-3 font-bold text-sm" colSpan={4}>TOTAL</td>
                      <td className="px-4 py-3 text-right font-bold font-mono">{fmtRON(summary.total_value)}</td>
                      <td className="px-4 py-3 text-right"><PLCell value={summary.pl_ron} percent={summary.pl_percent} /></td>
                      <td className="px-4 py-3 text-right"><PLCell value={summary.today_pl} /></td>
                      <td></td>
                      <td className="px-4 py-3 text-right">
                        {dividends?.total_annual_income > 0 && (
                          <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                            {fmtRON(dividends.total_annual_income)}{t('common.perYear')}
                          </span>
                        )}
                      </td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
              <div className="px-4 py-2.5 border-t bg-muted/10">
                <p className="text-xs text-muted-foreground">{t('portfolio.liveDataNote')}</p>
              </div>
            </Card>

            <SourcesSection items={[
              {
                label: t('portfolio.bvbPricesSource'),
                description: t('portfolio.bvbPricesDesc'),
                link: 'https://bvb.ro/FinancialInstruments/Markets/Shares/SharesListForDownload',
              },
              {
                label: 'P&L (Profit/Loss)',
                description: t('portfolio.plDescription'),
                formula: t('portfolio.plFormula'),
              },
              {
                label: 'RSI (Relative Strength Index)',
                description: t('portfolio.rsiDescription'),
                formula: t('portfolio.rsiFormula'),
                link: 'https://www.investopedia.com/terms/r/rsi.asp',
              },
              {
                label: 'Dividend Yield',
                description: t('portfolio.divYieldDescription'),
                formula: t('portfolio.divYieldFormula'),
                link: 'https://bvb.ro/FinancialInstruments/CorporateActions/InfoDividend',
              },
            ]} />
          </TabsContent>

          {/* ── TAB: ANALYSIS ── */}
          <TabsContent value="analysis">
            <AnalysisSection analysis={analysis} loading={loadingAnalysis} />
            {!analysis && !loadingAnalysis && (
              <Card>
                <CardContent className="py-12 text-center">
                  <BarChart3 className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                  <p className="text-muted-foreground text-sm">{t('portfolio.loadingAnalysis')}</p>
                  <Button variant="outline" size="sm" className="mt-4" onClick={fetchAnalysis}>
                    <RefreshCw className="w-4 h-4 mr-2" /> {t('portfolio.loadAnalysis')}
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* ── TAB: AI ADVISOR ── */}
          <TabsContent value="ai">
            <AIAdvisorSection advice={aiAdvice} loading={loadingAI} onGenerate={fetchAIAdvice} />
          </TabsContent>

          {/* ── TAB: DIVIDENDS ── */}
          <TabsContent value="dividends">
            {dividends ? (
              <div className="space-y-4">
                {/* Dividend Summary */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-5 text-center">
                      <p className="text-sm text-muted-foreground mb-1">{t('portfolio.annualEstimatedIncome')}</p>
                      <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                        {fmtRON(dividends.total_annual_income || 0)}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">{t('portfolio.fromBVBDividends')}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-5 text-center">
                      <p className="text-sm text-muted-foreground mb-1">{t('portfolio.avgPortfolioYield')}</p>
                      <p className="text-2xl font-bold">
                        {dividends.dividends?.length > 0
                          ? fmt(dividends.dividends.filter(d => d.dividend_yield_pct).reduce((s, d) => s + d.dividend_yield_pct, 0) / dividends.dividends.filter(d => d.dividend_yield_pct).length)
                          : '0'}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">{t('portfolio.trailing12m')}</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-5 text-center">
                      <p className="text-sm text-muted-foreground mb-1">{t('portfolio.stocksWithDividends')}</p>
                      <p className="text-2xl font-bold">
                        {dividends.dividends?.filter(d => d.trailing_annual_dividend > 0).length || 0}
                        <span className="text-base text-muted-foreground"> / {positions.length}</span>
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">{t('portfolio.payDividends')}</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Dividend per Position Table */}
                <Card>
                  <CardHeader className="py-3 px-4 border-b">
                    <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                      {t('portfolio.dividendsPerPosition')}
                    </CardTitle>
                  </CardHeader>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b bg-muted/40">
                          <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.symbolHeader')}</th>
                          <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.sharesHeader')}</th>
                          <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.dividendPerShare')}</th>
                          <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Yield</th>
                          <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">{t('portfolio.annualIncome')}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {(dividends.dividends || [])
                          .sort((a, b) => (b.annual_income_ron || 0) - (a.annual_income_ron || 0))
                          .map(d => (
                          <tr key={d.symbol} className="hover:bg-muted/30">
                            <td className="px-4 py-3">
                              <div className="flex items-center gap-2">
                                <StockLogo symbol={d.symbol} logoUrl={d.logo_url} size="sm" />
                                <Link to={`/stocks/bvb/${d.symbol}`} className="font-bold text-blue-600 hover:underline">{d.symbol}</Link>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-right font-mono">{fmt(d.shares, 0)}</td>
                            <td className="px-4 py-3 text-right font-mono">
                              {d.trailing_annual_dividend > 0 ? `${fmt(d.trailing_annual_dividend, 4)} RON` : <span className="text-muted-foreground">—</span>}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {d.dividend_yield_pct > 0 ? (
                                <span className="font-mono text-emerald-600 dark:text-emerald-400 font-medium">{fmt(d.dividend_yield_pct)}%</span>
                              ) : <span className="text-muted-foreground">—</span>}
                            </td>
                            <td className="px-4 py-3 text-right">
                              {d.annual_income_ron > 0 ? (
                                <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{fmtRON(d.annual_income_ron)}</span>
                              ) : <span className="text-muted-foreground">—</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr className="border-t-2 bg-muted/20">
                          <td className="px-4 py-3 font-bold" colSpan={4}>{t('portfolio.totalAnnualIncome')}</td>
                          <td className="px-4 py-3 text-right font-bold font-mono text-emerald-600 dark:text-emerald-400">
                            {fmtRON(dividends.total_annual_income || 0)}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                  <div className="px-4 py-2.5 border-t bg-muted/10">
                    <p className="text-xs text-muted-foreground">
                      {t('portfolio.dividendSourceNote')} ·{' '}
                      <a href="https://bvb.ro/FinancialInstruments/CorporateActions/InfoDividend" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline inline-flex items-center gap-0.5">
                        {t('portfolio.checkOnBVB')} <ExternalLink className="w-3 h-3" />
                      </a>
                    </p>
                  </div>
                </Card>

                <SourcesSection items={[
                  {
                    label: t('portfolio.divSourceLabel'),
                    description: t('portfolio.divSourceDesc'),
                    link: 'https://bvb.ro/FinancialInstruments/CorporateActions/InfoDividend',
                  },
                  {
                    label: t('portfolio.divYieldLabel'),
                    description: t('portfolio.divYieldCalcDesc'),
                    formula: t('portfolio.divYieldFormula'),
                  },
                  {
                    label: t('portfolio.annualEstimatedIncome'),
                    description: t('portfolio.annualIncomeDesc'),
                    formula: t('portfolio.annualIncomeFormula'),
                  },
                  {
                    label: t('portfolio.divTaxLabel'),
                    description: t('portfolio.divTaxDesc'),
                    formula: t('portfolio.divTaxFormula'),
                  },
                ]} />
              </div>
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <Banknote className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                  <p className="text-muted-foreground text-sm">{t('portfolio.loadingDividends')}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* ── TAB: NEWS ── */}
          <TabsContent value="news">
            {news ? (
              <PortfolioNewsSection news={news} />
            ) : (
              <Card>
                <CardContent className="py-12 text-center">
                  <Newspaper className="w-10 h-10 text-muted-foreground mx-auto mb-3 opacity-40" />
                  <p className="text-muted-foreground text-sm">{t('portfolio.loadingNews')}</p>
                  <Button variant="outline" size="sm" className="mt-4" onClick={fetchNews}>
                    <RefreshCw className="w-4 h-4 mr-2" /> {t('portfolio.loadingNews')}
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      )}

      {/* ── DIALOGS ── */}
      <PositionDialog open={showAdd} onClose={() => setShowAdd(false)} onSave={handleAdd} editData={null} loading={saving} />
      <PositionDialog open={!!editPos} onClose={() => setEditPos(null)} onSave={handleUpdate} editData={editPos} loading={saving} />
      <CSVImportDialog open={showCSVImport} onClose={() => setShowCSVImport(false)} token={token} onImportComplete={() => fetchPortfolio(true)} />

      {/* Delete confirm */}
      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader><DialogTitle>{t('portfolio.deleteTitle')} {deleteConfirm}?</DialogTitle></DialogHeader>
          <p className="text-sm text-muted-foreground">{t('portfolio.deleteConfirm')}</p>
          <DialogFooter className="gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>{t('common.cancel')}</Button>
            <Button variant="destructive" onClick={() => handleDelete(deleteConfirm)}>
              <Trash2 className="w-4 h-4 mr-2" /> {t('common.delete')}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
