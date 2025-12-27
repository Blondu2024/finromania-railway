import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, Shield, DollarSign, GraduationCap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Link } from 'react-router-dom';

const FAQ_DATA = [
  {
    category: 'General',
    icon: <HelpCircle className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este FinRomania?',
        a: 'FinRomania este prima platformă de date financiare și educație din România. Oferim date live de pe Bursa de Valori București, știri financiare agregate, cursuri valutare BNR, două programe educaționale complete (Trading School + Educație Financiară), asistent AI și mult mai multe - totul în limba română!'
      },
      {
        q: 'Este cu adevărat gratuit?',
        a: 'DA! TOTUL pe FinRomania este 100% gratuit: date BVB live, știri, convertor valutar, glosar, AI Advisor, cele 17 lecții Trading School, și cele 15 lecții de Educație Financiară. Misiunea noastră e să oferim românilor acces gratuit la educație financiară de calitate!'
      },
      {
        q: 'Datele sunt reale sau simulate?',
        a: 'Toate datele sunt REALE! Folosim EODHD API pentru date BVB, yfinance pentru indici globali, și BNR pentru cursuri valutare. Știrile sunt agregate din surse românești de încredere (ZF, Profit.ro, Bursa, Wall-Street). Nu folosim date simulate!'
      },
      {
        q: 'Pentru cine este platforma?',
        a: 'Pentru ORICINE vrea să învețe despre finanțe personale și investiții! De la complet începători (care vor să învețe bazele bugetării și economisirii) până la cei interesați de trading pe bursa. Nu ai nevoie de cunoștințe prealabile.'
      }
    ]
  },
  {
    category: 'Educație Financiară',
    icon: <DollarSign className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este cursul de Educație Financiară?',
        a: 'Este un program complet cu 15 lecții care te învață bazele finanțelor personale: cum să faci un buget (regula 50/30/20), să construiești un fond de urgență, să înțelegi inflația, conturile bancare, creditele, pensiile, taxele din România, și chiar bazele investițiilor în ETF-uri.'
      },
      {
        q: 'Care e diferența între Educație Financiară și Trading School?',
        a: 'Educația Financiară (15 lecții) te învață BAZELE: bugete, economii, pensii, taxe, investiții simple. Trading School (17 lecții) e pentru cei care vor să facă trading activ: analiză tehnică, indicatori, leverage, strategii. Recomandare: Începe cu Educația Financiară dacă ești începător!'
      },
      {
        q: 'Am nevoie de cunoștințe anterioare?',
        a: 'NU! Cursul de Educație Financiară e conceput de la ZERO. Prima lecție explică de ce educația financiară e importantă și ce vei învăța. Nu presupunem nicio cunoștință anterioară - totul e explicat pas cu pas, cu exemple din România.'
      },
      {
        q: 'Ce voi ști după ce termin cursul?',
        a: 'Vei ști să: faci un buget eficient, economisești inteligent, înțelegi inflația și dobânzile, alegi conturi bancare și asigurări potrivite, planifici pentru pensie, declari taxele corect, și să începi să investești în ETF-uri. Practic: vei avea controlul finanțelor tale!'
      }
    ]
  },
  {
    category: 'Trading School',
    icon: <GraduationCap className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este Trading School?',
        a: 'Trading School este un curs complet de trading cu 17 lecții interactive - 100% GRATUIT! Înveți de la bază (ce e o acțiune, cum funcționează bursa) până la avansat (indicatori tehnici, strategii de trading, managementul riscului). Toate lecțiile sunt disponibile pentru toată lumea!'
      },
      {
        q: 'Cum funcționează lecțiile?',
        a: 'Fiecare lecție include conținut detaliat cu exemple practice din piața românească, urmat de un quiz interactiv. Trebuie să obții minim 80% la quiz pentru a debloca lecția următoare. Progress-ul e salvat automat dacă ești autentificat.'
      },
      {
        q: 'Pot folosi cunoștințele pentru trading real?',
        a: 'Absolut! Lecțiile te pregătesc pentru trading real pe orice platformă de brokeraj (XTB, eToro, Interactive Brokers, etc.). Înveți concepte universale: analiză tehnică și fundamentală, managementul riscului, psihologia tradingului.'
      }
    ]
  },
  {
    category: 'Date & Securitate',
    icon: <Shield className="w-5 h-5" />,
    questions: [
      {
        q: 'Cât de actualizate sunt datele de pe BVB?',
        a: 'Datele BVB se actualizează automat la fiecare 5 minute în timpul programului bursei. Datele provin de la EODHD, un furnizor licențiat de date financiare. Vezi prețuri reale pentru: Banca Transilvania, Hidroelectrica, OMV Petrom, și alte 20+ acțiuni.'
      },
      {
        q: 'Sunt datele mele personale în siguranță?',
        a: 'Da! Folosim autentificare securizată prin Google, encriptare HTTPS pentru toate comunicările, și respectăm GDPR. Nu stocăm parole, nu vindem datele tale, și poți șterge contul oricând.'
      },
      {
        q: 'Pot face trading efectiv pe platformă?',
        a: 'NU! FinRomania este o platformă EDUCAȚIONALĂ și de DATE, nu un broker. Nu poți cumpăra sau vinde acțiuni aici. Te pregătim să folosești platforme de brokeraj licențiate când ești gata.'
      }
    ]
  },
  {
    category: 'AI Advisor',
    icon: <BookOpen className="w-5 h-5" />,
    questions: [
      {
        q: 'Cum funcționează AI Advisor?',
        a: 'AI Advisor răspunde la întrebări despre trading, investiții și finanțe personale în română. Poți întreba orice: "Ce este un ETF?", "Cum funcționează Pilonul II de pensii?", "Ce înseamnă P/E ratio?". Primești răspunsuri clare cu exemple practice!'
      },
      {
        q: 'Poate AI să-mi recomande acțiuni de cumpărat?',
        a: 'NU! AI-ul explică concepte și analizează general, dar NU oferă sfaturi de investiții personalizate. Este un instrument educațional, nu un consilier financiar licențiat. Toate deciziile de investiții sunt responsabilitatea ta!'
      }
    ]
  }
];

