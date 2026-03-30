import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import { Link } from 'react-router-dom';
import {
  AlertTriangle, CheckCircle, XCircle, TrendingUp, Shield,
  ArrowRight, Info, BookOpen, DollarSign, BarChart2,
  Building2, Globe, ChevronDown, ChevronUp, ExternalLink
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

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

  const FAQ_ITEMS = [
    { q: t('cfd.faq_q1'), a: t('cfd.faq_a1') },
    { q: t('cfd.faq_q2'), a: t('cfd.faq_a2') },
    { q: t('cfd.faq_q3'), a: t('cfd.faq_a3') },
    { q: t('cfd.faq_q4'), a: t('cfd.faq_a4') },
    { q: t('cfd.faq_q5'), a: t('cfd.faq_a5') },
    { q: t('cfd.faq_q6'), a: t('cfd.faq_a6') },
  ];

  const COMPARISON_ROWS = [
    { aspect: t('cfd.row_ownership'), real: true, cfd: false },
    { aspect: t('cfd.row_dividends'), real: true, cfd: false },
    { aspect: t('cfd.row_voting'), real: true, cfd: false },
    { aspect: t('cfd.row_limitedRisk'), real: true, cfd: false },
    { aspect: t('cfd.row_247'), real: false, cfd: true },
    { aspect: t('cfd.row_leverage'), real: false, cfd: true },
    { aspect: t('cfd.row_dividendTax'), real: true, cfd: false },
    { aspect: t('cfd.row_conflict'), real: false, cfd: true },
    { aspect: t('cfd.row_regulated'), real: true, cfd: false },
    { aspect: t('cfd.row_marginCall'), real: false, cfd: true },
  ];

  const alternatives = [
    {
      icon: Building2,
      title: t('cfd.altBvbTitle'),
      desc: t('cfd.altBvbDesc'),
      color: 'blue',
      link: '/stocks',
      linkText: t('cfd.altBvbLink')
    },
    {
      icon: DollarSign,
      title: t('cfd.altDivTitle'),
      desc: t('cfd.altDivDesc'),
      color: 'green',
      link: '/calculator-dividende',
      linkText: t('cfd.altDivLink')
    },
    {
      icon: TrendingUp,
      title: t('cfd.altScreenerTitle'),
      desc: t('cfd.altScreenerDesc'),
      color: 'amber',
      link: '/screener-pro',
      linkText: t('cfd.altScreenerLink')
    },
    {
      icon: BookOpen,
      title: t('cfd.altAcademyTitle'),
      desc: t('cfd.altAcademyDesc'),
      color: 'orange',
      link: '/trading-school',
      linkText: t('cfd.altAcademyLink')
    }
  ];

  const brokers = [
    { name: 'Tradeville', desc: t('cfd.brokerTradeville'), url: 'https://www.tradeville.ro' },
    { name: 'BT Capital Partners', desc: t('cfd.brokerBT'), url: 'https://www.btcapital.ro' },
    { name: 'XTB', desc: t('cfd.brokerXTB'), url: 'https://www.xtb.com/ro' },
    { name: 'Interactive Brokers', desc: t('cfd.brokerIBKR'), url: 'https://www.interactivebrokers.com' },
  ];

  return (
    <>
    <SEO title={t('cfd.seoTitle')} description={t('cfd.seoDesc')} />
    <div className="max-w-4xl mx-auto space-y-10 pb-12">

      {/* HERO */}
      <div className="text-center space-y-4 py-8">
        <Badge variant="destructive" className="text-sm px-3 py-1" data-testid="cfd-alert-badge">
          <AlertTriangle className="w-4 h-4 mr-1" /> {t('cfd.alertBadge')}
        </Badge>
        <h1 className="text-4xl sm:text-5xl font-bold leading-tight" data-testid="cfd-page-title">
          {t('cfd.pageTitle')}
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          {t('cfd.heroDesc')}
        </p>
      </div>

      {/* WARNING BANNER */}
      <Card className="border-red-300 bg-red-50 dark:bg-red-950/30 dark:border-red-800" data-testid="cfd-warning-card">
        <CardContent className="p-6">
          <div className="flex gap-4">
            <AlertTriangle className="w-8 h-8 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-red-800 dark:text-red-300 mb-2">
                {t('cfd.warningTitle')}
              </h2>
              <p className="text-red-700 dark:text-red-400 text-sm leading-relaxed">
                {t('cfd.warningText')}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* CE SUNT CFD-URILE */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Info className="w-6 h-6 text-blue-600" />
          {t('cfd.whatIsCfdTitle')}
        </h2>
        <div className="space-y-4 text-muted-foreground leading-relaxed">
          <p dangerouslySetInnerHTML={{ __html: t('cfd.whatIsCfdText') }} />
          <Card className="bg-muted/40">
            <CardContent className="p-5">
              <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" /> {t('cfd.exampleTitle')}
              </h3>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-medium text-foreground" dangerouslySetInnerHTML={{ __html: t('cfd.exampleRealLabel') }} /><br />
                  <span dangerouslySetInnerHTML={{ __html: t('cfd.exampleRealText') }} />
                </p>
                <hr className="border-border" />
                <p>
                  <span className="font-medium text-foreground" dangerouslySetInnerHTML={{ __html: t('cfd.exampleCfdLabel') }} /><br />
                  <span dangerouslySetInnerHTML={{ __html: t('cfd.exampleCfdText') }} />
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
          {t('cfd.comparisonTitle')}
        </h2>
        <div className="overflow-x-auto rounded-lg border" data-testid="comparison-table">
          <table className="w-full">
            <thead>
              <tr className="bg-muted/60">
                <th className="text-left px-4 py-3 font-semibold text-sm">{t('cfd.colAspect')}</th>
                <th className="text-center px-4 py-3 font-semibold text-sm text-green-700 dark:text-green-400">
                  {t('cfd.colRealStocks')}
                </th>
                <th className="text-center px-4 py-3 font-semibold text-sm text-red-700 dark:text-red-400">
                  {t('cfd.colCfd')}
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
          {t('cfd.marketHoursTitle')}
        </h2>
        <Card className="border-orange-200 bg-orange-50 dark:bg-orange-950/20" data-testid="market-hours-card">
          <CardContent className="p-6 space-y-4">
            <p className="text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: t('cfd.marketHoursReal') }} />
            <hr className="border-orange-200" />
            <p className="text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: t('cfd.marketHoursCfd') }} />
            <div className="flex items-start gap-3 bg-orange-100 dark:bg-orange-900/30 p-4 rounded-lg">
              <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-orange-800 dark:text-orange-300">
                {t('cfd.marketHoursWarning')}
              </p>
            </div>
          </CardContent>
        </Card>
      </section>

      {/* EFECTUL DE LEVIER */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-red-600" />
          {t('cfd.leverageTitle')}
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <Card className="border-green-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-green-700 dark:text-green-400 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" /> {t('cfd.leverageRealTitle')}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p dangerouslySetInnerHTML={{ __html: t('cfd.leverageRealLine1') }} />
              <p>{t('cfd.leverageRealLine2')}</p>
              <p dangerouslySetInnerHTML={{ __html: t('cfd.leverageRealLine3') }} />
              <p className="text-green-700 font-medium">{t('cfd.leverageRealLine4')}</p>
              <p className="text-muted-foreground">{t('cfd.leverageRealLine5')}</p>
            </CardContent>
          </Card>
          <Card className="border-red-200">
            <CardHeader className="pb-2">
              <CardTitle className="text-base text-red-700 dark:text-red-400 flex items-center gap-2">
                <XCircle className="w-5 h-5" /> {t('cfd.leverageCfdTitle')}
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <p dangerouslySetInnerHTML={{ __html: t('cfd.leverageCfdLine1') }} />
              <p>{t('cfd.leverageCfdLine2')}</p>
              <p className="text-red-700 font-medium">{t('cfd.leverageCfdLine3')}</p>
              <p dangerouslySetInnerHTML={{ __html: t('cfd.leverageCfdLine4') }} />
              <p className="text-muted-foreground">{t('cfd.leverageCfdLine5')}</p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CE SA FACI IN SCHIMB */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Shield className="w-6 h-6 text-blue-600" />
          {t('cfd.alternativesTitle')}
        </h2>
        <div className="grid sm:grid-cols-2 gap-4" data-testid="alternatives-section">
          {alternatives.map((item, i) => (
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
          {t('cfd.brokersTitle')}
        </h2>
        <Card>
          <CardContent className="p-5">
            <p className="text-sm text-muted-foreground mb-4">
              {t('cfd.brokersIntro')}
            </p>
            <div className="grid sm:grid-cols-2 gap-3">
              {brokers.map((broker, i) => (
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
              {t('cfd.brokersDisclaimer')}
            </p>
          </CardContent>
        </Card>
      </section>

      {/* FAQ */}
      <section>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <BookOpen className="w-6 h-6 text-blue-600" />
          {t('cfd.faqTitle')}
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
          <p className="text-xs text-muted-foreground leading-relaxed" dangerouslySetInnerHTML={{ __html: t('cfd.disclaimerText') }} />
        </CardContent>
      </Card>

      {/* CTA FINAL */}
      <div className="text-center space-y-4 py-6 border-t" data-testid="cfd-page-cta">
        <h2 className="text-2xl font-bold">{t('cfd.ctaTitle')}</h2>
        <p className="text-muted-foreground">
          {t('cfd.ctaDesc')}
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link to="/stocks">
            <Button data-testid="cta-stocks-btn">
              <TrendingUp className="w-4 h-4 mr-2" /> {t('cfd.ctaBvb')}
            </Button>
          </Link>
          <Link to="/calculator-dividende">
            <Button variant="outline" data-testid="cta-calculator-btn">
              <DollarSign className="w-4 h-4 mr-2" /> {t('cfd.ctaCalc')}
            </Button>
          </Link>
        </div>
      </div>
    </div>
    </>
  );
}
