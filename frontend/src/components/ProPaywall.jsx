import React from 'react';
import { Link } from 'react-router-dom';
import { Crown, Lock, Check, Sparkles, Calculator, Bot, TrendingUp, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const PRO_FEATURES = [
  { icon: Calculator, text: "Calculator Fiscal complet (BVB + Internațional)" },
  { icon: Bot, text: "AI Fiscal Advisor nelimitat" },
  { icon: TrendingUp, text: "AI Market Advisor cu date live" },
  { icon: BarChart3, text: "Indicatori tehnici avansați (RSI, MACD)" },
  { icon: Check, text: "Acces la toate nivelurile fără quiz" },
  { icon: Check, text: "Portofoliu avansat cu analiză fundamentală" },
];

const ProPaywall = ({ 
  feature = "această funcție",
  showFullPage = true,
  onClose = null 
}) => {
  if (!showFullPage) {
    // Compact version for inline use
    return (
      <Card className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/30">
        <CardContent className="p-6 text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold mb-2">Funcție PRO</h3>
          <p className="text-muted-foreground mb-4">
            {feature} este disponibilă doar pentru utilizatorii PRO.
          </p>
          <Link to="/pricing">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600">
              <Crown className="w-4 h-4 mr-2" />
              Activează PRO - 49 RON/lună
            </Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  // Full page paywall
  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-amber-500/30 overflow-hidden">
          {/* Header gradient */}
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 p-6 text-white text-center">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Crown className="w-10 h-10" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Funcție PRO Exclusivă</h1>
            <p className="text-white/90">
              {feature} este disponibilă doar pentru utilizatorii PRO
            </p>
          </div>

          <CardContent className="p-8">
            {/* Features list */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                Ce primești cu PRO:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {PRO_FEATURES.map((feature, idx) => (
                  <div key={idx} className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3">
                    <div className="p-2 bg-amber-500/20 rounded-lg">
                      <feature.icon className="w-4 h-4 text-amber-500" />
                    </div>
                    <span className="text-sm text-gray-300">{feature.text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing */}
            <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <Badge className="bg-amber-500 text-white mb-2">RECOMANDATĂ</Badge>
                  <h4 className="text-2xl font-bold text-white">PRO Lunar</h4>
                  <p className="text-gray-400">Acces complet la toate funcțiile</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-amber-500">49 <span className="text-lg">RON</span></p>
                  <p className="text-gray-500">/lună</p>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                <div>
                  <h4 className="text-lg font-semibold text-white">PRO Anual</h4>
                  <p className="text-green-400 text-sm">Economisești 2 luni!</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-white">490 <span className="text-sm">RON</span></p>
                  <p className="text-gray-500">/an</p>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="space-y-3">
              <Link to="/pricing" className="block">
                <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12 text-lg">
                  <Crown className="w-5 h-5 mr-2" />
                  Activează PRO Acum
                </Button>
              </Link>
              
              <Link to="/" className="block">
                <Button variant="ghost" className="w-full text-gray-400 hover:text-white">
                  Înapoi la pagina principală
                </Button>
              </Link>
            </div>

            {/* Trust badges */}
            <div className="mt-6 pt-6 border-t border-slate-700 text-center">
              <p className="text-xs text-gray-500">
                ✓ Anulare oricând &nbsp;•&nbsp; ✓ Plată securizată &nbsp;•&nbsp; ✓ Acces instant
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Free alternative */}
        <Card className="mt-4 bg-slate-800/50 border-slate-700">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Vrei să înveți gratuit?</p>
                <p className="text-sm text-gray-400">Școala de Trading este 100% gratuită</p>
              </div>
              <Link to="/educatie">
                <Button variant="outline" size="sm">
                  Vezi cursurile gratuite
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProPaywall;
