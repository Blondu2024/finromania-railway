import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Calculator, TrendingUp, Building2, User, Crown, Lock, ChevronRight, CheckCircle, XCircle, Info, AlertTriangle, Sparkles, Clock, Calendar, MessageCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Slider } from '../components/ui/slider';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';
import FiscalAIChat from '../components/FiscalAIChat';
import PortfolioImport from '../components/PortfolioImport';
import ProPaywall from '../components/ProPaywall';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Format number as RON
const formatRON = (value) => {
  return new Intl.NumberFormat('ro-RO', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value) + ' RON';
};

// Entity icons
const EntityIcon = ({ type, className = "w-8 h-8" }) => {
  switch (type) {
    case 'pf':
      return <User className={className} />;
    case 'pfa':
      return <Calculator className={className} />;
    case 'srl_micro':
      return <Building2 className={className} />;
    default:
      return <Calculator className={className} />;
  }
};

// Result Card Component
const ResultCard = ({ scenario, isBest, isWorst, t }) => {
  const bgColor = isBest ? 'bg-green-500/10 border-green-500' :
                  isWorst ? 'bg-red-500/10 border-red-500' :
                  'bg-gray-100 dark:bg-zinc-800 border-gray-200 dark:border-zinc-700';

  return (
    <Card className={`${bgColor} border-2 transition-all hover:shadow-lg`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isBest ? 'bg-green-500/20' : isWorst ? 'bg-red-500/20' : 'bg-gray-200 dark:bg-zinc-700'}`}>
              <EntityIcon type={scenario.tip_entitate} className={`w-6 h-6 ${isBest ? 'text-green-600' : isWorst ? 'text-red-600' : 'text-slate-600 dark:text-slate-300'}`} />
            </div>
            <div>
              <CardTitle className="text-lg">{scenario.nume_entitate}</CardTitle>
              {isBest && <Badge className="bg-green-500 text-white mt-1">{t('fiscal.recommended')}</Badge>}
              {isWorst && <Badge variant="destructive" className="mt-1">{t('fiscal.notRecommended')}</Badge>}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">{t('fiscal.effectiveRate')}</p>
            <p className={`text-2xl font-bold ${isBest ? 'text-green-600' : isWorst ? 'text-red-600' : ''}`}>
              {scenario.rata_efectiva_impozitare.toFixed(1)}%
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Key Numbers */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white dark:bg-zinc-900 rounded-lg p-3">
            <p className="text-sm text-muted-foreground">{t('fiscal.totalTaxes')}</p>
            <p className="text-lg font-semibold text-red-600">{formatRON(scenario.total_taxe)}</p>
          </div>
          <div className="bg-white dark:bg-zinc-900 rounded-lg p-3">
            <p className="text-sm text-muted-foreground">{t('fiscal.netIncome')}</p>
            <p className={`text-lg font-semibold ${isBest ? 'text-green-600' : ''}`}>{formatRON(scenario.venit_net)}</p>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2">
          <p className="text-sm font-medium">{t('fiscal.calcDetails')}</p>
          {scenario.detalii.map((detaliu, idx) => (
            <p key={idx} className="text-sm text-muted-foreground flex items-start gap-2">
              <ChevronRight className="w-3 h-3 mt-1 flex-shrink-0" />
              <span>{detaliu}</span>
            </p>
          ))}
        </div>

        {/* Pros & Cons */}
        <div className="grid grid-cols-1 gap-4 pt-2 border-t">
          <div>
            <p className="text-sm font-medium text-green-600 mb-2 flex items-center gap-1">
              <CheckCircle className="w-4 h-4" /> {t('fiscal.advantages')}
            </p>
            <ul className="space-y-1">
              {scenario.avantaje.map((av, idx) => (
                <li key={idx} className="text-xs text-muted-foreground">{av}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
              <XCircle className="w-4 h-4" /> {t('fiscal.disadvantages')}
            </p>
            <ul className="space-y-1">
              {scenario.dezavantaje.map((dez, idx) => (
                <li key={idx} className="text-xs text-muted-foreground">{dez}</li>
              ))}
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default function FiscalCalculatorPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [preview, setPreview] = useState(null);
  const [constante, setConstante] = useState(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);
  const [checkingSubscription, setCheckingSubscription] = useState(true);

  // Form state - adaptat pentru investiții
  const [castigCapital, setCastigCapital] = useState(50000);
  const [dividende, setDividende] = useState(10000);
  const [tipPiata, setTipPiata] = useState('bvb');
  const [perioadaDetinere, setPerioadaDetinere] = useState('mixt');
  const [procentTermenLung, setProcentTermenLung] = useState(50);
  const [areSalariu, setAreSalariu] = useState(true);
  const [areAngajat, setAreAngajat] = useState(false);

  // Check subscription status
  useEffect(() => {
    const checkSubscription = async () => {
      if (!user || !token) {
        setCheckingSubscription(false);
        return;
      }

      try {
        const response = await fetch(`${API_URL}/api/subscriptions/status`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setSubscriptionStatus(data);
        }
      } catch (error) {
        console.error('Error checking subscription:', error);
      } finally {
        setCheckingSubscription(false);
      }
    };

    checkSubscription();
  }, [user, token]);

  useEffect(() => {
    fetchConstante();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchPreview();
    }, 300);
    return () => clearTimeout(timer);
  }, [castigCapital, dividende, areSalariu, tipPiata]);

  const fetchConstante = async () => {
    try {
      const response = await fetch(`${API_URL}/api/fiscal/constante`);
      if (response.ok) {
        const data = await response.json();
        setConstante(data);
      }
    } catch (error) {
      console.error('Error fetching constante:', error);
    }
  };

  const fetchPreview = async () => {
    try {
      const response = await fetch(
        `${API_URL}/api/fiscal/preview?castig=${castigCapital}&dividende=${dividende}&are_salariu=${areSalariu}&piata=${tipPiata}`
      );
      if (response.ok) {
        const data = await response.json();
        setPreview(data);
      }
    } catch (error) {
      console.error('Error fetching preview:', error);
    }
  };

  const handleCalculate = async () => {
    if (!user || !token) {
      window.location.href = '/login';
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/fiscal/calculeaza`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          castig_capital_anual: castigCapital,
          dividende_anuale: dividende,
          tip_piata: tipPiata,
          perioada_detinere: perioadaDetinere,
          procent_termen_lung: procentTermenLung,
          are_alte_venituri_cass: areSalariu,
          are_angajat_srl: areAngajat
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      }
    } catch (error) {
      console.error('Error calculating:', error);
    } finally {
      setLoading(false);
    }
  };

  // Find best and worst scenarios
  const bestScenario = results?.scenarii?.reduce((best, curr) =>
    curr.venit_net > best.venit_net ? curr : best, results.scenarii[0]);
  const worstScenario = results?.scenarii?.reduce((worst, curr) =>
    curr.venit_net < worst.venit_net ? curr : worst, results.scenarii[0]);

  const venitTotal = castigCapital + dividende;

  // Check if user has PRO access
  const isPro = subscriptionStatus?.subscription?.is_pro;
  const isLoggedIn = !!user;

  // Show loading while checking subscription
  if (checkingSubscription) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show paywall for non-PRO users
  if (!isPro) {
    // Structured data pentru Calculator (chiar dacă e PRO-only)
    const calcStructuredData = {
      "@context": "https://schema.org",
      "@type": "WebApplication",
      "name": "Calculator Fiscal Romania - PF vs SRL 2026",
      "description": "Calculator fiscal profesional pentru alegerea între PF, PFA și SRL în România. Legislatie 2026, calcul impozite, CASS, economii fiscale.",
      "url": "https://finromania.ro/calculator-fiscal",
      "applicationCategory": "FinanceApplication",
      "operatingSystem": "Any",
      "featureList": ["Calcul impozit BVB 3-6%", "Calcul SRL Micro 1%+16%", "Comparație economii", "Legislatie 2026"],
      "inLanguage": "ro",
      "areaServed": "RO"
    };

    return (
      <>
        <SEO
          title="Calculator Fiscal Romania 2026 - PF vs SRL | FinRomania"
          description="Calculator fiscal gratuit pentru România: compară impozite PF, PFA, SRL. Legislatie 2026, calcul CASS, CAS, economii fiscale. Află care formă juridică e optimă pentru tine."
          keywords="calculator fiscal romania 2026, pf vs srl, impozit dividende, microîntreprindere, pfa impozit, calculator impozit venit, legislatie fiscala 2026, CASS 2026"
          structuredData={calcStructuredData}
        />
        <ProPaywall feature="Calculatorul Fiscal cu AI" />
      </>
    );
  }

  // Structured data pentru versiunea PRO
  const proStructuredData = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Calculator Fiscal PRO - Investiții BVB",
    "description": "Calculator fiscal avansat pentru investiții la Bursa București. Compară PF vs SRL pentru acțiuni BVB. Impozit 3-6% optimizat.",
    "url": "https://finromania.ro/calculator-fiscal",
    "applicationCategory": "FinanceApplication",
    "featureList": ["Calcul impozit BVB 3-6%", "PF vs SRL comparație", "Optimizare fiscală", "AI Advisor fiscal"],
    "inLanguage": "ro",
    "areaServed": "RO"
  };

  return (
    <>
      <SEO
        title="Calculator Fiscal Investiții BVB 2026 - PF vs SRL | FinRomania"
        description="Calculator fiscal pentru investiții la Bursa București (BVB). Compară impozite PF vs PFA vs SRL pentru câștiguri din acțiuni. Legislatie 2026, impozit 3-6% BVB conform Cod Fiscal 2026."
        keywords="calculator fiscal bvb, impozit acțiuni românia, pf vs srl trading, fiscal bursă bucurești, impozit dividende bvb, optimizare fiscală trading"
        structuredData={proStructuredData}
      />

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-1">
            {t('fiscal.updated2026')}
          </Badge>
          <h1 className="text-2xl sm:text-4xl md:text-5xl font-bold">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-blue-500">{t('fiscal.title')}</span>
          </h1>
          <p className="text-base sm:text-xl text-muted-foreground max-w-2xl mx-auto">
            {t('fiscal.subtitle')}
          </p>
        </div>

        {/* Main Tabs: Calculator vs Import */}
        <Tabs defaultValue="calculator" className="w-full">
          <TabsList className="grid grid-cols-2 w-full max-w-md mx-auto">
            <TabsTrigger value="calculator">{t('fiscal.manualCalc')}</TabsTrigger>
            <TabsTrigger value="import">{t('fiscal.importPortfolio')}</TabsTrigger>
          </TabsList>

          <TabsContent value="import" className="mt-6">
            <PortfolioImport />
          </TabsContent>

          <TabsContent value="calculator" className="mt-6 space-y-8">

        {/* Key Info Cards */}
        <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3">
          <Card className="bg-green-500/10 border-green-500/30">
            <CardContent className="p-4 text-center">
              <Calendar className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-green-600">3%</p>
              <p className="text-xs text-muted-foreground">🇷🇴 BVB ≥1 an</p>
            </CardContent>
          </Card>
          <Card className="bg-yellow-500/10 border-yellow-500/30">
            <CardContent className="p-4 text-center">
              <Clock className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-yellow-600">6%</p>
              <p className="text-xs text-muted-foreground">🇷🇴 BVB &lt;1 an</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-500/10 border-blue-500/30">
            <CardContent className="p-4 text-center">
              <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-blue-600">16%</p>
              <p className="text-xs text-muted-foreground">{t('fiscal.internationalRates')}</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-500/10 border-blue-500/30">
            <CardContent className="p-4 text-center">
              <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-blue-600">16%</p>
              <p className="text-xs text-muted-foreground">{t('common.dividend')} RO</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Preview */}
        {preview && !results && (
          <Card className={`${tipPiata === 'bvb' ? 'bg-gradient-to-r from-green-600 to-emerald-600' : 'bg-gradient-to-r from-blue-700 to-blue-500'} text-white`}>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <Sparkles className="w-12 h-12" />
                  <div>
                    <p className="text-white/80">Pentru {formatRON(venitTotal)} venit din investiții</p>
                    <p className="text-2xl font-bold">{preview.mesaj_principal}</p>
                    {preview.bonus_bvb && tipPiata === 'bvb' && (
                      <p className="text-sm text-white/90 mt-1">💡 {preview.bonus_bvb}</p>
                    )}
                    {preview.nota_bvb && tipPiata === 'international' && (
                      <p className="text-sm text-amber-200 mt-1">⚠️ {preview.nota_bvb}</p>
                    )}
                  </div>
                </div>
                <div className="text-center md:text-right">
                  <p className="text-sm text-white/80">{t('fiscal.totalTaxes')} ({tipPiata === 'bvb' ? 'BVB' : t('fiscal.internationalRates')})</p>
                  <p className="text-3xl font-bold">
                    {formatRON(tipPiata === 'bvb' ? preview.comparatie?.pf_bvb?.total_taxe || 0 : preview.comparatie?.pf_international?.total_taxe || 0)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Form */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                {t('fiscal.yourData')}
              </CardTitle>
              <CardDescription>{t('fiscal.enterGains')}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Câștig Capital */}
              <div className="space-y-3">
                <Label className="flex items-center justify-between">
                  {t('fiscal.capitalGain')}
                  <span className="font-bold text-blue-600">{formatRON(castigCapital)}</span>
                </Label>
                <Slider
                  value={[castigCapital]}
                  onValueChange={(v) => setCastigCapital(v[0])}
                  min={0}
                  max={500000}
                  step={5000}
                  className="cursor-pointer"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0</span>
                  <span>250k</span>
                  <span>500k RON</span>
                </div>
              </div>

              {/* Dividende */}
              <div className="space-y-3">
                <Label className="flex items-center justify-between">
                  {t('fiscal.dividendsReceived')}
                  <span className="font-bold text-blue-600">{formatRON(dividende)}</span>
                </Label>
                <Slider
                  value={[dividende]}
                  onValueChange={(v) => setDividende(v[0])}
                  min={0}
                  max={100000}
                  step={1000}
                  className="cursor-pointer"
                />
              </div>

              {/* Tip Piață */}
              <div className="space-y-3">
                <Label>{t('fiscal.market')}</Label>
                <Tabs value={tipPiata} onValueChange={setTipPiata}>
                  <TabsList className="grid grid-cols-2 w-full">
                    <TabsTrigger value="bvb">🇷🇴 BVB</TabsTrigger>
                    <TabsTrigger value="international">🌍 Global</TabsTrigger>
                  </TabsList>
                </Tabs>
                {tipPiata === 'bvb' && (
                  <p className="text-xs text-green-600">✅ {t('fiscal.bvbRates')}: 3-6%</p>
                )}
                {tipPiata === 'international' && (
                  <p className="text-xs text-yellow-600">⚠️ {t('fiscal.internationalRates')}: 16%</p>
                )}
              </div>

              {/* Perioada Deținere (doar pentru BVB) */}
              {tipPiata === 'bvb' && (
                <div className="space-y-3">
                  <Label>{t('fiscal.holdingPeriod')}</Label>
                  <Tabs value={perioadaDetinere} onValueChange={setPerioadaDetinere}>
                    <TabsList className="grid grid-cols-3 w-full">
                      <TabsTrigger value="peste_1_an" className="text-xs">{t('fiscal.longTerm')}</TabsTrigger>
                      <TabsTrigger value="sub_1_an" className="text-xs">{t('fiscal.shortTerm')}</TabsTrigger>
                      <TabsTrigger value="mixt" className="text-xs">{t('fiscal.mixed')}</TabsTrigger>
                    </TabsList>
                  </Tabs>

                  {perioadaDetinere === 'mixt' && (
                    <div className="space-y-2 mt-2">
                      <Label className="text-xs">{t('fiscal.longTermPercent')}: {procentTermenLung}%</Label>
                      <Slider
                        value={[procentTermenLung]}
                        onValueChange={(v) => setProcentTermenLung(v[0])}
                        min={0}
                        max={100}
                        step={10}
                      />
                    </div>
                  )}
                </div>
              )}

              {/* Switches */}
              <div className="space-y-4 pt-4 border-t">
                <div className="flex items-center justify-between">
                  <Label htmlFor="salariu" className="cursor-pointer text-sm">
                    {t('fiscal.hasSalary')}
                  </Label>
                  <Switch
                    id="salariu"
                    checked={areSalariu}
                    onCheckedChange={setAreSalariu}
                  />
                </div>
                {!areSalariu && (
                  <p className="text-xs text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-2 rounded">
                    ⚠️ {t('fiscal.cassWarning')}
                  </p>
                )}
              </div>

              {/* Calculate Button */}
              <Button
                className="w-full bg-gradient-to-r from-blue-700 to-blue-500 hover:from-blue-700 hover:to-blue-700"
                size="lg"
                onClick={handleCalculate}
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    {t('fiscal.calculating')}
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Calculator className="w-4 h-4" />
                    {t('fiscal.calculate')}
                  </span>
                )}
              </Button>

              {!user && (
                <p className="text-sm text-center text-muted-foreground">
                  <Lock className="w-4 h-4 inline mr-1" />
                  {t('fiscal.loginForFull')}
                </p>
              )}
            </CardContent>
          </Card>

          {/* Results */}
          <div className="lg:col-span-2 space-y-6">
            {results ? (
              <>
                {/* Summary Card */}
                <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30">
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">{t('fiscal.savingsVsWorst')}</p>
                        <p className="text-4xl font-bold text-green-600">{formatRON(results.economie_maxima)}</p>
                      </div>
                      <div className="text-right">
                        <Badge className="bg-green-500 text-white mb-2">{results.recomandare}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Scenario Cards */}
                <div className="space-y-4">
                  {results.scenarii.map((scenario) => (
                    <ResultCard
                      key={scenario.tip_entitate}
                      scenario={scenario}
                      isBest={scenario.tip_entitate === bestScenario?.tip_entitate}
                      isWorst={scenario.tip_entitate === worstScenario?.tip_entitate}
                      t={t}
                    />
                  ))}
                </div>

                {/* Detailed Explanation */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Info className="w-5 h-5" />
                      {t('fiscal.explanation')}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose dark:prose-invert max-w-none text-sm">
                      <div dangerouslySetInnerHTML={{
                        __html: results.explicatie_detaliata
                          .replace(/###\s*(.*)/g, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n/g, '<br/>')
                          .replace(/\|(.+)\|/g, '<code>$1</code>')
                      }} />
                    </div>
                  </CardContent>
                </Card>

                {/* Legal Note */}
                {results.nota_legala && (
                  <Card className="bg-amber-500/10 border-amber-500/30">
                    <CardContent className="p-4">
                      <p className="text-sm text-amber-800 dark:text-amber-200">
                        {results.nota_legala}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card className="h-full min-h-[400px] flex items-center justify-center">
                <CardContent className="text-center space-y-4">
                  <div className="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto">
                    <TrendingUp className="w-8 h-8 text-green-600" />
                  </div>
                  <h3 className="text-xl font-semibold">{t('fiscal.investOnBVB')}</h3>
                  <p className="text-muted-foreground max-w-md">
                    {t('fiscal.investOnBVBDesc')}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {t('fiscal.enterGains')}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Tax Constants Info */}
        {constante && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5" />
                {t('fiscal.legislation')} {constante.an_fiscal}
              </CardTitle>
              <CardDescription>{t('fiscal.lastUpdate')}: {constante.ultima_actualizare}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">🇷🇴 {t('fiscal.bvbRates')}</h4>
                  <p className="text-sm text-muted-foreground">{t('fiscal.gainLong')}: <strong>3%</strong></p>
                  <p className="text-sm text-muted-foreground">{t('fiscal.gainShort')}: <strong>6%</strong></p>
                  <p className="text-sm text-muted-foreground">{t('fiscal.dividendsLabel')}: <strong>16%</strong></p>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">🌍 {t('fiscal.internationalRates')}</h4>
                  <p className="text-sm text-muted-foreground">{t('fiscal.capitalGainLabel')}: <strong>16%</strong></p>
                  <p className="text-sm text-muted-foreground">{t('fiscal.dividendsLabel')}: <strong>16%</strong></p>
                </div>
                <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-amber-700 dark:text-amber-300 mb-2">🏥 {t('fiscal.cassRates')}</h4>
                  <p className="text-sm text-muted-foreground">{t('fiscal.rate')}: <strong>10%</strong></p>
                  <p className="text-sm text-muted-foreground">{t('fiscal.threshold')}: <strong>{constante.cass?.prag_activare}</strong></p>
                  <p className="text-xs text-muted-foreground mt-1">{constante.cass?.nota}</p>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">🏢 {t('fiscal.srlMicro')}</h4>
                  <p className="text-sm text-muted-foreground">{t('fiscal.withEmployee')}: <strong>{constante.micro_srl?.cu_angajat}</strong></p>
                  <p className="text-sm text-muted-foreground">{t('fiscal.withoutEmployee')}: <strong>{constante.micro_srl?.fara_angajat}</strong></p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI Fiscal Advisor */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-gradient-to-br from-blue-600/10 to-blue-600/10 border-blue-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-blue-500" />
                {t('fiscal.fiscalQuestions')}
              </CardTitle>
              <CardDescription>
                {t('fiscal.fiscalQuestionsDesc')}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Cum completez Declarația Unică?
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Ce e W-8BEN și când am nevoie?
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Cum calculez CASS pentru investiții?
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Pot compensa pierderile cu câștigurile?
                </li>
              </ul>
            </CardContent>
          </Card>

          <FiscalAIChat />
        </div>

        {/* Cross-link to Simulator */}
        <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200">
          <CardContent className="p-4 flex items-center justify-between">
            <div>
              <p className="font-semibold text-sm">{t('fiscal.hasSRLOrPFA')}</p>
              <p className="text-xs text-muted-foreground">{t('fiscal.simulatorDesc')}</p>
            </div>
            <a href="/simulator-fiscal">
              <Button variant="outline" size="sm">{t('fiscal.simulatorBtn')}</Button>
            </a>
          </CardContent>
        </Card>

          </TabsContent>
        </Tabs>

        {/* Disclaimer */}
        <Card className="bg-gray-100 dark:bg-zinc-800 border-slate-300 dark:border-slate-600">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-slate-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold">{t('common.disclaimer')}</h4>
                <p className="text-sm text-muted-foreground mt-1">
                  {t('fiscal.disclaimerText')}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
