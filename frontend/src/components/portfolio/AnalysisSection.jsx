import React from 'react';
import { BarChart3, PieChart as PieIcon } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip as ReTooltip, PieChart, Pie, Cell,
} from 'recharts';
import { fmt, SECTOR_COLORS } from './shared';
import { FundCell } from './PortfolioUtils';

const EvolutionTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-background border rounded-lg px-3 py-2 text-sm shadow-lg">
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="font-bold font-mono">{fmt(payload[0].value)} RON</p>
    </div>
  );
};

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

export default function AnalysisSection({ analysis, loading }) {
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

  return (
    <div className="space-y-4 mt-4" data-testid="analysis-section">
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
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} stroke="currentColor" className="opacity-50" />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={v => `${(v / 1000).toFixed(0)}k`} stroke="currentColor" className="opacity-50" />
                  <ReTooltip content={<EvolutionTooltip />} />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
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
              <div className="flex flex-col sm:flex-row items-center gap-4">
                <div className="w-full sm:w-[60%] flex-shrink-0">
                  <ResponsiveContainer width="100%" height={180}>
                    <PieChart>
                      <Pie data={sector_allocation} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value">
                        {sector_allocation.map((_, i) => (
                          <Cell key={i} fill={SECTOR_COLORS[i % SECTOR_COLORS.length]} />
                        ))}
                      </Pie>
                      <ReTooltip content={<SectorTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex-1 space-y-1.5 min-w-0 w-full">
                  {sector_allocation.map((s, i) => (
                    <div key={s.sector} className="flex items-center gap-2 text-xs">
                      <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: SECTOR_COLORS[i % SECTOR_COLORS.length] }} />
                      <span className="truncate text-foreground">{s.sector}</span>
                      <span className="ml-auto font-mono text-muted-foreground flex-shrink-0">{s.percent}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Fundamentale per poziție */}
      {fundamentals.length > 0 && (
        <Card data-testid="fundamentals-table">
          <CardHeader className="py-3 px-4 border-b">
            <CardTitle className="text-sm font-medium">
              Fundamentale per Acțiune
              <span className="ml-2 text-xs font-normal text-muted-foreground">
                — date reale confirmate (N/A dacă lipsesc)
              </span>
            </CardTitle>
          </CardHeader>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/30">
                  <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">Simbol</th>
                  {[
                    ['P/E', 'Preț / Profit per acțiune (mai mic = mai ieftin)'],
                    ['ROE %', 'Return on Equity — rentabilitatea capitalului propriu'],
                    ['EPS (RON)', 'Earnings per Share — profit net per acțiune'],
                    ['D/E', 'Debt / Equity — gradul de îndatorare'],
                    ['P/B', 'Preț / Valoare contabilă'],
                  ].map(([label, tip]) => (
                    <th key={label} className="text-right px-4 py-2.5 font-medium text-muted-foreground">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger className="cursor-help">{label}</TooltipTrigger>
                          <TooltipContent>{tip}</TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </th>
                  ))}
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
                    <FundCell value={f.roe_percent} suffix="%" good={v => v > 15} bad={v => v < 0} />
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
}
