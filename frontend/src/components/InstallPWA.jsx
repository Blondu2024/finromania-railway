import React, { useState, useEffect } from 'react';
import { Download, X, Share } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Button } from './ui/button';

// ─── Detectare platformă ──────────────────────────────────────────────────────
function getInstallContext() {
  const ua = navigator.userAgent;
  const isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
  const isAndroid = /Android/.test(ua);
  const isSafari = /^((?!chrome|android).)*safari/i.test(ua);
  const isChrome = /Chrome/.test(ua) && /Google Inc/.test(navigator.vendor);
  const isInStandalone =
    window.matchMedia('(display-mode: standalone)').matches ||
    window.navigator.standalone === true;

  return { isIOS, isAndroid, isSafari, isChrome, isInStandalone };
}

// ─── Banner iOS (instrucțiuni Share → Adaugă la ecran) ───────────────────────
function IOSInstallBanner({ onDismiss }) {
  const { t } = useTranslation();
  return (
    <div
      className="fixed bottom-4 left-3 right-3 bg-white dark:bg-zinc-900 border border-border rounded-2xl p-4 shadow-2xl z-50 animate-in slide-in-from-bottom-4"
      data-testid="pwa-ios-banner"
    >
      {/* Close */}
      <button
        onClick={onDismiss}
        className="absolute top-3 right-3 p-1 hover:bg-muted rounded-full transition-colors"
        aria-label={t('common.close')}
      >
        <X className="w-4 h-4 text-muted-foreground" />
      </button>

      {/* Header */}
      <div className="flex items-center gap-3 mb-3 pr-6">
        <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-lg">F</span>
        </div>
        <div>
          <p className="font-bold text-sm">{t('pwa.installTitle')}</p>
          <p className="text-xs text-muted-foreground">{t('pwa.subtitle')}</p>
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-2.5">
        <div className="flex items-center gap-3 text-sm">
          <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">1</span>
          <span>{t('pwa.iosStep1Prefix')} <strong className="inline-flex items-center gap-1">Share <Share className="w-3.5 h-3.5 text-blue-600" /></strong> {t('pwa.iosStep1Suffix')}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">2</span>
          <span>{t('pwa.iosStep2Prefix')} <strong>{t('pwa.iosStep2Action')}</strong></span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs font-bold flex items-center justify-center flex-shrink-0">3</span>
          <span>{t('pwa.iosStep3Prefix')} <strong>{t('pwa.iosStep3Action')}</strong> {t('pwa.iosStep3Done')}</span>
        </div>
      </div>

      {/* Arrow pointing down to share button */}
      <div className="flex justify-center mt-3">
        <p className="text-xs text-muted-foreground text-center">
          {t('pwa.offlineNote')}
        </p>
      </div>

      {/* Bottom triangle pointing to bottom bar */}
      <div className="absolute -bottom-2.5 left-1/2 -translate-x-1/2 w-5 h-5 bg-white dark:bg-zinc-900 border-r border-b border-border rotate-45" />
    </div>
  );
}

// ─── Banner Android/Desktop (beforeinstallprompt) ────────────────────────────
function AndroidInstallBanner({ onInstall, onDismiss }) {
  const { t } = useTranslation();
  return (
    <div
      className="fixed bottom-4 left-3 right-3 sm:left-auto sm:right-4 sm:w-80 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl p-4 shadow-2xl z-50 animate-in slide-in-from-bottom-4"
      data-testid="pwa-android-banner"
    >
      <button
        onClick={onDismiss}
        className="absolute top-2.5 right-2.5 p-1 hover:bg-white/20 rounded-full transition-colors"
        aria-label={t('common.close')}
      >
        <X className="w-4 h-4" />
      </button>

      <div className="flex items-start gap-3">
        <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <Download className="w-6 h-6" />
        </div>
        <div className="flex-1 min-w-0 pr-4">
          <h4 className="font-bold text-sm">{t('pwa.installTitle')}</h4>
          <p className="text-xs text-blue-100 mt-0.5">
            {t('pwa.androidSubtitle')}
          </p>
          <Button
            onClick={onInstall}
            size="sm"
            variant="secondary"
            className="mt-2 text-xs h-8"
            data-testid="pwa-install-btn"
          >
            {t('pwa.installNow')}
          </Button>
        </div>
      </div>
    </div>
  );
}

// ─── MAIN COMPONENT ───────────────────────────────────────────────────────────
export default function InstallPWA() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showAndroidBanner, setShowAndroidBanner] = useState(false);
  const [showIOSBanner, setShowIOSBanner] = useState(false);

  useEffect(() => {
    const { isIOS, isSafari, isInStandalone } = getInstallContext();

    // Dacă e deja instalată — nu arăta nimic
    if (isInStandalone) return;

    // Verifică dacă bannerul a fost dat dismiss recent (48 ore)
    const dismissedAt = localStorage.getItem('pwa_banner_dismissed');
    if (dismissedAt && Date.now() - parseInt(dismissedAt) < 48 * 60 * 60 * 1000) return;

    if (isIOS && isSafari) {
      // iOS Safari — arată instrucțiunile manuale după 4 secunde
      const timer = setTimeout(() => setShowIOSBanner(true), 4000);
      return () => clearTimeout(timer);
    }

    // Android Chrome / Desktop — ascultă beforeinstallprompt
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setTimeout(() => setShowAndroidBanner(true), 5000);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, []);

  const handleAndroidInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') setShowAndroidBanner(false);
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowAndroidBanner(false);
    setShowIOSBanner(false);
    localStorage.setItem('pwa_banner_dismissed', Date.now().toString());
  };

  if (showIOSBanner) return <IOSInstallBanner onDismiss={handleDismiss} />;
  if (showAndroidBanner && deferredPrompt) return <AndroidInstallBanner onInstall={handleAndroidInstall} onDismiss={handleDismiss} />;
  return null;
}
