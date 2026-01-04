import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  ChevronRight, X, Sparkles, MousePointer2,
  BarChart3, Globe, Newspaper, Calendar, DollarSign,
  GraduationCap, Bot, Star, HelpCircle, Zap
} from 'lucide-react';
import { Button } from './ui/button';

const TOUR_STORAGE_KEY = 'finromania_tour_completed';

// Tour Steps - targeting real DOM elements
const tourSteps = [
  {
    id: 'welcome',
    type: 'modal', // Full screen welcome
    title: 'Bine ai venit pe FinRomania! 🇷🇴',
    description: 'Hai să-ți arăt ce poți face aici. Durează doar 60 de secunde!',
    icon: Sparkles,
    gradient: 'from-blue-600 via-purple-600 to-pink-600',
  },
  {
    id: 'logo',
    type: 'spotlight',
    selector: 'a[href="/"]', // Logo/Home link
    title: 'Acasă',
    description: 'Oricând vrei să te întorci la pagina principală, apasă aici.',
    position: 'bottom',
    icon: BarChart3,
  },
  {
    id: 'bvb',
    type: 'spotlight',
    selector: 'a[href="/stocks"]',
    title: '📈 Acțiuni BVB',
    description: 'Toate acțiunile de pe Bursa de Valori București, cu prețuri LIVE!',
    position: 'bottom',
    icon: BarChart3,
    highlight: true,
  },
  {
    id: 'global',
    type: 'spotlight',
    selector: 'a[href="/global"]',
    title: '🌍 Piețe Globale',
    description: 'S&P 500, Bitcoin, Aur, Petrol - toate piețele mondiale într-un singur loc!',
    position: 'bottom',
    icon: Globe,
    highlight: true,
  },
  {
    id: 'education',
    type: 'spotlight',
    selector: 'a[href="/trading-school"]',
    title: '🎓 Învață Trading',
    description: 'Cursuri GRATUITE de trading și investiții. De la zero la expert!',
    position: 'bottom',
    icon: GraduationCap,
    highlight: true,
  },
  {
    id: 'news',
    type: 'spotlight',
    selector: 'a[href="/news"]',
    title: '📰 Știri Financiare',
    description: 'Știri din România și internaționale, traduse automat în română cu analiză AI!',
    position: 'bottom',
    icon: Newspaper,
  },
  {
    id: 'calendar',
    type: 'spotlight',
    selector: 'a[href="/calendar"]',
    title: '📅 Calendar Dividende',
    description: 'Nu rata niciun dividend! Vezi când și cât plătesc companiile.',
    position: 'bottom',
    icon: Calendar,
  },
  {
    id: 'converter',
    type: 'spotlight',
    selector: 'a[href="/converter"]',
    title: '💱 Convertor Valutar',
    description: 'Curs BNR în timp real. Convertește rapid între valute!',
    position: 'bottom',
    icon: DollarSign,
  },
  {
    id: 'search',
    type: 'spotlight',
    selector: 'input[placeholder*="Caută"]',
    fallbackSelector: '.search-bar, [data-search]',
    title: '🔍 Caută Orice',
    description: 'Caută acțiuni, știri sau termeni din glosar. Găsești totul instant!',
    position: 'bottom',
    icon: Star,
  },
  {
    id: 'login',
    type: 'spotlight',
    selector: '[class*="UserMenu"] button, button[class*="default"]',
    title: '👤 Conectează-te',
    description: 'Creează-ți cont GRATUIT pentru Watchlist, Alerte și multe altele!',
    position: 'left',
    icon: Star,
    highlight: true,
  },
  {
    id: 'final',
    type: 'modal',
    title: 'Gata! Ești pregătit! 🚀',
    description: 'Acum cunoști platforma! Creează-ți un cont GRATUIT pentru experiența completă.',
    icon: Zap,
    gradient: 'from-green-600 via-emerald-600 to-teal-600',
    showCTA: true,
  },
];

