import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import SEO from '../components/SEO';

export default function PrivacyPolicyPage() {
  const { t } = useTranslation();
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <SEO title="Privacy Policy | FinRomania" description="FinRomania privacy policy - how we protect and handle your personal data." />
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('privacyPage.backButton')}
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <Shield className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">{t('privacyPage.title')}</h1>
      </div>

      <p className="text-muted-foreground">{t('privacyPage.lastUpdated')}</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section1Title')}</h2>
            <p>
              {t('privacyPage.section1Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section2Title')}</h2>
            <p>{t('privacyPage.section2Text')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>{t('privacyPage.section2Item1Label')}</strong> {t('privacyPage.section2Item1Text')}</li>
              <li><strong>{t('privacyPage.section2Item2Label')}</strong> {t('privacyPage.section2Item2Text')}</li>
              <li><strong>{t('privacyPage.section2Item3Label')}</strong> {t('privacyPage.section2Item3Text')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section3Title')}</h2>
            <p>{t('privacyPage.section3Text')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('privacyPage.section3Item1')}</li>
              <li>{t('privacyPage.section3Item2')}</li>
              <li>{t('privacyPage.section3Item3')}</li>
              <li>{t('privacyPage.section3Item4')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section4Title')}</h2>
            <p>
              {t('privacyPage.section4Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section5Title')}</h2>
            <p>
              {t('privacyPage.section5Text')}
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section6Title')}</h2>
            <p>{t('privacyPage.section6Text')}</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>{t('privacyPage.section6Item1')}</li>
              <li>{t('privacyPage.section6Item2')}</li>
              <li>{t('privacyPage.section6Item3')}</li>
              <li>{t('privacyPage.section6Item4')}</li>
              <li>{t('privacyPage.section6Item5')}</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">{t('privacyPage.section7Title')}</h2>
            <p>
              {t('privacyPage.section7Text')} <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
