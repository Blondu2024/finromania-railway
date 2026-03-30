import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { TrendingUp, Award, BookOpen, Info, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import IndexCard from '../components/IndexCard';
import AIAssistant from '../components/AIAssistant';
import { Link } from 'react-router-dom';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function LearnTradingPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [indices, setIndices] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(null);
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [step, setStep] = useState('select'); // select, confirm, trade
  const [aiMessages, setAiMessages] = useState([]);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    try {
      // Fetch curated indices
      const indicesRes = await fetch(`${API_URL}/api/curated/beginner`);
      if (indicesRes.ok) {
        const data = await indicesRes.json();
        setIndices(data.indices || []);
      }

      // Fetch portfolio status
      const portfolioRes = await fetch(`${API_URL}/api/portfolio/status`, {
      });

      if (portfolioRes.ok) {
        const portfolioData = await portfolioRes.json();
        setPortfolio(portfolioData);
      } else if (portfolioRes.status === 404) {
        // Need to initialize
        await initializePortfolio();
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const initializePortfolio = async () => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experience_level: 'beginner',
          completed_tutorial: false
        })
      });

      if (res.ok) {
        fetchData();
      }
    } catch (error) {
      console.error('Error initializing portfolio:', error);
    }
  };

  const handleSelectIndex = (index) => {
    setSelectedIndex(index);
    setStep('confirm');
    
    // AI message
    setAiMessages([`${t('education.greatChoice')} ${index.name} ${index.learning_tip}`]);
  };

  const handleStartTrading = () => {
    setStep('trade');
    setAiMessages([
      `${t('education.letsStartWith')} ${selectedIndex.name}!`,
      t('education.step1BuySmall')
    ]);
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold">{t('education.learnTradingFree')}</h2>
        <p className="text-muted-foreground mb-4">{t('education.loginToStart')}</p>
        <Link to="/login">
          <Button size="lg">{t('common.login')}</Button>
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
        <p>{t('common.loading')}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-20">
      <SEO title="Learn Trading | FinRomania" description="Start your trading journey with free lessons, quizzes, and practical examples from the Romanian stock market." />
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="flex items-center justify-center gap-2">
          <span className="text-4xl">🎓</span>
          <h1 className="text-4xl font-bold">{t('education.learnTradingTitle')}</h1>
        </div>
        <p className="text-xl text-muted-foreground">
          {t('education.learnTradingSubtitle')}
        </p>
      </div>

      {/* Demo Banner */}
      <Alert className="bg-green-50 border-green-200">
        <Info className="w-4 h-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <strong>🟢 {t('education.demoMode')}</strong> - {t('education.virtualMoney')}: {portfolio?.cash?.toLocaleString('ro-RO') || '50,000'} RON
          · {t('education.level')}: <Badge variant="outline" className="ml-1">{portfolio?.experience_level || 'beginner'}</Badge>
        </AlertDescription>
      </Alert>

      {/* Step Indicator */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step === 'select' ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>
                1
              </div>
              <span className="text-sm font-medium">{t('education.chooseAsset')}</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200 mx-2" />
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step === 'confirm' || step === 'trade' ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>
                2
              </div>
              <span className="text-sm font-medium">{t('education.confirm')}</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200 mx-2" />
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                step === 'trade' ? 'bg-blue-600 text-white' : 'bg-gray-200'
              }`}>
                3
              </div>
              <span className="text-sm font-medium">{t('education.trade')}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content based on step */}
      {step === 'select' && (
        <div>
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="w-5 h-5" />
                {t('education.step1ChooseAsset')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                {t('education.step1Desc')} 🎯
              </p>
            </CardContent>
          </Card>

          {/* Index Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {indices.map((index) => (
              <IndexCard
                key={index.id}
                index={index}
                onSelect={handleSelectIndex}
                isSelected={selectedIndex?.id === index.id}
              />
            ))}
          </div>
        </div>
      )}

      {step === 'confirm' && selectedIndex && (
        <div className="max-w-2xl mx-auto space-y-6">
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle className="flex items-center justify-center gap-3">
                <span className="text-4xl">{selectedIndex.emoji}</span>
                <span>{selectedIndex.name}</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert className="bg-blue-50 border-blue-200">
                <Info className="w-4 h-4 text-blue-600" />
                <AlertDescription className="text-blue-800">
                  <strong>{t('education.tipLabel')}:</strong> {selectedIndex.learning_tip}
                </AlertDescription>
              </Alert>

              <div className="bg-gray-50 p-4 rounded-lg space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{t('education.category')}:</span>
                  <span className="font-medium">{selectedIndex.category_ro}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{t('education.volatility')}:</span>
                  <span className="font-medium">{selectedIndex.volatility_ro}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">{t('education.riskLabel')}:</span>
                  <span className="font-medium">
                    {selectedIndex.risk_level === 'low' ? t('education.riskLow') :
                     selectedIndex.risk_level === 'medium' ? t('education.riskMedium') : t('education.riskHigh')}
                  </span>
                </div>
              </div>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setStep('select');
                    setSelectedIndex(null);
                    setAiMessages([]);
                  }}
                >
                  {t('education.backBtn')}
                </Button>
                <Button
                  className="flex-1"
                  size="lg"
                  onClick={handleStartTrading}
                >
                  {t('education.continue')} →
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {step === 'trade' && selectedIndex && (
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle>{t('education.firstTrade')} {selectedIndex.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <p className="text-muted-foreground mb-4">
                  {t('education.tradingComingSoon')}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t('education.fullPortfolioLink')} <Link to="/portfolio" className="text-blue-600 underline">{t('education.fullPortfolio')}</Link>.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* AI Assistant */}
      <AIAssistant 
        messages={aiMessages}
        achievements={portfolio?.achievements || []}
        onAskQuestion={(q) => {
          console.log('User asked:', q);
          // TODO: Integrate with AI Advisor API
        }}
      />
    </div>
  );
}