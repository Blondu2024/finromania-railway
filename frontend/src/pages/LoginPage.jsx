import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { BarChart3, TrendingUp, Star, Briefcase, Loader2 } from 'lucide-react';

export default function LoginPage() {
  const { login, user, loading } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Redirect if already logged in
  useEffect(() => {
    if (!loading && user) {
      console.log('User already logged in, redirecting to home');
      navigate('/', { replace: true });
    }
  }, [user, loading, navigate]);

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  // If user is logged in, show nothing (will redirect)
  if (user) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <>
    <SEO title={`${t('login.welcome')} | FinRomania`} description={t('login.subtitle')} />
    <div className="min-h-[70vh] flex items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4">
            <BarChart3 className="w-12 h-12 text-blue-600" />
          </div>
          <CardTitle className="text-2xl">{t('login.welcome')}</CardTitle>
          <CardDescription>
            {t('login.subtitle')}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Star className="w-5 h-5 text-yellow-500" />
              <span>{t('login.watchlistBenefit')}</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Briefcase className="w-5 h-5 text-green-500" />
              <span>{t('login.portfolioBenefit')}</span>
            </div>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <span>{t('login.alertsBenefit')}</span>
            </div>
          </div>
          
          <Button onClick={login} className="w-full" size="lg">
            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            {t('login.continueGoogle')}
          </Button>
          
          <p className="text-xs text-center text-muted-foreground">
            {t('login.acceptTerms')} <a href="/terms" className="underline">{t('login.termsLink')}</a> {t('common.and', 'și')} <a href="/privacy" className="underline">{t('login.privacyLink')}</a>
          </p>
        </CardContent>
      </Card>
    </div>
    </>
  );
}
