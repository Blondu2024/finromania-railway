import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Plus, Trash2, Calculator, AlertTriangle, Info, AlertCircle, Building2, User, Briefcase } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const ENTITY_TYPES = [
  { value: 'pf', label: 'Persoană Fizică (PF)', icon: User },
  { value: 'pfa_norma', label: 'PFA - Normă de Venit', icon: Briefcase },
  { value: 'pfa_real', label: 'PFA - Sistem Real', icon: Briefcase },
  { value: 'pfi', label: 'PFI - Profesie Liberală', icon: Briefcase },
  { value: 'srl_micro', label: 'SRL Micro-întreprindere', icon: Building2 },
  { value: 'srl_profit', label: 'SRL - Impozit Profit', icon: Building2 },
];

const CAEN_CODES = [
  { value: 'none', label: 'Selectează (opțional)' },
  { value: '6201', label: '6201 - Software la comandă (IT)' },
  { value: '6202', label: '6202 - Consultanță IT' },
  { value: '6209', label: '6209 - Alte servicii IT' },
  { value: '6311', label: '6311 - Prelucrare date, web hosting' },
  { value: '6312', label: '6312 - Portaluri web' },
  { value: '8621', label: '8621 - Asistență medicală generală' },
  { value: '8622', label: '8622 - Asistență medicală specializată' },
  { value: '8559', label: '8559 - Alte forme de învățământ' },
  { value: '4711', label: '4711 - Comerț cu amănuntul' },
  { value: '4719', label: '4719 - Comerț cu amănuntul nespecializat' },
  { value: '7022', label: '7022 - Consultanță pentru afaceri' },
];

