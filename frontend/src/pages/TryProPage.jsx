import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Crown, Check, X, Sparkles, Zap, ArrowRight, Lock, Shield, Clock, TrendingUp, Calculator, Brain, Target } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import FreeVsProComparison from '../components/FreeVsProComparison';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// WHY_PRO_CARDS and FAQ_ITEMS moved inside component for i18n access

export default function TryProPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  const WHY_PRO_CARDS = [
    { icon: Calculator, title: t('pricing.whyPro1Title'), description: t('pricing.whyPro1Desc'), gradient: "from-amber-500 to-orange-500" },
    { icon: Brain, title: t('pricing.whyPro2Title'), description: t('pricing.whyPro2Desc'), gradient: "from-blue-500 to-blue-500" },
    { icon: TrendingUp, title: t('pricing.whyPro3Title'), description: t('pricing.whyPro3Desc'), gradient: "from-green-500 to-emerald-500" },
    { icon: Target, title: t('pricing.whyPro4Title'), description: t('pricing.whyPro4Desc'), gradient: "from-blue-500 to-cyan-500" },
  ];

  const FAQ_ITEMS = [
    { q: t('pricing.faqWhyPayQ'), a: t('pricing.faqWhyPayA') },
    { q: t('pricing.faqCalcQ'), a: t('pricing.faqCalcA') },
    { q: t('pricing.faqDelayQ'), a: t('pricing.faqDelayA') },
    { q: t('pricing.faqWatchlistQ'), a: t('pricing.faqWatchlistA') },
    { q: t('pricing.faqQuizQ'), a: t('pricing.faqQuizA') },
  ];

  useEffect(() => {
    if (user && token) {
      fetchSubscriptionStatus();
    } else {
      setLoading(false);
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
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const isPro = subscriptionStatus?.subscription?.is_pro;

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={t('pro.seoTitle')}
        description={t('pro.seoDescription')}
      />
      
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-16">
        {/* Hero */}
        <div className="text-center space-y-6">
          <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-2 text-lg">
            <Crown className="w-5 h-5 mr-2" />
            {t('pro.tryProBadge')}
          </Badge>
          <h1 className="text-5xl md:text-6xl font-bold">
            {t('pro.unlockEverything')} <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-orange-600">{t('pro.unlockEverythingHighlight')}</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed" dangerouslySetInnerHTML={{ __html: `${t('pro.heroDesc1')} ${t('pro.heroDesc2')} ${t('pro.heroDesc3')}` }} />
        </div>

        {/* Current Status */}
        {user && (
          <Card className={isPro ? 'bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500' : 'bg-gray-100 dark:bg-zinc-800'}>
            <CardContent className="p-8 text-center">
              {isPro ? (
                <div className="flex items-center justify-center gap-3">
                  <Crown className="w-8 h-8 text-amber-500" />
                  <div>
                    <p className="text-2xl font-bold">{t('pro.proAlreadyActive')} 🎉</p>
                    <p className="text-muted-foreground">{t('pro.enjoyPremium')}</p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center gap-3">
                  <Lock className="w-8 h-8 text-gray-500" />
                  <div>
                    <p className="text-xl font-semibold">{t('pro.currentPlanFree')}</p>
                    <p className="text-muted-foreground">{t('pro.upgradeToUnlock')}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Why PRO Cards */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">{t('pro.whyProTitle')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {WHY_PRO_CARDS.map((card, idx) => (
              <Card key={idx} className="bg-gradient-to-br from-white to-gray-50 dark:from-zinc-900 dark:to-zinc-800 hover:shadow-xl transition-all">
                <CardContent className="p-6 text-center">
                  <div className={`w-16 h-16 bg-gradient-to-br ${card.gradient} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                    <card.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-lg font-bold mb-2">{card.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {card.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Main Comparison Table */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">{t('pro.comparisonTitle')}</h2>
          <FreeVsProComparison />
        </div>

        {/* Pricing */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">{t('pro.choosePlanTitle')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-2xl">{t('pro.proMonthly')}</CardTitle>
                <CardDescription>{t('pro.monthlyFlexible')}</CardDescription>
                <div className="pt-4">
                  <span className="text-5xl font-bold">49</span>
                  <span className="text-2xl text-muted-foreground"> RON</span>
                  <span className="text-muted-foreground">{t('common.perMonth')}</span>
                </div>
              </CardHeader>
              <CardContent>
                <Link to="/pricing">
                  <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12">
                    <Crown className="w-4 h-4 mr-2" />
                    {t('pro.activateMonthly')}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
                <p className="text-xs text-center text-muted-foreground mt-3">
                  {t('pro.cancelNoHidden')}
                </p>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-500 relative shadow-xl">
              <div className="absolute -top-3 right-4">
                <Badge className="bg-green-500 text-white px-3 py-1">{`📈 ${t('pro.save2Months')}`}</Badge>
              </div>
              <CardHeader>
                <CardTitle className="text-2xl">{t('pro.proAnnual')}</CardTitle>
                <CardDescription>{t('pro.bestPrice')}</CardDescription>
                <div className="pt-4">
                  <span className="text-5xl font-bold">490</span>
                  <span className="text-2xl text-muted-foreground"> RON</span>
                  <span className="text-muted-foreground">{t('common.perYear')}</span>
                </div>
                <p className="text-sm text-green-600 font-semibold">{t('pro.annualSavings')}</p>
              </CardHeader>
              <CardContent>
                <Link to="/pricing">
                  <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 h-12">
                    <Crown className="w-4 h-4 mr-2" />
                    {t('pro.activateAnnual')}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </Button>
                </Link>
                <p className="text-xs text-center text-muted-foreground mt-3">
                  {t('pro.bestOffer')}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* FAQ */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">{t('pro.faqTitle')}</h2>
          <div className="max-w-4xl mx-auto space-y-4">
            {FAQ_ITEMS.map((item, idx) => (
              <Card key={idx} className="bg-gradient-to-br from-white to-gray-50 dark:from-zinc-900 dark:to-zinc-800">
                <CardHeader>
                  <CardTitle className="text-lg flex items-start gap-3">
                    <span className="text-amber-600 flex-shrink-0">Q{idx + 1}.</span>
                    <span>{item.q}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground leading-relaxed pl-8">
                    {item.a}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Trust & Security */}
        <Card className="bg-gradient-to-r from-blue-50 to-blue-50 dark:from-blue-900/20 dark:to-blue-900/20">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-4">
                <Shield className="w-12 h-12 text-blue-600" />
                <div>
                  <h3 className="text-xl font-bold mb-1">{t('pro.secureCompliant')}</h3>
                  <p className="text-muted-foreground">
                    {t('pro.secureCompliantDesc')}
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <Link to="/privacy">
                  <Button variant="outline" size="sm">
                    {t('pro.privacy')}
                  </Button>
                </Link>
                <Link to="/terms">
                  <Button variant="outline" size="sm">
                    {t('pro.terms')}
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Final CTA */}
        <div className="text-center bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-red-500/10 rounded-3xl p-12 border-2 border-amber-500/20">
          <h2 className="text-4xl font-bold mb-4">{t('pro.readyToUnlock')}</h2>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            {t('pro.readyToUnlockDesc')}
          </p>
          <Link to="/pricing">
            <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-12 h-16 text-xl">
              <Crown className="w-6 h-6 mr-3" />
              {t('pro.activateProNow')}
              <ArrowRight className="w-6 h-6 ml-3" />
            </Button>
          </Link>
          <p className="text-sm text-muted-foreground mt-4">
            {`💳 ${t('pro.trustSecure')} • 🔄 ${t('pro.trustCancel')} • ⚡ ${t('pro.trustInstant')}`}
          </p>
        </div>
      </div>
    </>
  );
}
