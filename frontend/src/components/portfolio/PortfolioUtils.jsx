import React from 'react';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import { fmt } from './shared';

export const PLCell = ({ value, percent, size = 'sm' }) => {
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

export const RSIBadge = ({ signal, rsi }) => {
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

export const FundCell = ({ value, suffix = '', good, bad }) => {
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
