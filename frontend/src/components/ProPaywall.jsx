import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Crown, Lock, Check, Sparkles, Calculator, Bot, TrendingUp, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const ProPaywall = ({
  feature,
  showFullPage = true,
  onClose = null
}) => {
  const { t } = useTranslation();
  const featureLabel = feature || t('pricing.thisFeature');

  const PRO_FEATURES = [
    { icon: Calculator, text: t('pricing.fullFiscalCalc') },
    { icon: Bot, text: t('pricing.unlimitedAI') },
    { icon: TrendingUp, text: "AI Market Advisor" },
    { icon: BarChart3, text: t('pricing.advancedTech') },
    { icon: Check, text: t('pricing.allLevelsNoQuiz') },
    { icon: Check, text: t('pricing.advancedPortfolio') },
  ];

  if (!showFullPage) {
    return (
      <Card className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/30">
        <CardContent className="p-6 text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-amber-500 to-orange-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lock className="w-8 h-8 text-white" />
          </div>
          <h3 className="text-xl font-bold mb-2">{t('pricing.proFeature')}</h3>
          <p className="text-muted-foreground mb-4">
            {featureLabel} — PRO
          </p>
          <Link to="/pricing">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600">
              <Crown className="w-4 h-4 mr-2" />
              {t('pricing.proFeature')} - 49 RON{t('pricing.plansAndPricing') ? '' : ''}/{t('common.back') ? 'mo' : 'mo'}
            </Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        <Card className="bg-gradient-to-br from-zinc-900 to-zinc-800 border-amber-500/30 overflow-hidden">
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 p-6 text-white text-center">
            <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Crown className="w-10 h-10" />
            </div>
            <h1 className="text-3xl font-bold mb-2">{t('pricing.proExclusive')}</h1>
            <p className="text-white/90">
              {featureLabel} — PRO
            </p>
          </div>

          <CardContent className="p-8">
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-amber-500" />
                PRO:
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {PRO_FEATURES.map((f, idx) => (
                  <div key={idx} className="flex items-center gap-3 bg-zinc-800/50 rounded-lg p-3">
                    <div className="p-2 bg-amber-500/20 rounded-lg">
                      <f.icon className="w-4 h-4 text-amber-500" />
                    </div>
                    <span className="text-sm text-gray-300">{f.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <Badge className="bg-amber-500 text-white mb-2">{t('pricing.recommended')}</Badge>
                  <h4 className="text-2xl font-bold text-white">PRO</h4>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-amber-500">49 <span className="text-lg">RON</span></p>
                  <p className="text-gray-500">{t('pricing.plansAndPricing') ? '/mo' : '/mo'}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-zinc-700">
                <div>
                  <h4 className="text-lg font-semibold text-white">PRO Annual</h4>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-white">490 <span className="text-sm">RON</span></p>
                  <p className="text-gray-500">/year</p>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <Link to="/pricing" className="block">
                <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12 text-lg">
                  <Crown className="w-5 h-5 mr-2" />
                  PRO
                </Button>
              </Link>

              <Link to="/" className="block">
                <Button variant="ghost" className="w-full text-gray-400 hover:text-white">
                  {t('common.back')}
                </Button>
              </Link>
            </div>

            <div className="mt-6 pt-6 border-t border-zinc-700 text-center">
              <p className="text-xs text-gray-500">
                ✓ {t('pricing.securePayment')}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ProPaywall;
