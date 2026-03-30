import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  AlertTriangle, CheckCircle, XCircle, TrendingUp, Shield,
  ArrowRight, Info, BookOpen, DollarSign, BarChart2,
  Building2, Globe, ChevronDown, ChevronUp, ExternalLink
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

const FAQ_ITEMS = [
  {
    q: 'Pot pierde mai mult decât am investit pe CFD-uri?',
    a: 'Da, absolut! CFD-urile cu efect de levier îți pot aduce pierderi ce depășesc suma investită inițial. De exemplu, cu un levier 1:10 și 1.000 EUR investiți, controlezi 10.000 EUR. O mișcare adversă de 10% înseamnă pierderea totală a celor 1.000 EUR, plus posibil mai mult (margin call). Pe acțiunile reale, nu poți pierde mai mult decât ai investit.'
  },
  {
    q: 'De ce Plus500 / eToro / XTB arată date diferite față de FinRomania?',
    a: 'Platforma FinRomania afișează datele REALE de la bursele oficiale (BVB, NYSE, etc.) care se opresc după orele de tranzacționare și sunt închise în weekenduri și sărbători. Platformele CFD ca Plus500 sunt deschise 24/7 deoarece nu tranzacționezi pe bursă — tranzacționezi cu brokerul, care poate seta orice preț dorește în afara orelor de bursă (preț "sintetic").'
  },
  {
    q: 'CFD-urile sunt legale în România?',
    a: 'Da, CFD-urile sunt produse financiare reglementate de ASF (Autoritatea de Supraveghere Financiară) în România și de ESMA la nivel european. Totuși, ESMA impune restricții stricte: levier maxim 1:30 pentru retail, avertismente obligatorii că 74-89% din conturile de retail pierd bani pe CFD-uri.'
  },
  {
    q: 'Dacă am dividende pe acțiunile CFD, le primesc?',
    a: 'Nu primești dividende reale. Brokerul poate credita un "ajustament de dividend" în contul tău, dar nu este același lucru cu un dividend oficial de la companie. Nu vei figura în registrul acționarilor companiei și nu ai drept de vot în Adunările Generale.'
  },
  {
    q: 'Cum cumpăr acțiuni BVB reale?',
    a: 'Prin brokeri autorizați BVB: Tradeville, BT Capital Partners, XTB (secțiunea "Acțiuni", nu CFD), Interactive Brokers. Deschizi cont, depui fonduri și cumperi acțiunile direct. Acțiunile apar în Depozitarul Central (Ro) și ești proprietar real.'
  },
  {
    q: 'Ce este margin call?',
    a: 'Când pierderile tale pe CFD-uri depășesc suma de garanție (marja), brokerul îți cere să depui bani suplimentari. Dacă nu depui, îți închide pozițiile automat, adesea în cel mai prost moment. Acest lucru nu există la acțiunile reale — acțiunile tale rămân ale tale chiar dacă prețul scade.'
  }
];

const COMPARISON_ROWS = [
  { aspect: 'Proprietate reală', real: true, cfd: false },
  { aspect: 'Dividende oficiale', real: true, cfd: false },
  { aspect: 'Drept de vot', real: true, cfd: false },
  { aspect: 'Risc limitat (max. suma investită)', real: true, cfd: false },
  { aspect: 'Tranzacționare 24/7', real: false, cfd: true },
  { aspect: 'Efect de levier inclus', real: false, cfd: true },
  { aspect: 'Supus impozitului pe dividende 16%', real: true, cfd: false },
  { aspect: 'Broker contraparte (conflict de interese)', real: false, cfd: true },
  { aspect: 'Reglementat BVB / Bursă oficială', real: true, cfd: false },
  { aspect: 'Poate genera margin call', real: false, cfd: true },
];

function FAQItem({ item }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        className="w-full text-left px-5 py-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
        onClick={() => setOpen(!open)}
        data-testid="faq-toggle"
      >
        <span className="font-medium pr-4">{item.q}</span>
        {open ? <ChevronUp className="w-5 h-5 flex-shrink-0 text-blue-600" /> : <ChevronDown className="w-5 h-5 flex-shrink-0 text-muted-foreground" />}
      </button>
      {open && (
        <div className="px-5 pb-5 pt-1 text-sm text-muted-foreground border-t bg-muted/20">
          {item.a}
        </div>
      )}
    </div>
  );
}

