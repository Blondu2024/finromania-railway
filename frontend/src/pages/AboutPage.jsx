import React from 'react';
import { Heart, Target, Users, Zap, Award, TrendingUp, BookOpen, Globe } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';

export default function AboutPage() {
  const { t } = useTranslation();
  return (
    <>
      <SEO
        title={`${t('about.title')} - FinRomania`}
        description={t('about.subtitle')}
        url="https://finromania.ro/about"
      />
      
      <div className="max-w-5xl mx-auto px-4 py-12 space-y-16">
        {/* Hero Section */}
        <div className="text-center space-y-6">
          <div className="inline-block p-6 bg-gradient-to-br from-blue-700 to-blue-500 rounded-full">
            <Heart className="w-16 h-16 text-white" />
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold">
            {t('about.title')}
          </h1>
          <p className="text-xl sm:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            {t('about.subtitle')}
          </p>
        </div>

        {/* Story Section */}
        <Card className="border-2 border-blue-200">
          <CardContent className="p-8 md:p-12">
            <div className="prose prose-lg max-w-none">
              <h2 className="text-3xl font-bold mb-6 flex items-center gap-3">
                <Target className="w-8 h-8 text-blue-600" />
                {t('about.whyTitle')}
              </h2>
              
              <p className="text-lg leading-relaxed text-muted-foreground">
                {t('about.whyParagraph1')}
              </p>

              <p className="text-lg leading-relaxed text-muted-foreground" dangerouslySetInnerHTML={{ __html: t('about.whyParagraph2') }} />

            </div>
          </CardContent>
        </Card>

        {/* Values */}
        <div>
          <h2 className="text-3xl font-bold text-center mb-8">{t('about.values')}</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                  <Globe className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">{t('about.freeValue')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.freeValueDesc')}
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-green-100 rounded-full mb-4">
                  <BookOpen className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">{t('about.qualityValue')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.qualityValueDesc')}
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
                  <Zap className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">{t('about.innovationValue')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.innovationValueDesc')}
                </p>
              </CardContent>
            </Card>

            <Card className="text-center hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="inline-block p-4 bg-orange-100 rounded-full mb-4">
                  <Users className="w-8 h-8 text-orange-600" />
                </div>
                <h3 className="font-bold text-lg mb-2">{t('about.communityValue')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.communityValueDesc')}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Features Highlight */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-50 rounded-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-center mb-8">{t('about.whatWeOffer')}</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">{t('about.featureRealBVB')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.featureRealBVBDesc')}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-lg flex items-center justify-center">
                  <BookOpen className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">{t('about.featureTradingSchool')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.featureTradingSchoolDesc')}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-green-600 text-white rounded-lg flex items-center justify-center">
                  <Zap className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">{t('about.featureAIAdvisor')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.featureAIAdvisorDesc')}
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-orange-600 text-white rounded-lg flex items-center justify-center">
                  <Award className="w-6 h-6" />
                </div>
              </div>
              <div>
                <h3 className="font-bold mb-2">{t('about.featureProTools')}</h3>
                <p className="text-sm text-muted-foreground">
                  {t('about.featureProToolsDesc')}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-4xl font-bold text-blue-600 mb-2">17</div>
            <div className="text-sm text-muted-foreground">{t('about.statLessons')}</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-600 mb-2">99</div>
            <div className="text-sm text-muted-foreground">{t('about.statGlossary')}</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-blue-600 mb-2">20+</div>
            <div className="text-sm text-muted-foreground">{t('about.statStocks')}</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-orange-600 mb-2">100%</div>
            <div className="text-sm text-muted-foreground">{t('about.statFree')}</div>
          </div>
        </div>

        {/* CTA */}
        <Card className="bg-gradient-to-r from-blue-700 to-blue-500 text-white border-0">
          <CardContent className="p-8 md:p-12 text-center">
            <h2 className="text-3xl font-bold mb-4">{t('about.startToday')}</h2>
            <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
              {t('about.joinThousands')}
            </p>
            <div className="flex gap-4 justify-center flex-wrap">
              <Link to="/trading-school">
                <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-blue-50 transition-colors">
                  🎓 {t('about.ctaTradingSchool')}
                </button>
              </Link>
              <Link to="/stocks">
                <button className="bg-white/20 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white/30 transition-colors border-2 border-white/40">
                  📈 {t('about.ctaExploreBVB')}
                </button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Team / Contact */}
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-bold">{t('about.questionsTitle')}</h2>
          <p className="text-muted-foreground">
            {t('about.questionsDesc')}
          </p>
          <div className="flex gap-3 justify-center">
            <Link to="/faq">
              <button className="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors">
                ❓ FAQ
              </button>
            </Link>
            <Link to="/advisor">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                🤖 {t('about.askAI')}
              </button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
}