import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Brain, TrendingUp, TrendingDown, Minus, Lock, Crown,
  Activity, Target, BarChart3, Zap, RefreshCw, ChevronDown
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const PERIOD_KEYS = [
  { key: 'techAnalysis.week1', value: '1w' },
  { key: 'techAnalysis.month1', value: '1m' },
  { key: 'techAnalysis.month3', value: '3m' },
  { key: 'techAnalysis.month6', value: '6m' },
  { key: 'techAnalysis.year1', value: '1y' },
];

export default function AITechnicalAnalysis({ symbol, isPro, token }) {
  const { t } = useTranslation();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('1m');
  const [isOpen, setIsOpen] = useState(false);

  const runAnalysis = async () => {
    if (!isPro) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_URL}/api/ai-analysis/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ symbol, period })
      });

      if (res.ok) {
        const data = await res.json();
        setAnalysis(data);
        setIsOpen(true);
      } else {
        const err = await res.json();
        setError(err.detail || t('techAnalysis.errorAnalysis'));
      }
    } catch (err) {
      setError(t('techAnalysis.couldNotConnect'));
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (signal) => {
    if (signal?.includes('FAVORABIL')) return <TrendingUp className="w-5 h-5" />;
    if (signal?.includes('RISCANT')) return <TrendingDown className="w-5 h-5" />;
    return <Minus className="w-5 h-5" />;
  };

  const getSignalColor = (signal) => {
    if (signal?.includes('FAVORABIL')) return 'text-green-600 bg-green-100';
    if (signal?.includes('RISCANT')) return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getTrendIcon = (direction) => {
    if (direction === 'bullish') return <TrendingUp className="w-4 h-4 text-green-500" />;
    if (direction === 'bearish') return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-gray-500" />;
  };

  // Locked state for non-PRO users
  if (!isPro) {
    return (
      <Card className="border-2 border-dashed border-amber-300 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Brain className="w-5 h-5 text-amber-500" />
            {t('techAnalysis.title')}
            <Badge className="bg-amber-500">PRO</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-6">
          <Lock className="w-12 h-12 mx-auto text-amber-400 mb-4" />
          <h3 className="font-semibold mb-2">{t('techAnalysis.proFeature')}</h3>
          <p className="text-sm text-muted-foreground mb-4">
            {t('techAnalysis.proDescription')}
          </p>
          <ul className="text-sm text-left space-y-2 mb-4 max-w-xs mx-auto">
            <li className="flex items-center gap-2">
              <Target className="w-4 h-4 text-amber-500" />
              {t('techAnalysis.supportResistance')}
            </li>
            <li className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-500" />
              {t('techAnalysis.rsiCalculated')}
            </li>
            <li className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-green-500" />
              {t('techAnalysis.evaluation')}
            </li>
            <li className="flex items-center gap-2">
              <Brain className="w-4 h-4 text-blue-500" />
              {t('techAnalysis.aiInterpretation')}
            </li>
          </ul>
          <Link to="/pricing">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-500">
              <Crown className="w-4 h-4 mr-2" />
              {t('techAnalysis.upgradePro')}
            </Button>
          </Link>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-2 border-amber-400 bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-950/10 dark:to-orange-950/10">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-lg">
            <Brain className="w-5 h-5 text-amber-500" />
            {t('techAnalysis.title')}
            <Badge className="bg-gradient-to-r from-amber-500 to-orange-500">PRO</Badge>
          </div>
          {analysis && (
            <Button 
              variant="ghost" 
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
            >
              <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </Button>
          )}
        </CardTitle>
      </CardHeader>
      
      <CardContent>
        {/* Period selector + Run button */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span className="text-sm text-muted-foreground">{t('techAnalysis.period')}</span>
          {PERIOD_KEYS.map(p => (
            <Button
              key={p.value}
              size="sm"
              variant={period === p.value ? 'default' : 'outline'}
              onClick={() => setPeriod(p.value)}
              className={period === p.value ? 'bg-amber-500 hover:bg-amber-600' : ''}
            >
              {t(p.key)}
            </Button>
          ))}
          <Button
            onClick={runAnalysis}
            disabled={loading}
            className="ml-auto bg-gradient-to-r from-amber-500 to-orange-500 hover:opacity-90"
          >
            {loading ? (
              <><RefreshCw className="w-4 h-4 mr-2 animate-spin" /> {t('techAnalysis.analyzing')}</>
            ) : (
              <><Brain className="w-4 h-4 mr-2" /> {t('techAnalysis.analyze')}</>
            )}
          </Button>
        </div>

        {/* Error */}
        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        <AnimatePresence>
          {analysis && isOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              {/* Evaluation Banner */}
              <div className={`p-4 rounded-xl flex items-center justify-between ${getSignalColor(analysis.analysis?.signal)}`}>
                <div className="flex items-center gap-3">
                  {getSignalIcon(analysis.analysis?.signal)}
                  <div>
                    <p className="font-bold text-lg">{analysis.analysis?.signal}</p>
                    <p className="text-sm opacity-80">{t('techAnalysis.confidenceLevel', { percent: analysis.analysis?.confidence })}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm opacity-70">{t('techAnalysis.currentPrice')}</p>
                  <p className="font-bold text-xl">{analysis.analysis?.current_price?.toFixed(2)} RON</p>
                </div>
              </div>

              {/* Indicators Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Target className="w-3 h-3 text-green-500" /> {t('techAnalysis.support')}
                  </p>
                  <p className="text-lg font-bold text-green-600">
                    {analysis.analysis?.support?.toFixed(2)} RON
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Target className="w-3 h-3 text-red-500" /> {t('techAnalysis.resistance')}
                  </p>
                  <p className="text-lg font-bold text-red-600">
                    {analysis.analysis?.resistance?.toFixed(2)} RON
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Activity className="w-3 h-3 text-blue-500" /> RSI
                  </p>
                  <p className={`text-lg font-bold ${
                    analysis.analysis?.rsi < 30 ? 'text-green-600' :
                    analysis.analysis?.rsi > 70 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {analysis.analysis?.rsi?.toFixed(1)}
                    <span className="text-xs ml-1">
                      {analysis.analysis?.rsi < 30 ? t('techAnalysis.oversold') :
                       analysis.analysis?.rsi > 70 ? t('techAnalysis.overbought') : ''}
                    </span>
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    {getTrendIcon(analysis.analysis?.trend_direction)} {t('techAnalysis.trend')}
                  </p>
                  <p className={`text-lg font-bold capitalize ${
                    analysis.analysis?.trend_direction === 'bullish' ? 'text-green-600' :
                    analysis.analysis?.trend_direction === 'bearish' ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {analysis.analysis?.trend_direction === 'bullish' ? t('techAnalysis.bullish') :
                     analysis.analysis?.trend_direction === 'bearish' ? t('techAnalysis.bearish') : t('techAnalysis.neutral')}
                    <span className="text-xs ml-1">({analysis.analysis?.trend_strength}%)</span>
                  </p>
                </div>
              </div>

              {/* Volume & Market Context Section */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* Volume Analysis */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mb-2">
                    <BarChart3 className="w-3 h-3 text-blue-500" /> {t('common.volume')}
                  </p>
                  <p className="text-lg font-bold">
                    {analysis.analysis?.volume_ratio?.toFixed(2)}x
                    <span className="text-xs ml-1 font-normal text-muted-foreground">{t('techAnalysis.vsAverage')}</span>
                  </p>
                  <p className={`text-xs mt-1 ${
                    analysis.analysis?.volume_status === 'FOARTE_MARE' ? 'text-orange-600' :
                    analysis.analysis?.volume_status === 'MARE' ? 'text-green-600' :
                    analysis.analysis?.volume_status === 'FOARTE_MIC' ? 'text-red-600' : 'text-gray-500'
                  }`}>
                    {analysis.analysis?.volume_alert}
                  </p>
                </div>

                {/* Market Context */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mb-2">
                    <TrendingUp className="w-3 h-3 text-blue-500" /> {t('techAnalysis.bvbMarket')}
                  </p>
                  <p className={`text-lg font-bold ${
                    analysis.analysis?.bet_change > 0 ? 'text-green-600' :
                    analysis.analysis?.bet_change < 0 ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {analysis.analysis?.bet_change !== null ? `${analysis.analysis?.bet_change > 0 ? '+' : ''}${analysis.analysis?.bet_change?.toFixed(2)}%` : 'N/A'}
                  </p>
                  <p className="text-xs mt-1 text-muted-foreground">
                    {analysis.analysis?.market_description || analysis.analysis?.market_sentiment}
                  </p>
                </div>

                {/* Liquidity */}
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mb-2">
                    <Zap className="w-3 h-3 text-cyan-500" /> {t('techAnalysis.liquidity')}
                  </p>
                  <p className="text-lg font-bold">
                    {analysis.analysis?.liquidity_score}/5
                    <span className={`text-xs ml-2 px-1.5 py-0.5 rounded ${
                      analysis.analysis?.liquidity_score >= 4 ? 'bg-green-100 text-green-700' :
                      analysis.analysis?.liquidity_score >= 3 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                    }`}>
                      {analysis.analysis?.liquidity_tier}
                    </span>
                  </p>
                  <p className="text-xs mt-1 text-muted-foreground">
                    {analysis.analysis?.liquidity_description}
                  </p>
                </div>
              </div>

              {/* Moving Averages */}
              <div className="flex flex-wrap gap-2">
                {analysis.analysis?.ma20 && (
                  <Badge variant="outline" className="text-sm">
                    MA20: {analysis.analysis.ma20.toFixed(2)}
                  </Badge>
                )}
                {analysis.analysis?.ma50 && (
                  <Badge variant="outline" className="text-sm">
                    MA50: {analysis.analysis.ma50.toFixed(2)}
                  </Badge>
                )}
                {analysis.analysis?.ma200 && (
                  <Badge variant="outline" className="text-sm">
                    MA200: {analysis.analysis.ma200.toFixed(2)}
                  </Badge>
                )}
              </div>

              {/* Reasons */}
              {analysis.analysis?.reasons?.length > 0 && (
                <div className="bg-white dark:bg-gray-800 p-3 rounded-lg border">
                  <p className="text-xs text-muted-foreground mb-2">{t('techAnalysis.evaluationFactors')}</p>
                  <ul className="text-sm space-y-1">
                    {analysis.analysis.reasons.map((reason, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Warnings */}
              {analysis.analysis?.warnings?.length > 0 && (
                <div className="bg-orange-50 dark:bg-orange-950/20 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
                  <p className="text-xs text-orange-700 dark:text-orange-400 font-medium mb-2">{`⚠️ ${t('techAnalysis.warnings')}`}</p>
                  <ul className="text-sm space-y-1 text-orange-700 dark:text-orange-300">
                    {analysis.analysis.warnings.map((warning, idx) => (
                      <li key={idx} className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                        {warning}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* AI Interpretation */}
              <div className="bg-gradient-to-r from-blue-50 to-blue-50 dark:from-blue-950/20 dark:to-blue-950/20 p-4 rounded-xl border border-blue-200 dark:border-blue-800">
                <div className="flex items-center gap-2 mb-2">
                  <Brain className="w-5 h-5 text-blue-600" />
                  <p className="font-semibold text-blue-800 dark:text-blue-300">{t('techAnalysis.aiInterpretationTitle')}</p>
                </div>
                <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
                  {analysis.ai_interpretation}
                </p>
              </div>

              {/* Disclaimer */}
              <p className="text-xs text-muted-foreground text-center">
                {`⚠️ ${t('techAnalysis.disclaimer')}`}
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Initial state - no analysis yet */}
        {!analysis && !loading && (
          <div className="text-center py-4 text-sm text-muted-foreground">
            <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
            {t('techAnalysis.initialPrompt')}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
