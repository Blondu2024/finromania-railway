import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Check, X, Crown, Lock, Zap, Sparkles, ArrowRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const COMPARISON_FEATURES = [
  {
    categoryKey: "pricing.cat.fiscalCalc",
    free: { available: false, textKey: "pricing.free.fiscalCalc" },
    pro: { available: true, textKey: "pricing.pro.fiscalCalc" }
  },
  {
    categoryKey: "pricing.cat.aiQueries",
    free: { available: true, textKey: "pricing.free.aiQueries" },
    pro: { available: true, textKey: "pricing.pro.aiQueries" }
  },
  {
    categoryKey: "pricing.cat.delayBVB",
    free: { available: true, textKey: "pricing.free.delayBVB" },
    pro: { available: true, textKey: "pricing.pro.delayBVB" }
  },
  {
    categoryKey: "pricing.cat.delayGlobal",
    free: { available: true, textKey: "pricing.free.delayGlobal" },
    pro: { available: true, textKey: "pricing.pro.delayGlobal" }
  },
  {
    categoryKey: "pricing.cat.watchlist",
    free: { available: true, textKey: "pricing.free.watchlist" },
    pro: { available: true, textKey: "pricing.pro.watchlist" }
  },
  {
    categoryKey: "pricing.cat.priceAlerts",
    free: { available: true, textKey: "pricing.free.priceAlerts" },
    pro: { available: true, textKey: "pricing.pro.priceAlerts" }
  },
  {
    categoryKey: "pricing.cat.bvbStocks",
    free: { available: true, textKey: "pricing.free.bvbStocks" },
    pro: { available: true, textKey: "pricing.pro.bvbStocks" }
  },
  {
    categoryKey: "pricing.cat.accessLevels",
    free: { available: true, textKey: "pricing.free.accessLevels" },
    pro: { available: true, textKey: "pricing.pro.accessLevels" }
  },
  {
    categoryKey: "pricing.cat.technicalIndicators",
    free: { available: false, textKey: "pricing.free.technicalIndicators" },
    pro: { available: true, textKey: "pricing.pro.technicalIndicators" }
  },
  {
    categoryKey: "pricing.cat.fundamentalAnalysis",
    free: { available: false, textKey: "pricing.free.fundamentalAnalysis" },
    pro: { available: true, textKey: "pricing.pro.fundamentalAnalysis" }
  },
  {
    categoryKey: "pricing.cat.aiPortfolio",
    free: { available: false, textKey: "pricing.free.aiPortfolio" },
    pro: { available: true, textKey: "pricing.pro.aiPortfolio" }
  },
  {
    categoryKey: "pricing.cat.aiChartLines",
    free: { available: false, textKey: "pricing.free.aiChartLines" },
    pro: { available: true, textKey: "pricing.pro.aiChartLines" }
  },
  {
    categoryKey: "pricing.cat.globalMarkets",
    free: { available: true, textKey: "pricing.free.globalMarkets" },
    pro: { available: true, textKey: "pricing.pro.globalMarkets" }
  }
];

export default function FreeVsProComparison() {
  const { t } = useTranslation();

  return (
    <Card className="overflow-hidden">
      <CardHeader className="bg-gradient-to-r from-gray-100 to-gray-50 dark:from-zinc-900 dark:to-zinc-800 border-b">
        <CardTitle className="text-2xl text-center">{t('pricing.comparisonTitle')}</CardTitle>
        <p className="text-center text-muted-foreground">{t('pricing.comparisonSubtitle')}</p>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-gray-50 dark:bg-zinc-900">
                <th className="text-left p-4 font-semibold">{t('pricing.feature')}</th>
                <th className="text-center p-4 w-1/3">
                  <div className="flex flex-col items-center gap-1">
                    <Lock className="w-5 h-5 text-gray-500" />
                    <span className="font-semibold">{t('pricing.freeLabel')}</span>
                    <span className="text-xs text-muted-foreground">0 RON</span>
                  </div>
                </th>
                <th className="text-center p-4 w-1/3 bg-amber-500/10">
                  <div className="flex flex-col items-center gap-1">
                    <Crown className="w-5 h-5 text-amber-500" />
                    <span className="font-semibold text-amber-600">PRO</span>
                    <span className="text-xs text-amber-600">{t('pricing.proPrice')}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {COMPARISON_FEATURES.map((feature, idx) => (
                <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-zinc-900/50 transition-colors">
                  <td className="p-4 font-medium">{t(feature.categoryKey)}</td>

                  {/* FREE Column */}
                  <td className="text-center p-4">
                    {feature.free.available ? (
                      <div className="flex flex-col items-center gap-1">
                        <Check className="w-5 h-5 text-green-500" />
                        <span className="text-sm text-muted-foreground">{t(feature.free.textKey)}</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center gap-1">
                        <X className="w-5 h-5 text-red-400" />
                        <span className="text-sm text-red-400">{t(feature.free.textKey)}</span>
                      </div>
                    )}
                  </td>

                  {/* PRO Column */}
                  <td className="text-center p-4 bg-amber-500/5">
                    <div className="flex flex-col items-center gap-1">
                      <Sparkles className="w-5 h-5 text-amber-500" />
                      <span className="text-sm font-semibold text-amber-700 dark:text-amber-400">{t(feature.pro.textKey)}</span>
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
            <p className="font-semibold text-lg">{t('pricing.readyToUnlock')}</p>
            <p className="text-sm text-muted-foreground">{t('pricing.upgradeSubtext')}</p>
          </div>
          <Link to="/pricing">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-8">
              <Crown className="w-4 h-4 mr-2" />
              {t('pricing.viewPlans')}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
