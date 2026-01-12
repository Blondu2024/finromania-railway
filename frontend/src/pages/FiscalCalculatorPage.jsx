import React, { useState, useEffect } from 'react';
import { Calculator, TrendingUp, Building2, User, Crown, Lock, ChevronRight, CheckCircle, XCircle, Info, AlertTriangle, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Slider } from '../components/ui/slider';
import { Switch } from '../components/ui/switch';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

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
              {isBest && <Badge className="bg-green-500 text-white mt-1">Cel mai avantajos</Badge>}
              {isWorst && <Badge variant="destructive" className="mt-1">Cel mai costisitor</Badge>}
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
            <p key={idx} className="text-sm text-muted-foreground flex items-center gap-2">
              <ChevronRight className="w-3 h-3" />
              {detaliu}
            </p>
          ))}
        </div>

        {/* Pros & Cons */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div>
            <p className="text-sm font-medium text-green-600 mb-2 flex items-center gap-1">
              <CheckCircle className="w-4 h-4" /> Avantaje
            </p>
            <ul className="space-y-1">
              {scenario.avantaje.slice(0, 3).map((av, idx) => (
                <li key={idx} className="text-xs text-muted-foreground">• {av}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
              <XCircle className="w-4 h-4" /> Dezavantaje
            </p>
            <ul className="space-y-1">
              {scenario.dezavantaje.slice(0, 3).map((dez, idx) => (
                <li key={idx} className="text-xs text-muted-foreground">• {dez}</li>
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
  
  // Form state
  const [venitAnual, setVenitAnual] = useState(100000);
  const [tipVenit, setTipVenit] = useState('mixt');
  const [procentDividende, setProcentDividende] = useState(50);
  const [areAlteVenituri, setAreAlteVenituri] = useState(true);
  const [areAngajat, setAreAngajat] = useState(false);

  useEffect(() => {
    fetchConstante();
    fetchPreview();
  }, []);

  useEffect(() => {
    // Update preview when venit changes
    const timer = setTimeout(() => {
      fetchPreview();
    }, 500);
    return () => clearTimeout(timer);
  }, [venitAnual]);

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
      const response = await fetch(`${API_URL}/api/fiscal/preview?venit=${venitAnual}`);
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
      // Redirect to login
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
          venit_brut_anual: venitAnual,
          tip_venit: tipVenit,
          procent_dividende: procentDividende,
          are_alte_venituri_cass: areAlteVenituri,
          are_angajat_srl: areAngajat,
          cheltuieli_deductibile_pfa: 0
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResults(data);
      } else {
        const error = await response.json();
        if (error.detail?.error === 'pro_required') {
          // Show upgrade prompt
          alert('Calculatorul complet este disponibil doar pentru PRO');
        }
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

  return (
    <>
      <SEO 
        title="Calculator Fiscal | FinRomania"
        description="Compară PF vs PFA vs SRL. Află cum să optimizezi impozitele din investiții în România."
      />
      
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <Badge className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-1">
            <Crown className="w-4 h-4 mr-1 inline" />
            Feature PRO
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold">
            Calculator <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Fiscal</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Compară PF vs PFA vs SRL și află cum să economisești mii de lei la impozite
          </p>
        </div>

        {/* Quick Preview for Everyone */}
        {preview && !results && (
          <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex items-center gap-4">
                  <Sparkles className="w-12 h-12" />
                  <div>
                    <p className="text-blue-100">Pentru un venit de {formatRON(venitAnual)}</p>
                    <p className="text-2xl font-bold">{preview.mesaj}</p>
                  </div>
                </div>
                <Button 
                  size="lg" 
                  className="bg-white text-blue-600 hover:bg-blue-50"
                  onClick={handleCalculate}
                >
                  {user ? 'Calculează Acum' : 'Conectează-te pentru Calcul Complet'}
                </Button>
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
              <CardDescription>Ajustează parametrii pentru calcul</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Venit Anual */}
              <div className="space-y-3">
                <Label className="flex items-center justify-between">
                  Venit Anual din Investiții
                  <span className="font-bold text-blue-600">{formatRON(venitAnual)}</span>
                </Label>
                <Slider
                  value={[venitAnual]}
                  onValueChange={(v) => setVenitAnual(v[0])}
                  min={10000}
                  max={1000000}
                  step={10000}
                  className="cursor-pointer"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>10k</span>
                  <span>500k</span>
                  <span>1M RON</span>
                </div>
              </div>

              {/* Tip Venit */}
              <div className="space-y-3">
                <Label>Tip Venit</Label>
                <Tabs value={tipVenit} onValueChange={setTipVenit}>
                  <TabsList className="grid grid-cols-3 w-full">
                    <TabsTrigger value="castig_capital">Capital</TabsTrigger>
                    <TabsTrigger value="dividende">Dividende</TabsTrigger>
                    <TabsTrigger value="mixt">Mixt</TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Procent Dividende (doar pentru mixt) */}
              {tipVenit === 'mixt' && (
                <div className="space-y-3">
                  <Label className="flex items-center justify-between">
                    Procent Dividende
                    <span className="font-bold">{procentDividende}%</span>
                  </Label>
                  <Slider
                    value={[procentDividende]}
                    onValueChange={(v) => setProcentDividende(v[0])}
                    min={0}
                    max={100}
                    step={5}
                  />
                </div>
              )}

              {/* Switches */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="alte-venituri" className="cursor-pointer">
                    Am salariu/alte venituri cu CASS
                  </Label>
                  <Switch
                    id="alte-venituri"
                    checked={areAlteVenituri}
                    onCheckedChange={setAreAlteVenituri}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <Label htmlFor="angajat" className="cursor-pointer">
                    SRL-ul are angajat
                  </Label>
                  <Switch
                    id="angajat"
                    checked={areAngajat}
                    onCheckedChange={setAreAngajat}
                  />
                </div>
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
                    Calculează Impozitele
                  </span>
                )}
              </Button>

              {!user && (
                <p className="text-sm text-center text-muted-foreground">
                  <Lock className="w-4 h-4 inline mr-1" />
                  Conectează-te pentru calcul complet
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
                        <p className="text-sm text-muted-foreground">Economie maximă posibilă</p>
                        <p className="text-4xl font-bold text-green-600">{formatRON(results.economie_maxima)}/an</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Recomandare</p>
                        <p className="font-semibold">{results.recomandare}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Scenario Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                      Explicație Detaliată
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="prose dark:prose-invert max-w-none">
                      <div dangerouslySetInnerHTML={{ 
                        __html: results.explicatie_detaliata
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n/g, '<br/>')
                      }} />
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              /* Placeholder when no results */
              <Card className="h-full min-h-[400px] flex items-center justify-center">
                <CardContent className="text-center space-y-4">
                  <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto">
                    <Calculator className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-xl font-semibold">Ajustează parametrii și calculează</h3>
                  <p className="text-muted-foreground max-w-md">
                    Introdu venitul tău anual din investiții și setările pentru a vedea comparația 
                    completă între PF, PFA și SRL.
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Info Section */}
        <Card className="bg-amber-500/10 border-amber-500/30">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-amber-800 dark:text-amber-200">Disclaimer Important</h4>
                <p className="text-sm text-muted-foreground mt-1">
                  Acest calculator oferă estimări orientative bazate pe legislația fiscală din România. 
                  Rezultatele nu constituie consultanță fiscală sau juridică. Pentru situația ta specifică, 
                  te recomandăm să consulți un contabil autorizat sau un consultant fiscal.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tax Constants Info */}
        {constante && (
          <Card>
            <CardHeader>
              <CardTitle>Constante Fiscale {constante.an_fiscal}</CardTitle>
              <CardDescription>Valorile folosite în calcule</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
                  <p className="text-sm text-muted-foreground">Salariu Minim</p>
                  <p className="font-semibold">{formatRON(constante.salariu_minim_brut)}</p>
                </div>
                <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
                  <p className="text-sm text-muted-foreground">Impozit Capital</p>
                  <p className="font-semibold">{constante.impozite.castig_capital}</p>
                </div>
                <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
                  <p className="text-sm text-muted-foreground">Impozit Dividende</p>
                  <p className="font-semibold">{constante.impozite.dividende}</p>
                </div>
                <div className="bg-slate-100 dark:bg-slate-800 rounded-lg p-3">
                  <p className="text-sm text-muted-foreground">SRL Micro (cu angajat)</p>
                  <p className="font-semibold">{constante.micro_srl.cu_angajat}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
