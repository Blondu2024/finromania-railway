import React, { useState, useEffect } from 'react';
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
const ResultCard = ({ scenario, isBest, isWorst }) => {
  const bgColor = isBest ? 'bg-green-500/10 border-green-500' : 
                  isWorst ? 'bg-red-500/10 border-red-500' : 
                  'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700';
  
  return (
    <Card className={`${bgColor} border-2 transition-all hover:shadow-lg`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${isBest ? 'bg-green-500/20' : isWorst ? 'bg-red-500/20' : 'bg-slate-200 dark:bg-slate-700'}`}>
              <EntityIcon type={scenario.tip_entitate} className={`w-6 h-6 ${isBest ? 'text-green-600' : isWorst ? 'text-red-600' : 'text-slate-600 dark:text-slate-300'}`} />
            </div>
            <div>
              <CardTitle className="text-lg">{scenario.nume_entitate}</CardTitle>
              {isBest && <Badge className="bg-green-500 text-white mt-1">✅ Recomandat</Badge>}
              {isWorst && <Badge variant="destructive" className="mt-1">❌ Nu e recomandat</Badge>}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Rată efectivă</p>
            <p className={`text-2xl font-bold ${isBest ? 'text-green-600' : isWorst ? 'text-red-600' : ''}`}>
              {scenario.rata_efectiva_impozitare.toFixed(1)}%
            </p>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Key Numbers */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white dark:bg-slate-900 rounded-lg p-3">
            <p className="text-sm text-muted-foreground">Total Taxe</p>
            <p className="text-lg font-semibold text-red-600">{formatRON(scenario.total_taxe)}</p>
          </div>
          <div className="bg-white dark:bg-slate-900 rounded-lg p-3">
            <p className="text-sm text-muted-foreground">Venit Net</p>
            <p className={`text-lg font-semibold ${isBest ? 'text-green-600' : ''}`}>{formatRON(scenario.venit_net)}</p>
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2">
          <p className="text-sm font-medium">Detalii calcul:</p>
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
              <CheckCircle className="w-4 h-4" /> Avantaje
            </p>
            <ul className="space-y-1">
              {scenario.avantaje.map((av, idx) => (
                <li key={idx} className="text-xs text-muted-foreground">{av}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
              <XCircle className="w-4 h-4" /> Dezavantaje
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
    return (
      <>
        <SEO 
          title="Calculator Fiscal PRO | FinRomania"
          description="Calculator fiscal profesional pentru investiții la bursă. Funcție PRO exclusivă."
        />
        <ProPaywall feature="Calculatorul Fiscal cu AI" />
      </>
    );
  }

  return (
    <>
      <SEO 
        title="Calculator Fiscal Investiții BVB | FinRomania"
        description="Calculează impozitele pe câștiguri din acțiuni BVB. Compară PF vs PFA vs SRL. Impozit 1-3% pentru BVB!"
      />
      
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <Badge className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-1">
            🏆 Actualizat 2024-2025
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold">
            Calculator <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Fiscal BVB</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Știai că pe BVB plătești doar <strong className="text-green-600">1-3% impozit</strong> pe câștiguri?
            Calculează exact cât datorezi statului.
          </p>
        </div>

        {/* Key Info Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card className="bg-green-500/10 border-green-500/30">
            <CardContent className="p-4 text-center">
              <Calendar className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-green-600">1%</p>
              <p className="text-xs text-muted-foreground">🇷🇴 BVB ≥1 an</p>
            </CardContent>
          </Card>
          <Card className="bg-yellow-500/10 border-yellow-500/30">
            <CardContent className="p-4 text-center">
              <Clock className="w-6 h-6 text-yellow-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-yellow-600">3%</p>
              <p className="text-xs text-muted-foreground">🇷🇴 BVB &lt;1 an</p>
            </CardContent>
          </Card>
          <Card className="bg-blue-500/10 border-blue-500/30">
            <CardContent className="p-4 text-center">
              <TrendingUp className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-blue-600">10%</p>
              <p className="text-xs text-muted-foreground">🌍 Internațional</p>
            </CardContent>
          </Card>
          <Card className="bg-purple-500/10 border-purple-500/30">
            <CardContent className="p-4 text-center">
              <TrendingUp className="w-6 h-6 text-purple-600 mx-auto mb-2" />
              <p className="text-xl font-bold text-purple-600">8%</p>
              <p className="text-xs text-muted-foreground">Dividende RO</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Preview */}
        {preview && !results && (
          <Card className={`${tipPiata === 'bvb' ? 'bg-gradient-to-r from-green-600 to-emerald-600' : 'bg-gradient-to-r from-blue-600 to-purple-600'} text-white`}>
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
                  <p className="text-sm text-white/80">Total taxe ca PF ({tipPiata === 'bvb' ? 'BVB' : 'Internațional'})</p>
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
                Datele Tale
              </CardTitle>
              <CardDescription>Introdu câștigurile din investiții</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Câștig Capital */}
              <div className="space-y-3">
                <Label className="flex items-center justify-between">
                  Câștig din vânzare acțiuni
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
                  Dividende primite
                  <span className="font-bold text-purple-600">{formatRON(dividende)}</span>
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
                <Label>Piața</Label>
                <Tabs value={tipPiata} onValueChange={setTipPiata}>
                  <TabsList className="grid grid-cols-2 w-full">
                    <TabsTrigger value="bvb">🇷🇴 BVB</TabsTrigger>
                    <TabsTrigger value="international">🌍 Global</TabsTrigger>
                  </TabsList>
                </Tabs>
                {tipPiata === 'bvb' && (
                  <p className="text-xs text-green-600">✅ Impozit avantajos: 1-3%</p>
                )}
                {tipPiata === 'international' && (
                  <p className="text-xs text-yellow-600">⚠️ Impozit: 10%</p>
                )}
              </div>

              {/* Perioada Deținere (doar pentru BVB) */}
              {tipPiata === 'bvb' && (
                <div className="space-y-3">
                  <Label>Perioada de deținere</Label>
                  <Tabs value={perioadaDetinere} onValueChange={setPerioadaDetinere}>
                    <TabsList className="grid grid-cols-3 w-full">
                      <TabsTrigger value="peste_1_an" className="text-xs">≥1 an (1%)</TabsTrigger>
                      <TabsTrigger value="sub_1_an" className="text-xs">&lt;1 an (3%)</TabsTrigger>
                      <TabsTrigger value="mixt" className="text-xs">Mixt</TabsTrigger>
                    </TabsList>
                  </Tabs>
                  
                  {perioadaDetinere === 'mixt' && (
                    <div className="space-y-2 mt-2">
                      <Label className="text-xs">% pe termen lung (≥1 an): {procentTermenLung}%</Label>
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
                    Am salariu (plătesc CASS de acolo)
                  </Label>
                  <Switch
                    id="salariu"
                    checked={areSalariu}
                    onCheckedChange={setAreSalariu}
                  />
                </div>
                {!areSalariu && (
                  <p className="text-xs text-amber-600 bg-amber-50 dark:bg-amber-900/20 p-2 rounded">
                    ⚠️ Fără salariu, vei datora CASS (10%) dacă venitul &gt; 22.200 RON/an
                  </p>
                )}
              </div>

              {/* Calculate Button */}
              <Button 
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                size="lg"
                onClick={handleCalculate}
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Se calculează...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Calculator className="w-4 h-4" />
                    Calculează
                  </span>
                )}
              </Button>

              {!user && (
                <p className="text-sm text-center text-muted-foreground">
                  <Lock className="w-4 h-4 inline mr-1" />
                  Conectează-te pentru comparație completă
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
                        <p className="text-sm text-muted-foreground">Economie vs cea mai scumpă opțiune</p>
                        <p className="text-4xl font-bold text-green-600">{formatRON(results.economie_maxima)}</p>
                      </div>
                      <div className="text-right">
                        <Badge className="bg-green-500 text-white mb-2">🏆 {results.recomandare}</Badge>
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
                    />
                  ))}
                </div>

                {/* Detailed Explanation */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Info className="w-5 h-5" />
                      Explicație
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
                  <h3 className="text-xl font-semibold">Investești pe BVB?</h3>
                  <p className="text-muted-foreground max-w-md">
                    Vești bune! România are unul dintre cele mai avantajoase regimuri fiscale 
                    pentru investitorii la bursă: doar <strong className="text-green-600">1-3%</strong> impozit pe câștiguri!
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Completează formularul pentru a calcula exact cât datorezi.
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
                Legislație Fiscală {constante.an_fiscal}
              </CardTitle>
              <CardDescription>Ultima actualizare: {constante.ultima_actualizare}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-green-700 dark:text-green-300 mb-2">🇷🇴 BVB</h4>
                  <p className="text-sm text-muted-foreground">Câștig ≥1 an: <strong>1%</strong></p>
                  <p className="text-sm text-muted-foreground">Câștig &lt;1 an: <strong>3%</strong></p>
                  <p className="text-sm text-muted-foreground">Dividende: <strong>8%</strong></p>
                </div>
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">🌍 Internațional</h4>
                  <p className="text-sm text-muted-foreground">Câștig capital: <strong>10%</strong></p>
                  <p className="text-sm text-muted-foreground">Dividende: <strong>10%</strong></p>
                </div>
                <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-amber-700 dark:text-amber-300 mb-2">🏥 CASS</h4>
                  <p className="text-sm text-muted-foreground">Rată: <strong>10%</strong></p>
                  <p className="text-sm text-muted-foreground">Prag: <strong>{constante.cass?.prag_activare}</strong></p>
                  <p className="text-xs text-muted-foreground mt-1">{constante.cass?.nota}</p>
                </div>
                <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">🏢 SRL Micro</h4>
                  <p className="text-sm text-muted-foreground">Cu angajat: <strong>{constante.micro_srl?.cu_angajat}</strong></p>
                  <p className="text-sm text-muted-foreground">Fără angajat: <strong>{constante.micro_srl?.fara_angajat}</strong></p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI Fiscal Advisor */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="bg-gradient-to-br from-blue-600/10 to-purple-600/10 border-blue-500/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5 text-blue-500" />
                Întrebări despre Fiscalitate?
              </CardTitle>
              <CardDescription>
                AI-ul nostru fiscal îți răspunde la întrebări despre impozite, declarații, CASS, W-8BEN și multe altele.
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

        {/* Disclaimer */}
        <Card className="bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-600">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-slate-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold">Disclaimer</h4>
                <p className="text-sm text-muted-foreground mt-1">
                  Calculele sunt orientative și bazate pe legislația în vigoare. Legislația fiscală 
                  se poate modifica. Pentru situația ta specifică, consultă un contabil autorizat CECCAR.
                  FinRomania nu oferă consiliere fiscală sau juridică.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
