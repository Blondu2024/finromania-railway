import React, { useState } from 'react';
import { Calculator, ArrowRight, Lock, Crown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Link } from 'react-router-dom';

export default function QuickCalculator({ user }) {
  const [venit, setVenit] = useState(100000);
  const [tipPiata, setTipPiata] = useState('bvb');
  
  // Calcul simplu pentru preview
  const calculateQuickPreview = () => {
    if (tipPiata === 'bvb') {
      // Asumăm 50% termen lung (1%), 50% termen scurt (3%)
      const impozitPF = venit * 0.02; // Media 2%
      const impozitSRL = venit * 0.09; // 1% micro + 8% dividend
      const economie = impozitSRL - impozitPF;
      
      return {
        impozitPF: Math.round(impozitPF),
        impozitSRL: Math.round(impozitSRL),
        economie: Math.round(economie)
      };
    } else {
      // Internațional: 10% PF vs 11% SRL
      const impozitPF = venit * 0.10;
      const impozitSRL = venit * 0.11;
      const economie = impozitSRL - impozitPF;
      
      return {
        impozitPF: Math.round(impozitPF),
        impozitSRL: Math.round(impozitSRL),
        economie: Math.round(economie)
      };
    }
  };
  
  const preview = calculateQuickPreview();
  const isPro = user && user.subscription_level === 'pro';
  
  return (
    <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-amber-200 dark:border-amber-800">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="w-6 h-6 text-amber-600" />
          Calculator Rapid Economie Fiscală
        </CardTitle>
        {!isPro && (
          <Badge className="bg-amber-500 text-white w-fit">
            <Lock className="w-3 h-3 mr-1" />
            Versiune FREE (limitată)
          </Badge>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label>Câștig Anual (RON)</Label>
            <Input 
              type="number"
              value={venit}
              onChange={(e) => setVenit(parseInt(e.target.value) || 0)}
              className="text-lg font-bold"
            />
          </div>
          <div>
            <Label>Piață</Label>
            <div className="flex gap-2">
              <Button 
                variant={tipPiata === 'bvb' ? 'default' : 'outline'}
                onClick={() => setTipPiata('bvb')}
                className="flex-1"
              >
                🇷🇴 BVB
              </Button>
              <Button 
                variant={tipPiata === 'international' ? 'default' : 'outline'}
                onClick={() => setTipPiata('international')}
                className="flex-1"
              >
                🌍 Global
              </Button>
            </div>
          </div>
        </div>

        {/* Quick Results */}
        <div className="bg-white dark:bg-zinc-900 rounded-lg p-4 space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Impozit ca PF:</span>
            <span className="font-bold">{preview.impozitPF.toLocaleString()} RON</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Impozit ca SRL:</span>
            <span className="font-bold">{preview.impozitSRL.toLocaleString()} RON</span>
          </div>
          <div className="border-t pt-3 flex justify-between items-center">
            <span className="font-semibold text-green-600">Economie ca PF:</span>
            <span className="text-2xl font-bold text-green-600">+{preview.economie.toLocaleString()} RON</span>
          </div>
        </div>

        {/* FREE: Upgrade Prompt */}
        {!isPro && (
          <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 rounded-lg p-4 border border-amber-500/30">
            <div className="flex items-start gap-3 mb-3">
              <Lock className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <p className="font-semibold text-amber-900 dark:text-amber-200">Deblochează Calculul Complet</p>
                <p className="text-sm text-amber-700 dark:text-amber-300">Cu PRO primești:</p>
                <ul className="text-xs text-amber-700 dark:text-amber-300 mt-2 space-y-1">
                  <li>✓ Calcul detaliat pentru PF, PFA, SRL Micro</li>
                  <li>✓ Analiză CASS precisă</li>
                  <li>✓ Scenariu BVB vs Internațional</li>
                  <li>✓ AI Fiscal Advisor pentru întrebări complexe</li>
                  <li>✓ Avantaje/Dezavantaje detaliate</li>
                </ul>
              </div>
            </div>
            <Link to="/pricing">
              <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600">
                <Crown className="w-4 h-4 mr-2" />
                Upgrade la PRO - 49 RON/lună
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        )}

        {/* PRO: Full Access CTA */}
        {isPro && (
          <Link to="/calculator-fiscal">
            <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600">
              <Calculator className="w-4 h-4 mr-2" />
              Calculează Detaliat (Versiunea Completă)
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        )}
      </CardContent>
    </Card>
  );
}
