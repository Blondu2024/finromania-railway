import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus, Trash2, Download, RefreshCw, Crown, Edit2,
  TrendingUp, TrendingDown, Minus, AlertCircle, Info
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../components/ui/dialog';
import {
  Tooltip, TooltipContent, TooltipProvider, TooltipTrigger,
} from '../components/ui/tooltip';
import { toast } from 'sonner';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// ─────────────────────────────────────────
// FORMATTERS
// ─────────────────────────────────────────
const fmt = (v, dec = 2) =>
  v != null ? Number(v).toLocaleString('ro-RO', { minimumFractionDigits: dec, maximumFractionDigits: dec }) : '—';

const fmtRON = (v) => v != null ? `${fmt(v)} RON` : '—';

const PLCell = ({ value, percent, size = 'sm' }) => {
  if (value == null) return <span className="text-muted-foreground">—</span>;
  const pos = value >= 0;
  const cls = pos ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400';
  return (
    <div className={`${cls} font-mono ${size === 'lg' ? 'text-lg font-bold' : 'text-sm'}`}>
      <span>{pos ? '+' : ''}{fmt(value)}</span>
      {percent != null && (
        <span className="ml-1.5 text-xs opacity-80">({pos ? '+' : ''}{fmt(percent)}%)</span>
      )}
    </div>
  );
};