export default function CFDvsActiuniPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-12">

      {/* HERO */}
      <div className="text-center space-y-4 py-8">
        <Badge variant="destructive" className="text-sm px-3 py-1" data-testid="cfd-alert-badge">
          <AlertTriangle className="w-4 h-4 mr-1" /> Avertisment important pentru investitori
        </Badge>
        <h1 className="text-4xl sm:text-5xl font-bold leading-tight" data-testid="cfd-page-title">
          CFD-uri vs. Acțiuni Reale
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          De ce platformele ca Plus500 NU sunt burse reale și cum să îți protejezi banii investind corect
        </p>
      </div>

      {/* WARNING BANNER */}
      <Card className="border-red-300 bg-red-50 dark:bg-red-950/30 dark:border-red-800" data-testid="cfd-warning-card">
        <CardContent className="p-6">
          <div className="flex gap-4">
            <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-red-800 dark:text-red-300 mb-2">
                Știai că 74-89% din conturile retail pierd bani pe CFD-uri?
              </h2>
              <p className="text-red-700 dark:text-red-400 text-sm leading-relaxed">
                Aceasta este avertizarea obligatorie pe care orice broker CFD reglementat trebuie să o afișeze
                conform regulamentelor ESMA. Nu este o statistică inventată — este realitatea milioanelor de
                investitori care au confundat platformele CFD cu burse reale.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* CE SUNT CFD-URILE */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Info className="w-6 h-6 text-blue-600" />
          Ce este un CFD (Contract for Difference)?
        </h2>
        <div className="space-y-4 text-muted-foreground leading-relaxed">
          <p>
            Un <strong className="text-foreground">CFD (Contract for Difference)</strong> este un contract financiar
            derivat în care tu și brokerul sunteți de acord să schimbați diferența de preț a unui activ
            (acțiune, index, materie primă) de la momentul deschiderii până la închiderea contractului.
          </p>
          <Card className="bg-muted/40">
            <CardContent className="p-5">
              <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" /> Exemplu concret:
              </h3>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium text-foreground">Scenariul 1 — Acțiune reală TLV:</span><br />
                  Cumperi 100 acțiuni TLV la 18 RON = 1.800 RON. Dacă prețul crește la 20 RON, vinzi și câștigi 200 RON.
                  Dacă TLV plătește dividende de 2 RON/acțiune, primești 200 RON dividende în contul tău bancar.
                  Ești <strong>proprietarul</strong> acelor acțiuni, înregistrat la Depozitarul Central.
                </p>
                <hr className="border-border" />
                <p>
                  <span className="font-medium text-foreground">Scenariul 2 — CFD TLV pe Plus500:</span><br />
                  Deschizi un CFD pe TLV cu 1.800 RON. Dacă prețul crește la 20 RON, primești diferența de 200 RON.
                  Brokerul poate credita un "ajustament de dividend", dar nu ești proprietar — nu figurezi nicăieri ca acționar.
                  Dacă pierderea ta depășește 1.800 RON (din cauza levierului), poți ajunge pe minus.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* TABEL COMPARATIV */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <BarChart2 className="w-6 h-6 text-blue-600" />
          Comparație directă: Acțiuni Reale vs. CFD-uri
        </h2>
        <div className="overflow-x-auto rounded-lg border" data-testid="comparison-table">
          <table className="w-full">
            <thead>
              <tr className="bg-muted/60">
                <th className="text-left px-4 py-3 font-semibold text-sm">Aspect</th>
                <th className="text-center px-4 py-3 font-semibold text-sm text-green-700 dark:text-green-400">
                  Acțiuni Reale (BVB, NYSE)
                </th>
                <th className="text-center px-4 py-3 font-semibold text-sm text-red-700 dark:text-red-400">
                  CFD-uri (Plus500, eToro, etc.)
                </th>
              </tr>
            </thead>
            <tbody>
              {COMPARISON_ROWS.map((row, i) => (
                <tr key={i} className={i % 2 === 0 ? 'bg-background' : 'bg-muted/20'}>
                  <td className="px-4 py-3 text-sm font-medium">{row.aspect}</td>
                  <td className="px-4 py-3 text-center">
                    {row.real
                      ? <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      : <XCircle className="w-5 h-5 text-red-500 mx-auto" />}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {row.cfd
                      ? <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      : <XCircle className="w-5 h-5 text-red-500 mx-auto" />}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* DE CE PLUS500 E "DESCHIS" 24/7 */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Globe className="w-6 h-6 text-orange-500" />
          De ce Plus500 arată date 24/7, iar FinRomania arată "ÎNCHIS" vineri seara?
        </h2>
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20" data-testid="market-hours-card">
          <CardContent className="p-6 space-y-4">
            <p className="text-sm leading-relaxed">
              <strong>Bursa reală</strong> (NYSE, BVB, etc.) funcționează conform unui program oficial.
              NYSE este deschisă luni-vineri, 15:30 - 22:00 (ora României). Este <strong>ÎNCHISĂ</strong> în
              weekenduri, sărbători legale (Good Friday, Thanksgiving, Crăciun, etc.).
              FinRomania afișează date reale de la aceste burse, deci când bursa este închisă, afișăm ultimul preț oficial.
            </p>
            <hr className="border-orange-200" />
            <p className="text-sm leading-relaxed">
              <strong>Plus500 / CFD brokeri</strong> nu trimite ordinele tale la bursă.
              Tu tranzacționezi <em>cu brokerul</em>, care este contrapartea ta. El poate afișa prețuri
              "sintetice" 24/7, bazate pe futures sau calcule interne. Dacă piezi, brokerul câștigă direct.
              Acesta este modelul de business: <strong>conflict de interese fundamental</strong>.
            </p>
            <div className="flex items-start gap-3 bg-orange-100 dark:bg-orange-900/30 p-4 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-orange-800 dark:text-orange-300">
                Prețurile afișate sâmbătă sau duminică pe Plus500 pentru S&P 500 nu sunt prețuri reale
                de bursă — sunt prețuri generate de broker, care pot include spread-uri mai mari și
                nu reflectă realitatea pieței.
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* EFECTUL DE LEVIER */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-red-600" />
          Pericolul levierului — cum poți pierde mai mult decât ai investit
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <Card className="border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-green-700 dark:text-green-400 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" /> Acțiuni Reale (fără levier)
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>Investești <strong>1.000 RON</strong> în TLV la 18 RON/acțiune → 55 acțiuni</p>
              <p>TLV scade cu 50% → prețul devine 9 RON</p>
              <p>Portofoliul tău valorează acum <strong>495 RON</strong></p>
              <p className="text-green-700 font-medium">Pierdere maximă: 1.000 RON (suma investită)</p>
              <p className="text-muted-foreground">Acțiunile rămân ale tale. Prețul poate reveni.</p>
            </CardContent>
          </Card>
          <Card className="border-red-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-red-700 dark:text-red-400 flex items-center gap-2">
                <XCircle className="w-5 h-5" /> CFD cu levier 1:10
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p>Depui <strong>1.000 RON</strong> marjă și controlezi poziție de <strong>10.000 RON</strong></p>
              <p>Activul scade cu 10% → pierdere de 1.000 RON</p>
              <p className="text-red-700 font-medium">Ai pierdut 100% din suma depusă!</p>
              <p>Dacă piața scade mai mult → <strong>margin call</strong> sau sold negativ</p>
              <p className="text-muted-foreground">Poți ajunge să datorezi bani brokerului.</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CE SĂ FACI ÎN SCHIMB */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-600" />
          Cum investești corect — alternativele sănătoase
        </h2>
        <div className="grid sm:grid-cols-2 gap-4" data-testid="alternatives-section">
          {[
            {
              icon: Building2,
              title: 'BVB — Bursa de Valori București',
              desc: 'Cumperi acțiuni reale la companii românești (TLV, SNP, BRD, H2O, SNN). Primești dividende, ești proprietar real.',
              color: 'blue',
              link: '/stocks',
              linkText: 'Explorează acțiunile BVB'
            },
            {
              icon: DollarSign,
              title: 'Calculator Dividende PRO',
              desc: 'Planifică-ți veniturile pasive din dividende BVB cu calculatorul nostru fiscal 2026. Calculează impozit 16% și CASS exact.',
              color: 'green',
              link: '/calculator-dividende',
              linkText: 'Calculează dividendele tale'
            },
            {
              icon: TrendingUp,
              title: 'Screener PRO',
              desc: 'Identifică cele mai bune oportunități pe BVB cu indicatori tehnici (RSI, MACD) și fundamentali (P/E, ROE).',
              color: 'amber',
              link: '/screener-pro',
              linkText: 'Deschide Screener PRO'
            },
            {
              icon: BookOpen,
              title: 'Academia FinRomania',
              desc: 'Învață de la zero cum să investești corect pe bursă, ce sunt indicatorii tehnici și cum să citești situațiile financiare.',
              color: 'orange',
              link: '/trading-school',
              linkText: 'Începe să înveți'
            }
          ].map((item, i) => (
            <Card key={i} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5">
                <div className={`w-10 h-10 rounded-lg bg-${item.color}-100 dark:bg-${item.color}-900/30 flex items-center justify-center mb-3`}>
                  <item.icon className={`w-5 h-5 text-${item.color}-600`} />
                </div>
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground mb-3">{item.desc}</p>
                <Link to={item.link}>
                  <Button variant="outline" size="sm" className="w-full">
                    {item.linkText} <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* BROKERI AUTORIZATI */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <CheckCircle className="w-6 h-6 text-green-600" />
          Brokeri autorizați pentru acțiuni BVB reale
        </h2>
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground mb-4">
              Aceștia sunt brokeri reglementați ASF/BVB prin care poți cumpăra acțiuni reale, nu CFD-uri:
            </p>
            <div className="grid sm:grid-cols-2 gap-3">
              {[
                { name: 'Tradeville', desc: 'Broker românesc, cel mai utilizat pe BVB', url: 'https://www.tradeville.ro' },
                { name: 'BT Capital Partners', desc: 'Subsidiara Banca Transilvania, broker autorizat BVB', url: 'https://www.btcapital.ro' },
                { name: 'XTB (secțiunea Acțiuni)', desc: 'Atenție: alege "Acțiuni" nu "CFD". XTB oferă ambele.', url: 'https://www.xtb.com/ro' },
                { name: 'Interactive Brokers', desc: 'International, comisioane mici, acces global', url: 'https://www.interactivebrokers.com' },
              ].map((broker, i) => (
                <div key={i} className="flex items-start gap-3 p-3 border rounded-lg">
                  <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">{broker.name}</p>
                    <p className="text-xs text-muted-foreground">{broker.desc}</p>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground mt-4">
              * FinRomania nu este afiliat cu niciun broker și nu primește comisioane pentru recomandări. Lista are scop pur educațional.
            </p>
          </CardContent>
        </Card>
      </section>

      {/* FAQ */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-blue-600" />
          Întrebări frecvente
        </h2>
        <div className="space-y-2" data-testid="faq-section">
          {FAQ_ITEMS.map((item, i) => (
            <FAQItem key={i} item={item} />
          ))}
        </div>
      </section>

      {/* DISCLAIMER */}
      <Card className="bg-muted/30 border-dashed">
        <CardContent className="p-5">
          <p className="text-xs text-muted-foreground leading-relaxed">
            <strong>Disclaimer:</strong> Conținutul acestei pagini are scop exclusiv educațional și nu constituie
            consultanță financiară. FinRomania nu este autorizat ca consultant de investiții.
            Investițiile implică riscuri. Înainte de a investi, consultați un specialist financiar autorizat ASF.
            Datele despre brokeri sunt furnizate cu titlu informativ și pot fi actualizate independent.
          </p>
        </CardContent>
      </Card>

      {/* CTA FINAL */}
      <div className="text-center space-y-4 py-6 border-t" data-testid="cfd-page-cta">
        <h2 className="text-2xl font-bold">Investește inteligent, nu specula orbește</h2>
        <p className="text-muted-foreground">
          Folosește FinRomania pentru date reale de la bursele oficiale și ia decizii informate.
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link to="/stocks">
            <Button data-testid="cta-stocks-btn">
              <TrendingUp className="w-4 h-4 mr-2" /> Acțiuni BVB
            </Button>
          </Link>
          <Link to="/calculator-dividende">
            <Button variant="outline" data-testid="cta-calculator-btn">
              <DollarSign className="w-4 h-4 mr-2" /> Calculator Dividende
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