export default function FiscalSimulatorPage() {
  const [entities, setEntities] = useState([
    { tip: 'srl_micro', nume: '', cod_caen: 'none', venit_anual_estimat: 0, procent_detinere: 100, are_angajati: false, platitor_tva: false, norma_venit_anuala: 0, an_infiintare: null, marja_profit: 20 }
  ]);
  const [areSalariu, setAreSalariu] = useState(false);
  const [salariuBrut, setSalariuBrut] = useState(0);
  const [alteAsocieri, setAlteAsocieri] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const addEntity = () => {
    setEntities([...entities, {
      tip: 'srl_micro',
      nume: '',
      cod_caen: 'none',
      venit_anual_estimat: 0,
      procent_detinere: 100,
      are_angajati: false,
      platitor_tva: false,
      norma_venit_anuala: 0,
      an_infiintare: null,
      marja_profit: 20
    }]);
  };

  const removeEntity = (index) => {
    setEntities(entities.filter((_, i) => i !== index));
  };

  const updateEntity = (index, field, value) => {
    const updated = [...entities];
    updated[index] = { ...updated[index], [field]: value };
    setEntities(updated);
  };

  const simulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/fiscal-simulator/simuleaza`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entitati: entities,
          are_salariu: areSalariu,
          salariu_brut_lunar: salariuBrut,
          alte_asocieri_peste_25: alteAsocieri
        })
      });
      
      if (!response.ok) throw new Error('Eroare la simulare');
      
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getAlertVariant = (tip) => {
    switch (tip) {
      case 'danger': return 'destructive';
      case 'warning': return 'default';
      default: return 'default';
    }
  };

  const getAlertIcon = (tip) => {
    switch (tip) {
      case 'danger': return <AlertCircle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      default: return <Info className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2">Simulator Fiscal Antreprenor</h1>
        <p className="text-muted-foreground">
          Înțelege cum funcționează impozitarea pentru multiple entități
        </p>
        <Badge variant="outline" className="mt-2 text-orange-600 border-orange-300">
          EDUCATIV - Nu reprezintă consiliere fiscală
        </Badge>
      </div>

      {/* Disclaimer */}
      <Alert className="mb-6 bg-amber-50 border-amber-200">
        <AlertTriangle className="h-4 w-4 text-amber-600" />
        <AlertTitle className="text-amber-800">Scop Educativ - Reguli 2026</AlertTitle>
        <AlertDescription className="text-amber-700">
          Acest simulator folosește regulile fiscale pentru <strong>2026</strong> (OUG 89/2025, OUG 8/2026). 
          Pentru decizii fiscale reale, consultă obligatoriu un expert contabil autorizat!
        </AlertDescription>
      </Alert>

      {/* Entities Input */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            Entitățile Tale
          </CardTitle>
          <CardDescription>
            Adaugă toate formele juridice pe care le deții (SRL, PFA, PFI, etc.)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {entities.map((entity, index) => (
            <div key={index} className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-900 space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-medium">Entitate #{index + 1}</span>
                {entities.length > 1 && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => removeEntity(index)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Tip Entitate</Label>
                  <Select 
                    value={entity.tip} 
                    onValueChange={(v) => updateEntity(index, 'tip', v)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ENTITY_TYPES.map(t => (
                        <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Nume (opțional)</Label>
                  <Input 
                    placeholder="ex: SRL-ul meu IT"
                    value={entity.nume}
                    onChange={(e) => updateEntity(index, 'nume', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Cod CAEN Principal</Label>
                  <Select 
                    value={entity.cod_caen} 
                    onValueChange={(v) => updateEntity(index, 'cod_caen', v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selectează..." />
                    </SelectTrigger>
                    <SelectContent>
                      {CAEN_CODES.map(c => (
                        <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Venit Anual Estimat (RON)</Label>
                  <Input 
                    type="number"
                    min="0"
                    value={entity.venit_anual_estimat}
                    onChange={(e) => updateEntity(index, 'venit_anual_estimat', parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>% Deținere</Label>
                  <Input 
                    type="number"
                    min="0"
                    max="100"
                    value={entity.procent_detinere}
                    onChange={(e) => updateEntity(index, 'procent_detinere', parseFloat(e.target.value) || 0)}
                  />
                </div>

                {/* Câmpuri condiționale */}
                {entity.tip === 'pfa_norma' && (
                  <div className="space-y-2">
                    <Label>Norma de Venit ANAF (RON/an)</Label>
                    <Input 
                      type="number"
                      min="0"
                      placeholder="Norma stabilită de ANAF"
                      value={entity.norma_venit_anuala || ''}
                      onChange={(e) => updateEntity(index, 'norma_venit_anuala', parseFloat(e.target.value) || 0)}
                    />
                    <p className="text-xs text-muted-foreground">Lasă 0 dacă nu știi - se va folosi venitul estimat</p>
                  </div>
                )}

                {(entity.tip === 'srl_micro' || entity.tip === 'srl_profit') && (
                  <div className="space-y-2">
                    <Label>An Înființare</Label>
                    <Input
                      type="number"
                      min="2000"
                      max="2026"
                      placeholder="ex: 2024"
                      value={entity.an_infiintare || ''}
                      onChange={(e) => updateEntity(index, 'an_infiintare', parseInt(e.target.value) || null)}
                    />
                    <p className="text-xs text-muted-foreground">Important pentru regimul fiscal în primul an</p>
                  </div>
                )}

                {entity.tip === 'srl_profit' && (
                  <div className="space-y-2">
                    <Label>Marjă Profit Estimată (%)</Label>
                    <Input
                      type="number"
                      min="1"
                      max="90"
                      value={entity.marja_profit || 20}
                      onChange={(e) => updateEntity(index, 'marja_profit', parseFloat(e.target.value) || 20)}
                    />
                    <p className="text-xs text-muted-foreground">
                      Profit / Venit × 100. Ex: IT/Consulting ~40-50%, Retail ~5-10%, Servicii ~20-30%
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-between pt-6">
                  <div className="flex items-center space-x-2">
                    <Switch 
                      checked={entity.are_angajati}
                      onCheckedChange={(v) => updateEntity(index, 'are_angajati', v)}
                    />
                    <Label>Are angajați</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch 
                      checked={entity.platitor_tva}
                      onCheckedChange={(v) => updateEntity(index, 'platitor_tva', v)}
                    />
                    <Label>Plătitor TVA</Label>
                  </div>
                </div>
              </div>
            </div>
          ))}

          <Button variant="outline" onClick={addEntity} className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Adaugă Entitate
          </Button>
        </CardContent>
      </Card>

      {/* Întrebare critică despre asocieri */}
      <Card className="mb-6 border-amber-300 bg-amber-50 dark:bg-amber-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            Întrebare Importantă
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-amber-800 dark:text-amber-300">Ești asociat/administrator în ALTE firme cu peste 25% deținere?</Label>
              <p className="text-sm text-amber-700 dark:text-amber-400">
                (Firme care NU sunt incluse în lista de mai sus)
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                Acest lucru afectează calculul agregat pentru pragul micro de 100.000 EUR!
              </p>
            </div>
            <Switch checked={alteAsocieri} onCheckedChange={setAlteAsocieri} />
          </div>
        </CardContent>
      </Card>

      {/* Additional Options */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Alte Venituri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label>Ai salariu cu CASS plătit?</Label>
              <p className="text-sm text-muted-foreground">
                Dacă da, nu mai datorezi CASS din PFA/PFI
              </p>
            </div>
            <Switch checked={areSalariu} onCheckedChange={setAreSalariu} />
          </div>
        </CardContent>
      </Card>

      {/* Simulate Button */}
      <Button 
        onClick={simulate} 
        disabled={loading || entities.length === 0}
        className="w-full mb-8"
        size="lg"
      >
        <Calculator className="w-5 h-5 mr-2" />
        {loading ? 'Se calculează...' : 'Simulează Situația Fiscală'}
      </Button>

      {/* Error */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Eroare</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Rezultat Simulare</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">Total Venituri</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {result.total_venituri.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-red-50 dark:bg-red-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">Impozite Estimate</p>
                  <p className="text-2xl font-bold text-red-600">
                    {result.total_impozite_estimate.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">Rata Efectivă</p>
                  <p className="text-2xl font-bold text-green-600">
                    {result.rata_efectiva_globala.toFixed(1)}%
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Warnings */}
          {result.avertismente && result.avertismente.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-amber-500" />
                  Avertismente Importante
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.avertismente.map((a, i) => (
                  <Alert key={i} variant={getAlertVariant(a.tip)}>
                    {getAlertIcon(a.tip)}
                    <AlertTitle>{a.titlu}</AlertTitle>
                    <AlertDescription>
                      {a.descriere}
                      {a.actiune_recomandata && (
                        <p className="mt-2 font-medium">{a.actiune_recomandata}</p>
                      )}
                    </AlertDescription>
                  </Alert>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Entity Details */}
          <Card>
            <CardHeader>
              <CardTitle>Detalii pe Entități</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {result.entitati.map((e, i) => (
                <div key={i} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-semibold">{e.nume}</h4>
                      <Badge variant="outline">{e.tip.toUpperCase()}</Badge>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold">{e.impozit_estimat.toLocaleString('ro-RO')} RON</p>
                      <p className="text-sm text-muted-foreground">
                        din {e.venit.toLocaleString('ro-RO')} RON ({e.rata_impozitare}%)
                      </p>
                    </div>
                  </div>
                  
                  <p className="text-sm mb-2">
                    <span className="font-medium">TVA:</span> {e.regim_tva}
                  </p>
                  
                  {e.scutiri_active && e.scutiri_active.length > 0 && (
                    <div className="mb-2">
                      {e.scutiri_active.map((s, j) => (
                        <Badge key={j} variant="secondary" className="mr-1 mb-1 text-green-600">
                          {s}
                        </Badge>
                      ))}
                    </div>
                  )}

                  {/* Pași de calcul - NOU */}
                  {e.pasi_calcul && e.pasi_calcul.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-zinc-900 rounded-lg">
                      <p className="text-xs font-medium text-muted-foreground mb-2">Cum s-a calculat:</p>
                      <div className="space-y-1">
                        {e.pasi_calcul.map((pas, j) => (
                          <div key={j} className="text-xs">
                            <span className="font-medium">{pas.descriere}</span>
                            {pas.formula && <span className="text-blue-600 ml-2">{pas.formula}</span>}
                            {pas.rezultat && <span className="text-green-600 ml-2">→ {pas.rezultat}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Comparații - NOU */}
                  {e.comparatii && e.comparatii.length > 0 && (
                    <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-950/30 rounded-lg">
                      <p className="text-xs font-medium text-blue-700 dark:text-blue-400 mb-2">Comparație cu alternative:</p>
                      {e.comparatii.map((c, j) => (
                        <div key={j} className="text-xs flex justify-between items-center py-1 border-b border-blue-100 last:border-0">
                          <span>{c.alternativa}</span>
                          <span className={c.diferenta < 0 ? 'text-green-600' : 'text-red-600'}>
                            {c.diferenta < 0 ? '↓' : '↑'} {Math.abs(c.diferenta).toLocaleString('ro-RO')} RON
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {e.observatii && e.observatii.length > 0 && (
                    <ul className="text-sm text-muted-foreground list-disc list-inside mt-3">
                      {e.observatii.map((o, j) => (
                        <li key={j}>{o}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Sumar Comparativ Global - NOU */}
          {result.sumar_comparativ && (
            <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20">
              <CardHeader>
                <CardTitle className="text-blue-700 dark:text-blue-400">Sumar Comparativ</CardTitle>
                <CardDescription>Dacă toate veniturile ar fi pe un singur regim</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">Ca Micro (1%)</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_micro?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">Ca Profit (16%)</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_profit?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">Ca PFA (10%)</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_pfa?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded">
                    <p className="text-xs text-green-700 dark:text-green-400">Economie vs Profit</p>
                    <p className="font-bold text-green-600">{result.sumar_comparativ.economie_vs_profit?.toLocaleString('ro-RO')} RON</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Disclaimer */}
          <Alert className="bg-gray-100 dark:bg-gray-900">
            <Info className="h-4 w-4" />
            <AlertTitle>Disclaimer</AlertTitle>
            <AlertDescription className="whitespace-pre-line text-sm">
              {result.disclaimer}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
