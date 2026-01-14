import React, { useState, useEffect } from 'react';
import { Check, Crown, Sparkles, Zap, Shield, Star, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FEATURES = {
  free: [
    "5 întrebări AI pe zi",
    "Nivel Începător BVB",
    "Date BVB de bază",
    "Fear & Greed Index",
    "Știri financiare",
    "Portofoliu simplu"
  ],
  pro: [
    "Întrebări AI NELIMITATE",
    "Toate nivelurile (Începător, Mediu, Expert)",
    "Acces FĂRĂ quiz",
    "Calculator Fiscal complet (BVB + Internațional)",
    "AI Fiscal Advisor",
    "Indicatori tehnici avansați (RSI, MA, MACD)",
    "Analiză fundamentală completă",
    "AI trasează linii pe grafice",
    "Portofoliu avansat cu AI",
    "Suport prioritar"
  ]
};

export default function PricingPage() {
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
            💎 Planuri & Prețuri
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold">
            Alege Planul <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Potrivit</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Începe gratuit, treci la PRO pentru funcții avansate
          </p>
        </div>

        {/* Current Status */}
        {user && subscriptionStatus && (
          <Card className={isPro ? 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-amber-500/30' : 'bg-slate-100 dark:bg-slate-800'}>
            <CardContent className="p-6 text-center">
              <div className="flex items-center justify-center gap-3 mb-2">
                {isPro ? <Crown className="w-6 h-6 text-amber-500" /> : <Shield className="w-6 h-6 text-gray-500" />}
                <p className="text-lg font-semibold">
                  Plan curent: <strong>{isPro ? 'PRO' : 'Gratuit'}</strong>
                </p>
              </div>
              {isPro && subscriptionStatus.subscription.expires_at && (
                <p className="text-sm text-muted-foreground">
                  Expiră la: {new Date(subscriptionStatus.subscription.expires_at).toLocaleDateString('ro-RO')}
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
                <Badge variant="outline">Gratuit</Badge>
              </div>
              <CardTitle className="text-2xl">Gratuit</CardTitle>
              <CardDescription>Perfect pentru a începe</CardDescription>
              <div className="pt-4">
                <span className="text-4xl font-bold">0 RON</span>
                <span className="text-muted-foreground">/lună</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                {FEATURES.free.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <Check className="w-5 h-5 text-green-500 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
              <Button 
                variant="outline" 
                className="w-full"
                onClick={() => !user && (window.location.href = '/login')}
                disabled={user}
              >
                {user ? 'Plan Actual' : 'Începe Gratuit'}
              </Button>
            </CardContent>
          </Card>

          {/* PRO Plan */}
          <Card className="relative overflow-hidden border-2 border-amber-500 shadow-2xl">
            {/* Badge Recomandată */}
            <div className="absolute top-4 right-4">
              <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white">
                <Star className="w-3 h-3 mr-1" />
                RECOMANDATĂ
              </Badge>
            </div>

            <CardHeader>
              <Crown className="w-10 h-10 text-amber-500" />
              <CardTitle className="text-2xl">PRO</CardTitle>
              <CardDescription>Toate funcțiile avansate</CardDescription>
              <div className="pt-4 space-y-2">
                <div>
                  <span className="text-4xl font-bold">49 RON</span>
                  <span className="text-muted-foreground">/lună</span>
                </div>
                <div className="text-sm text-muted-foreground">
                  sau <strong className="text-green-600">490 RON/an</strong> (economisești 2 luni!)
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-xs font-semibold text-amber-600 mb-2">Tot ce e în GRATUIT, PLUS:</p>
                {FEATURES.pro.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <Sparkles className="w-5 h-5 text-amber-500 mt-0.5" />
                    <span className="text-sm font-medium">{feature}</span>
                  </div>
                ))}
              </div>
              
              {isPro ? (
                <Button 
                  className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600"
                  disabled
                >
                  <Check className="w-4 h-4 mr-2" />
                  Plan Activ
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
                      Se procesează...
                    </span>
                  ) : (
                    <>
                      <Crown className="w-5 h-5 mr-2" />
                      Activează PRO Acum
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
            <CardTitle className="text-center">Comparație Detalii Planuri</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Funcție</th>
                    <th className="text-center p-3">Gratuit</th>
                    <th className="text-center p-3 bg-amber-500/10">PRO</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  <tr>
                    <td className="p-3">Întrebări AI</td>
                    <td className="text-center p-3">5/zi</td>
                    <td className="text-center p-3 bg-amber-500/10 font-bold text-amber-600">NELIMITATE</td>
                  </tr>
                  <tr>
                    <td className="p-3">Niveluri Acces</td>
                    <td className="text-center p-3">Începător</td>
                    <td className="text-center p-3 bg-amber-500/10 font-bold text-amber-600">Toate (3)</td>
                  </tr>
                  <tr>
                    <td className="p-3">Calculator Fiscal</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅</td>
                  </tr>
                  <tr>
                    <td className="p-3">Indicatori Tehnici</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ RSI, MA, MACD</td>
                  </tr>
                  <tr>
                    <td className="p-3">Analiză Fundamentală</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ Completă</td>
                  </tr>
                  <tr>
                    <td className="p-3">AI Grafice</td>
                    <td className="text-center p-3">❌</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ Linii suport/rezistență</td>
                  </tr>
                  <tr>
                    <td className="p-3">Portofoliu Avansat</td>
                    <td className="text-center p-3">Basic</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ Cu AI</td>
                  </tr>
                  <tr>
                    <td className="p-3">Quiz-uri pentru Nivele</td>
                    <td className="text-center p-3">Da (7/10)</td>
                    <td className="text-center p-3 bg-amber-500/10">✅ SKIP direct</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* FAQ */}
        <Card className="max-w-5xl mx-auto">
          <CardHeader>
            <CardTitle>Întrebări Frecvente</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-1">Pot anula oricând?</h3>
              <p className="text-sm text-muted-foreground">
                Da! Poți anula abonamentul PRO oricând. Vei avea acces până la sfârșitul perioadei plătite.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">Ce metode de plată acceptați?</h3>
              <p className="text-sm text-muted-foreground">
                Acceptăm carduri bancare prin Stripe (securizat). În curând și alte metode.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">Pot schimba planul din Lunar în Anual?</h3>
              <p className="text-sm text-muted-foreground">
                Da! Contactează-ne și îți facem upgrade cu discount proporțional.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-1">Există trial gratuit pentru PRO?</h3>
              <p className="text-sm text-muted-foreground">
                Momentan nu, dar planul Gratuit îți oferă o previzualizare bună a platformei. PRO deblochează funcții avansate.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Trust Badges */}
        <div className="text-center">
          <div className="inline-flex items-center gap-6 p-4 bg-slate-100 dark:bg-slate-800 rounded-lg">
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="text-sm">Plată Securizată</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span className="text-sm">Date Reale BVB</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-amber-500" />
              <span className="text-sm">Activare Instant</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
