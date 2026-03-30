import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import SEO from '../components/SEO';

export default function TermsOfServicePage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <SEO title="Terms of Service | FinRomania" description="FinRomania terms and conditions for using our financial education platform." />
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('termsPage.backButton')}
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <FileText className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">{t('termsPage.title')}</h1>
      </div>

      <p className="text-muted-foreground">{t('termsPage.lastUpdated')}</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section1Title')}</h2>
            <p>
              {t('termsPage.section1Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section2Title')}</h2>
            <p>
              {t('termsPage.section2Text')}
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('termsPage.section2Item1')}</li>
              <li>{t('termsPage.section2Item2')}</li>
              <li>{t('termsPage.section2Item3')}</li>
              <li>{t('termsPage.section2Item4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section3Title')}</h2>
            <p className="font-semibold text-red-600 dark:text-red-400">
              {t('termsPage.section3Text1')}
            </p>
            <p>
              {t('termsPage.section3Text2')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section4Title')}</h2>
            <p>
              {t('termsPage.section4Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section5Title')}</h2>
            <p>{t('termsPage.section5Text')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>{t('termsPage.section5Item1Label')}</strong> {t('termsPage.section5Item1Text')}</li>
              <li><strong>{t('termsPage.section5Item2Label')}</strong> {t('termsPage.section5Item2Text')}</li>
              <li><strong>{t('termsPage.section5Item3Label')}</strong> {t('termsPage.section5Item3Text')}</li>
              <li><strong>{t('termsPage.section5Item4Label')}</strong> {t('termsPage.section5Item4Text')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section6Title')}</h2>
            <p>
              {t('termsPage.section6Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section7Title')}</h2>
            <p>
              {t('termsPage.section7Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section8Title')}</h2>
            <p>
              {t('termsPage.section8Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section9Title')}</h2>
            <p>
              {t('termsPage.section9Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('termsPage.section10Title')}</h2>
            <p>
              {t('termsPage.section10Text')} <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
