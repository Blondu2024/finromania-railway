import React from 'react';
import { Card, CardContent } from '../ui/card';

export default function MetricCard({ label, value, sub, highlight, icon: Icon }) {
  return (
    <Card className={highlight ? 'border-emerald-500/30 bg-emerald-500/5 dark:bg-emerald-500/5' : ''}>
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
}
