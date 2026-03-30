import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, Cookie } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import SEO from '../components/SEO';

export default function CookiePolicyPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <SEO title="Cookie Policy | FinRomania" description="FinRomania cookie policy - how we use cookies to improve your experience." />
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('cookiesPage.backButton')}
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <Cookie className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">{t('cookiesPage.title')}</h1>
      </div>

      <p className="text-muted-foreground">{t('cookiesPage.lastUpdated')}</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section1Title')}</h2>
            <p>
              {t('cookiesPage.section1Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section2Title')}</h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('cookiesPage.tableType')}</TableHead>
                  <TableHead>{t('cookiesPage.tablePurpose')}</TableHead>
                  <TableHead>{t('cookiesPage.tableDuration')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">{t('cookiesPage.essentialType')}</TableCell>
                  <TableCell>{t('cookiesPage.essentialPurpose')}</TableCell>
                  <TableCell>{t('cookiesPage.essentialDuration')}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">{t('cookiesPage.preferencesType')}</TableCell>
                  <TableCell>{t('cookiesPage.preferencesPurpose')}</TableCell>
                  <TableCell>{t('cookiesPage.preferencesDuration')}</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">{t('cookiesPage.analyticsType')}</TableCell>
                  <TableCell>{t('cookiesPage.analyticsPurpose')}</TableCell>
                  <TableCell>{t('cookiesPage.analyticsDuration')}</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section3Title')}</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>{t('cookiesPage.section3Item1Label')}</strong> {t('cookiesPage.section3Item1Text')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section4Title')}</h2>
            <p>
              {t('cookiesPage.section4Text')}
            </p>
            <p>{t('cookiesPage.section4BrowserGuide')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Chrome</a></li>
              <li><a href="https://support.mozilla.org/kb/cookies-information-websites-store-on-your-computer" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Mozilla Firefox</a></li>
              <li><a href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Safari</a></li>
              <li><a href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Microsoft Edge</a></li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section5Title')}</h2>
            <p>
              {t('cookiesPage.section5Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section6Title')}</h2>
            <p>
              {t('cookiesPage.section6Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('cookiesPage.section7Title')}</h2>
            <p>
              {t('cookiesPage.section7Text')} <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
