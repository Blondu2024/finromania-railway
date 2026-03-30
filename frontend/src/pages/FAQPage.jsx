import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, BookOpen, Shield, DollarSign, GraduationCap, Crown } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';

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
  const { t } = useTranslation();
  const [openItems, setOpenItems] = useState({});

  const toggleItem = (category, index) => {
    const key = `${category}-${index}`;
    setOpenItems(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const FAQ_DATA = [
    {
      category: t('faq.catGeneral'),
      icon: <HelpCircle className="w-5 h-5" />,
      questions: [
        { q: t('faq.general_q1'), a: t('faq.general_a1') },
        { q: t('faq.general_q2'), a: t('faq.general_a2') },
        { q: t('faq.general_q3'), a: t('faq.general_a3') },
        { q: t('faq.general_q4'), a: t('faq.general_a4') },
        { q: t('faq.general_q5'), a: t('faq.general_a5') },
      ]
    },
    {
      category: t('faq.catPro'),
      icon: <Crown className="w-5 h-5" />,
      questions: [
        { q: t('faq.pro_q1'), a: t('faq.pro_a1') },
        { q: t('faq.pro_q2'), a: t('faq.pro_a2') },
        { q: t('faq.pro_q3'), a: t('faq.pro_a3') },
        { q: t('faq.pro_q4'), a: t('faq.pro_a4') },
      ]
    },
    {
      category: t('faq.catEducation'),
      icon: <GraduationCap className="w-5 h-5" />,
      questions: [
        { q: t('faq.edu_q1'), a: t('faq.edu_a1') },
        { q: t('faq.edu_q2'), a: t('faq.edu_a2') },
        { q: t('faq.edu_q3'), a: t('faq.edu_a3') },
      ]
    },
    {
      category: t('faq.catSecurity'),
      icon: <Shield className="w-5 h-5" />,
      questions: [
        { q: t('faq.security_q1'), a: t('faq.security_a1') },
        { q: t('faq.security_q2'), a: t('faq.security_a2') },
        { q: t('faq.security_q3'), a: t('faq.security_a3') },
      ]
    }
  ];

  return (
    <>
      <SEO
        title={`${t('faq.title')} | FinRomania`}
        description={t('faq.subtitle')}
      />

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        <div className="text-center space-y-4">
          <Badge className="bg-blue-500 text-white">{t('faq.title')}</Badge>
          <h1 className="text-2xl font-bold">{t('faq.subtitle')}</h1>
          <p className="text-xl text-muted-foreground">{t('faq.description')}</p>
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
            <h3 className="text-xl font-bold mb-2">{t('faq.noAnswer')}</h3>
            <p className="text-muted-foreground mb-4">
              {t('faq.contactUs')}
            </p>
            <Link to="/contact">
              <button className="text-blue-600 hover:underline">
                {t('faq.sendMessage')}
              </button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
