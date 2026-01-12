import React from 'react';
import { Link } from 'react-router-dom';
import { Check, X, Crown, Lock, Zap, Sparkles, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const COMPARISON_FEATURES = [
  {
    category: "Calculator Fiscal",
    free: { available: false, text: "Blocat" },
    pro: { available: true, text: "Acces Complet + AI Fiscal" }
  },
  {
    category: "AI Queries",
    free: { available: true, text: "5 întrebări/zi" },
    pro: { available: true, text: "NELIMITATE ∞" }
  },
  {
    category: "Acțiuni BVB",
    free: { available: true, text: "Doar BET (10 companii)" },
    pro: { available: true, text: "Toate (50+ companii)" }
  },
  {
    category: "Nivele Acces",
    free: { available: true, text: "Începător (+ quiz pentru mai mult)" },
    pro: { available: true, text: "Toate 3 DIRECT (fără quiz)" }
  },
  {
    category: "Indicatori Tehnici",
    free: { available: false, text: "Blocat" },
    pro: { available: true, text: "RSI, MA, MACD, Volume" }
  },
  {
    category: "Analiză Fundamentală",
    free: { available: false, text: "Blocat" },
    pro: { available: true, text: "P/E, P/B, ROE, Cash Flow" }
  },
  {
    category: "AI Portfolio Analysis",
    free: { available: false, text: "Blocat" },
    pro: { available: true, text: "Diversificare + Sugestii" }
  },
  {
    category: "AI Chart Lines",
    free: { available: false, text: "Blocat" },
    pro: { available: true, text: "Suport/Rezistență Automat" }
  },
  {
    category: "Global Markets",
    free: { available: true, text: "Vizualizare" },
    pro: { available: true, text: "Vizualizare + Analiză AI" }
  }
];

export default function FreeVsProComparison() {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-slate-100 to-slate-50 dark:from-slate-900 dark:to-slate-800 border-b">
        <CardTitle className="text-2xl text-center">Ce Primești cu Fiecare Plan?</CardTitle>
        <p className="text-center text-muted-foreground">Separare clară FREE vs PRO</p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-slate-50 dark:bg-slate-900">
                <th className="text-left p-4 font-semibold">Funcție</th>
                <th className="text-center p-4 w-1/3">
                  <div className="flex flex-col items-center gap-1">
                    <Lock className="w-5 h-5 text-gray-500" />
                    <span className="font-semibold">GRATUIT</span>
                    <span className="text-xs text-muted-foreground">0 RON</span>
                  </div>
                </th>
                <th className="text-center p-4 w-1/3 bg-amber-500/10">
                  <div className="flex flex-col items-center gap-1">
                    <Crown className="w-5 h-5 text-amber-500" />
                    <span className="font-semibold text-amber-600">PRO</span>
                    <span className="text-xs text-amber-600">49 RON/lună</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {COMPARISON_FEATURES.map((feature, idx) => (
                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-900/50 transition-colors">
                  <td className="p-4 font-medium">{feature.category}</td>
                  
                  {/* FREE Column */}
                  <td className="text-center p-4">
                    {feature.free.available ? (
                      <div className="flex flex-col items-center gap-1">
                        <Check className="w-5 h-5 text-green-500" />
                        <span className="text-sm text-muted-foreground">{feature.free.text}</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-1">
                        <X className="w-5 h-5 text-red-400" />
                        <span className="text-sm text-red-400">{feature.free.text}</span>
                      </div>
                    )}
                  </td>
                  
                  {/* PRO Column */}
                  <td className="text-center p-4 bg-amber-500/5">
                    <div className="flex flex-col items-center gap-1">
                      <Sparkles className="w-5 h-5 text-amber-500" />
                      <span className="text-sm font-semibold text-amber-700 dark:text-amber-400">{feature.pro.text}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* CTA Footer */}
        <div className="p-6 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-t flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-lg">Gata să deblochezi totul?</p>
            <p className="text-sm text-muted-foreground">Upgrade la PRO și economisește mii de RON</p>
          </div>
          <Link to="/pricing">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-8">
              <Crown className="w-4 h-4 mr-2" />
              Vezi Planuri PRO
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
