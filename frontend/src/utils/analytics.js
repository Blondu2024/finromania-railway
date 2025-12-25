// Google Analytics 4 Setup
import ReactGA from 'react-ga4';

const MEASUREMENT_ID = process.env.REACT_APP_GA_MEASUREMENT_ID || 'G-XXXXXXXXXX'; // Replace with real ID when available

export const initGA = () => {
  // Only initialize if we have a real measurement ID
  if (MEASUREMENT_ID && MEASUREMENT_ID !== 'G-XXXXXXXXXX') {
    ReactGA.initialize(MEASUREMENT_ID, {
      gaOptions: {
        siteSpeedSampleRate: 100,
      },
    });
    console.log('✅ Google Analytics initialized');
  } else {
    console.log('ℹ️ Google Analytics not configured (no measurement ID)');
  }
};

// Track page view
export const trackPageView = (path, title) => {
  if (MEASUREMENT_ID && MEASUREMENT_ID !== 'G-XXXXXXXXXX') {
    ReactGA.send({ hitType: 'pageview', page: path, title });
  }
};

// Track custom events
export const trackEvent = (category, action, label = '', value = 0) => {
  if (MEASUREMENT_ID && MEASUREMENT_ID !== 'G-XXXXXXXXXX') {
    ReactGA.event({
      category,
      action,
      label,
      value,
    });
  }
};

// Predefined events for common actions
export const Analytics = {
  // Trading School events
  lessonStarted: (lessonId) => trackEvent('TradingSchool', 'lesson_started', lessonId),
  lessonCompleted: (lessonId) => trackEvent('TradingSchool', 'lesson_completed', lessonId),
  quizPassed: (lessonId, score) => trackEvent('TradingSchool', 'quiz_passed', lessonId, score),
  quizFailed: (lessonId, score) => trackEvent('TradingSchool', 'quiz_failed', lessonId, score),
  
  // User engagement
  aiQuestionAsked: (question) => trackEvent('AIAdvisor', 'question_asked', question.substring(0, 50)),
  stockViewed: (symbol) => trackEvent('Stocks', 'stock_viewed', symbol),
  newsArticleRead: (articleId) => trackEvent('News', 'article_read', articleId),
  
  // Conversions (if we add premium later)
  signupStarted: () => trackEvent('User', 'signup_started'),
  signupCompleted: () => trackEvent('User', 'signup_completed'),
  
  // Tools usage
  currencyConverted: (from, to) => trackEvent('Tools', 'currency_converted', `${from}_${to}`),
  watchlistAdded: (symbol) => trackEvent('Tools', 'watchlist_added', symbol),
  riskAssessmentCompleted: (profile) => trackEvent('Tools', 'risk_assessment', profile),
};

export default Analytics;
