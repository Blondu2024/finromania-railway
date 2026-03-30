import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { AlertTriangle, TrendingUp, TrendingDown, DollarSign, Award, RefreshCw, Info, BookOpen, Bot } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Link } from 'react-router-dom';
import TradeModal from '../components/TradeModal';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PortfolioPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showTradeModal, setShowTradeModal] = useState(false);

  useEffect(() => {
    if (user) {
      fetchPortfolio();
    }
  }, [user]);

  const fetchPortfolio = async () => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio/status`, {
      });

      if (res.status === 404) {
        setShowOnboarding(true);
        setLoading(false);
        return;
      }

      if (res.ok) {
        const data = await res.json();
        setPortfolio(data);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const initializePortfolio = async (experienceLevel) => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio/init`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          experience_level: experienceLevel,
          completed_tutorial: true
        })
      });

      if (res.ok) {
        setShowOnboarding(false);
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Error initializing portfolio:', error);
    }
  };

  const resetPortfolio = async () => {
    if (!window.confirm(t('virtualPortfolio.resetConfirm'))) {
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/portfolio/reset`, {
        method: 'POST'
      });

      if (res.ok) {
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Error resetting portfolio:', error);
    }
  };

  const closePosition = async (positionId) => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio/close/${positionId}`, {
        method: 'POST'
      });

      if (res.ok) {
        const result = await res.json();
        alert(`${t('virtualPortfolio.positionClosed')}\nP&L: ${result.pnl.toFixed(2)} RON (${result.pnl_percent.toFixed(2)}%)`);
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Error closing position:', error);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <DollarSign className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold">{t('virtualPortfolio.title')}</h2>
        <p className="text-muted-foreground mb-4">{t('virtualPortfolio.loginRequired')}</p>
        <Link to="/login">
          <Button size="lg">{t('virtualPortfolio.loginButton')}</Button>
        </Link>
      </div>
    );
  }

  // BETA MODE - Only admin access
  if (!user.is_admin) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="border-2 border-orange-400">
          <CardContent className="p-8 text-center space-y-4">
            <div className="inline-block p-4 bg-orange-100 rounded-full">
              <DollarSign className="w-12 h-12 text-orange-600" />
            </div>
            <Badge variant="destructive" className="text-lg px-4 py-2">
              🚧 {t('virtualPortfolio.betaComingSoon')}
            </Badge>
            <h2 className="text-2xl font-bold">{t('virtualPortfolio.inDevelopment')}</h2>
            <p className="text-muted-foreground">
              {t('virtualPortfolio.developmentDesc')}
            </p>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-blue-900">
                💡 <strong>{t('virtualPortfolio.meanwhile')}</strong> {t('virtualPortfolio.meanwhileTry')} <Link to="/trading-school" className="text-blue-600 underline font-semibold">Trading School</Link> -
                {t('virtualPortfolio.meanwhileDesc')}
              </p>
            </div>
            <div className="flex gap-3 justify-center">
              <Link to="/trading-school">
                <Button size="lg">
                  🎓 {t('virtualPortfolio.startLearning')}
                </Button>
              </Link>
              <Link to="/">
                <Button variant="outline" size="lg">
                  ← {t('virtualPortfolio.home')}
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4" />
        <p>{t('virtualPortfolio.loading')}</p>
      </div>
    );
  }

  // Onboarding Modal
  if (showOnboarding) {
    return (
      <div className="max-w-2xl mx-auto py-12">
        <Card className="border-2 border-blue-200">
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              🎉 {t('virtualPortfolio.welcomeTitle')}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <Alert>
              <Info className="w-4 h-4" />
              <AlertDescription>
                <strong>{t('virtualPortfolio.demoMode')}</strong> {t('virtualPortfolio.demoDesc')}
              </AlertDescription>
            </Alert>

            <div>
              <h3 className="font-semibold mb-2">📖 {t('virtualPortfolio.whatYouLearn')}</h3>
              <ul className="space-y-2 text-sm">
                <li>✓ {t('virtualPortfolio.learnBuySell')}</li>
                <li>✓ {t('virtualPortfolio.learnLeverage')}</li>
                <li>✓ {t('virtualPortfolio.learnStopLoss')}</li>
                <li>✓ {t('virtualPortfolio.learnStrategies')}</li>
                <li>✓ {t('virtualPortfolio.learnIndicators')}</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-3">🎯 {t('virtualPortfolio.selectLevel')}</h3>
              <div className="space-y-3">
                <Card 
                  className="cursor-pointer hover:border-blue-500 transition-colors"
                  onClick={() => initializePortfolio('beginner')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">🌱</span>
                      <div className="flex-1">
                        <h4 className="font-semibold">{t('virtualPortfolio.beginner')}</h4>
                        <p className="text-sm text-muted-foreground">{t('virtualPortfolio.beginnerDesc')}</p>
                        <Badge variant="secondary" className="mt-2">{t('virtualPortfolio.recommended')}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card 
                  className="cursor-pointer hover:border-orange-500 transition-colors"
                  onClick={() => initializePortfolio('intermediate')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">🌿</span>
                      <div className="flex-1">
                        <h4 className="font-semibold">{t('virtualPortfolio.intermediate')}</h4>
                        <p className="text-sm text-muted-foreground">{t('virtualPortfolio.intermediateDesc')}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card 
                  className="cursor-pointer hover:border-red-500 transition-colors"
                  onClick={() => initializePortfolio('advanced')}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">🌳</span>
                      <div className="flex-1">
                        <h4 className="font-semibold">{t('virtualPortfolio.advanced')}</h4>
                        <p className="text-sm text-muted-foreground">{t('virtualPortfolio.advancedDesc')}</p>
                        <Badge variant="destructive" className="mt-2">{t('virtualPortfolio.highRisk')}</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <Alert className="bg-yellow-50 border-yellow-200">
              <AlertTriangle className="w-4 h-4 text-yellow-600" />
              <AlertDescription className="text-yellow-800">
                <strong>{t('virtualPortfolio.importantWarning')}</strong> {t('virtualPortfolio.warningText')}
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!portfolio) return null;

  const isProfitable = portfolio.total_pnl >= 0;

  return (
    <div className="space-y-6">
      <SEO title="Portfolio Simulator | FinRomania" description="Practice portfolio management with a virtual trading simulator. Risk-free learning environment." />
      {/* Demo Banner */}
      <Alert className="bg-green-50 border-green-200">
        <Info className="w-4 h-4 text-green-600" />
        <AlertDescription className="text-green-800">
          <strong>🟢 {t('virtualPortfolio.demoModeBanner')}</strong> - {t('virtualPortfolio.virtualMoney')} · {t('virtualPortfolio.capital')}: 50,000 RON · {t('virtualPortfolio.level')}: <Badge variant="outline">{portfolio.experience_level}</Badge>
        </AlertDescription>
      </Alert>

      {/* Portfolio Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">{t('virtualPortfolio.totalValue')}</div>
            <div className="text-2xl font-bold">{portfolio.total_value.toLocaleString('ro-RO')} RON</div>
            <div className={`text-sm flex items-center gap-1 ${isProfitable ? 'text-green-600' : 'text-red-600'}`}>
              {isProfitable ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {isProfitable ? '+' : ''}{portfolio.total_pnl.toFixed(2)} RON ({portfolio.total_pnl_percent.toFixed(2)}%)
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">{t('virtualPortfolio.availableCash')}</div>
            <div className="text-2xl font-bold">{portfolio.cash.toLocaleString('ro-RO')} RON</div>
            <div className="text-sm text-muted-foreground">{t('virtualPortfolio.marginUsed')}: {portfolio.margin_used.toFixed(2)} RON</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">{t('virtualPortfolio.openPositionsCount')}</div>
            <div className="text-2xl font-bold">{portfolio.open_positions_count}</div>
            <div className="text-sm text-muted-foreground">{t('virtualPortfolio.positionsValue')}: {portfolio.positions_value.toFixed(2)} RON</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground mb-1">{t('virtualPortfolio.maxLeverage')}</div>
            <div className="text-2xl font-bold">{portfolio.max_leverage}x</div>
            <div className="text-sm text-muted-foreground">{t('virtualPortfolio.trades')}: {portfolio.trades_count}</div>
          </CardContent>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 flex-wrap">
        <Button onClick={() => setShowTradeModal(true)}>
          <TrendingUp className="w-4 h-4 mr-2" />
          {t('virtualPortfolio.newTrade')}
        </Button>
        <Button variant="outline" onClick={fetchPortfolio}>
          <RefreshCw className="w-4 h-4 mr-2" />
          {t('virtualPortfolio.refresh')}
        </Button>
        <Button variant="outline" onClick={resetPortfolio}>
          🔄 {t('virtualPortfolio.resetPortfolio')}
        </Button>
        <Link to="/glossary">
          <Button variant="outline">
            <BookOpen className="w-4 h-4 mr-2" />
            {t('virtualPortfolio.glossary')}
          </Button>
        </Link>
        <Link to="/advisor">
          <Button variant="outline">
            <Bot className="w-4 h-4 mr-2" />
            {t('virtualPortfolio.aiAdvisor')}
          </Button>
        </Link>
      </div>

      {/* Open Positions */}
      {portfolio.open_positions && portfolio.open_positions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>{t('virtualPortfolio.openPositions')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {portfolio.open_positions.map((pos) => (
                <Card key={pos.position_id} className="border">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h4 className="font-semibold">{pos.symbol}</h4>
                          <Badge variant="secondary">{pos.name}</Badge>
                          <Badge variant={pos.position_type === 'long' ? 'default' : 'destructive'}>
                            {pos.position_type.toUpperCase()}
                          </Badge>
                          {pos.leverage > 1 && (
                            <Badge variant="outline">{pos.leverage}x</Badge>
                          )}
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <div className="text-muted-foreground">{t('virtualPortfolio.quantity')}</div>
                            <div className="font-medium">{pos.quantity}</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">{t('virtualPortfolio.entry')}</div>
                            <div className="font-medium">{pos.entry_price.toFixed(2)} RON</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">{t('virtualPortfolio.current')}</div>
                            <div className="font-medium">{pos.current_price.toFixed(2)} RON</div>
                          </div>
                          <div>
                            <div className="text-muted-foreground">P&L</div>
                            <div className={`font-bold ${pos.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)} RON ({pos.pnl_percent.toFixed(2)}%)
                            </div>
                          </div>
                        </div>
                        {(pos.stop_loss || pos.take_profit) && (
                          <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                            {pos.stop_loss && <div>Stop Loss: {pos.stop_loss} RON</div>}
                            {pos.take_profit && <div>Take Profit: {pos.take_profit} RON</div>}
                          </div>
                        )}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => closePosition(pos.position_id)}
                      >
                        {t('virtualPortfolio.closePosition')}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Achievements */}
      {portfolio.achievements && portfolio.achievements.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              {t('virtualPortfolio.achievements')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {portfolio.achievements.map((ach) => (
                <Badge key={ach} variant="secondary" className="text-sm">
                  🏆 {ach.replace('_', ' ')}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trade Modal */}
      <TradeModal 
        open={showTradeModal} 
        onClose={() => setShowTradeModal(false)}
        onSuccess={fetchPortfolio}
        portfolio={portfolio}
      />
    </div>
  );
}
