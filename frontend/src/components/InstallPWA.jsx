import React, { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';
import { Button } from './ui/button';

export default function InstallPWA() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if already installed
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    if (isStandalone) return;

    // Check if dismissed recently (24 hours)
    const dismissedTime = localStorage.getItem('pwa_banner_dismissed');
    if (dismissedTime && Date.now() - parseInt(dismissedTime) < 24 * 60 * 60 * 1000) {
      return;
    }

    // Listen for beforeinstallprompt (Chrome Android/Desktop)
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      // Show banner after 5 seconds
      setTimeout(() => setShowBanner(true), 5000);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    return () => window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setShowBanner(false);
    }
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem('pwa_banner_dismissed', Date.now().toString());
  };

  // Only show on Chrome/Android/Desktop - not iOS
  if (!showBanner || !deferredPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:w-80 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl p-4 shadow-2xl z-50 animate-in slide-in-from-bottom-5">
      <button 
        onClick={handleDismiss}
        className="absolute top-2 right-2 p-1 hover:bg-white/20 rounded-full transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
      
      <div className="flex items-start gap-3">
        <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center flex-shrink-0">
          <Download className="w-6 h-6" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-bold text-sm">Instalează FinRomania</h4>
          <p className="text-xs text-blue-100 mt-0.5">
            Adaugă aplicația pe telefon pentru acces rapid
          </p>
          <Button 
            onClick={handleInstall}
            size="sm"
            variant="secondary"
            className="mt-2 text-xs h-8"
          >
            Instalează Acum
          </Button>
        </div>
      </div>
    </div>
  );
}
