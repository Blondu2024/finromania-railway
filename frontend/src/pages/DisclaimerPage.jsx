import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '../components/ui/alert';
import SEO from '../components/SEO';

export default function DisclaimerPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <SEO title="Disclaimer | FinRomania" description="Legal disclaimer - FinRomania provides educational content, not investment advice." />
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('disclaimerPage.backButton')}
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <AlertTriangle className="w-8 h-8 text-yellow-600" />
        <h1 className="text-3xl font-bold">{t('disclaimerPage.title')}</h1>
      </div>

      <p className="text-muted-foreground">{t('disclaimerPage.lastUpdated')}</p>

      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>{t('disclaimerPage.warningTitle')}</AlertTitle>
        <AlertDescription>
          {t('disclaimerPage.warningText')}
        </AlertDescription>
      </Alert>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section1Title')}</h2>
            <p>
              {t('disclaimerPage.section1Text')}
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('disclaimerPage.section1Item1')}</li>
              <li>{t('disclaimerPage.section1Item2')}</li>
              <li>{t('disclaimerPage.section1Item3')}</li>
              <li>{t('disclaimerPage.section1Item4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section2Title')}</h2>
            <p>
              {t('disclaimerPage.section2Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section3Title')}</h2>
            <p>
              {t('disclaimerPage.section3Text')}
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('disclaimerPage.section3Item1')}</li>
              <li>{t('disclaimerPage.section3Item2')}</li>
              <li>{t('disclaimerPage.section3Item3')}</li>
              <li>{t('disclaimerPage.section3Item4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section4Title')}</h2>
            <p>
              {t('disclaimerPage.section4Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section5Title')}</h2>
            <p className="font-semibold">
              {t('disclaimerPage.section5Text1')}
            </p>
            <p>
              {t('disclaimerPage.section5Text2')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section6Title')}</h2>
            <p>
              {t('disclaimerPage.section6Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section7Title')}</h2>
            <p>
              {t('disclaimerPage.section7Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section8Title')}</h2>
            <p className="bg-blue-100 dark:bg-blue-900 p-4 rounded-lg">
              <strong>{t('disclaimerPage.section8Label')}</strong> {t('disclaimerPage.section8Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section9Title')}</h2>
            <p>{t('disclaimerPage.section9Text')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>{t('disclaimerPage.section9Item1Label')}</strong> {t('disclaimerPage.section9Item1Text')}</li>
              <li><strong>{t('disclaimerPage.section9Item2Label')}</strong> {t('disclaimerPage.section9Item2Text')}</li>
              <li><strong>{t('disclaimerPage.section9Item3Label')}</strong> {t('disclaimerPage.section9Item3Text')}</li>
              <li><strong>{t('disclaimerPage.section9Item4Label')}</strong> {t('disclaimerPage.section9Item4Text')}</li>
            </ul>
            <p className="mt-2">
              {t('disclaimerPage.section9Footer')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('disclaimerPage.section10Title')}</h2>
            <p>
              {t('disclaimerPage.section10Text')} <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
