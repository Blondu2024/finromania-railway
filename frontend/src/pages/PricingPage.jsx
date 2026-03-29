import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Check, Crown, Sparkles, Zap, Shield, Star, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import EarlyAdopterBanner from '../components/EarlyAdopterBanner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FEATURE_KEYS = {
  free: [
    "pricing.featureFreeAi",
    "pricing.featureFreeBeginner",
    "pricing.featureFreeData",
    "pricing.featureFreeFearGreed",
    "pricing.featureFreeNews",
    "pricing.featureFreePortfolio"
  ],
  pro: [
    "pricing.featureProUnlimitedAi",
    "pricing.featureProAllLevels",
    "pricing.featureProNoQuiz",
    "pricing.featureProTaxCalc",
    "pricing.featureProFiscalAdvisor",
    "pricing.featureProTechIndicators",
    "pricing.featureProFundAnalysis",
    "pricing.featureProAiCharts",
    "pricing.featureProAdvPortfolio",
    "pricing.featureProPrioritySupport"
  ]
};

export default function PricingPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [loadingCheckout, setLoadingCheckout] = useState(false);

  useEffect(() => {
    if (user && token) {
      fetchSubscriptionStatus();
    }
  }, [user, token]);

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/subscriptions/status`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSubscriptionStatus(data);
      }
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const handleActivatePro = async (packageId) => {
    if (!user || !token) {
      window.location.href = '/login';
      return;
    }

    setLoadingCheckout(true);
    try {
      // Get current origin for Stripe redirects
      const originUrl = window.location.origin;
      
      // Create Stripe checkout session
      const response = await fetch(`${API_URL}/api/payments/checkout`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({
          package_id: packageId,
          origin_url: originUrl
        })
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to Stripe Checkout
        window.location.href = data.url;
      } else {
        const error = await response.json();
        alert(`Eroare: ${error.detail}`);
        setLoadingCheckout(false);
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      alert('Eroare la inițializarea plății');
      setLoadingCheckout(false);
    }
  };

  const isPro = subscriptionStatus?.subscription?.is_pro;

  return (
    <>
      <SEO 
        title="Prețuri & Abonamente | FinRomania"
        description="Alege planul potrivit pentru tine. PRO: 49 RON/lună sau 490 RON/an. Acces complet la toate funcțiile avansate."
      />
      
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-12">
        {/* Header */}
        <div className="text-center space-y-4">
          <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-1">
            💎 {t('pricing.plansAndPricing')}
          </Badge>
          <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold">
            {t('pricing.title')}
          </h1>
          <p className="text-base sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            {t('pricing.subtitle')}
          </p>
        </div>

        {/* Early Adopter Banner - înainte de a cere bani */}
        <EarlyAdopterBanner variant="full" />

        {/* Current Status */}
        {user && subscriptionStatus && (
          <Card className={isPro ? 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/30' : 'bg-gray-100 dark:bg-zinc-800'}>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                {isPro ? <Crown className="w-6 h-6 text-amber-500" /> : <Shield className="w-6 h-6 text-gray-500" />}
                <p className="text-lg font-semibold">
                  {t('pricing.currentPlan')} <strong>{isPro ? t('pricing.proPlan') : t('pricing.freePlan')}</strong>
                </p>
              </div>
              {isPro && subscriptionStatus.subscription.expires_at && (
                <p className="text-sm text-muted-foreground">
                  {t('pricing.expiresAt')} {new Date(subscriptionStatus.subscription.expires_at).toLocaleDateString('ro-RO')}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* FREE Plan */}
          <Card className="relative overflow-hidden">
            <CardHeader>
              <div className="flex items-center justify-between">
                <Shield className="w-10 h-10 text-gray-500" />
                <Badge variant="outline">{t('pricing.freePlan')}</Badge>
              </div>
              <CardTitle className="text-2xl">{t('pricing.freePlan')}</CardTitle>
              <CardDescription>{t('pricing.freeDescription')}</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">0 RON</span>
                <span className="text-muted-foreground">/lună</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {FEATURE_KEYS.free.map((key, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-500 mt-0.5" />
                    <span className="text-sm">{t(key)}</span>
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => !user && (window.location.href = '/login')}
                disabled={user}
              >
                {user ? t('pricing.currentPlanBtn') : t('pricing.startFree')}
              </Button>
            </CardContent>
          </Card>

          {/* PRO Plan */}
          <Card className="relative overflow-hidden border-2 border-amber-500 shadow-2xl">
            {/* Badge Recomandată */}
            <div className="absolute top-4 right-4">
              <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                <Star className="w-3 h-3 mr-1" />
                {t('pricing.recommended')}
              </Badge>
            </div>

            <CardHeader>
              <Crown className="w-10 h-10 text-amber-500" />
              <CardTitle className="text-2xl">{t('pricing.proPlan')}</CardTitle>
              <CardDescription>{t('pricing.proDescription')}</CardDescription>
              <div className="pt-4 space-y-2">
                <div>
                  <span className="text-4xl font-bold">{t('pricing.monthlyPrice')}</span>
                  <span className="text-muted-foreground">/lună</span>
                </div>
                <div className="text-sm text-muted-foreground">
                  sau <strong className="text-green-600">{t('pricing.annualPrice')}</strong> ({t('pricing.annualSavings')}!)
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-xs font-semibold text-amber-600 mb-2">{t('pricing.everythingInFree')}</p>
                {FEATURE_KEYS.pro.map((key, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <Sparkles className="w-5 h-5 text-amber-500 mt-0.5" />
                    <span className="text-sm font-medium">{t(key)}</span>
                  </div>
                ))}
              </div>
              
              {isPro ? (
                <Button 
                  className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
                  disabled
                >
                  <Check className="w-4 h-4 mr-2" />
                  {t('pricing.planActive')}
                </Button>
              ) : (
                <Button 
                  className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12 text-lg"
                  onClick={() => handleActivatePro('pro_monthly')}
                  disabled={loadingCheckout}
                >
                  {loadingCheckout ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      {t('pricing.processing')}
                    </span>
                  ) : (
                    <>
                      <Crown className="w-5 h-5 mr-2" />
                      {t('pricing.activatePro')}
                    </>
                  )}
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Feature Comparison Table */}
        <Card className="max-w-5xl mx-auto">
          <CardHeader>
            <CardTitle className="text-center">{t('pricing.detailedComparison')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">{t('pricing.feature')}</th>
                    <th className="text-center p-3">{t('pricing.freePlan')}</th>
                    <th className="text-center p-3 bg-amber-500/10">{t('pricing.proPlan')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr>
                    <td className="p-3">{t('pricing.tableAiQuestions')}</td>
                    <td className="text-center p-3">{t('pricing.tableFivePerDay')}</td>
                    <td className="text-center p-3 bg-amber-500/10 font-bold text-amber-600">{t('pricing.tableUnlimited')}</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableAccessLevels')}</td>
                    <td className="text-center p-3">{t('pricing.tableBeginner')}</td>
                    <td className="text-center p-3 bg-amber-500/10 font-bold text-amber-600">{t('pricing.tableAllLevels')}</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableTaxCalc')}</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableTechIndicators')}</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ RSI, MA, MACD</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableFundAnalysis')}</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">{t('pricing.tableComplete')}</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableAiCharts')}</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">{t('pricing.tableSupportResistance')}</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableAdvPortfolio')}</td>
                    <td className="text-center p-3">Basic</td>
                    <td className="text-center p-3 bg-amber-500/10">{t('pricing.tableWithAi')}</td>
                  </tr>
                  <tr>
                    <td className="p-3">{t('pricing.tableQuizLevels')}</td>
                    <td className="text-center p-3">{t('pricing.tableYesScore')}</td>
                    <td className="text-center p-3 bg-amber-500/10">{t('pricing.tableSkipDirect')}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQ */}
        <Card className="max-w-5xl mx-auto">
          <CardHeader>
            <CardTitle>{t('pricing.faqTitle')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-1">{t('pricing.faqCancelQ')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('pricing.faqCancelA')}
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t('pricing.faqPaymentQ')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('pricing.faqPaymentA')}
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t('pricing.faqSwitchQ')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('pricing.faqSwitchA')}
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">{t('pricing.faqTrialQ')}</h3>
              <p className="text-sm text-muted-foreground">
                {t('pricing.faqTrialA')}
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Trust Badges */}
        <div className="text-center">
          <div className="inline-flex items-center gap-6 p-4 bg-gray-100 dark:bg-zinc-800 rounded-lg">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="text-sm">{t('pricing.securePayment')}</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span className="text-sm">{t('pricing.realData')}</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-500" />
              <span className="text-sm">{t('pricing.instantActivation')}</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
