import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Plus, Trash2, Calculator, AlertTriangle, Info, AlertCircle, Building2, User, Briefcase, Wallet, ArrowRightLeft, Users, BadgeCheck } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

// ============================================
// SALARY CALCULATOR COMPONENT
// ============================================

function SalaryCalculator({ t }) {
  const [suma, setSuma] = useState(5000);
  const [tipCalcul, setTipCalcul] = useState('brut_la_net');
  const [sector, setSector] = useState('normal');
  const [nrPersoane, setNrPersoane] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const SECTORS = [
    { value: 'normal', label: t('simulator.sectorNormal') },
    { value: 'it', label: t('simulator.sectorIT') },
    { value: 'constructii', label: t('simulator.sectorConstructii') },
    { value: 'agricultura', label: t('simulator.sectorAgricultura') },
    { value: 'alimentar', label: t('simulator.sectorAlimentar') },
  ];

  const calculate = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/fiscal-simulator/calcul-salariu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          suma,
          tip_calcul: tipCalcul,
          sector,
          numar_persoane_intretinere: nrPersoane,
          tip_contract: 'full_time'
        })
      });
      if (!response.ok) throw new Error(t('simulator.errorSimulation'));
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSectorLabel = (val) => {
    const s = SECTORS.find(s => s.value === val);
    return s ? s.label : val;
  };

  return (
    <div className="space-y-6">
      {/* Input Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wallet className="w-5 h-5" />
            {t('simulator.salaryCalc')}
          </CardTitle>
          <CardDescription>{t('simulator.salaryCalcDesc')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Tip calcul toggle */}
          <div className="flex gap-2">
            <Button
              variant={tipCalcul === 'brut_la_net' ? 'default' : 'outline'}
              onClick={() => setTipCalcul('brut_la_net')}
              className="flex-1"
              size="sm"
            >
              <ArrowRightLeft className="w-4 h-4 mr-1" />
              {t('simulator.brutToNet')}
            </Button>
            <Button
              variant={tipCalcul === 'net_la_brut' ? 'default' : 'outline'}
              onClick={() => setTipCalcul('net_la_brut')}
              className="flex-1"
              size="sm"
            >
              <ArrowRightLeft className="w-4 h-4 mr-1" />
              {t('simulator.netToBrut')}
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Sumă */}
            <div className="space-y-2">
              <Label>{t('simulator.salaryAmount')}</Label>
              <Input
                type="number"
                min="0"
                value={suma}
                onChange={(e) => setSuma(parseFloat(e.target.value) || 0)}
                placeholder={tipCalcul === 'brut_la_net' ? t('simulator.salaryBrutPlaceholder') : t('simulator.salaryNetPlaceholder')}
              />
            </div>

            {/* Sector */}
            <div className="space-y-2">
              <Label>{t('simulator.sector')}</Label>
              <Select value={sector} onValueChange={setSector}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {SECTORS.map(s => (
                    <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Nr persoane întreținere */}
            <div className="space-y-2 md:col-span-2">
              <Label className="flex items-center gap-2">
                <Users className="w-4 h-4" />
                {t('simulator.persIntretinere')}: {nrPersoane}
              </Label>
              <div className="flex items-center gap-3">
                {[0, 1, 2, 3, 4].map(n => (
                  <Button
                    key={n}
                    variant={nrPersoane === n ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setNrPersoane(n)}
                    className="w-10 h-10"
                  >
                    {n}
                  </Button>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">{t('simulator.persIntretinereHint')}</p>
            </div>
          </div>

          {/* Calculate Button */}
          <Button onClick={calculate} disabled={loading || suma <= 0} className="w-full" size="lg">
            <Calculator className="w-5 h-5 mr-2" />
            {loading ? t('fiscal.calculating') : t('simulator.calculate')}
          </Button>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{t('simulator.errorLabel')}</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Main Result Card */}
          <Card>
            <CardHeader>
              <CardTitle>{t('simulator.salaryResult')}</CardTitle>
            </CardHeader>
            <CardContent>
              {/* Big numbers */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('simulator.salaryBrut')}</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {result.salariu_brut?.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('simulator.salaryNet')}</p>
                  <p className="text-2xl font-bold text-green-600">
                    {result.salariu_net?.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('simulator.costTotalAngajator')}</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {result.cost_total_angajator?.toLocaleString('ro-RO')} RON
                  </p>
                </div>
              </div>

              {/* Exemptions */}
              {result.scutiri_aplicate && result.scutiri_aplicate.length > 0 && (
                <div className="mb-4">
                  {result.scutiri_aplicate.map((s, i) => (
                    <Badge key={i} variant="secondary" className="mr-1 mb-1 text-green-600">
                      <BadgeCheck className="w-3 h-3 mr-1" />
                      {s}
                    </Badge>
                  ))}
                </div>
              )}

              {/* Calculation Steps — Waterfall */}
              <div className="p-4 bg-gray-50 dark:bg-zinc-900 rounded-lg">
                <p className="text-sm font-medium text-muted-foreground mb-3">{t('simulator.pasiiCalcul')}</p>
                <div className="space-y-2">
                  {result.pasi_calcul?.map((pas, i) => (
                    <div key={i} className={`flex justify-between items-center py-1.5 px-2 rounded text-sm ${
                      pas.semn === '=' ? 'bg-white dark:bg-zinc-800 font-semibold border' :
                      pas.semn === 'info' ? 'text-blue-600' : ''
                    }`}>
                      <div className="flex items-center gap-2">
                        {pas.semn === '-' && <span className="text-red-500 font-mono w-4">−</span>}
                        {pas.semn === '+' && <span className="text-orange-500 font-mono w-4">+</span>}
                        {pas.semn === '=' && <span className="text-green-600 font-mono w-4">=</span>}
                        {pas.semn === '' && <span className="font-mono w-4"> </span>}
                        {pas.semn === 'info' && <Info className="w-3 h-3 text-blue-500" />}
                        <span>{pas.descriere}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        {pas.formula && <span className="text-xs text-muted-foreground hidden md:inline">{pas.formula}</span>}
                        <span className={`font-mono ${
                          pas.semn === '-' ? 'text-red-600' :
                          pas.semn === '+' ? 'text-orange-600' :
                          pas.semn === '=' ? 'text-green-600 font-bold' :
                          pas.semn === 'info' ? 'text-blue-600' : ''
                        }`}>
                          {pas.valoare?.toLocaleString('ro-RO')} RON
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sector Comparison Table */}
          {result.comparatie_sectoare && result.comparatie_sectoare.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ArrowRightLeft className="w-5 h-5" />
                  {t('simulator.comparatieSectoare')}
                </CardTitle>
                <CardDescription>{t('simulator.comparatieDesc')}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2 px-2">{t('simulator.sectorCol')}</th>
                        <th className="text-right py-2 px-2">{t('simulator.netCol')}</th>
                        <th className="text-right py-2 px-2">{t('simulator.impozitCol')}</th>
                        <th className="text-right py-2 px-2 hidden md:table-cell">{t('simulator.costCol')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.comparatie_sectoare.map((comp, i) => (
                        <tr key={i} className={`border-b last:border-0 ${comp.sector === result.sector ? 'bg-blue-50 dark:bg-blue-950/30 font-medium' : ''}`}>
                          <td className="py-2 px-2">
                            {getSectorLabel(comp.sector)}
                            {comp.scutiri?.length > 0 && (
                              <Badge variant="outline" className="ml-2 text-xs text-green-600">scutit</Badge>
                            )}
                          </td>
                          <td className="text-right py-2 px-2 font-mono text-green-600">
                            {comp.net?.toLocaleString('ro-RO')}
                          </td>
                          <td className="text-right py-2 px-2 font-mono text-red-600">
                            {comp.impozit?.toLocaleString('ro-RO')}
                          </td>
                          <td className="text-right py-2 px-2 font-mono hidden md:table-cell">
                            {comp.cost_angajator?.toLocaleString('ro-RO')}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Disclaimer */}
          <Alert className="bg-gray-100 dark:bg-gray-900">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-sm">
              {t('simulator.salaryDisclaimer')}
            </AlertDescription>
          </Alert>
        </>
      )}
    </div>
  );
}

// ============================================
// ENTITY TYPES & CAEN CODES
// ============================================

function getEntityTypes(t) {
  return [
    { value: 'pf', label: t('simulator.entityPF'), icon: User },
    { value: 'pfa_norma', label: t('simulator.entityPFANorma'), icon: Briefcase },
    { value: 'pfa_real', label: t('simulator.entityPFAReal'), icon: Briefcase },
    { value: 'pfi', label: t('simulator.entityPFI'), icon: Briefcase },
    { value: 'srl_micro', label: t('simulator.entitySRLMicro'), icon: Building2 },
    { value: 'srl_profit', label: t('simulator.entitySRLProfit'), icon: Building2 },
  ];
}

function getCaenCodes(t) {
  return [
    { value: 'none', label: t('simulator.caenNone') },
    { value: '6201', label: t('simulator.caen6201') },
    { value: '6202', label: t('simulator.caen6202') },
    { value: '6209', label: t('simulator.caen6209') },
    { value: '6311', label: t('simulator.caen6311') },
    { value: '6312', label: t('simulator.caen6312') },
    { value: '8621', label: t('simulator.caen8621') },
    { value: '8622', label: t('simulator.caen8622') },
    { value: '8559', label: t('simulator.caen8559') },
    { value: '4711', label: t('simulator.caen4711') },
    { value: '4719', label: t('simulator.caen4719') },
    { value: '7022', label: t('simulator.caen7022') },
  ];
}

export default function FiscalSimulatorPage() {
  const { t } = useTranslation();
  const ENTITY_TYPES = getEntityTypes(t);
  const CAEN_CODES = getCaenCodes(t);
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

      if (!response.ok) throw new Error(t('simulator.errorSimulation'));

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
    <>
    <SEO title={`${t('simulator.title')} | FinRomania`} description={t('simulator.subtitle')} />
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2">{t('simulator.title')}</h1>
        <p className="text-muted-foreground">
          {t('simulator.subtitle')}
        </p>
        <Badge variant="outline" className="mt-2 text-orange-600 border-orange-300">
          {t('simulator.educational')}
        </Badge>
      </div>

      {/* Disclaimer */}
      <Alert className="mb-6 bg-amber-50 border-amber-200">
        <AlertTriangle className="h-4 w-4 text-amber-600" />
        <AlertTitle className="text-amber-800">{t('simulator.rules2026')}</AlertTitle>
        <AlertDescription className="text-amber-700">
          {t('simulator.rules2026Desc')}
        </AlertDescription>
      </Alert>

      {/* Tabs: Calculator Salariu | Simulator Entități */}
      <Tabs defaultValue="salary" className="mb-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="salary" className="flex items-center gap-2">
            <Wallet className="w-4 h-4" />
            {t('simulator.salaryCalcTab')}
          </TabsTrigger>
          <TabsTrigger value="entities" className="flex items-center gap-2">
            <Building2 className="w-4 h-4" />
            {t('simulator.simulatorTab')}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="salary">
          <SalaryCalculator t={t} />
        </TabsContent>

        <TabsContent value="entities">

      {/* Entities Input */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            {t('simulator.yourEntities')}
          </CardTitle>
          <CardDescription>
            {t('simulator.addEntitiesDesc')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {entities.map((entity, index) => (
            <div key={index} className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-900 space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-medium">{t('simulator.entity')} #{index + 1}</span>
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
                  <Label>{t('simulator.entityType')}</Label>
                  <Select
                    value={entity.tip}
                    onValueChange={(v) => updateEntity(index, 'tip', v)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {ENTITY_TYPES.map(et => (
                        <SelectItem key={et.value} value={et.value}>{et.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>{t('simulator.nameOptional')}</Label>
                  <Input
                    placeholder={t('simulator.namePlaceholder')}
                    value={entity.nume}
                    onChange={(e) => updateEntity(index, 'nume', e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>{t('simulator.caenCode')}</Label>
                  <Select
                    value={entity.cod_caen}
                    onValueChange={(v) => updateEntity(index, 'cod_caen', v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('simulator.selectPlaceholder')} />
                    </SelectTrigger>
                    <SelectContent>
                      {CAEN_CODES.map(c => (
                        <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>{t('simulator.annualRevenue')}</Label>
                  <Input
                    type="number"
                    min="0"
                    value={entity.venit_anual_estimat}
                    onChange={(e) => updateEntity(index, 'venit_anual_estimat', parseFloat(e.target.value) || 0)}
                  />
                </div>

                <div className="space-y-2">
                  <Label>{t('simulator.ownershipPercent')}</Label>
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
                    <Label>{t('simulator.normANAF')}</Label>
                    <Input
                      type="number"
                      min="0"
                      placeholder={t('simulator.normPlaceholder')}
                      value={entity.norma_venit_anuala || ''}
                      onChange={(e) => updateEntity(index, 'norma_venit_anuala', parseFloat(e.target.value) || 0)}
                    />
                    <p className="text-xs text-muted-foreground">{t('simulator.normHint')}</p>
                  </div>
                )}

                {(entity.tip === 'srl_micro' || entity.tip === 'srl_profit') && (
                  <div className="space-y-2">
                    <Label>{t('simulator.foundingYear')}</Label>
                    <Input
                      type="number"
                      min="2000"
                      max="2026"
                      placeholder={t('simulator.foundingYearPlaceholder')}
                      value={entity.an_infiintare || ''}
                      onChange={(e) => updateEntity(index, 'an_infiintare', parseInt(e.target.value) || null)}
                    />
                    <p className="text-xs text-muted-foreground">{t('simulator.foundingYearHint')}</p>
                  </div>
                )}

                {entity.tip === 'srl_profit' && (
                  <div className="space-y-2">
                    <Label>{t('simulator.profitMargin')}</Label>
                    <Input
                      type="number"
                      min="1"
                      max="90"
                      value={entity.marja_profit || 20}
                      onChange={(e) => updateEntity(index, 'marja_profit', parseFloat(e.target.value) || 20)}
                    />
                    <p className="text-xs text-muted-foreground">
                      {t('simulator.profitMarginHint')}
                    </p>
                  </div>
                )}

                <div className="flex items-center justify-between pt-6">
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={entity.are_angajati}
                      onCheckedChange={(v) => updateEntity(index, 'are_angajati', v)}
                    />
                    <Label>{t('simulator.hasEmployees')}</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      checked={entity.platitor_tva}
                      onCheckedChange={(v) => updateEntity(index, 'platitor_tva', v)}
                    />
                    <Label>{t('simulator.vatPayer')}</Label>
                  </div>
                </div>
              </div>
            </div>
          ))}

          <Button variant="outline" onClick={addEntity} className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            {t('simulator.addEntity')}
          </Button>
        </CardContent>
      </Card>

      {/* Întrebare critică despre asocieri */}
      <Card className="mb-6 border-amber-300 bg-amber-50 dark:bg-amber-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            {t('simulator.importantQuestion')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label className="text-amber-800 dark:text-amber-300">{t('simulator.otherAssociations')}</Label>
              <p className="text-sm text-amber-700 dark:text-amber-400">
                {t('simulator.otherAssociationsHint')}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {t('simulator.otherAssociationsImpact')}
              </p>
            </div>
            <Switch checked={alteAsocieri} onCheckedChange={setAlteAsocieri} />
          </div>
        </CardContent>
      </Card>

      {/* Additional Options */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('simulator.otherRevenue')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <Label>{t('simulator.hasSalaryWithCASS')}</Label>
              <p className="text-sm text-muted-foreground">
                {t('simulator.cassFromSalaryHint')}
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
        {loading ? t('fiscal.calculating') : t('simulator.simulate')}
      </Button>

      {/* Error */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>{t('simulator.errorLabel')}</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Summary */}
          <Card>
            <CardHeader>
              <CardTitle>{t('simulator.result')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('simulator.totalRevenue')}</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {result.total_venituri.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-red-50 dark:bg-red-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('simulator.estimatedTaxes')}</p>
                  <p className="text-2xl font-bold text-red-600">
                    {result.total_impozite_estimate.toLocaleString('ro-RO')} RON
                  </p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg text-center">
                  <p className="text-sm text-muted-foreground">{t('fiscal.effectiveRate')}</p>
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
                  {t('simulator.warnings')}
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
              <CardTitle>{t('simulator.entityDetails')}</CardTitle>
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

                  {/* Pași de calcul */}
                  {e.pasi_calcul && e.pasi_calcul.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 dark:bg-zinc-900 rounded-lg">
                      <p className="text-xs font-medium text-muted-foreground mb-2">{t('simulator.howCalculated')}</p>
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

                  {/* Comparații */}
                  {e.comparatii && e.comparatii.length > 0 && (
                    <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-950/30 rounded-lg">
                      <p className="text-xs font-medium text-blue-700 dark:text-blue-400 mb-2">{t('simulator.alternatives')}</p>
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

          {/* Sumar Comparativ Global */}
          {result.sumar_comparativ && (
            <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20">
              <CardHeader>
                <CardTitle className="text-blue-700 dark:text-blue-400">{t('simulator.comparativeSummary')}</CardTitle>
                <CardDescription>{t('simulator.allOnOneRegime')}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-center">
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">{t('simulator.asMicro')}</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_micro?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">{t('simulator.asProfit')}</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_profit?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-white dark:bg-gray-800 rounded">
                    <p className="text-xs text-muted-foreground">{t('simulator.asPFA')}</p>
                    <p className="font-bold">{result.sumar_comparativ.total_ca_pfa?.toLocaleString('ro-RO')} RON</p>
                  </div>
                  <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded">
                    <p className="text-xs text-green-700 dark:text-green-400">{t('simulator.savingsVsProfit')}</p>
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

        </TabsContent>
      </Tabs>
    </div>
    </>
  );
}