export default function FAQPage() {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleQuestion = (catIdx, qIdx) => {
    const key = `${catIdx}-${qIdx}`;
    setOpenIndex(openIndex === key ? null : key);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-12 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="inline-block p-4 bg-blue-100 rounded-full">
          <HelpCircle className="w-12 h-12 text-blue-600" />
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold">Întrebări Frecvente</h1>
        <p className="text-xl text-muted-foreground">
          Tot ce trebuie să știi despre FinRomania
        </p>
      </div>

      {/* FAQ Categories */}
      {FAQ_DATA.map((category, catIdx) => (
        <div key={catIdx}>
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
              {category.icon}
            </div>
            <h2 className="text-2xl font-bold">{category.category}</h2>
          </div>

          <div className="space-y-3">
            {category.questions.map((item, qIdx) => {
              const isOpen = openIndex === `${catIdx}-${qIdx}`;
              
              return (
                <Card key={qIdx} className="border-2 hover:border-blue-300 transition-colors">
                  <CardContent className="p-0">
                    <button
                      className="w-full p-6 text-left flex items-center justify-between"
                      onClick={() => toggleQuestion(catIdx, qIdx)}
                    >
                      <span className="font-semibold pr-4">{item.q}</span>
                      {isOpen ? (
                        <ChevronUp className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      )}
                    </button>
                    
                    {isOpen && (
                      <div className="px-6 pb-6">
                        <div className="pt-4 border-t">
                          <p className="text-muted-foreground leading-relaxed">{item.a}</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      ))}

      {/* Still have questions? */}
      <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white border-0 mt-12">
        <CardContent className="p-8 text-center">
          <h3 className="text-2xl font-bold mb-2">Mai ai întrebări?</h3>
          <p className="text-blue-100 mb-6">
            Întreabă AI Advisor-ul nostru sau contactează-ne direct!
          </p>
          <div className="flex gap-3 justify-center flex-wrap">
            <Link to="/advisor">
              <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                🤖 Întreabă AI
              </button>
            </Link>
            <Link to="/contact">
              <button className="bg-white/20 text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors border-2 border-white/40">
                📧 Contactează-ne
              </button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}