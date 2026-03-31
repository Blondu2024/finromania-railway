import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Gift, Zap, ArrowRight } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { useAuth } from '../context/AuthContext';

export default function EarlyAdopterBanner({ variant = 'full' }) {
  const { t } = useTranslation();
  const { user } = useAuth();

  // Daca userul e logat si are PRO, nu arata nimic
  if (user?.subscription_level === 'pro' || user?.is_early_adopter) {
    return null;
  }

  // Banner pentru useri nelogati / fara PRO
  return (
    <Card className="bg-gradient-to-r from-green-600 to-emerald-600 text-white border-0 overflow-hidden" data-testid="free-pro-banner">
      <CardContent className="p-6 md:p-8">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="flex-1">
            <Badge className="bg-white/20 text-white border-0 mb-3">
              <Gift className="w-3 h-3 mr-1" />
              {t('earlyAdopter.specialOffer')}
            </Badge>
            <h2 className="text-2xl md:text-3xl font-bold mb-2">
              {t('earlyAdopter.title')}
            </h2>
            <p className="text-green-100 text-sm md:text-base mb-4">
              {t('earlyAdopter.description')}
            </p>
            <div className="flex flex-wrap gap-2 text-xs text-green-100">
              <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {t('earlyAdopter.fiscalCalc')}</span>
              <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {t('earlyAdopter.unlimitedAlerts')}</span>
              <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {t('earlyAdopter.fastData')}</span>
              <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> {t('earlyAdopter.aiAdvisor')}</span>
            </div>
          </div>
          <div className="text-center">
            <Link to="/login">
              <Button size="lg" className="bg-white text-green-700 hover:bg-green-50 font-bold text-base px-8" data-testid="free-pro-signup-btn">
                {t('earlyAdopter.startFree')} <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <p className="text-xs text-green-200 mt-2">{t('earlyAdopter.noCard')}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
