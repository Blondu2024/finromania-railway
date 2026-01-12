import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Crown, Check, X, Sparkles, Zap, ArrowRight, Lock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import FreeVsProComparison from '../components/FreeVsProComparison';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TryProPage() {
  const { user, token } = useAuth();
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);

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
      console.error('Error:', error);
    }
  };

  const isPro = subscriptionStatus?.subscription?.is_pro;

  return (
    <>
      <SEO 
        title="Încearcă PRO | FinRomania"
        description="Descoperă ce primești cu abonamentul PRO: Calculator Fiscal, AI nelimitat, toate nivelurile, indicatori tehnici și mai mult."
      />
      
      <div className="max-w-7xl mx-auto px-4 py-12 space-y-12">
        {/* Hero */}
        <div className="text-center space-y-4">
          <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2 text-lg">
            <Crown className="w-4 h-4 mr-1" />
            Încearcă PRO
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold">
            Deblochează <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-orange-600">Toate Funcțiile</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            De la 5 întrebări AI pe zi la NELIMITATE. De la BET la TOATE acțiunile BVB. 
            De la nivel Începător la EXPERT fără quiz.
          </p>
        </div>

        {/* Current Status */}
        {user && (
          <Card className={isPro ? 'bg-green-500/10 border-green-500' : 'bg-slate-100 dark:bg-slate-800'}>
            <CardContent className="p-6 text-center">
              <p className="text-lg">
                {isPro ? (
                  <span className="flex items-center justify-center gap-2">
                    <Crown className="w-6 h-6 text-amber-500" />
                    <strong>Felicitări! Ai deja PRO activ</strong>
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <Lock className="w-6 h-6 text-gray-500" />
                    <strong>Plan curent: GRATUIT</strong>
                  </span>
                )}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Main Comparison Table */}
        <FreeVsProComparison />

        {/* Why PRO Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-gradient-to-br from-amber-50 to-white dark:from-amber-900/20 dark:to-slate-800">
            <CardHeader>
              <Sparkles className="w-8 h-8 text-amber-500 mb-2" />
              <CardTitle>Economisește Mii de RON</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Doar Calculatorul Fiscal îți poate arăta cum să economisești până la 50.000+ RON/an 
                prin alegerea corectă între PF, PFA și SRL.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/20 dark:to-slate-800">
            <CardHeader>
              <Zap className="w-8 h-8 text-blue-500 mb-2" />
              <CardTitle>Învață Mai Rapid</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                AI nelimitat înseamnă că poți întreba orice, oricând. Fără limite de 5/zi. 
                Înveți în ritmul tău.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-white dark:from-purple-900/20 dark:to-slate-800">
            <CardHeader>
              <Crown className="w-8 h-8 text-purple-500 mb-2" />
              <CardTitle>Acces Complet</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                Toate cele 3 nivele (Începător, Mediu, Expert) fără quiz. 
                Indicatori tehnici, analiză fundamentală, AI chart lines.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <Card className="border-2">
            <CardHeader>
              <CardTitle className="text-2xl">PRO Lunar</CardTitle>
              <div className="pt-4">
                <span className="text-5xl font-bold">49</span>
                <span className="text-2xl text-muted-foreground"> RON</span>
                <span className="text-muted-foreground">/lună</span>
              </div>
            </CardHeader>
            <CardContent>
              <Link to="/pricing">
                <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 h-12">
                  <Crown className="w-4 h-4 mr-2" />
                  Activează Lunar
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <p className="text-xs text-center text-muted-foreground mt-3">
                Anulare oricând
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-green-500 relative">
            <div className="absolute -top-3 right-4">
              <Badge className="bg-green-500 text-white">Economisești 2 luni!</Badge>
            </div>
            <CardHeader>
              <CardTitle className="text-2xl">PRO Anual</CardTitle>
              <div className="pt-4">
                <span className="text-5xl font-bold">490</span>
                <span className="text-2xl text-muted-foreground"> RON</span>
                <span className="text-muted-foreground">/an</span>
              </div>
              <p className="text-sm text-green-600">vs 588 RON (2 luni gratuite)</p>
            </CardHeader>
            <CardContent>
              <Link to="/pricing">
                <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 h-12">
                  <Crown className="w-4 h-4 mr-2" />
                  Activează Anual
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <p className="text-xs text-center text-muted-foreground mt-3">
                Cea mai bună ofertă
              </p>
            </CardContent>
          </Card>
        </div>

        {/* FAQ */}
        <Card>
          <CardHeader>
            <CardTitle>Întrebări Frecvente despre PRO</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2">De ce să plătesc pentru educație?</h3>
              <p className="text-sm text-muted-foreground">
                Educația (lecții, cursuri) rămâne 100% GRATUITĂ! PRO îți deblochează <strong>INSTRUMENTE AVANSATE</strong> 
                precum Calculatorul Fiscal (economisește mii de RON), AI nelimitat, indicatori tehnici PRO și analiză fundamentală completă.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Ce înseamnă "toate nivelurile fără quiz"?</h3>
              <p className="text-sm text-muted-foreground">
                FREE users trebuie să treacă un quiz (7/10) pentru a accesa nivelele Mediu și Expert. 
                PRO users au acces DIRECT la toate cele 3 nivele din prima zi.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Calculatorul Fiscal chiar merită?</h3>
              <p className="text-sm text-muted-foreground">
                Da! Un singur calcul corect te poate ajuta să economisești mii sau zeci de mii de RON anual. 
                Compară PF vs PFA vs SRL Micro pentru investiții BVB și internaționale. Include și AI Fiscal Advisor.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Pot anula oricând?</h3>
              <p className="text-sm text-muted-foreground">
                Da, 100%! Anulezi când vrei. Vei avea acces până la sfârșitul perioadei plătite.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Final CTA */}
        <div className="text-center bg-gradient-to-r from-amber-500/10 to-orange-500/10 rounded-2xl p-8">
          <h2 className="text-3xl font-bold mb-4">Gata să deblochezi totul?</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Alătură-te investitorilor care folosesc instrumente PRO pentru decizii mai bune.
          </p>
          <Link to="/pricing">
            <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 px-8 h-14 text-lg">
              <Crown className="w-5 h-5 mr-2" />
              Vezi Planurile PRO
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </div>
    </>
  );
}