// Animated Pointer/Finger Component
const AnimatedPointer = ({ x, y, direction = 'down' }) => {
  const rotation = {
    down: 0,
    up: 180,
    left: 90,
    right: -90,
  };

  return (
    <motion.div
      className="absolute z-[1002] pointer-events-none"
      style={{ left: x, top: y }}
      initial={{ opacity: 0, scale: 0 }}
      animate={{ 
        opacity: 1, 
        scale: 1,
        y: [0, 10, 0],
      }}
      transition={{ 
        y: { duration: 0.8, repeat: Infinity, ease: "easeInOut" }
      }}
    >
      <motion.div
        style={{ rotate: rotation[direction] }}
        className="relative"
      >
        {/* Glowing hand/pointer */}
        <div className="relative">
          <motion.div
            className="absolute inset-0 bg-yellow-400 rounded-full blur-xl opacity-60"
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
          <MousePointer2 className="w-10 h-10 text-yellow-400 drop-shadow-2xl relative z-10" />
        </div>
      </motion.div>
    </motion.div>
  );
};

// Spotlight Overlay with cutout
const SpotlightOverlay = ({ targetRect, onClick }) => {
  if (!targetRect) return null;

  const padding = 8;
  const borderRadius = 12;

  return (
    <motion.div
      className="fixed inset-0 z-[1000]"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClick}
    >
      {/* Dark overlay with spotlight hole */}
      <svg className="w-full h-full">
        <defs>
          <mask id="spotlight-mask">
            <rect width="100%" height="100%" fill="white" />
            <rect
              x={targetRect.left - padding}
              y={targetRect.top - padding}
              width={targetRect.width + padding * 2}
              height={targetRect.height + padding * 2}
              rx={borderRadius}
              fill="black"
            />
          </mask>
        </defs>
        <rect
          width="100%"
          height="100%"
          fill="rgba(0, 0, 0, 0.85)"
          mask="url(#spotlight-mask)"
        />
      </svg>

      {/* Glowing border around spotlight */}
      <motion.div
        className="absolute border-2 border-yellow-400 rounded-xl pointer-events-none"
        style={{
          left: targetRect.left - padding,
          top: targetRect.top - padding,
          width: targetRect.width + padding * 2,
          height: targetRect.height + padding * 2,
        }}
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ 
          opacity: 1, 
          scale: 1,
          boxShadow: [
            '0 0 20px rgba(250, 204, 21, 0.4)',
            '0 0 40px rgba(250, 204, 21, 0.6)',
            '0 0 20px rgba(250, 204, 21, 0.4)',
          ]
        }}
        transition={{ 
          boxShadow: { duration: 1.5, repeat: Infinity }
        }}
      />
    </motion.div>
  );
};

