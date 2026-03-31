import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { 
  BarChart3, TrendingUp, GraduationCap, Bot, Globe, Star, 
  ChevronRight, ChevronLeft, X, Sparkles, ArrowRight,
  BookOpen, PieChart, Zap, Shield, Users, Trophy,
  Newspaper, Calendar, DollarSign
} from 'lucide-react';
import { Button } from './ui/button';

const TOUR_STORAGE_KEY = 'finromania_tour_completed';

// Tour Steps Configuration
const tourSteps = [
  {
    id: 'welcome',
    titleKey: 'onboarding.welcome.title',
    subtitleKey: 'onboarding.welcome.subtitle',
    descriptionKey: 'onboarding.welcome.description',
    icon: Sparkles,
    gradient: 'from-blue-600 via-blue-500 to-cyan-500',
    path: null,
    features: [
      { icon: GraduationCap, textKey: 'onboarding.welcome.feature1' },
      { icon: TrendingUp, textKey: 'onboarding.welcome.feature2' },
      { icon: Bot, textKey: 'onboarding.welcome.feature3' },
    ]
  },
  {
    id: 'bvb',
    titleKey: 'onboarding.bvb.title',
    subtitleKey: 'onboarding.bvb.subtitle',
    descriptionKey: 'onboarding.bvb.description',
    icon: BarChart3,
    gradient: 'from-emerald-600 via-teal-600 to-cyan-600',
    path: '/stocks',
    highlightKeys: ['onboarding.bvb.highlight1', 'onboarding.bvb.highlight2', 'onboarding.bvb.highlight3'],
    ctaKey: 'onboarding.bvb.cta'
  },
  {
    id: 'global',
    titleKey: 'onboarding.global.title',
    subtitleKey: 'onboarding.global.subtitle',
    descriptionKey: 'onboarding.global.description',
    icon: Globe,
    gradient: 'from-orange-600 via-red-600 to-pink-600',
    path: '/global',
    highlightKeys: ['onboarding.global.highlight1', 'onboarding.global.highlight2', 'onboarding.global.highlight3'],
    ctaKey: 'onboarding.global.cta'
  },
  {
    id: 'news',
    titleKey: 'onboarding.news.title',
    subtitleKey: 'onboarding.news.subtitle',
    descriptionKey: 'onboarding.news.description',
    icon: Newspaper,
    gradient: 'from-rose-600 via-pink-600 to-rose-700',
    path: '/news',
    highlightKeys: ['onboarding.news.highlight1', 'onboarding.news.highlight2', 'onboarding.news.highlight3'],
    ctaKey: 'onboarding.news.cta'
  },
  {
    id: 'dividends',
    titleKey: 'onboarding.dividends.title',
    subtitleKey: 'onboarding.dividends.subtitle',
    descriptionKey: 'onboarding.dividends.description',
    icon: Calendar,
    gradient: 'from-green-600 via-emerald-600 to-teal-600',
    path: '/calendar',
    highlightKeys: ['onboarding.dividends.highlight1', 'onboarding.dividends.highlight2', 'onboarding.dividends.highlight3'],
    ctaKey: 'onboarding.dividends.cta'
  },
  {
    id: 'converter',
    titleKey: 'onboarding.converter.title',
    subtitleKey: 'onboarding.converter.subtitle',
    descriptionKey: 'onboarding.converter.description',
    icon: DollarSign,
    gradient: 'from-sky-600 via-blue-600 to-blue-700',
    path: '/converter',
    highlightKeys: ['onboarding.converter.highlight1', 'onboarding.converter.highlight2', 'onboarding.converter.highlight3'],
    ctaKey: 'onboarding.converter.cta'
  },
  {
    id: 'education',
    titleKey: 'onboarding.education.title',
    subtitleKey: 'onboarding.education.subtitle',
    descriptionKey: 'onboarding.education.description',
    icon: GraduationCap,
    gradient: 'from-blue-600 via-blue-500 to-cyan-500',
    path: '/trading-school',
    highlightKeys: ['onboarding.education.highlight1', 'onboarding.education.highlight2', 'onboarding.education.highlight3'],
    ctaKey: 'onboarding.education.cta'
  },
  {
    id: 'ai',
    titleKey: 'onboarding.ai.title',
    subtitleKey: 'onboarding.ai.subtitle',
    descriptionKey: 'onboarding.ai.description',
    icon: Bot,
    gradient: 'from-cyan-600 via-blue-600 to-blue-700',
    path: '/advisor',
    highlightKeys: ['onboarding.ai.highlight1', 'onboarding.ai.highlight2', 'onboarding.ai.highlight3'],
    ctaKey: 'onboarding.ai.cta'
  },
  {
    id: 'watchlist',
    titleKey: 'onboarding.watchlist.title',
    subtitleKey: 'onboarding.watchlist.subtitle',
    descriptionKey: 'onboarding.watchlist.description',
    icon: Star,
    gradient: 'from-amber-600 via-yellow-600 to-orange-600',
    path: '/watchlist',
    highlightKeys: ['onboarding.watchlist.highlight1', 'onboarding.watchlist.highlight2', 'onboarding.watchlist.highlight3'],
    ctaKey: 'onboarding.watchlist.cta',
    requiresAuth: true
  },
  {
    id: 'faq',
    titleKey: 'onboarding.faq.title',
    subtitleKey: 'onboarding.faq.subtitle',
    descriptionKey: 'onboarding.faq.description',
    icon: BookOpen,
    gradient: 'from-slate-600 via-gray-700 to-zinc-800',
    path: '/faq',
    highlightKeys: ['onboarding.faq.highlight1', 'onboarding.faq.highlight2', 'onboarding.faq.highlight3'],
    ctaKey: 'onboarding.faq.cta'
  },
  {
    id: 'final',
    titleKey: 'onboarding.final.title',
    subtitleKey: 'onboarding.final.subtitle',
    descriptionKey: 'onboarding.final.description',
    icon: Trophy,
    gradient: 'from-green-600 via-emerald-600 to-teal-600',
    path: null,
    benefits: [
      { icon: Star, textKey: 'onboarding.final.benefit1' },
      { icon: PieChart, textKey: 'onboarding.final.benefit2' },
      { icon: BookOpen, textKey: 'onboarding.final.benefit3' },
      { icon: Shield, textKey: 'onboarding.final.benefit4' },
    ]
  }
];

