import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus, Trash2, Download, RefreshCw, Crown, Edit2, Upload,
  TrendingUp, TrendingDown, Info,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
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

// ─────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────
export default function PortfolioBVBPage() {
  const { user, token } = useAuth();

  // Subscription check (live — avoids stale context after PRO activation)
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

  const fetchDividendsAndNews = useCallback(async () => {
    if (!token) return;
    try {
      const [divRes, newsRes] = await Promise.all([
        fetch(`${API_URL}/api/portfolio-bvb/dividends`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_URL}/api/portfolio-bvb/news`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (divRes.ok) setDividends(await divRes.json());
      if (newsRes.ok) setNews(await newsRes.json());
    } catch (e) {
      console.error('Dividends/news fetch error:', e);
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
      else toast.error((await r.json()).detail || 'Eroare AI Advisor');
    } catch { toast.error('Eroare de conexiune'); }
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
        if ((data.positions || []).length > 0) {
          fetchAnalysis();
          fetchDividendsAndNews();
        }
      } else if (r.status === 403) {
        setPortfolio(null);
      }
    } catch { toast.error('Eroare la încărcare date'); }
    finally { setLoading(false); setRefreshing(false); }
  }, [token, fetchAnalysis, fetchDividendsAndNews]);

  useEffect(() => {
    if (user && isPro) fetchPortfolio();
    else setLoading(false);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, isPro]);

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
      if (r.ok) { toast.success(res.message || `${data.symbol} adăugat`); setShowAdd(false); fetchPortfolio(true); }
      else toast.error(res.detail || 'Eroare la adăugare');
    } catch { toast.error('Eroare de conexiune'); }
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
      if (r.ok) { toast.success(res.message || `${editPos.symbol} actualizat`); setEditPos(null); fetchPortfolio(true); }
      else toast.error(res.detail || 'Eroare la actualizare');
    } catch { toast.error('Eroare de conexiune'); }
    finally { setSaving(false); }
  };

  const handleDelete = async (symbol) => {
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const res = await r.json();
      if (r.ok) { toast.success(res.message || `${symbol} eliminat`); fetchPortfolio(true); }
      else toast.error(res.detail || 'Eroare');
    } catch { toast.error('Eroare de conexiune'); }
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
    } catch { toast.error('Eroare export'); }
  };

  // ── Guards ───────────────────────────────────────────────────────────────
  if (!user) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center">
          <Crown className="w-12 h-12 text-amber-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Autentificare necesară</h2>
          <Link to="/login">
            <Button className="bg-blue-600 hover:bg-blue-700 text-white">Conectare</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (subscriptionLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="text-center">
          <Crown className="w-10 h-10 text-amber-500 mx-auto mb-3 animate-pulse" />
          <p className="text-muted-foreground text-sm">Se verifică abonamentul...</p>
        </div>
      </div>
    );
  }

  if (!isPro) return <ProPaywall />;

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
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

  // Dividend map per symbol for fast lookup
  const divMap = {};
  (dividends?.dividends || []).forEach(d => { divMap[d.symbol] = d; });

  return (
    <>
      <SEO title="Portofoliu BVB PRO | FinRomania" />

      {/* ── HEADER ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Crown className="w-6 h-6 text-amber-500" />
            Portofoliu BVB PRO
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">Date live BVB · Exclusiv PRO</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={() => fetchPortfolio(true)} disabled={refreshing} data-testid="portfolio-refresh-btn">
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          {!isEmpty && (
            <Button variant="outline" size="sm" onClick={handleExport} data-testid="portfolio-export-btn">
              <Download className="w-4 h-4 mr-1.5" />
              Export CSV
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => setShowCSVImport(true)} data-testid="portfolio-import-btn">
            <Upload className="w-4 h-4 mr-1.5" />
            Import CSV
          </Button>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowAdd(true)} data-testid="portfolio-add-btn">
            <Plus className="w-4 h-4 mr-1.5" />
            Adaugă Poziție
          </Button>
        </div>
      </div>

      {/* ── SUMMARY METRICS ── */}
      {!isEmpty && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
          <MetricCard label="Valoare Totală" value={fmtRON(summary.total_value)} sub={`Investit: ${fmtRON(summary.total_invested)}`} highlight={plPos} />
          <MetricCard
            label="P&L Total"
            value={<PLCell value={summary.pl_ron} percent={summary.pl_percent} size="lg" />}
            sub={summary.pl_ron != null ? (plPos ? '▲ Profit' : '▼ Pierdere') : '—'}
          />
          <MetricCard
            label="P&L Astăzi"
            value={<PLCell value={summary.today_pl} size="lg" />}
            sub="Variație intraday"
            icon={todayPos ? TrendingUp : TrendingDown}
          />
          <MetricCard label="Poziții Active" value={summary.positions_count ?? '—'} sub="acțiuni BVB" />
          {dividends?.total_annual_income > 0 && (
            <MetricCard
              label="Income Dividende/An"
              value={<span className="text-emerald-600 dark:text-emerald-400">{fmtRON(dividends.total_annual_income)}</span>}
              sub="BVB.ro confirmat"
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
            <h3 className="text-lg font-semibold mb-2">Portofoliu gol</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-sm mx-auto">
              Adaugă poziții manual sau importă direct din XTB / Tradeville cu un CSV.
            </p>
            <div className="flex gap-3 justify-center">
              <Button className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowAdd(true)}>
                <Plus className="w-4 h-4 mr-2" /> Adaugă Manual
              </Button>
              <Button variant="outline" onClick={() => setShowCSVImport(true)}>
                <Upload className="w-4 h-4 mr-2" /> Import CSV
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* ── POSITIONS TABLE ── */
        <Card>
          <CardHeader className="py-3 px-4 border-b">
            <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
              Poziții Active — {positions.length}
            </CardTitle>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" data-testid="portfolio-table">
              <thead>
                <tr className="border-b bg-muted/40">
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">Simbol</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Cant.</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Preț Intrare</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Preț Curent</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Valoare</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">P&L</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Azi</th>
                  <th className="text-center px-4 py-2.5 font-medium text-muted-foreground">RSI</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider><Tooltip><TooltipTrigger className="cursor-help">Div Yield</TooltipTrigger><TooltipContent>Randament dividend trailing 12 luni (BVB.ro confirmat)</TooltipContent></Tooltip></TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider><Tooltip><TooltipTrigger className="cursor-help">Income/an</TooltipTrigger><TooltipContent>Venit estimat anual din dividende pentru cantitatea deținută</TooltipContent></Tooltip></TooltipProvider>
                  </th>
                  <th className="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {positions.map((pos) => {
                  const posPlus = (pos.pl_percent || 0) >= 0;
                  const todayPlus = (pos.price_change_percent || 0) >= 0;
                  return (
                    <tr key={pos.symbol} className="hover:bg-muted/30 transition-colors group" data-testid={`portfolio-row-${pos.symbol}`}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
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
                          <TooltipProvider><Tooltip><TooltipTrigger>
                            <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                              {fmt(divMap[pos.symbol].dividend_yield_pct)}%
                            </span>
                          </TooltipTrigger><TooltipContent>
                            <p className="text-xs">Dividend trailing: {fmt(divMap[pos.symbol].trailing_annual_dividend, 4)} RON</p>
                            <p className="text-xs text-emerald-400">BVB.ro confirmat</p>
                          </TooltipContent></Tooltip></TooltipProvider>
                        ) : <span className="text-muted-foreground text-xs">N/A</span>}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {divMap[pos.symbol]?.annual_income_ron != null ? (
                          <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400">{fmtRON(divMap[pos.symbol].annual_income_ron)}</span>
                        ) : <span className="text-muted-foreground text-xs">—</span>}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setEditPos(pos)} data-testid={`edit-${pos.symbol}`}>
                            <Edit2 className="w-3.5 h-3.5" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-7 w-7 text-red-500 hover:text-red-600" onClick={() => setDeleteConfirm(pos.symbol)} data-testid={`delete-${pos.symbol}`}>
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
                  <td colSpan={2}></td>
                  <td className="px-4 py-3 text-right">
                    {dividends?.total_annual_income > 0 && (
                      <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        {fmtRON(dividends.total_annual_income)}/an
                      </span>
                    )}
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>
          <div className="px-4 py-2.5 border-t bg-muted/10">
            <p className="text-xs text-muted-foreground">Date live BVB · RSI(14) · Prețuri cu delay 15min · Actualizare la refresh</p>
          </div>
        </Card>
      )}

      {/* ── ANALYSIS (Faza 2) ── */}
      {!isEmpty && <AnalysisSection analysis={analysis} loading={loadingAnalysis} />}

      {/* ── AI ADVISOR (Faza 3) ── */}
      {!isEmpty && <AIAdvisorSection advice={aiAdvice} loading={loadingAI} onGenerate={fetchAIAdvice} />}

      {/* ── NEWS (Faza 4) ── */}
      {!isEmpty && news && <PortfolioNewsSection news={news} />}

      {/* ── DIALOGS ── */}
      <PositionDialog open={showAdd} onClose={() => setShowAdd(false)} onSave={handleAdd} editData={null} loading={saving} />
      <PositionDialog open={!!editPos} onClose={() => setEditPos(null)} onSave={handleUpdate} editData={editPos} loading={saving} />

      <CSVImportDialog
        open={showCSVImport}
        onClose={() => setShowCSVImport(false)}
        token={token}
        onImportComplete={() => fetchPortfolio(true)}
      />

      {/* Delete confirm */}
      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Elimini {deleteConfirm}?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">Poziția va fi eliminată definitiv din portofoliu.</p>
          <DialogFooter className="gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>Anulează</Button>
            <Button variant="destructive" onClick={() => handleDelete(deleteConfirm)} data-testid="confirm-delete-btn">
              <Trash2 className="w-4 h-4 mr-2" /> Elimină
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
