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
        a: 'FinRomania este prima platformă educațională de trading și investiții din România. Oferim știri financiare în timp real, date live de pe Bursa de Valori București, instrumente educaționale interactive și asistent AI pentru a te ajuta să înveți trading - totul în limba română!'
      },
      {
        q: 'Este cu adevărat gratuit?',
        a: 'DA! Majoritatea features sunt 100% gratuite: știri, date BVB live, convertor valutar, glosar financiar, și primele 5 lecții din Trading School. Oferim și un pachet premium opțional (10 RON) pentru acces complet la toate cele 17 lecții avansate.'
      },
      {
        q: 'Datele sunt reale sau simulate?',
        a: 'Toate datele sunt REALE! Folosim surse licențiate și de încredere pentru date de pe Bursa de Valori București, indici globali, și cursuri valutare. Nu folosim date mock sau simulate - vezi prețuri reale în timp real!'
      }
    ]
  },
  {
    category: 'Trading School',
    icon: <GraduationCap className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este Trading School?',
        a: 'Trading School este un curs interactiv complet de trading cu 17 lecții, quizzes, și scenarii practice. Înveți concepte de la bază (ce e o acțiune) până la avansat (indicatori tehnici, strategii complexe). Primele 5 lecții sunt GRATUITE pentru toată lumea!'
      },
      {
        q: 'Cum funcționează lecțiile?',
        a: 'Fiecare lecție include conținut educațional detaliat cu exemple practice din piața românească, urmat de un quiz interactiv pentru verificarea cunoștințelor. Trebuie să obții minim 80% la quiz pentru a debloca lecția următoare. Progress-ul tău este salvat automat dacă ești autentificat.'
      },
      {
        q: 'Primesc certificat la final?',
        a: 'Da! Utilizatorii care completează toate lecțiile cu scor de minim 80% vor primi un certificat digital descărcabil care atestă parcurgerea cursului Trading School. Poți folosi certificatul pentru CV sau LinkedIn!'
      },
      {
        q: 'Pot folosi cunoștințele pentru trading real?',
        a: 'Absolut! Lecțiile te pregătesc pentru trading real pe orice platformă de brokeraj. Înveți concepte universale aplicabile pe toate piețele: analiza tehnică, managementul riscului, psihologia tradingului, și strategii practice.'
      }
    ]
  },
  {
    category: 'Plăți & Premium',
    icon: <DollarSign className="w-5 h-5" />,
    questions: [
      {
        q: 'Cât costă accesul Premium?',
        a: 'Pachetul Premium costă doar 10 RON (plată unică) și îți dă acces permanent la toate cele 12 lecții avansate. Plătești o singură dată și ai acces pe viață - nu este abonament!'
      },
      {
        q: 'Cum plătesc în siguranță?',
        a: 'Folosim un procesor de plăți internațional securizat, certificat PCI-DSS. Acceptăm toate cardurile bancare (Visa, Mastercard). Tranzacția este criptată 100% - nu stocăm niciodată informații despre cardul tău. După plată, lecțiile se deblochează instant!'
      },
      {
        q: 'Pot cere refund?',
        a: 'Deoarece este conținut digital cu acces instant, nu oferim refund după achiziție. DAR poți testa GRATUIT primele 5 lecții înainte de a cumpăra premium, așa că știi exact ce primești! Recomandăm să parcurgi lecțiile gratuite mai întâi.'
      },
      {
        q: 'Primesc factură fiscală?',
        a: 'Da! Vei primi automat chitanță/invoice pe email după efectuarea plății. Documentul poate fi folosit pentru contabilitate sau decontări fiscale.'
      }
    ]
  },
  {
    category: 'Date & Securitate',
    icon: <Shield className="w-5 h-5" />,
    questions: [
      {
        q: 'Cât de actualizate sunt datele de pe BVB?',
        a: 'Datele de pe Bursa de Valori București se actualizează automat la fiecare câteva minute. Vezi prețuri reale pentru acțiunile principale: Banca Transilvania, Hidroelectrica, OMV Petrom, și multe altele. Datele provin de la surse oficiale licențiate.'
      },
      {
        q: 'Sunt datele mele personale în siguranță?',
        a: 'Absolut! Folosim autentificare securizată prin Google, encriptare HTTPS pentru toate comunicările, și respectăm strict regulamentul GDPR. Nu stocăm parole în format text, nu vindem datele tale nimănui, și poți șterge contul oricând.'
      },
      {
        q: 'Pot face trading efectiv pe platformă?',
        a: 'NU! FinRomania este o platformă EDUCAȚIONALĂ, nu un broker. Nu poți cumpăra sau vinde acțiuni reale aici. Învățătura noastră te pregătește pentru a folosi platforme de brokeraj licențiate (XTB, eToro, Interactive Brokers, etc.) când ești gata.'
      }
    ]
  },
  {
    category: 'AI Advisor',
    icon: <BookOpen className="w-5 h-5" />,
    questions: [
      {
        q: 'Cum funcționează AI Advisor?',
        a: 'AI Advisor este un asistent inteligent care răspunde la întrebări despre trading, investiții, și piețe financiare în limba română. Poți întreba orice: "Ce este un ETF?", "Cum setez Stop Loss?", "Cum analizez o acțiune?". Primești răspunsuri clare cu exemple practice!'
      },
      {
        q: 'AI Advisor este gratuit?',
        a: 'Da! Ai acces gratuit la funcțiile de bază ale AI Advisor, inclusiv "Sfatul Zilei". Pentru utilizatorii autentificați, există și mai multe credite disponibile pentru întrebări personalizate.'
      },
      {
        q: 'Poate AI să-mi recomande acțiuni specifice de cumpărat?',
        a: 'AI-ul poate analiza companii și explica concepte financiare, DAR nu oferă sfaturi financiare personalizate de tipul "cumpără acțiunea X acum!". Este un instrument educațional, nu un consilier financiar licențiat. Toate deciziile de investiții rămân responsabilitatea ta!'
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