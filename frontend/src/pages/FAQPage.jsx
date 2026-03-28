import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, Shield, DollarSign, GraduationCap, Crown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

const FAQ_DATA = [
  {
    category: 'General',
    icon: <HelpCircle className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este FinRomania?',
        a: 'FinRomania este o platformă de educație financiară și analiză de piață pentru investitorii români. Oferim date live BVB și Global Markets, instrumente de analiză, cursuri gratuite și asistent AI - totul în română!'
      },
      {
        q: 'Este cu adevărat gratuit?',
        a: 'DA! Planul GRATUIT include: educație completă (32 lecții), date BVB și Global, știri, convertor valutar, 5 întrebări AI/zi. Planul PRO (49 RON/lună) deblochează: Calculator Fiscal, AI nelimitat, date mai rapide, indicatori tehnici.'
      },
      {
        q: 'Datele sunt reale?',
        a: 'DA! Colaborăm cu furnizori licențiați de date financiare pentru BVB, piețe globale și cursuri BNR. Știrile din surse verificate (ZF, Capital, Bursa). Toate datele sunt reale, nu simulate.'
      },
      {
        q: 'Pentru cine e platforma?',
        a: 'Pentru ORICINE vrea să învețe despre finanțe! De la începători (economisire, bugete) până la investitori activi BVB. Fără cunoștințe prealabile - totul explicat pas cu pas.'
      },
      {
        q: 'Pot investi direct pe platformă?',
        a: 'NU. FinRomania e platformă de EDUCAȚIE și ANALIZĂ, nu broker. Oferim date și cunoștințe pentru decizii informate. Pentru investiții reale, ai nevoie de broker autorizat (XTB, BT Capital Partners, etc.).'
      }
    ]
  },
  {
    category: 'Plan PRO',
    icon: <Crown className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce primesc cu PRO?',
        a: 'PRO (49 RON/lună): Calculator Fiscal, AI nelimitat, toate nivelurile fără quiz, watchlist nelimitat (vs 3 FREE), alerte nelimitate (vs 2 FREE), date rapide (15min BVB vs 30min, 1s Global vs 15min), indicatori tehnici, analiză fundamentală.'
      },
      {
        q: 'Calculator Fiscal merită?',
        a: 'DA! Un calcul corect (PF vs SRL) poate economisi 10.000-50.000 RON/an pentru investitori activi. Se plătește singur din prima lună. Include AI Fiscal Advisor pentru întrebări complexe despre taxe.'
      },
      {
        q: 'Ce înseamnă delay-uri?',
        a: 'FREE: BVB delay 30min, Global 15min (OK pentru educație). PRO: BVB delay 15min, Global 1 secundă (esențial pentru decizii rapide). Datele sunt reale, doar actualizarea e diferită.'
      },
      {
        q: 'Pot anula PRO?',
        a: 'Da, oricând! Fără costuri ascunse. Acces PRO până la sfârșitul perioadei plătite. Anual (490 RON) = 2 luni economie vs lunar.'
      }
    ]
  },
  {
    category: 'Educație',
    icon: <GraduationCap className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce e Educația Financiară?',
        a: 'Program GRATUIT cu 15 lecții: bugete (50/30/20), economii, inflație, pensii, taxe România, investiții ETF. Pentru control finanțe personale.'
      },
      {
        q: 'Diferența Educație vs Trading School?',
        a: 'Educație (15 lecții): BAZELE - bugete, economii, taxe. Trading School (17 lecții): TRADING - analiză tehnică, strategii. Începe cu Educația dacă ești nou!'
      },
      {
        q: 'Trebuie cunoștințe anterioare?',
        a: 'NU! Cursurile de la ZERO. Totul explicat pas cu pas, exemple România. Oricine poate învăța.'
      }
    ]
  },
  {
    category: 'Date & Securitate',
    icon: <Shield className="w-5 h-5" />,
    questions: [
      {
        q: 'Cât de actualizate sunt datele?',
        a: 'Actualizare automată: BVB la 5 min, Global la 5 min, BNR zilnic, Știri la 15 min. Furnizori licențiați pentru acuratețe.'
      },
      {
        q: 'Datele mele sunt sigure?',
        a: 'DA! Autentificare Google (fără parole stocate), SSL, GDPR. Nu vindem date. Ștergi contul oricând.'
      },
      {
        q: 'De unde vin datele?',
        a: 'Furnizori licențiați pentru BVB și Global. Cursuri de la BNR. Știri din surse verificate. Toate reale.'
      }
    ]
  }
];

function FAQItem({ question, answer, isOpen, onToggle }) {
  return (
    <Card className="border-2 hover:border-blue-500/50 transition-colors">
      <button onClick={onToggle} className="w-full text-left">
        <CardHeader className="flex flex-row items-center justify-between space-y-0">
          <CardTitle className="text-lg font-semibold pr-4">{question}</CardTitle>
          {isOpen ? (
            <ChevronUp className="w-5 h-5 flex-shrink-0 text-blue-600" />
          ) : (
            <ChevronDown className="w-5 h-5 flex-shrink-0 text-muted-foreground" />
          )}
        </CardHeader>
      </button>
      {isOpen && (
        <CardContent className="pt-0">
          <p className="text-muted-foreground leading-relaxed">{answer}</p>
        </CardContent>
      )}
    </Card>
  );
}

export default function FAQPage() {
  const [openItems, setOpenItems] = useState({});

  const toggleItem = (category, index) => {
    const key = `${category}-${index}`;
    setOpenItems(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <>
      <SEO 
        title="Întrebări Frecvente (FAQ) | FinRomania"
        description="Răspunsuri despre FinRomania: educație financiară, date BVB, planuri PRO, securitate."
      />
      
      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        <div className="text-center space-y-4">
          <Badge className="bg-blue-500 text-white">Întrebări Frecvente</Badge>
          <h1 className="text-2xl font-bold">Ai întrebări? Avem răspunsuri!</h1>
          <p className="text-xl text-muted-foreground">Tot ce trebuie să știi despre FinRomania</p>
        </div>

        {FAQ_DATA.map((category, catIdx) => (
          <div key={catIdx} className="space-y-4">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                {category.icon}
              </div>
              <h2 className="text-2xl font-bold">{category.category}</h2>
            </div>
            
            <div className="space-y-3">
              {category.questions.map((item, idx) => (
                <FAQItem
                  key={idx}
                  question={item.q}
                  answer={item.a}
                  isOpen={openItems[`${catIdx}-${idx}`]}
                  onToggle={() => toggleItem(catIdx, idx)}
                />
              ))}
            </div>
          </div>
        ))}

        <Card className="bg-gradient-to-r from-blue-50 to-blue-50 dark:from-blue-900/20 dark:to-blue-900/20">
          <CardContent className="p-8 text-center">
            <h3 className="text-xl font-bold mb-2">Nu ai găsit răspunsul?</h3>
            <p className="text-muted-foreground mb-4">
              Contactează-ne la <strong>contact@finromania.ro</strong>
            </p>
            <Link to="/contact">
              <button className="text-blue-600 hover:underline">
                Trimite-ne un mesaj →
              </button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