// Floating Particles Component
const FloatingParticles = () => (
  <div className="absolute inset-0 overflow-hidden pointer-events-none">
    {[...Array(20)].map((_, i) => (
      <motion.div
        key={i}
        className="absolute w-2 h-2 rounded-full bg-white/20"
        initial={{ 
          x: Math.random() * window.innerWidth, 
          y: Math.random() * window.innerHeight,
          scale: Math.random() * 0.5 + 0.5
        }}
        animate={{ 
          y: [null, Math.random() * -200 - 100],
          opacity: [0.2, 0.8, 0.2]
        }}
        transition={{ 
          duration: Math.random() * 3 + 2,
          repeat: Infinity,
          repeatType: 'reverse'
        }}
      />
    ))}
  </div>
);

// Progress Bar Component
const ProgressBar = ({ current, total }) => (
  <div className="flex items-center gap-2">
    {[...Array(total)].map((_, i) => (
      <motion.div
        key={i}
        className={`h-1.5 rounded-full transition-all duration-300 ${
          i <= current ? 'bg-white' : 'bg-white/30'
        }`}
        initial={{ width: 20 }}
        animate={{ width: i === current ? 40 : 20 }}
      />
    ))}
  </div>
);

// Step Content Component
const StepContent = ({ step, onNavigate }) => {
  const { t } = useTranslation();
  const Icon = step.icon;

  return (
    <motion.div
      key={step.id}
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -30, scale: 0.95 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="text-center"
    >
      {/* Icon */}
      <motion.div
        className={`w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br ${step.gradient} flex items-center justify-center shadow-2xl`}
        initial={{ rotate: -10, scale: 0 }}
        animate={{ rotate: 0, scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
      >
        <Icon className="w-10 h-10 text-white" />
      </motion.div>

      {/* Title */}
      <motion.h2
        className="text-3xl md:text-4xl font-bold text-white mb-2"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        {t(step.titleKey)}
      </motion.h2>

      {/* Subtitle */}
      <motion.p
        className="text-lg md:text-xl text-blue-200 mb-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        {t(step.subtitleKey)}
      </motion.p>

      {/* Description */}
      <motion.p
        className="text-base text-white/80 max-w-md mx-auto mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        {t(step.descriptionKey)}
      </motion.p>

      {/* Features/Highlights */}
      {step.features && (
        <motion.div
          className="flex flex-wrap justify-center gap-4 mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          {step.features.map((feature, i) => (
            <motion.div
              key={i}
              className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-4 py-2"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <feature.icon className="w-4 h-4 text-blue-300" />
              <span className="text-sm text-white">{t(feature.textKey)}</span>
            </motion.div>
          ))}
        </motion.div>
      )}

      {step.highlightKeys && (
        <motion.div
          className="flex flex-wrap justify-center gap-3 mb-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {step.highlightKeys.map((key, i) => (
            <motion.span
              key={i}
              className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-1.5 text-sm text-white"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              {t(key)}
            </motion.span>
          ))}
        </motion.div>
      )}

      {step.benefits && (
        <motion.div
          className="grid grid-cols-2 gap-2 max-w-sm mx-auto mb-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          {step.benefits.map((benefit, i) => (
            <motion.div
              key={i}
              className="flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-lg px-2 py-1.5"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + i * 0.1 }}
            >
              <benefit.icon className="w-3 h-3 text-green-400 flex-shrink-0" />
              <span className="text-xs text-white leading-tight">{t(benefit.textKey)}</span>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* CTA Button for pages */}
      {step.ctaKey && step.path && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Button
            onClick={() => onNavigate(step.path)}
            variant="outline"
            className="bg-white/10 border-white/30 text-white hover:bg-white/20 backdrop-blur-sm"
          >
            {t(step.ctaKey)}
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
};

