import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Loader2, Crown, ArrowRight, TrendingUp, Sparkles } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PaymentSuccessPage() {
  const { t } = useTranslation();
  const [status, setStatus] = useState('checking'); // checking, success, error
  const [paymentInfo, setPaymentInfo] = useState(null);
  const navigate = useNavigate();
  const { user, checkAuth } = useAuth();

  useEffect(() => {
    // Get session_id from URL
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');

    if (!sessionId) {
      setStatus('error');
      return;
    }

    // Poll payment status
    pollPaymentStatus(sessionId);
  }, []);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    
    if (attempts >= maxAttempts) {
      setStatus('error');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/payments/status/${sessionId}`);
      
      if (!response.ok) {
        throw new Error('Failed to check payment status');
      }

      const data = await response.json();
      
      if (data.payment_status === 'paid') {
        setStatus('success');
        setPaymentInfo(data);
        // Refresh user context so PRO features unlock immediately without page reload
        checkAuth();
        return;
      } else if (data.status === 'expired') {
        setStatus('error');
        return;
      }

      // Still pending - poll again
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      console.error('Error checking payment:', error);
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    }
  };

  if (status === 'checking') {
    return (
      <>
        <SEO title={t('payment.checkingTitle')} />
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md w-full">
            <CardContent className="p-8 text-center">
              <Loader2 className="w-16 h-16 mx-auto text-blue-600 animate-spin mb-4" />
              <h2 className="text-2xl font-bold mb-2">{t('payment.checking')}</h2>
              <p className="text-muted-foreground">
                {t('payment.checkingDesc')}
              </p>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  if (status === 'error') {
    return (
      <>
        <SEO title={t('payment.errorTitle')} />
        <div className="min-h-screen flex items-center justify-center p-4">
          <Card className="max-w-md w-full border-red-200">
            <CardContent className="p-8 text-center">
              <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
                <span className="text-3xl">❌</span>
              </div>
              <h2 className="text-2xl font-bold mb-2">{t('payment.notProcessed')}</h2>
              <p className="text-muted-foreground mb-6">
                {t('payment.errorDesc')}
              </p>
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => navigate('/pricing')} className="flex-1">
                  {t('payment.backToPricing')}
                </Button>
                <Button onClick={() => navigate('/')} className="flex-1">
                  {t('payment.home')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  // Success
  return (
    <>
      <SEO title={t('payment.successTitle')} />
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full border-green-200">
          <CardHeader className="bg-gradient-to-r from-green-600 to-emerald-600 text-white">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-12 h-12" />
              <div>
                <CardTitle className="text-3xl">{t('payment.welcomePro')} 🎉</CardTitle>
                <p className="text-green-100 mt-1">{t('payment.successProcessed')}</p>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-8">
            {/* Payment Info */}
            <div className="bg-muted/50 rounded-lg p-4 mb-6">
              <h3 className="font-bold mb-2">{t('payment.details')}</h3>
              <div className="space-y-1 text-sm">
                <p>{t('payment.package')}: <span className="font-semibold">{paymentInfo?.package || 'PRO'}</span></p>
                <p>{t('payment.amount')}: <span className="font-semibold">{paymentInfo?.amount} {paymentInfo?.currency}</span></p>
                <p>{t('payment.status')}: <span className="text-green-600 font-semibold">✅ {t('payment.paid')}</span></p>
              </div>
            </div>

            {/* PRO Features Unlocked */}
            <div className="mb-6">
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                <Crown className="w-5 h-5 text-amber-500" />
                {t('payment.featuresUnlocked')}
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {[
                  `✅ ${t('payment.unlimitedAI')}`,
                  `✅ ${t('payment.intradayCharts')}`,
                  `✅ ${t('payment.proIndicators')}`,
                  `✅ ${t('payment.candlestickCharts')}`,
                  `✅ ${t('payment.taxCalcFull')}`,
                  `✅ ${t('payment.liveData')}`,
                  `✅ ${t('payment.unlimitedWatchlist')}`,
                  `✅ ${t('payment.unlimitedAlerts')}`
                ].map((feature, i) => (
                  <p key={i} className="text-sm flex items-center gap-2">
                    {feature}
                  </p>
                ))}
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button 
                className="flex-1 bg-gradient-to-r from-blue-700 to-blue-500"
                onClick={() => navigate('/global')}
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                {t('payment.exploreProCharts')}
              </Button>
              <Button 
                variant="outline"
                className="flex-1"
                onClick={() => navigate('/stocks')}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                {t('payment.seeBVB')}
              </Button>
            </div>

            <p className="text-center text-sm text-muted-foreground mt-6">
              {t('payment.emailConfirmation', { email: user?.email || 'N/A' })}
            </p>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
