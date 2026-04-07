import React, { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  BarChart3, Menu, Moon, Sun, User, LogOut, Star, Briefcase, Shield,
  TrendingUp, Globe, Calendar, Crown, Calculator, Building2, RefreshCw,
  GraduationCap, BookOpen, AlertTriangle, Bell, Settings, Search,
  ChevronRight, Activity, FileText, Newspaper, Coins, BookMarked, MessageSquare
} from 'lucide-react';
import { Button } from './components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from './components/ui/sheet';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from './components/ui/dropdown-menu';
import { Badge } from './components/ui/badge';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Skeleton } from './components/ui/skeleton';
import { initializePushNotifications } from './utils/pushNotifications';
import NotificationBell, { CriticalNotificationBanner } from './components/NotificationBell';
import FeedbackButton, { BetaDisclaimer, BetaBadge } from './components/BetaFeedback';
import FinAssistant from './components/FinAssistant';
import LanguageSwitcher from './components/LanguageSwitcher';
import './App.css';

initializePushNotifications();

// ============================================
// LAZY LOADED PAGES
// ============================================
const HomePage = lazy(() => import('./pages/HomePage'));
const StocksPage = lazy(() => import('./pages/StocksPage'));
const NewsPage = lazy(() => import('./pages/NewsPage'));
const GlobalMarketsPage = lazy(() => import('./pages/GlobalMarketsPage'));
const TradingSchoolPage = lazy(() => import('./pages/TradingSchoolPage'));
const FinancialEducationPage = lazy(() => import('./pages/FinancialEducationPage'));
const LessonPage = lazy(() => import('./pages/LessonPage'));
const FinLessonPage = lazy(() => import('./pages/FinLessonPage'));
const EducationPage = lazy(() => import('./pages/EducationPage'));
const CurrencyConverterPage = lazy(() => import('./pages/CurrencyConverterPage'));
const DividendCalendarPage = lazy(() => import('./pages/DividendCalendarPage'));
const DividendCalculatorPage = lazy(() => import('./pages/DividendCalculatorPage'));
const StockScreenerPage = lazy(() => import('./pages/StockScreenerPage'));
const ScreenerProPage = lazy(() => import('./pages/ScreenerProPage'));
const GlossaryPage = lazy(() => import('./pages/GlossaryPage'));
const StockDetailPage = lazy(() => import('./pages/StockDetailPage'));
const ArticleDetailPage = lazy(() => import('./pages/ArticleDetailPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const AuthCallback = lazy(() => import('./pages/AuthCallback'));
const WatchlistPage = lazy(() => import('./pages/WatchlistPage'));
const PortfolioPage = lazy(() => import('./pages/PortfolioPage'));
const NotificationSettingsPage = lazy(() => import('./pages/NotificationSettingsPage'));
const CurrenciesPage = lazy(() => import('./pages/CurrenciesPage'));
const AIAdvisorPage = lazy(() => import('./pages/AIAdvisorPage'));
const RiskAssessmentPage = lazy(() => import('./pages/RiskAssessmentPage'));
const LearnTradingPage = lazy(() => import('./pages/LearnTradingPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboardPro'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const CookiePolicyPage = lazy(() => import('./pages/CookiePolicyPage'));
const DisclaimerPage = lazy(() => import('./pages/DisclaimerPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const FAQPage = lazy(() => import('./pages/FAQPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));
const QuizPage = lazy(() => import('./pages/QuizPage'));
const CommunityPage = lazy(() => import('./pages/CommunityPage'));
const FiscalCalculatorPage = lazy(() => import('./pages/FiscalCalculatorPage'));
const FiscalSimulatorPage = lazy(() => import('./pages/FiscalSimulatorPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const PortfolioBVBPage = lazy(() => import('./pages/PortfolioBVBPage'));
const TryProPage = lazy(() => import('./pages/TryProPage'));
const DailySummaryPage = lazy(() => import('./pages/DailySummaryPage'));
const PaymentSuccessPage = lazy(() => import('./pages/PaymentSuccessPage'));
const CFDvsActiuniPage = lazy(() => import('./pages/CFDvsActiuniPage'));

const TickerBar = lazy(() => import('./components/TickerBar'));
const SearchBar = lazy(() => import('./components/SearchBar'));
const NewsletterSignup = lazy(() => import('./components/NewsletterSignup'));
const InstallPWA = lazy(() => import('./components/InstallPWA'));
const InteractiveTour = lazy(() => import('./components/InteractiveTour'));

// ============================================
// LOADERS
// ============================================
const PageLoader = () => {
  const { t } = useTranslation();
  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center space-y-4">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-muted-foreground text-sm">{t('nav.loading')}</p>
      </div>
    </div>
  );
};
const TickerLoader = () => <div className="h-10 bg-gray-100 dark:bg-zinc-800 animate-pulse" />;
const SearchLoader = () => <Skeleton className="h-9 w-36" />;


// ============================================
// USER MENU
// ============================================
function UserMenu() {
  const { user, logout, login } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  if (!user) {
    return (
      <Button onClick={login} variant="default" size="sm" className="h-8 text-sm">
        <User className="w-4 h-4 mr-1.5" />
        {t('nav.login')}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="flex items-center gap-2 h-8">
          {user.picture ? (
            <img src={user.picture} alt="" className="w-6 h-6 rounded-full" loading="lazy" />
          ) : (
            <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-blue-600 font-bold text-xs">{user.name?.[0]}</span>
            </div>
          )}
          <span className="hidden md:inline text-sm">{user.name?.split(' ')[0]}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <div className="px-2 py-1.5">
          <p className="text-sm font-medium">{user.name}</p>
          <p className="text-xs text-muted-foreground">{user.email}</p>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => navigate('/watchlist')}>
          <Star className="w-4 h-4 mr-2" /> {t('nav.watchlist')}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate('/portfolio-bvb')}>
          <Briefcase className="w-4 h-4 mr-2" /> {t('nav.portfolio')}
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate('/notifications')}>
          <Bell className="w-4 h-4 mr-2" /> {t('nav.notifications')}
        </DropdownMenuItem>
        {user.is_admin && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate('/admin')}>
              <Shield className="w-4 h-4 mr-2" /> Admin Dashboard
            </DropdownMenuItem>
          </>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout} className="text-red-600">
          <LogOut className="w-4 h-4 mr-2" /> {t('nav.logout')}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}


// ============================================
// TOP NAVBAR — Simple, main items only
// ============================================
function TopNavbar({ darkMode, toggleDarkMode, onMobileSidebarOpen }) {
  const location = useLocation();
  const { t } = useTranslation();

  const mainItems = [
    { path: '/', label: t('nav.home') },
    { path: '/stocks', label: t('nav.stocks') },
    { path: '/global', label: t('nav.globalMarkets') },
    { path: '/news', label: t('nav.news') },
    { path: '/rezumat-zilnic', label: t('nav.summary') },
    { path: '/community', label: t('nav.community', 'Comunitate') },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-13 items-center px-4 gap-2">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 mr-4 flex-shrink-0">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          <span className="font-bold text-base hidden sm:inline">FinRomania</span>
          <BetaBadge />
        </Link>

        {/* Main nav items — desktop only */}
        <nav className="hidden lg:flex items-center gap-0.5 flex-1">
          {mainItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors whitespace-nowrap ${
                location.pathname === item.path
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Right side actions */}
        <div className="flex items-center gap-1.5 ml-auto">
          <div className="hidden md:block">
            <Suspense fallback={<SearchLoader />}>
              <SearchBar />
            </Suspense>
          </div>
          <NotificationBell />
          <LanguageSwitcher />
          <Button variant="ghost" size="icon" className="h-8 w-8" onClick={toggleDarkMode}>
            {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <UserMenu />

          {/* Mobile hamburger */}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 lg:hidden"
            onClick={onMobileSidebarOpen}
            data-testid="mobile-menu-btn"
          >
            <Menu className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}


// ============================================
// SIDEBAR — stil profesional, mereu vizibil pe desktop
// ============================================
function Sidebar({ mobileOpen, onMobileClose }) {
  const location = useLocation();
  const { user } = useAuth();
  const { t } = useTranslation();

  const sections = [
    {
      label: t('nav.markets'),
      items: [
        { path: '/stocks', label: t('nav.stocks'), icon: TrendingUp },
        { path: '/global', label: t('nav.globalMarkets'), icon: Globe },
        { path: '/calendar', label: t('nav.dividendCalc'), icon: Calendar },
        { path: '/news', label: t('nav.news'), icon: Newspaper },
        { path: '/community', label: t('nav.community', 'Comunitate'), icon: MessageSquare },
      ],
    },
    {
      label: t('nav.proTools'),
      items: [
        { path: '/screener-pro', label: t('nav.screenerPro'), icon: Crown, badge: t('nav.pro'), badgeColor: 'bg-amber-500' },
        { path: '/calculator-dividende', label: t('nav.dividendCalc'), icon: Coins, badge: t('nav.new'), badgeColor: 'bg-blue-500' },
        { path: '/screener', label: t('nav.screenerBasic'), icon: Search },
      ],
    },
    {
      label: t('nav.tools'),
      items: [
        { path: '/calculator-fiscal', label: t('nav.fiscalCalc'), icon: Calculator },
        { path: '/simulator-fiscal', label: t('nav.simulator'), icon: Building2 },
        { path: '/converter', label: t('nav.converter'), icon: RefreshCw },
        { path: '/rezumat-zilnic', label: t('nav.dailySummary'), icon: FileText },
      ],
    },
    {
      label: t('nav.academy'),
      items: [
        { path: '/trading-school', label: t('nav.tradingSchool'), icon: GraduationCap },
        { path: '/financial-education', label: t('nav.financialEducation'), icon: BookOpen },
        { path: '/educatie-cfd-vs-actiuni', label: t('nav.cfdVsStocks'), icon: AlertTriangle, badge: t('nav.new'), badgeColor: 'bg-orange-500' },
        { path: '/glossary', label: t('nav.glossary'), icon: BookMarked },
      ],
    },
    ...(user ? [{
      label: t('nav.myAccount'),
      items: [
        { path: '/watchlist', label: t('nav.watchlist'), icon: Star },
        { path: '/portfolio-bvb', label: t('nav.portfolio'), icon: Briefcase },
        { path: '/notifications', label: t('nav.notifications'), icon: Bell },
      ],
    }] : []),
  ];

  const NavLink = ({ item, onClick }) => {
    const Icon = item.icon;
    const isActive = location.pathname === item.path;
    return (
      <Link
        to={item.path}
        onClick={onClick}
        className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors group ${
          isActive
            ? 'bg-primary text-primary-foreground'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent'
        }`}
      >
        <Icon className="w-4 h-4 flex-shrink-0" />
        <span className="flex-1 truncate">{item.label}</span>
        {item.badge && (
          <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold text-white ${item.badgeColor || 'bg-gray-500'}`}>
            {item.badge}
          </span>
        )}
      </Link>
    );
  };

  const SidebarContent = ({ onLinkClick }) => (
    <div className="flex flex-col gap-4 py-2">
      {sections.map((section) => (
        <div key={section.label}>
          <p className="px-3 mb-1 text-[10px] font-bold tracking-wider text-muted-foreground/60 uppercase">
            {section.label}
          </p>
          <div className="space-y-0.5">
            {section.items.map((item) => (
              <NavLink key={item.path} item={item} onClick={onLinkClick} />
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <>
      {/* Desktop sidebar — always visible on lg+ */}
      <aside className="hidden lg:flex flex-col w-52 xl:w-56 border-r bg-background sticky top-[57px] h-[calc(100vh-57px)] overflow-y-auto flex-shrink-0">
        <div className="px-2 py-3">
          <SidebarContent onLinkClick={undefined} />
        </div>
      </aside>

      {/* Mobile sidebar — Sheet from left */}
      <Sheet open={mobileOpen} onOpenChange={onMobileClose}>
        <SheetContent side="left" className="w-64 overflow-y-auto pt-0 pb-8">
          <div className="flex items-center gap-2 h-14 border-b mb-3">
            <BarChart3 className="h-5 w-5 text-blue-600" />
            <span className="font-bold text-base">FinRomania</span>
            <BetaBadge />
          </div>
          {/* Search on mobile */}
          <div className="px-1 mb-3">
            <Suspense fallback={<SearchLoader />}>
              <SearchBar />
            </Suspense>
          </div>
          <div className="px-1">
            <SidebarContent onLinkClick={onMobileClose} />
          </div>
        </SheetContent>
      </Sheet>
    </>
  );
}


// ============================================
// APP ROUTER
// ============================================
function AppRouter() {
  const location = useLocation();

  if (location.hash?.includes('session_id=')) {
    return (
      <Suspense fallback={<PageLoader />}>
        <AuthCallback />
      </Suspense>
    );
  }

  return (
    <ErrorBoundary>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/stocks" element={<StocksPage />} />
          <Route path="/stocks/:type/:symbol" element={<StockDetailPage />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/news/:articleId" element={<ArticleDetailPage />} />
          <Route path="/currencies" element={<CurrenciesPage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/terms" element={<TermsOfServicePage />} />
          <Route path="/cookies" element={<CookiePolicyPage />} />
          <Route path="/disclaimer" element={<DisclaimerPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="/watchlist" element={<WatchlistPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/manage" element={<AdminPage />} />
          <Route path="/education" element={<EducationPage />} />
          <Route path="/education/success" element={<EducationPage />} />
          <Route path="/education/lesson/:lessonId" element={<LessonPage />} />
          <Route path="/community" element={<CommunityPage />} />
          <Route path="/risk-assessment" element={<RiskAssessmentPage />} />
          <Route path="/advisor" element={<AIAdvisorPage />} />
          <Route path="/converter" element={<CurrencyConverterPage />} />
          <Route path="/glossary" element={<GlossaryPage />} />
          <Route path="/learn" element={<LearnTradingPage />} />
          <Route path="/trading-school" element={<TradingSchoolPage />} />
          <Route path="/trading-school/:lessonId" element={<LessonPage />} />
          <Route path="/financial-education" element={<FinancialEducationPage />} />
          <Route path="/financial-education/:lessonId" element={<FinLessonPage />} />
          <Route path="/faq" element={<FAQPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/calendar" element={<DividendCalendarPage />} />
          <Route path="/calculator-dividende" element={<DividendCalculatorPage />} />
          <Route path="/screener" element={<StockScreenerPage />} />
          <Route path="/screener-pro" element={<ScreenerProPage />} />
          <Route path="/notifications" element={<NotificationSettingsPage />} />
          <Route path="/global" element={<GlobalMarketsPage />} />
          <Route path="/quiz/:level" element={<QuizPage />} />
          <Route path="/calculator-fiscal" element={<FiscalCalculatorPage />} />
          <Route path="/simulator-fiscal" element={<FiscalSimulatorPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/portfolio-bvb" element={<PortfolioBVBPage />} />
          <Route path="/incearca-pro" element={<TryProPage />} />
          <Route path="/rezumat-zilnic" element={<DailySummaryPage />} />
          <Route path="/payment/success" element={<PaymentSuccessPage />} />
          <Route path="/educatie-cfd-vs-actiuni" element={<CFDvsActiuniPage />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}


// ============================================
// FOOTER — Compact
// ============================================
function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="border-t py-6 mt-8 bg-muted/30">
      <div className="px-4 lg:px-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
          <div>
            <h4 className="font-semibold mb-2 text-sm">FinRomania</h4>
            <p className="text-xs text-muted-foreground">
              {t('footer.description')}
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-sm">{t('footer.navigation')}</h4>
            <ul className="space-y-1 text-xs">
              <li><Link to="/" className="text-muted-foreground hover:text-foreground">{t('nav.home')}</Link></li>
              <li><Link to="/stocks" className="text-muted-foreground hover:text-foreground">{t('nav.stocks')}</Link></li>
              <li><Link to="/trading-school" className="text-muted-foreground hover:text-foreground">{t('nav.tradingSchool')}</Link></li>
              <li><Link to="/financial-education" className="text-muted-foreground hover:text-foreground">{t('nav.financialEducation')}</Link></li>
              <li><Link to="/educatie-cfd-vs-actiuni" className="text-muted-foreground hover:text-foreground">{t('nav.cfdVsStocks')}</Link></li>
              <li><Link to="/glossary" className="text-muted-foreground hover:text-foreground">{t('nav.glossary')}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-sm">{t('footer.legal')}</h4>
            <ul className="space-y-1 text-xs">
              <li><Link to="/about" className="text-muted-foreground hover:text-foreground">{t('footer.about')}</Link></li>
              <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground">{t('footer.privacy')}</Link></li>
              <li><Link to="/terms" className="text-muted-foreground hover:text-foreground">{t('footer.terms')}</Link></li>
              <li><Link to="/disclaimer" className="text-muted-foreground hover:text-foreground">{t('footer.disclaimer')}</Link></li>
              <li><Link to="/faq" className="text-muted-foreground hover:text-foreground">{t('footer.faq')}</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-sm">Newsletter</h4>
            <p className="text-xs text-muted-foreground mb-2">
              {t('footer.newsletterDesc')}
            </p>
            <Suspense fallback={<Skeleton className="h-10 w-full" />}>
              <NewsletterSignup variant="inline" />
            </Suspense>
          </div>
        </div>
        <div className="border-t pt-4 text-center">
          <p className="text-xs text-muted-foreground">
            {t('footer.copyright')}
          </p>
        </div>
      </div>
    </footer>
  );
}


// ============================================
// ERROR BOUNDARY
// ============================================
function ErrorFallback() {
  const { t } = useTranslation();
  return (
    <div className="min-h-screen flex items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">{t('error.title')}</h1>
        <p className="text-muted-foreground mb-4">{t('error.message')}</p>
        <button onClick={() => window.location.reload()} className="px-4 py-2 bg-blue-600 text-white rounded-lg">
          {t('error.reload')}
        </button>
      </div>
    </div>
  );
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}

// ============================================
// MAIN APP
// ============================================
function App() {
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode');
      return saved ? JSON.parse(saved) : false;
    }
    return false;
  });
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  return (
    <AuthProvider>
      <Router>
        <div className={`min-h-screen bg-background ${darkMode ? 'dark' : ''}`}>
          <BetaDisclaimer />
          <CriticalNotificationBanner />

          {/* Top navbar — full width */}
          <TopNavbar
            darkMode={darkMode}
            toggleDarkMode={() => setDarkMode(!darkMode)}
            onMobileSidebarOpen={() => setSidebarOpen(true)}
          />

          {/* Ticker bar */}
          <Suspense fallback={<TickerLoader />}>
            <TickerBar />
          </Suspense>

          {/* Layout: Sidebar + Content */}
          <div className="flex">
            <Sidebar
              mobileOpen={sidebarOpen}
              onMobileClose={() => setSidebarOpen(false)}
            />
            <div className="flex-1 min-w-0 flex flex-col">
            <main className="flex-1 px-3 lg:px-6 py-4 lg:py-5 bg-background min-w-0 overflow-x-hidden">
                <AppRouter />
              </main>
              <Footer />
            </div>
          </div>

          {/* Global overlays */}
          <Suspense fallback={null}>
            <InstallPWA />
          </Suspense>
          <Suspense fallback={null}>
            <InteractiveTour />
          </Suspense>
          <FinAssistant />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