// Main Onboarding Tour Component
export default function OnboardingTour() {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  // Check if tour should be shown
  useEffect(() => {
    // Don't show if user is logged in
    if (user) {
      setIsVisible(false);
      return;
    }

    // Check if tour was completed
    const tourCompleted = localStorage.getItem(TOUR_STORAGE_KEY);
    if (!tourCompleted) {
      // Small delay for better UX
      const timer = setTimeout(() => setIsVisible(true), 1000);
      return () => clearTimeout(timer);
    }
  }, [user]);

  const handleNext = useCallback(() => {
    if (currentStep < tourSteps.length - 1) {
      setCurrentStep(prev => prev + 1);
    }
  }, [currentStep]);

  const handlePrev = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1);
    }
  }, [currentStep]);

  const handleSkip = useCallback(() => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setIsVisible(false);
  }, []);

  const handleComplete = useCallback(() => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setIsVisible(false);
    // Trigger login
    login();
  }, [login]);

  const handleNavigate = useCallback((path) => {
    localStorage.setItem(TOUR_STORAGE_KEY, 'true');
    setIsVisible(false);
    navigate(path);
  }, [navigate]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isVisible) return;
      if (e.key === 'ArrowRight' || e.key === 'Enter') handleNext();
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'Escape') handleSkip();
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isVisible, handleNext, handlePrev, handleSkip]);

  if (!isVisible) return null;

  const step = tourSteps[currentStep];
  const isLastStep = currentStep === tourSteps.length - 1;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center"
      >
        {/* Animated Background */}
        <motion.div 
          className={`absolute inset-0 bg-gradient-to-br ${step.gradient} transition-all duration-700`}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        />
        
        {/* Overlay Pattern */}
        <div className="absolute inset-0 bg-black/30" />
        
        {/* Floating Particles */}
        <FloatingParticles />

        {/* Content Container */}
        <div className="relative z-10 w-full max-w-2xl mx-4">
          {/* Skip Button */}
          <motion.button
            onClick={handleSkip}
            className="absolute -top-12 right-0 text-white/60 hover:text-white transition-colors flex items-center gap-1 text-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            {t('onboarding.skipTour')}
            <X className="w-4 h-4" />
          </motion.button>

          {/* Main Card */}
          <motion.div
            className="bg-white/10 backdrop-blur-xl rounded-3xl p-6 md:p-10 shadow-2xl border border-white/20 max-h-[85vh] overflow-y-auto"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 200 }}
          >
            {/* Progress */}
            <div className="flex justify-center mb-8">
              <ProgressBar current={currentStep} total={tourSteps.length} />
            </div>

            {/* Step Content */}
            <AnimatePresence mode="wait">
              <StepContent 
                step={step} 
                onNavigate={handleNavigate} 
              />
            </AnimatePresence>

            {/* Navigation Buttons */}
            <motion.div 
              className="flex items-center justify-between mt-8 pt-6 border-t border-white/20"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              {/* Back Button */}
              <Button
                onClick={handlePrev}
                variant="ghost"
                disabled={currentStep === 0}
                className={`text-white hover:bg-white/10 ${currentStep === 0 ? 'invisible' : ''}`}
              >
                <ChevronLeft className="w-4 h-4 mr-1" />
                {t('common.back')}
              </Button>

              {/* Step Counter */}
              <span className="text-white/60 text-sm">
                {currentStep + 1} / {tourSteps.length}
              </span>

              {/* Next/Complete Button */}
              {isLastStep ? (
                <motion.div
                  className="relative"
                  initial={{ scale: 0.9 }}
                  animate={{ scale: [0.9, 1.05, 1] }}
                  transition={{ delay: 0.5, duration: 0.5 }}
                >
                  {/* Glow effect */}
                  <motion.div
                    className="absolute inset-0 bg-white rounded-lg blur-lg"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  />
                  <Button
                    onClick={handleComplete}
                    className="relative bg-white text-gray-900 hover:bg-gray-100 font-bold px-6 shadow-xl text-base"
                  >
                    <Zap className="w-5 h-5 mr-2 text-yellow-500" />
                    {t('onboarding.createFreeAccount')}
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </motion.div>
              ) : (
                <Button
                  onClick={handleNext}
                  className="bg-white/20 text-white hover:bg-white/30 backdrop-blur-sm"
                >
                  {t('common.continue')}
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              )}
            </motion.div>
          </motion.div>

          {/* Keyboard Hint */}
          <motion.p
            className="text-center text-white/40 text-xs mt-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            {t('onboarding.keyboardHint')}
          </motion.p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
