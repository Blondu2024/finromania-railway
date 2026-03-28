import React, { useState } from 'react';
import {
  Brain, Sparkles, RefreshCw, ChevronDown, ChevronUp,
  CheckCircle, TrendingUp, AlertTriangle, AlertCircle, ShieldCheck,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

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

export default function AIAdvisorSection({ advice, loading, onGenerate }) {
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
              {loading
                ? <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                : <Sparkles className="w-3.5 h-3.5 mr-1.5" />
              }
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

      {loading && (
        <CardContent className="py-10 text-center">
          <RefreshCw className="w-10 h-10 text-blue-500 mx-auto mb-3 animate-spin" />
          <p className="text-sm font-medium">Se analizează portofoliul...</p>
          <p className="text-xs text-muted-foreground mt-1">GPT-4o procesează datele de piață</p>
        </CardContent>
      )}

      {advice && !loading && expanded && (
        <CardContent className="p-4 space-y-4">
          {advice.portfolio_summary && (() => {
            const ps = advice.portfolio_summary;
            const sigCfg = GLOBAL_CFG[ps.overall_signal] || GLOBAL_CFG['HOLD'];
            const riskCfg = RISK_CFG[ps.risk_level] || RISK_CFG['MEDIU'];
            const RiskIcon = riskCfg.icon;
            return (
              <div className="p-4 rounded-xl border bg-muted/20 space-y-3" data-testid="ai-portfolio-summary">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Sumar Global</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${sigCfg.cls}`}>{sigCfg.label}</span>
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

          <div className="grid sm:grid-cols-2 gap-3" data-testid="ai-positions-list">
            {(advice.positions || []).map((p) => {
              const cfg = SIGNAL_CFG[p.signal] || SIGNAL_CFG['PĂSTREAZĂ'];
              const Icon = cfg.icon;
              return (
                <div key={p.symbol} className={`p-4 rounded-xl border ${cfg.cls}`} data-testid={`ai-pos-${p.symbol}`}>
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
                  {p.reason && <p className="text-xs leading-relaxed text-foreground/90">{p.reason}</p>}
                  {p.key_metric && (
                    <p className="text-xs text-muted-foreground mt-1.5 font-medium">↳ {p.key_metric}</p>
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
}
