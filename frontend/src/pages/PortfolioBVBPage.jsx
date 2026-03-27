import React, { useState, useEffect, useCallback } from 'react';
import {
  Plus, Trash2, Download, RefreshCw, Crown, Edit2,
  TrendingUp, TrendingDown, AlertCircle, Info, BarChart3, PieChart as PieIcon,
  Brain, Sparkles, ShieldCheck, AlertTriangle, CheckCircle, ChevronDown, ChevronUp
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
import {
  ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ReTooltip,
  PieChart, Pie, Cell,
} from 'recharts';
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
        Urmărire poziții BVB cu date live, P&L în timp real, RSI per acțiune, AI Advisor și dividende estimate.
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
// FAZA 4: ȘTIRI PORTOFOLIU
// ─────────────────────────────────────────
const PortfolioNewsSection = ({ news }) => {
  const articles = news?.news || [];
  if (articles.length === 0) return null;

  return (
    <Card className="mt-4" data-testid="portfolio-news-section">
      <CardHeader className="py-3 px-4 border-b">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-500" />
          Știri Relevante — Portofoliul Tău
          <span className="text-xs font-normal text-muted-foreground">
            · filtrate după simbolurile deținute
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y">
          {articles.map((art, i) => (
            <a
              key={art.id || i}
              href={art.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex gap-3 p-3 hover:bg-muted/30 transition-colors"
              data-testid={`portfolio-news-${i}`}
            >
              {art.image_url && (
                <img
                  src={art.image_url}
                  alt=""
                  className="w-16 h-16 object-cover rounded flex-shrink-0"
                  loading="lazy"
                  onError={e => (e.target.style.display = 'none')}
                />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {(art.related_symbols || []).map(sym => (
                    <span key={sym} className="text-[10px] font-bold px-1.5 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded">
                      {sym}
                    </span>
                  ))}
                </div>
                <p className="font-medium text-sm line-clamp-2 leading-snug">
                  {art.title_ro || art.title}
                </p>
                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                  <span>{art.source?.name}</span>
                  <span>·</span>
                  <span>{new Date(art.published_at).toLocaleDateString('ro-RO')}</span>
                </div>
              </div>
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ─────────────────────────────────────────
// FAZA 3: AI ADVISOR SECTION
// ─────────────────────────────────────────

const SIGNAL_CFG = {
  'PĂSTREAZĂ': {
    icon: CheckCircle,
    cls: 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
    badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
    iconCls: 'text-blue-500',
  },
  'CUMPĂRĂ MAI MULT': {
    icon: TrendingUp,
    cls: 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800',
    badge: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300',
    iconCls: 'text-emerald-500',
  },
  'CONSIDERĂ VÂNZARE': {
    icon: AlertTriangle,
    cls: 'bg-amber-50 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800',
    badge: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
    iconCls: 'text-amber-500',
  },
};

const RISK_CFG = {
  'SCĂZUT': { cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400', icon: ShieldCheck },
  'MEDIU': { cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400', icon: AlertTriangle },
  'RIDICAT': { cls: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400', icon: AlertCircle },
};

const GLOBAL_CFG = {
  'HOLD': { label: 'MENȚINE', cls: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' },
  'BUY_MORE': { label: 'CUMPĂRĂ MAI MULT', cls: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' },
  'REDUCE': { label: 'REDUCE', cls: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' },
};

const AIAdvisorSection = ({ advice, loading, onGenerate }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <Card className="mt-4" data-testid="ai-advisor-section">
      <CardHeader className="py-3 px-4 border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Brain className="w-4 h-4 text-blue-500" />
            AI Advisor — Recomandări per Poziție
            <span className="text-xs font-normal text-muted-foreground">
              · GPT-4o · Date reale live · Cache 1h
            </span>
          </CardTitle>
          <div className="flex items-center gap-2">
            {advice && !loading && (
              <span className="text-xs text-muted-foreground">
                {advice.from_cache ? '📦 Din cache' : '✨ Proaspăt'} · {advice.generated_at?.slice(11, 16)} UTC
              </span>
            )}
            <Button
              size="sm"
              variant={advice ? 'outline' : 'default'}
              onClick={onGenerate}
              disabled={loading}
              className={advice ? '' : 'bg-blue-600 hover:bg-blue-700 text-white'}
              data-testid="ai-generate-btn"
            >
              {loading ? (
                <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              )}
              {loading ? 'Se analizează...' : advice ? 'Reîmprospătează' : 'Generează Analiză AI'}
            </Button>
            {advice && (
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setExpanded(e => !e)}>
                {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      {/* Empty state */}
      {!advice && !loading && (
        <CardContent className="py-10 text-center">
          <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-40" />
          <p className="text-sm text-muted-foreground mb-1">
            Analiză AI per fiecare poziție din portofoliu
          </p>
          <p className="text-xs text-muted-foreground">
            Bazată pe RSI, P/E, ROE, D/E, EPS și P&L — date reale live
          </p>
        </CardContent>
      )}

      {/* Loading */}
      {loading && (
        <CardContent className="py-10 text-center">
          <RefreshCw className="w-10 h-10 text-blue-500 mx-auto mb-3 animate-spin" />
          <p className="text-sm font-medium">Se analizează portofoliul...</p>
          <p className="text-xs text-muted-foreground mt-1">GPT-4o procesează datele de piață</p>
        </CardContent>
      )}

      {/* Results */}
      {advice && !loading && expanded && (
        <CardContent className="p-4 space-y-4">

          {/* Global summary */}
          {advice.portfolio_summary && (() => {
            const ps = advice.portfolio_summary;
            const sigCfg = GLOBAL_CFG[ps.overall_signal] || GLOBAL_CFG['HOLD'];
            const riskCfg = RISK_CFG[ps.risk_level] || RISK_CFG['MEDIU'];
            const RiskIcon = riskCfg.icon;

            return (
              <div className="p-4 rounded-xl border bg-muted/20 space-y-3" data-testid="ai-portfolio-summary">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Sumar Global</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${sigCfg.cls}`}>
                    {sigCfg.label}
                  </span>
                  <span className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full ${riskCfg.cls}`}>
                    <RiskIcon className="w-3 h-3" />
                    RISC {ps.risk_level}
                  </span>
                </div>
                {ps.global_recommendation && (
                  <p className="text-sm leading-relaxed">{ps.global_recommendation}</p>
                )}
                {ps.diversification_note && (
                  <p className="text-xs text-muted-foreground italic">{ps.diversification_note}</p>
                )}
              </div>
            );
          })()}

          {/* Per-position recommendations */}
          <div className="grid sm:grid-cols-2 gap-3" data-testid="ai-positions-list">
            {(advice.positions || []).map((p) => {
              const cfg = SIGNAL_CFG[p.signal] || SIGNAL_CFG['PĂSTREAZĂ'];
              const Icon = cfg.icon;
              return (
                <div
                  key={p.symbol}
                  className={`p-4 rounded-xl border ${cfg.cls}`}
                  data-testid={`ai-pos-${p.symbol}`}
                >
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-4 h-4 flex-shrink-0 ${cfg.iconCls}`} />
                      <span className="font-bold text-sm">{p.symbol}</span>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cfg.badge}`}>
                        {p.signal}
                      </span>
                      {p.confidence && (
                        <span className="text-xs text-muted-foreground">
                          {p.confidence === 'RIDICAT' ? '●●●' : p.confidence === 'MEDIU' ? '●●○' : '●○○'}
                        </span>
                      )}
                    </div>
                  </div>
                  {p.reason && (
                    <p className="text-xs leading-relaxed text-foreground/90">{p.reason}</p>
                  )}
                  {p.key_metric && (
                    <p className="text-xs text-muted-foreground mt-1.5 font-medium">
                      ↳ {p.key_metric}
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          <p className="text-xs text-muted-foreground text-center pt-1">
            ⚠️ Recomandările AI sunt generate automat și nu constituie sfaturi de investiții.
          </p>
        </CardContent>
      )}
    </Card>
  );
};

// ─────────────────────────────────────────
// SECTOR COLORS
// ─────────────────────────────────────────
const SECTOR_COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#f97316', '#84cc16', '#ec4899', '#6b7280',
];

// ─────────────────────────────────────────
// FAZA 2: ANALYSIS SECTION
// ─────────────────────────────────────────
const AnalysisSection = ({ analysis, loading }) => {
  if (loading) {
    return (
      <div className="grid lg:grid-cols-2 gap-4 mt-4">
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
        <div className="h-64 rounded-xl bg-muted animate-pulse" />
        <div className="h-40 rounded-xl bg-muted animate-pulse lg:col-span-2" />
      </div>
    );
  }

  if (!analysis) return null;

  const { sector_allocation = [], fundamentals = [], history = [] } = analysis;

  // Tooltip evoluție
  const EvolutionTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-background border rounded-lg px-3 py-2 text-sm shadow-lg">
        <p className="text-muted-foreground text-xs">{label}</p>
        <p className="font-bold font-mono">{fmt(payload[0].value)} RON</p>
      </div>
    );
  };

  // Tooltip sector
  const SectorTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null;
    const d = payload[0].payload;
    return (
      <div className="bg-background border rounded-lg px-3 py-2 text-sm shadow-lg">
        <p className="font-medium">{d.sector}</p>
        <p className="font-mono">{fmt(d.value)} RON</p>
        <p className="text-muted-foreground">{d.percent}%</p>
      </div>
    );
  };

  return (
    <div className="space-y-4 mt-4" data-testid="analysis-section">
      {/* ── Charts row ── */}
      <div className="grid lg:grid-cols-2 gap-4">

        {/* Evoluție portofoliu */}
        <Card>
          <CardHeader className="py-3 px-4 border-b">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-500" />
              Evoluție Valoare Portofoliu
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            {history.length < 2 ? (
              <div className="h-48 flex flex-col items-center justify-center text-muted-foreground text-sm">
                <BarChart3 className="w-8 h-8 mb-2 opacity-40" />
                <p>Date insuficiente pentru grafic</p>
                <p className="text-xs mt-1">Revino mâine pentru a vedea evoluția</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={history} margin={{ top: 4, right: 8, left: 8, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="opacity-10" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 10 }}
                    tickFormatter={d => d.slice(5)}
                    stroke="currentColor"
                    className="opacity-50"
                  />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    tickFormatter={v => `${(v / 1000).toFixed(0)}k`}
                    stroke="currentColor"
                    className="opacity-50"
                  />
                  <ReTooltip content={<EvolutionTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        {/* Alocare sector */}
        <Card>
          <CardHeader className="py-3 px-4 border-b">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-emerald-500" />
              Alocare per Sector
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4">
            {sector_allocation.length === 0 ? (
              <div className="h-48 flex items-center justify-center text-muted-foreground text-sm">
                Nu există date de sector
              </div>
            ) : (
              <div className="flex items-center gap-4">
                <ResponsiveContainer width="60%" height={180}>
                  <PieChart>
                    <Pie
                      data={sector_allocation}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {sector_allocation.map((_, i) => (
                        <Cell key={i} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />
                      ))}
                    </Pie>
                    <ReTooltip content={<SectorTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex-1 space-y-1.5 min-w-0">
                  {sector_allocation.map((s, i) => (
                    <div key={s.sector} className="flex items-center gap-2 text-xs">
                      <div
                        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                        style={{ backgroundColor: SECTOR_COLORS[i % SECTOR_COLORS.length] }}
                      />
                      <span className="truncate text-foreground">{s.sector}</span>
                      <span className="ml-auto font-mono text-muted-foreground flex-shrink-0">
                        {s.percent}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Fundamentale per poziție ── */}
      {fundamentals.length > 0 && (
        <Card data-testid="fundamentals-table">
          <CardHeader className="py-3 px-4 border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">
                Fundamentale per Acțiune
                <span className="ml-2 text-xs font-normal text-muted-foreground">
                  — date reale confirmate (N/A dacă lipsesc)
                </span>
              </CardTitle>
            </div>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/30">
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">Simbol</th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">P/E</TooltipTrigger>
                        <TooltipContent>Preț / Profit per acțiune (mai mic = mai ieftin)</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">ROE %</TooltipTrigger>
                        <TooltipContent>Return on Equity — rentabilitatea capitalului propriu</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">EPS (RON)</TooltipTrigger>
                        <TooltipContent>Earnings per Share — profit net per acțiune</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">D/E</TooltipTrigger>
                        <TooltipContent>Debt / Equity — gradul de îndatorare</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">P/B</TooltipTrigger>
                        <TooltipContent>Preț / Valoare contabilă</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {fundamentals.map((f) => (
                  <tr key={f.symbol} className="hover:bg-muted/20">
                    <td className="px-4 py-2.5 font-bold">
                      {f.symbol}
                      <p className="text-xs text-muted-foreground font-normal truncate max-w-[140px]">{f.name}</p>
                    </td>
                    <FundCell value={f.pe_ratio} good={v => v > 0 && v < 15} bad={v => v > 30} />
                    <FundCell
                      value={f.roe_percent}
                      suffix="%"
                      good={v => v > 15}
                      bad={v => v < 0}
                    />
                    <FundCell value={f.eps} good={v => v > 0} bad={v => v < 0} />
                    <FundCell value={f.debt_equity} bad={v => v > 3} />
                    <FundCell value={f.pb_ratio} good={v => v < 1.5} bad={v => v > 4} />
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-4 py-2 border-t bg-muted/10">
            <p className="text-xs text-muted-foreground">
              Sursa: date fundamentale confirmate · Verde = favorabil · Roșu = atenție · N/A = date indisponibile
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};

// Helper for fundamentals cells
const FundCell = ({ value, suffix = '', good, bad }) => {
  if (value == null) {
    return <td className="px-4 py-2.5 text-right text-muted-foreground text-xs">N/A</td>;
  }
  let cls = 'text-foreground';
  if (good && good(value)) cls = 'text-emerald-600 dark:text-emerald-400 font-medium';
  if (bad && bad(value)) cls = 'text-red-500 dark:text-red-400 font-medium';
  return (
    <td className={`px-4 py-2.5 text-right font-mono ${cls}`}>
      {fmt(value)}{suffix}
    </td>
  );
};

// ─────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────
export default function PortfolioBVBPage() {
  const { user, token } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [aiAdvice, setAiAdvice] = useState(null);
  const [dividends, setDividends] = useState(null);
  const [news, setNews] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [loadingAI, setLoadingAI] = useState(false);

  // Dialogs
  const [showAdd, setShowAdd] = useState(false);
  const [editPos, setEditPos] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const isPro = user?.subscription_level === 'pro' || user?.subscription_level === 'premium';

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
      if (r.ok) {
        setAiAdvice(await r.json());
      } else {
        const err = await r.json();
        toast.error(err.detail || 'Eroare AI Advisor');
      }
    } catch (e) {
      toast.error('Eroare de conexiune');
    } finally {
      setLoadingAI(false);
    }
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
    } catch (e) {
      toast.error('Eroare la încărcare date');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token, fetchAnalysis, fetchDividendsAndNews]);

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

  // Map dividende per simbol pentru accces rapid în tabel
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
          <p className="text-sm text-muted-foreground mt-0.5">
            Date live BVB · Exclusiv PRO
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
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
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
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">Div Yield</TooltipTrigger>
                        <TooltipContent>Randament dividend trailing 12 luni (BVB.ro confirmat)</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
                  <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger className="cursor-help">Income/an</TooltipTrigger>
                        <TooltipContent>Venit estimat anual din dividende pentru cantitatea deținută</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </th>
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

                      {/* Dividend Yield — BVB.ro confirmat */}
                      <td className="px-4 py-3 text-right">
                        {divMap[pos.symbol]?.dividend_yield_pct != null ? (
                          <TooltipProvider>
                            <Tooltip>
                              <TooltipTrigger>
                                <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400 font-medium">
                                  {fmt(divMap[pos.symbol].dividend_yield_pct)}%
                                </span>
                              </TooltipTrigger>
                              <TooltipContent>
                                <p className="text-xs">Dividend trailing: {fmt(divMap[pos.symbol].trailing_annual_dividend, 4)} RON</p>
                                <p className="text-xs text-emerald-400">BVB.ro confirmat</p>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        ) : (
                          <span className="text-muted-foreground text-xs">N/A</span>
                        )}
                      </td>

                      {/* Income anual estimat */}
                      <td className="px-4 py-3 text-right">
                        {divMap[pos.symbol]?.annual_income_ron != null ? (
                          <span className="font-mono text-xs text-emerald-600 dark:text-emerald-400">
                            {fmtRON(divMap[pos.symbol].annual_income_ron)}
                          </span>
                        ) : (
                          <span className="text-muted-foreground text-xs">—</span>
                        )}
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
                  <td className="px-4 py-3 text-right">
                    {dividends?.total_annual_income > 0 ? (
                      <span className="font-mono text-xs font-bold text-emerald-600 dark:text-emerald-400">
                        {fmtRON(dividends.total_annual_income)}/an
                      </span>
                    ) : null}
                  </td>
                  <td></td>
                </tr>
              </tfoot>
            </table>
          </div>

          {/* DATA NOTE */}
          <div className="px-4 py-2.5 border-t bg-muted/10">
            <p className="text-xs text-muted-foreground">
              Date live BVB · RSI(14) · Prețuri cu delay 15min · Actualizare la refresh
            </p>
          </div>
        </Card>
      )}

      {/* ── FAZA 2: ANALIZĂ ── */}
      {!isEmpty && (
        <AnalysisSection analysis={analysis} loading={loadingAnalysis} />
      )}

      {/* ── FAZA 3: AI ADVISOR ── */}
      {!isEmpty && (
        <AIAdvisorSection
          advice={aiAdvice}
          loading={loadingAI}
          onGenerate={fetchAIAdvice}
        />
      )}

      {/* ── FAZA 4: ȘTIRI PORTOFOLIU ── */}
      {!isEmpty && news && (
        <PortfolioNewsSection news={news} />
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
