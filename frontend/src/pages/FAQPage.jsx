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
        a: 'FinRomania este prima platformă educațională de trading și investiții din România. Oferim știri financiare în timp real, date live de pe BVB (Bursa de Valori București), instrumente educaționale interactive și AI Advisor pentru a te ajuta să înveți trading de la 0 la expert - 100% GRATUIT!'
      },
      {
        q: 'Este cu adevărat gratuit?',
        a: 'DA! Majoritatea features sunt 100% gratuite: știri, date BVB live, convertor valutar, watchlist, AI Advisor (cu limite), și primele 5 lecții din Trading School. Oferim și pachete premium opționale (10 RON) pentru acces complet la toate cele 16+ lecții avansate.'
      },
      {
        q: 'Datele sunt reale sau simulate?',
        a: 'TOATE datele sunt REALE! Folosim EODHD API (plătit $19.99/lună) pentru date BVB, Yahoo Finance pentru indici globali, și BNR pentru cursuri valutare. Nu folosim date mock sau simulate - vezi prețuri reale în timp real!'
      }
    ]
  },
  {
    category: 'Trading School',
    icon: <GraduationCap className="w-5 h-5" />,
    questions: [
      {
        q: 'Ce este Trading School?',
        a: 'Trading School este un curs interactiv de trading cu 16+ lecții, quizzes, și scenarii practice. Înveți concepte de la bază (ce e o acțiune) până la avansat (indicatori tehnici, strategii). Primele 5 lecții sunt GRATUITE, restul 11+ lecții costă 10 RON (pachet complet).'
      },
      {
        q: 'Cum funcționează lecțiile?',
        a: 'Fiecare lecție include: (1) Conținut educațional cu exemple practice, (2) Quiz cu 2-3 întrebări pentru verificare, (3) Feedback detaliat și explicații. Trebuie să treci quiz-ul cu 80%+ pentru a debloca lecția următoare. Progress-ul tău e salvat automat.'
      },
      {
        q: 'Primesc certificat la final?',
        a: 'Certificatul PDF descărcabil va fi disponibil în curând pentru utilizatorii care completează toate lecțiile cu scor 80%+. Vei putea share certificatul pe LinkedIn sau CV!'
      },
      {
        q: 'Pot folosi cunoștințele pentru trading real?',
        a: 'ABSOLUT! Lecțiile te pregătesc pentru trading real pe orice platformă (XTB, eToro, Interactive Brokers, etc.). Înveți concepte universale: leverage, stop loss, indicatori tehnici, money management - toate aplicabile în viața reală!'
      }
    ]
  },
  {
    category: 'Plăți & Premium',
    icon: <DollarSign className="w-5 h-5" />,
    questions: [
      {
        q: 'Cât costă Premium?',
        a: 'Premium costă doar 10 RON (one-time payment) și deblochează TOATE cele 11+ lecții avansate din Trading School. Primești acces permanent - plătești o singură dată, ai acces pe viață!'
      },
      {
        q: 'Cum plătesc?',
        a: 'Folosim Stripe (cel mai sigur procesor de plăți din lume). Accepți card bancar (Visa, Mastercard). Tranzacția este securizată 100% - nu stocăm informații despre card. După plată, lecțiile premium se deblochează instant!'
      },
      {
        q: 'Pot cere refund?',
        a: 'Deoarece e conținut digital instant access, refund-urile nu sunt disponibile după achiziție. DAR - poți testa GRATUIT primele 5 lecții înainte de a cumpăra premium! Așa știi exact ce primești.'
      },
      {
        q: 'Primesc factură?',
        a: 'DA! Stripe trimite automat chitanța/invoice pe email după plată. Poți folosi pentru contabilitate sau decontare (dacă ești PFA/SRL).'
      }
    ]
  },
  {
    category: 'Date & Securitate',
    icon: <Shield className="w-5 h-5" />,
    questions: [
      {
        q: 'Sunt datele BVB actualizate?',
        a: 'DA! Datele BVB se actualizează automat la fiecare 5 minute prin EODHD API. Vezi prețuri reale pentru TLV, H2O, SNP, și alte 20 acțiuni de pe Bursa de Valori București. Nu sunt simulate!'
      },
      {
        q: 'Datele mele sunt în siguranță?',
        a: 'ABSOLUT! Folosim autentificare Google OAuth (managed de Emergent), encriptare HTTPS, și MongoDB pentru stocare. NU stocăm parole în plain text. NU vindem datele tale. Respectăm GDPR.'
      },
      {
        q: 'Pot face trading efectiv pe platformă?',
        a: 'NU! FinRomania e o platformă EDUCAȚIONALĂ, nu broker. Nu poți cumpăra/vinde acțiuni reale aici. Portofoliul Virtual (în beta) e doar pentru învățare cu bani virtuali. Pentru trading real, folosește brokeri licențiați (XTB, eToro, etc.).'
      }
    ]
  },
  {
    category: 'AI Advisor',
    icon: <BookOpen className="w-5 h-5" />,
    questions: [
      {
        q: 'Cum funcționează AI Advisor?',
        a: 'AI Advisor folosește GPT-4 (prin Emergent Universal Key) pentru a răspunde la întrebări despre trading, investiții, și piețe financiare. Poți întreba orice: "Ce e un ETF?", "Cum setez Stop Loss?", "Cum analizez o acțiune?". AI răspunde în română cu exemple practice!'
      },
      {
        q: 'AI Advisor e gratuit?',
        a: 'DA! Ai access gratuit la Tip of the Day și întrebări limitate. Pentru utilizatori autentificați, ai mai multe credite. AI folosește Emergent Universal Key (nu plătești separat pentru OpenAI).'
      },
      {
        q: 'Poate AI să-mi recomande acțiuni specifice?',
        a: 'AI poate analiza acțiuni și explica concepte, DAR nu dă sfaturi financiare personalizate ("cumpără X acum!"). Folosește AI pentru educație, nu ca sfătuitor financiar licențiat. Deciziile de trading sunt RESPONSABILITATEA TA!'
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