// Tooltip Card Component
const TooltipCard = ({ step, position, targetRect, onNext, onSkip, currentStep, totalSteps }) => {
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [pointerPos, setPointerPos] = useState({ x: 0, y: 0 });
  const cardRef = useRef(null);

  useEffect(() => {
    if (!targetRect) return;

    const cardWidth = 320;
    const cardHeight = 180;
    const offset = 20;

    let x, y, pointerX, pointerY;

    switch (position) {
      case 'bottom':
        x = targetRect.left + targetRect.width / 2 - cardWidth / 2;
        y = targetRect.bottom + offset + 30; // Extra space for pointer
        pointerX = targetRect.left + targetRect.width / 2 - 20;
        pointerY = targetRect.bottom + offset;
        break;
      case 'top':
        x = targetRect.left + targetRect.width / 2 - cardWidth / 2;
        y = targetRect.top - cardHeight - offset - 30;
        pointerX = targetRect.left + targetRect.width / 2 - 20;
        pointerY = targetRect.top - offset - 40;
        break;
      case 'left':
        x = targetRect.left - cardWidth - offset - 50;
        y = targetRect.top + targetRect.height / 2 - cardHeight / 2;
        pointerX = targetRect.left - offset - 40;
        pointerY = targetRect.top + targetRect.height / 2 - 20;
        break;
      case 'right':
        x = targetRect.right + offset + 50;
        y = targetRect.top + targetRect.height / 2 - cardHeight / 2;
        pointerX = targetRect.right + offset;
        pointerY = targetRect.top + targetRect.height / 2 - 20;
        break;
      default:
        x = targetRect.left + targetRect.width / 2 - cardWidth / 2;
        y = targetRect.bottom + offset + 30;
        pointerX = targetRect.left + targetRect.width / 2 - 20;
        pointerY = targetRect.bottom + offset;
    }

    // Keep card within viewport
    x = Math.max(20, Math.min(x, window.innerWidth - cardWidth - 20));
    y = Math.max(20, Math.min(y, window.innerHeight - cardHeight - 20));

    setTooltipPos({ x, y });
    setPointerPos({ x: pointerX, y: pointerY });
  }, [targetRect, position]);

  const Icon = step.icon;

  return (
    <>
      {/* Animated Pointer */}
      <AnimatedPointer x={pointerPos.x} y={pointerPos.y} direction="down" />

      {/* Tooltip Card */}
      <motion.div
        ref={cardRef}
        className="fixed z-[1001] w-80"
        style={{ left: tooltipPos.x, top: tooltipPos.y }}
        initial={{ opacity: 0, y: 20, scale: 0.9 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -20, scale: 0.9 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      >
        <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-5 shadow-2xl border border-white/20 backdrop-blur-xl">
          {/* Header with icon */}
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg">
              <Icon className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-lg font-bold text-white">{step.title}</h3>
          </div>

          {/* Description */}
          <p className="text-sm text-gray-300 mb-4 leading-relaxed">
            {step.description}
          </p>

          {/* Footer */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">
              {currentStep + 1} / {totalSteps}
            </span>
            <div className="flex gap-2">
              <Button
                onClick={onSkip}
                variant="ghost"
                size="sm"
                className="text-gray-400 hover:text-white text-xs"
              >
                Sari
              </Button>
              <Button
                onClick={onNext}
                size="sm"
                className="bg-gradient-to-r from-yellow-400 to-orange-500 text-black font-semibold hover:from-yellow-300 hover:to-orange-400"
              >
                Continuă
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </div>
        </div>

        {/* Arrow pointing to element */}
        <div 
          className="absolute w-4 h-4 bg-slate-900 rotate-45 border-l border-t border-white/20"
          style={{
            top: position === 'bottom' ? -8 : position === 'top' ? 'auto' : '50%',
            bottom: position === 'top' ? -8 : 'auto',
            left: position === 'left' ? 'auto' : position === 'right' ? -8 : '50%',
            right: position === 'right' ? 'auto' : position === 'left' ? -8 : 'auto',
            transform: position === 'bottom' || position === 'top' ? 'translateX(-50%)' : 'translateY(-50%)',
          }}
        />
      </motion.div>
    </>
  );
};

// Welcome/Final Modal
const FullScreenModal = ({ step, onNext, onSkip, onComplete, isLast }) => {
  const { login } = useAuth();
  const Icon = step.icon;

  const handleCTA = () => {
    onComplete();
    login();
  };

  return (
    <motion.div
      className="fixed inset-0 z-[1000] flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Background */}
      <motion.div 
        className={`absolute inset-0 bg-gradient-to-br ${step.gradient}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      />
      <div className="absolute inset-0 bg-black/30" />

      {/* Floating particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full bg-white/20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0.2, 0.8, 0.2],
            }}
            transition={{
              duration: Math.random() * 3 + 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Content */}
      <motion.div
        className="relative z-10 text-center max-w-lg mx-4"
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 200 }}
      >
        {/* Icon */}
        <motion.div
          className="w-24 h-24 mx-auto mb-6 rounded-3xl bg-white/20 backdrop-blur-sm flex items-center justify-center"
          initial={{ rotate: -10, scale: 0 }}
          animate={{ rotate: 0, scale: 1 }}
          transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
        >
          <Icon className="w-12 h-12 text-white" />
        </motion.div>

        {/* Title */}
        <motion.h1
          className="text-4xl md:text-5xl font-bold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          {step.title}
        </motion.h1>

        {/* Description */}
        <motion.p
          className="text-xl text-white/80 mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          {step.description}
        </motion.p>

        {/* Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {isLast && step.showCTA ? (
            <>
              <Button
                onClick={handleCTA}
                size="lg"
                className="bg-white text-gray-900 hover:bg-gray-100 font-bold text-lg px-8 shadow-xl"
              >
                <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                Creează Cont GRATUIT
              </Button>
              <Button
                onClick={onComplete}
                variant="outline"
                size="lg"
                className="border-white/30 text-white hover:bg-white/10"
              >
                Explorează mai întâi
              </Button>
            </>
          ) : (
            <>
              <Button
                onClick={onNext}
                size="lg"
                className="bg-white text-gray-900 hover:bg-gray-100 font-bold text-lg px-8"
              >
                Hai să începem!
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
              <Button
                onClick={onSkip}
                variant="ghost"
                size="lg"
                className="text-white/60 hover:text-white hover:bg-white/10"
              >
                <X className="w-4 h-4 mr-2" />
                Sari peste tur
              </Button>
            </>
          )}
        </motion.div>
      </motion.div>
    </motion.div>
  );
};

// Main Interactive Tour Component
export default function InteractiveTour() {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [targetRect, setTargetRect] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Find DOM element for current step
  const findElement = useCallback((step) => {
    if (step.type !== 'spotlight') return null;

    let element = null;

    // Try main selector
    try {
      element = document.querySelector(step.selector);
    } catch (e) {
      console.log('Invalid selector:', step.selector);
    }
    
    // Try fallback
    if (!element && step.fallbackSelector) {
      try {
        element = document.querySelector(step.fallbackSelector);
      } catch (e) {
        console.log('Invalid fallback selector:', step.fallbackSelector);
      }
    }

    // Try finding navigation links by href
    if (!element) {
      const hrefMatch = step.selector.match(/href="([^"]+)"/);
      if (hrefMatch) {
        element = document.querySelector(`nav a[href="${hrefMatch[1]}"]`);
        if (!element) {
          element = document.querySelector(`a[href="${hrefMatch[1]}"]`);
        }
      }
    }

    // Special handling for login button - find by text content
    if (!element && step.id === 'login') {
      const buttons = document.querySelectorAll('button');
      for (const btn of buttons) {
        if (btn.textContent.includes('Conectare') || btn.querySelector('.lucide-user')) {
          element = btn;
          break;
        }
      }
    }

    // Special handling for search input
    if (!element && step.id === 'search') {
      element = document.querySelector('input[type="text"]') || 
                document.querySelector('input[placeholder]');
    }

    return element;
  }, []);

  // Update target rect when step changes
  useEffect(() => {
    if (!isVisible) return;

    const step = tourSteps[currentStep];
    if (step.type === 'spotlight') {
      const element = findElement(step);
      if (element) {
        const rect = element.getBoundingClientRect();
        setTargetRect(rect);

        // Scroll element into view if needed
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        // Element not found, skip to next
        console.log(`Element not found for step: ${step.id}, skipping...`);
        handleNext();
      }
    } else {
      setTargetRect(null);
    }
  }, [currentStep, isVisible, findElement]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      const step = tourSteps[currentStep];
      if (step.type === 'spotlight') {
        const element = findElement(step);
        if (element) {
          setTargetRect(element.getBoundingClientRect());
        }
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [currentStep, findElement]);

  // Check if tour should show
  useEffect(() => {
    if (user) {
      setIsVisible(false);
      return;
    }

    const tourCompleted = localStorage.getItem(TOUR_STORAGE_KEY);
    if (!tourCompleted && location.pathname === '/') {
      const timer = setTimeout(() => setIsVisible(true), 1500);
      return () => clearTimeout(timer);
    }
  }, [user, location]);

  const handleNext = useCallback(() => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep]);

  const handleSkip = useCallback(() => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setIsVisible(false);
    setCurrentStep(0);
  }, []);

  const handleComplete = useCallback(() => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setIsVisible(false);
    setCurrentStep(0);
  }, []);

  if (!isVisible) return null;

  const step = tourSteps[currentStep];
  const isLast = currentStep === tourSteps.length - 1;

  return (
    <AnimatePresence mode="wait">
      {step.type === 'modal' ? (
        <FullScreenModal
          key={step.id}
          step={step}
          onNext={handleNext}
          onSkip={handleSkip}
          onComplete={handleComplete}
          isLast={isLast}
        />
      ) : (
        <React.Fragment key={step.id}>
          <SpotlightOverlay
            targetRect={targetRect}
            onClick={handleNext}
          />
          {targetRect && (
            <TooltipCard
              step={step}
              position={step.position || 'bottom'}
              targetRect={targetRect}
              onNext={handleNext}
              onSkip={handleSkip}
              currentStep={currentStep}
              totalSteps={tourSteps.length}
            />
          )}
        </React.Fragment>
      )}
    </AnimatePresence>
  );
}
