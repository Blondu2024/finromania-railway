import React, { useState, useEffect } from 'react';
import { Download, X, Smartphone } from 'lucide-react';
import { Button } from './ui/button';

export default function InstallPWA() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showBanner, setShowBanner] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [showIOSInstructions, setShowIOSInstructions] = useState(false);

  useEffect(() => {
    // Check if already installed
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    if (isStandalone) return;

    // Check if dismissed recently (24 hours)
    const dismissedTime = localStorage.getItem('pwa_banner_dismissed');
    if (dismissedTime && Date.now() - parseInt(dismissedTime) < 24 * 60 * 60 * 1000) {
      return;
    }

    // Detect iOS
    const isIOSDevice = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(isIOSDevice);

    if (isIOSDevice) {
      // Show banner for iOS after 5 seconds
      const timer = setTimeout(() => setShowBanner(true), 5000);
      return () => clearTimeout(timer);
    }

    // Listen for beforeinstallprompt (Android/Desktop)
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
    if (isIOS) {
      setShowIOSInstructions(true);
      return;
    }

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
    setShowIOSInstructions(false);
    localStorage.setItem('pwa_banner_dismissed', Date.now().toString());
  };

  if (!showBanner) return null;

  // iOS Instructions Modal
  if (showIOSInstructions) {
    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-4">
        <div className="bg-background rounded-t-2xl sm:rounded-2xl w-full max-w-md p-6 space-y-4">
          <div className="flex justify-between items-start">
            <div className="flex items-center gap-3">
              <Smartphone className="w-8 h-8 text-blue-600" />
              <h3 className="font-bold text-lg">Instalează FinRomania</h3>
            </div>
            <button onClick={handleDismiss} className="p-1">
              <X className="w-5 h-5 text-muted-foreground" />
            </button>
          </div>
          
          <div className="space-y-3 text-sm">
            <p className="text-muted-foreground">Pentru a instala aplicația pe iPhone/iPad:</p>
            <ol className="space-y-2 list-decimal list-inside">
              <li>Apasă pe butonul <strong>Share</strong> (pătratul cu săgeată) din Safari</li>
              <li>Derulează și alege <strong>"Add to Home Screen"</strong></li>
              <li>Apasă <strong>"Add"</strong> în colțul din dreapta sus</li>
            </ol>
          </div>
          
          <Button onClick={handleDismiss} className="w-full">
            Am înțeles
          </Button>
        </div>
      </div>
    );
  }

  // Install Banner
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
            {isIOS ? 'Vezi cum' : 'Instalează'}
          </Button>
        </div>
      </div>
    </div>
  );
}
