import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Bell, BellOff, TrendingUp, Newspaper, Calendar, GraduationCap,
  Save, Check, Loader2, AlertTriangle, Smartphone, Mail, Globe, MailCheck
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Switch } from '../components/ui/switch';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Toggle Item Component
const ToggleItem = ({ label, description, checked, onChange, icon: Icon, disabled }) => (
  <div className={`flex items-center justify-between p-4 rounded-lg border ${
    disabled ? 'opacity-50 bg-muted/50' : 'hover:bg-muted/30'
  } transition-all`}>
    <div className="flex items-center gap-3">
      {Icon && <Icon className="w-5 h-5 text-muted-foreground" />}
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
    <Switch
      checked={checked}
      onCheckedChange={onChange}
      disabled={disabled}
    />
  </div>
);

// Category Section Component
const CategorySection = ({ title, icon: Icon, children, color }) => (
  <Card>
    <CardHeader className={`bg-gradient-to-r ${color} text-white rounded-t-lg`}>
      <CardTitle className="flex items-center gap-2 text-lg">
        <Icon className="w-5 h-5" />
        {title}
      </CardTitle>
    </CardHeader>
    <CardContent className="p-0 divide-y">
      {children}
    </CardContent>
  </Card>
);

export default function NotificationSettingsPage() {
  const { t } = useTranslation();
  const { user, token } = useAuth();
  const [preferences, setPreferences] = useState({
    market_open_close: false,
    market_big_moves: false,
    daily_summary: false,
    watchlist_price_alerts: true,
    watchlist_big_moves: true,
    dividend_announcements: false,
    important_news: false,
    watchlist_news: false,
    lesson_reminders: false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [browserPermission, setBrowserPermission] = useState('default');

  // Email subscription state
  const [emailSubscribed, setEmailSubscribed] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailSaved, setEmailSaved] = useState(false);

  // Check browser notification permission
  useEffect(() => {
    if ('Notification' in window) {
      setBrowserPermission(Notification.permission);
    }
  }, []);

  // Fetch preferences + email subscription status
  useEffect(() => {
    const fetchAll = async () => {
      if (!token) { setLoading(false); return; }
      try {
        const [prefsRes, emailRes] = await Promise.all([
          fetch(`${API_URL}/api/watchlist/notifications/preferences`, {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch(`${API_URL}/api/daily-summary/my-subscription`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ]);
        if (prefsRes.ok) {
          const data = await prefsRes.json();
          setPreferences(prev => ({ ...prev, ...data }));
        }
        if (emailRes.ok) {
          const data = await emailRes.json();
          setEmailSubscribed(data.subscribed);
        }
      } catch (err) {
        console.error('Error fetching preferences:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [token]);

  // Toggle email subscription
  const toggleEmailSubscription = async () => {
    if (!token) return;
    setEmailLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/daily-summary/toggle-subscription`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setEmailSubscribed(data.subscribed);
        setEmailSaved(true);
        setTimeout(() => setEmailSaved(false), 3000);
      }
    } catch (err) {
      console.error('Error toggling subscription:', err);
    } finally {
      setEmailLoading(false);
    }
  };

  // Request browser notification permission
  const requestPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission();
      setBrowserPermission(permission);
      
      if (permission === 'granted') {
        new Notification('🔔 FinRomania', {
          body: t('notifications.activated'),
          icon: '/favicon.ico'
        });
      }
    }
  };

  // Update preference
  const updatePreference = (key, value) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  // Save preferences
  const savePreferences = async () => {
    if (!token) return;

    setSaving(true);
    try {
      const res = await fetch(`${API_URL}/api/watchlist/notifications/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(preferences)
      });

      if (res.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      }
    } catch (err) {
      console.error('Error saving preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  // Not logged in
  if (!user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <Bell className="w-16 h-16 text-blue-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">{t('notifications.title')}</h2>
            <p className="text-muted-foreground mb-6">
              {t('notifications.loginPrompt')}
            </p>
            <div className="flex gap-3 justify-center">
              <Link to="/login">
                <Button>{t('common.login')}</Button>
              </Link>
              <Link to="/login">
                <Button variant="outline">{t('notifications.register')}</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <SEO
        title={`${t('notifications.title')} | FinRomania`}
        description={t('notifications.chooseNotifications')}
      />

      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Bell className="w-8 h-8 text-blue-500" />
            {t('notifications.title')}
          </h1>
          <p className="text-muted-foreground mt-1">
            {t('notifications.chooseNotifications')}
          </p>
        </motion.div>

        {/* Browser Permission Card */}
        {browserPermission !== 'granted' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <Card className="border-yellow-300 bg-yellow-50">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="w-6 h-6 text-yellow-600" />
                    <div>
                      <p className="font-semibold">{t('notifications.enableBrowser')}</p>
                      <p className="text-sm text-muted-foreground">
                        {t('notifications.enableBrowserDesc')}
                      </p>
                    </div>
                  </div>
                  <Button onClick={requestPermission}>
                    <Smartphone className="w-4 h-4 mr-2" />
                    {t('notifications.activate')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {browserPermission === 'granted' && (
          <Card className="border-green-300 bg-green-50">
            <CardContent className="p-4">
              <div className="flex items-center gap-3 text-green-700">
                <Check className="w-6 h-6" />
                <span className="font-medium">{t('notifications.browserActive')}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* EMAIL SUBSCRIPTION SECTION */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-blue-200 dark:border-blue-800">
            <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-500 text-white rounded-t-lg">
              <CardTitle className="flex items-center gap-2 text-lg">
                <MailCheck className="w-5 h-5" />
                {t('notifications.dailyEmailTitle')}
              </CardTitle>
              <CardDescription className="text-blue-100">
                {t('notifications.dailyEmailDesc')}
              </CardDescription>
            </CardHeader>
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${emailSubscribed ? 'bg-green-100 dark:bg-green-900/30' : 'bg-muted'}`}>
                    <Mail className={`w-5 h-5 ${emailSubscribed ? 'text-green-600' : 'text-muted-foreground'}`} />
                  </div>
                  <div>
                    <p className="font-medium">{t('notifications.dailySummaryBVB')}</p>
                    <p className="text-sm text-muted-foreground">
                      {emailSubscribed
                        ? t('notifications.emailActiveAt', { email: user?.email })
                        : t('notifications.emailDisabled')}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {emailSaved && (
                    <Badge variant="outline" className="text-green-600 border-green-300">
                      <Check className="w-3 h-3 mr-1" /> {t('notifications.saved')}
                    </Badge>
                  )}
                  {emailLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                  ) : (
                    <Switch
                      checked={emailSubscribed}
                      onCheckedChange={toggleEmailSubscription}
                      data-testid="daily-summary-email-toggle"
                    />
                  )}
                </div>
              </div>
              {emailSubscribed && (
                <div className="mt-4 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800 text-sm text-green-700 dark:text-green-400 flex items-start gap-2">
                  <Check className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span dangerouslySetInnerHTML={{ __html: t('notifications.subscribedConfirmation', { email: user?.email }) }} />
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Market Notifications */}
        <CategorySection
          title={`📈 ${t('notifications.marketCategory')}`}
          icon={TrendingUp}
          color="from-blue-500 to-blue-600"
        >
          <ToggleItem
            label={t('notifications.exchangeSchedule')}
            description={t('notifications.openCloseDesc')}
            checked={preferences.market_open_close}
            onChange={(v) => updatePreference('market_open_close', v)}
            icon={Globe}
          />
          <ToggleItem
            label={t('notifications.bigMovesMarket')}
            description={t('notifications.bigMovesMarketDesc')}
            checked={preferences.market_big_moves}
            onChange={(v) => updatePreference('market_big_moves', v)}
            icon={TrendingUp}
          />
          <ToggleItem
            label={t('notifications.eveningSummary')}
            description={t('notifications.eveningSummaryDesc')}
            checked={preferences.daily_summary}
            onChange={(v) => updatePreference('daily_summary', v)}
            icon={Mail}
          />
        </CategorySection>

        {/* Watchlist Notifications */}
        <CategorySection
          title={`⭐ ${t('notifications.watchlistCategory')}`}
          icon={Bell}
          color="from-yellow-500 to-amber-500"
        >
          <ToggleItem
            label={t('notifications.priceAlerts')}
            description={t('notifications.priceAlertsDesc')}
            checked={preferences.watchlist_price_alerts}
            onChange={(v) => updatePreference('watchlist_price_alerts', v)}
            icon={Bell}
          />
          <ToggleItem
            label={t('notifications.bigMovesWatchlist')}
            description={t('notifications.bigMovesWatchlistDesc')}
            checked={preferences.watchlist_big_moves}
            onChange={(v) => updatePreference('watchlist_big_moves', v)}
            icon={TrendingUp}
          />
          <ToggleItem
            label={t('notifications.dividendAnnouncements')}
            description={t('notifications.dividendAnnouncementsDesc')}
            checked={preferences.dividend_announcements}
            onChange={(v) => updatePreference('dividend_announcements', v)}
            icon={Calendar}
          />
        </CategorySection>

        {/* News Notifications */}
        <CategorySection
          title={`📰 ${t('notifications.newsCategory')}`}
          icon={Newspaper}
          color="from-blue-500 to-blue-600"
        >
          <ToggleItem
            label={t('notifications.importantNews')}
            description={t('notifications.importantNewsDesc')}
            checked={preferences.important_news}
            onChange={(v) => updatePreference('important_news', v)}
            icon={Newspaper}
          />
          <ToggleItem
            label={t('notifications.watchlistNews')}
            description={t('notifications.watchlistNewsDesc')}
            checked={preferences.watchlist_news}
            onChange={(v) => updatePreference('watchlist_news', v)}
            icon={Bell}
          />
        </CategorySection>

        {/* Education Notifications */}
        <CategorySection
          title={`🎓 ${t('notifications.educationCategory')}`}
          icon={GraduationCap}
          color="from-green-500 to-green-600"
        >
          <ToggleItem
            label={t('notifications.lessonReminder')}
            description={t('notifications.lessonReminderDesc')}
            checked={preferences.lesson_reminders}
            onChange={(v) => updatePreference('lesson_reminders', v)}
            icon={GraduationCap}
          />
        </CategorySection>

        {/* Save Button */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex justify-end gap-3"
        >
          {saved && (
            <Badge variant="outline" className="text-green-600 border-green-300 py-2 px-4">
              <Check className="w-4 h-4 mr-1" />
              {t('notifications.saved')}
            </Badge>
          )}
          <Button onClick={savePreferences} disabled={saving} size="lg">
            {saving ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> {t('notifications.saving')}</>
            ) : (
              <><Save className="w-4 h-4 mr-2" /> {t('notifications.savePreferences')}</>
            )}
          </Button>
        </motion.div>

        {/* Info */}
        <Card className="bg-slate-50">
          <CardContent className="p-4 text-sm text-muted-foreground">
            <p dangerouslySetInnerHTML={{ __html: `ℹ️ ${t('notifications.infoNote')}` }} />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