const RSIBadge = ({ signal, rsi }) => {
  if (!signal) return <span className="text-muted-foreground text-xs">—</span>;
  const cfg = {
    SUPRAVÂNDUT: { cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', short: 'SV' },
    FAVORABIL: { cls: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-500', short: 'FAV' },
    NEUTRU: { cls: 'bg-muted text-muted-foreground', short: 'N' },
    RIDICAT: { cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', short: 'RID' },
    SUPRACUMPĂRAT: { cls: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', short: 'SC' },
  };
  const c = cfg[signal] || cfg.NEUTRU;
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger>
          <span className={`inline-flex items-center gap-1 text-xs px-1.5 py-0.5 rounded font-medium ${c.cls}`}>
            {c.short} {rsi != null ? <span className="opacity-70">{fmt(rsi, 1)}</span> : null}
          </span>
        </TooltipTrigger>
        <TooltipContent>
          <p className="font-medium">{signal}</p>
          {rsi != null && <p className="text-xs text-muted-foreground">RSI(14) = {fmt(rsi, 1)}</p>}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

// ─────────────────────────────────────────
// PRO PAYWALL
// ─────────────────────────────────────────
const ProPaywall = () => (
  <div className="flex flex-col items-center justify-center py-24 gap-6">
    <div className="w-20 h-20 rounded-full bg-amber-500/10 flex items-center justify-center">
      <Crown className="w-10 h-10 text-amber-500" />
    </div>
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-2">Portofoliu PRO</h2>
      <p className="text-muted-foreground max-w-md">
        Urmărire poziții BVB cu date live EODHD, P&L în timp real, RSI per acțiune, AI Advisor și dividende estimate.
      </p>
    </div>
    <Link to="/pricing">
      <Button size="lg" className="bg-amber-500 hover:bg-amber-600 text-white">
        <Crown className="w-4 h-4 mr-2" />
        Upgrade la PRO
      </Button>
    </Link>
  </div>
);

// ─────────────────────────────────────────
// METRIC CARD
// ─────────────────────────────────────────
const MetricCard = ({ label, value, sub, highlight, icon: Icon }) => (
  <Card className={`${highlight ? 'border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-500/5' : ''}`}>
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{label}</p>
        {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
      </div>
      <div className="text-2xl font-bold font-mono mt-1">{value}</div>
      {sub && <p className="text-xs text-muted-foreground mt-0.5">{sub}</p>}
    </CardContent>
  </Card>
);

// ─────────────────────────────────────────
// ADD / EDIT DIALOG
// ─────────────────────────────────────────
const PositionDialog = ({ open, onClose, onSave, editData, bvbSymbols, loading }) => {
  const [form, setForm] = useState({
    symbol: '', shares: '', purchase_price: '', purchase_date: '', notes: ''
  });
  const [err, setErr] = useState('');

  useEffect(() => {
    if (editData) {
      setForm({
        symbol: editData.symbol || '',
        shares: String(editData.shares || ''),
        purchase_price: String(editData.purchase_price || ''),
        purchase_date: editData.purchase_date || '',
        notes: editData.notes || '',
      });
    } else {
      setForm({ symbol: '', shares: '', purchase_price: '', purchase_date: '', notes: '' });
    }
    setErr('');
  }, [editData, open]);

  const handleSave = () => {
    if (!form.symbol.trim()) return setErr('Introdu simbolul acțiunii (ex: TLV)');
    if (!form.shares || isNaN(Number(form.shares)) || Number(form.shares) <= 0)
      return setErr('Cantitate invalidă');
    if (!form.purchase_price || isNaN(Number(form.purchase_price)) || Number(form.purchase_price) <= 0)
      return setErr('Preț de intrare invalid');
    setErr('');
    onSave({
      symbol: form.symbol.trim().toUpperCase(),
      shares: Number(form.shares),
      purchase_price: Number(form.purchase_price),
      purchase_date: form.purchase_date || undefined,
      notes: form.notes || undefined,
    });
  };

  const isEdit = !!editData;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? `Editează ${editData?.symbol}` : 'Adaugă Poziție Nouă'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          {!isEdit && (
            <div>
              <Label>Simbol BVB <span className="text-red-500">*</span></Label>
              <Input
                placeholder="ex: TLV, SNP, BRD, H2O"
                value={form.symbol}
                onChange={e => setForm(p => ({ ...p, symbol: e.target.value.toUpperCase() }))}
                data-testid="portfolio-symbol-input"
                className="font-mono uppercase"
              />
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Cantitate (nr. acțiuni) <span className="text-red-500">*</span></Label>
              <Input
                type="number"
                min="1"
                step="1"
                placeholder="ex: 500"
                value={form.shares}
                onChange={e => setForm(p => ({ ...p, shares: e.target.value }))}
                data-testid="portfolio-shares-input"
                className="font-mono"
              />
            </div>
            <div>
              <Label>Preț mediu intrare (RON) <span className="text-red-500">*</span></Label>
              <Input
                type="number"
                min="0.01"
                step="0.01"
                placeholder="ex: 22.50"
                value={form.purchase_price}
                onChange={e => setForm(p => ({ ...p, purchase_price: e.target.value }))}
                data-testid="portfolio-price-input"
                className="font-mono"
              />
            </div>
          </div>
          <div>
            <Label>Dată intrare</Label>
            <Input
              type="date"
              value={form.purchase_date}
              onChange={e => setForm(p => ({ ...p, purchase_date: e.target.value }))}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div>
            <Label>Note (opțional)</Label>
            <Textarea
              placeholder="ex: Cumpărat la anunț dividende..."
              value={form.notes}
              onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
              rows={2}
            />
          </div>
          {err && (
            <div className="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle className="w-4 h-4" />
              {err}
            </div>
          )}
        </div>
        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose}>Anulează</Button>
          <Button
            onClick={handleSave}
            disabled={loading}
            data-testid="portfolio-save-btn"
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
            {isEdit ? 'Salvează' : 'Adaugă'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ─────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────
export default function PortfolioBVBPage() {
  const { user, token } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Dialogs
  const [showAdd, setShowAdd] = useState(false);
  const [editPos, setEditPos] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const isPro = user?.subscription_level === 'pro' || user?.subscription_level === 'premium';

  const fetchPortfolio = useCallback(async (quiet = false) => {
    if (!token) return;
    if (!quiet) setLoading(true);
    else setRefreshing(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        setPortfolio(await r.json());
      } else if (r.status === 403) {
        setPortfolio(null);
      }
    } catch (e) {
      toast.error('Eroare la încărcare date');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    if (user && isPro) fetchPortfolio();
    else setLoading(false);
  }, [user, isPro, fetchPortfolio]);

  const handleAdd = async (data) => {
    setSaving(true);
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(data),
      });
      const res = await r.json();
      if (r.ok) {
        toast.success(res.message || `${data.symbol} adăugat`);
        setShowAdd(false);
        fetchPortfolio(true);
      } else {
        toast.error(res.detail || 'Eroare la adăugare');
      }
    } catch {
      toast.error('Eroare de conexiune');
    } finally {
      setSaving(false);
    }
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
      if (r.ok) {
        toast.success(res.message || `${editPos.symbol} actualizat`);
        setEditPos(null);
        fetchPortfolio(true);
      } else {
        toast.error(res.detail || 'Eroare la actualizare');
      }
    } catch {
      toast.error('Eroare de conexiune');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (symbol) => {
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/position/${symbol}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      });
      const res = await r.json();
      if (r.ok) {
        toast.success(res.message || `${symbol} eliminat`);
        fetchPortfolio(true);
      } else {
        toast.error(res.detail || 'Eroare');
      }
    } catch {
      toast.error('Eroare de conexiune');
    } finally {
      setDeleteConfirm(null);
    }
  };

  const handleExport = async () => {
    try {
      const r = await fetch(`${API_URL}/api/portfolio-bvb/export`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (r.ok) {
        const blob = await r.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `portofoliu_bvb_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch {
      toast.error('Eroare export');
    }
  };

  // ── RENDER ──

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
          <p className="text-sm text-muted-foreground mt-0.5">
            Date live EODHD · Doar acțiuni BVB · Exclusiv PRO
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchPortfolio(true)}
            disabled={refreshing}
            data-testid="portfolio-refresh-btn"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          </Button>
          {!isEmpty && (
            <Button variant="outline" size="sm" onClick={handleExport} data-testid="portfolio-export-btn">
              <Download className="w-4 h-4 mr-1.5" />
              CSV
            </Button>
          )}
          <Button
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
            onClick={() => setShowAdd(true)}
            data-testid="portfolio-add-btn"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Adaugă Poziție
          </Button>
        </div>
      </div>

      {/* ── SUMMARY METRICS ── */}
      {!isEmpty && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <MetricCard
            label="Valoare Totală"
            value={fmtRON(summary.total_value)}
            sub={`Investit: ${fmtRON(summary.total_invested)}`}
            highlight={plPos}
          />
          <MetricCard
            label="P&L Total"
            value={
              <PLCell
                value={summary.pl_ron}
                percent={summary.pl_percent}
                size="lg"
              />
            }
            sub={summary.pl_ron != null ? (plPos ? '▲ Profit' : '▼ Pierdere') : '—'}
          />
          <MetricCard
            label="P&L Astăzi"
            value={
              <PLCell
                value={summary.today_pl}
                size="lg"
              />
            }
            sub="Variație intraday"
            icon={todayPos ? TrendingUp : TrendingDown}
          />
          <MetricCard
            label="Poziții Active"
            value={summary.positions_count ?? '—'}
            sub="acțiuni BVB"
          />
        </div>
      )}

      {/* ── EMPTY STATE ── */}
      {isEmpty ? (
        <Card className="border-dashed">
          <CardContent className="py-16 text-center">
            <TrendingUp className="w-14 h-14 text-muted-foreground mx-auto mb-4 opacity-40" />
            <h3 className="text-lg font-semibold mb-2">Portofoliu gol</h3>
            <p className="text-muted-foreground text-sm mb-6 max-w-sm mx-auto">
              Adaugă prima ta poziție BVB. Introdu simbolul, cantitatea și prețul de intrare
              — restul se calculează automat cu date live.
            </p>
            <Button
              className="bg-blue-600 hover:bg-blue-700 text-white"
              onClick={() => setShowAdd(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Adaugă Prima Poziție
            </Button>
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
                  <th className="px-4 py-2.5"></th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {positions.map((pos) => {
                  const posPlus = (pos.pl_percent || 0) >= 0;
                  const todayPlus = (pos.price_change_percent || 0) >= 0;
                  return (
                    <tr
                      key={pos.symbol}
                      className="hover:bg-muted/30 transition-colors group"
                      data-testid={`portfolio-row-${pos.symbol}`}
                    >
                      {/* Simbol */}
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Link
                            to={`/stocks/bvb/${pos.symbol}`}
                            className="font-bold text-blue-600 hover:underline"
                          >
                            {pos.symbol}
                          </Link>
                          {pos.notes && (
                            <TooltipProvider>
                              <Tooltip>
                                <TooltipTrigger>
                                  <Info className="w-3 h-3 text-muted-foreground" />
                                </TooltipTrigger>
                                <TooltipContent>{pos.notes}</TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground truncate max-w-[140px]">
                          {pos.name}
                        </p>
                      </td>

                      {/* Cantitate */}
                      <td className="px-4 py-3 text-right font-mono">
                        {fmt(pos.shares, 0)}
                      </td>

                      {/* Preț intrare */}
                      <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                        {fmt(pos.purchase_price)} RON
                      </td>

                      {/* Preț curent */}
                      <td className="px-4 py-3 text-right font-mono font-medium">
                        {pos.current_price != null ? (
                          <span>{fmt(pos.current_price)} RON</span>
                        ) : (
                          <span className="text-muted-foreground text-xs">N/A</span>
                        )}
                      </td>

                      {/* Valoare totală */}
                      <td className="px-4 py-3 text-right font-mono font-medium">
                        {pos.current_value != null ? fmtRON(pos.current_value) : '—'}
                      </td>

                      {/* P&L total */}
                      <td className="px-4 py-3 text-right">
                        <PLCell value={pos.pl_ron} percent={pos.pl_percent} />
                      </td>

                      {/* Variație azi */}
                      <td className="px-4 py-3 text-right">
                        {pos.price_change_percent != null ? (
                          <span className={`font-mono text-xs ${todayPlus ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-500 dark:text-red-400'}`}>
                            {todayPlus ? '+' : ''}{fmt(pos.price_change_percent)}%
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">—</span>
                        )}
                      </td>

                      {/* RSI */}
                      <td className="px-4 py-3 text-center">
                        <RSIBadge signal={pos.rsi_signal} rsi={pos.rsi} />
                      </td>

                      {/* Acțiuni */}
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7"
                            onClick={() => setEditPos(pos)}
                            data-testid={`edit-${pos.symbol}`}
                          >
                            <Edit2 className="w-3.5 h-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-7 w-7 text-red-500 hover:text-red-600"
                            onClick={() => setDeleteConfirm(pos.symbol)}
                            data-testid={`delete-${pos.symbol}`}
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>

              {/* TOTAL ROW */}
              <tfoot>
                <tr className="border-t-2 bg-muted/20">
                  <td className="px-4 py-3 font-bold text-sm" colSpan={4}>TOTAL</td>
                  <td className="px-4 py-3 text-right font-bold font-mono">
                    {fmtRON(summary.total_value)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <PLCell value={summary.pl_ron} percent={summary.pl_percent} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <PLCell value={summary.today_pl} />
                  </td>
                  <td colSpan={2}></td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* DATA NOTE */}
          <div className="px-4 py-2.5 border-t bg-muted/10">
            <p className="text-xs text-muted-foreground">
              Date live EODHD · RSI(14) · Prețuri BVB cu delay 15min · Actualizare la refresh
            </p>
          </div>
        </Card>
      )}

      {/* ── DIALOGS ── */}
      <PositionDialog
        open={showAdd}
        onClose={() => setShowAdd(false)}
        onSave={handleAdd}
        editData={null}
        loading={saving}
      />

      <PositionDialog
        open={!!editPos}
        onClose={() => setEditPos(null)}
        onSave={handleUpdate}
        editData={editPos}
        loading={saving}
      />

      {/* Delete confirm */}
      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Elimini {deleteConfirm}?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Poziția va fi eliminată definitiv din portofoliu.
          </p>
          <DialogFooter className="gap-2 mt-4">
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>Anulează</Button>
            <Button
              variant="destructive"
              onClick={() => handleDelete(deleteConfirm)}
              data-testid="confirm-delete-btn"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Elimină
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
