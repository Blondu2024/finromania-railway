import React, { useState, useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { BarChart3, Menu, Moon, Sun, User, LogOut, Star, Briefcase, Shield } from 'lucide-react';
import { Button } from './components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from './components/ui/sheet';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from './components/ui/dropdown-menu';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Skeleton } from './components/ui/skeleton';
import { initializePushNotifications } from './utils/pushNotifications';
import NotificationBell, { CriticalNotificationBanner } from './components/NotificationBell';
import FeedbackButton, { BetaDisclaimer, BetaBadge } from './components/BetaFeedback';
import './App.css';

// Initialize Service Worker for Push Notifications
initializePushNotifications();

// ============================================
// LAZY LOADED PAGES - Code Splitting
// ============================================

// Core pages (most visited)
const HomePage = lazy(() => import('./pages/HomePage'));
const StocksPage = lazy(() => import('./pages/StocksPage'));
const NewsPage = lazy(() => import('./pages/NewsPage'));
const GlobalMarketsPage = lazy(() => import('./pages/GlobalMarketsPage'));

// Education pages
const TradingSchoolPage = lazy(() => import('./pages/TradingSchoolPage'));
const FinancialEducationPage = lazy(() => import('./pages/FinancialEducationPage'));
const LessonPage = lazy(() => import('./pages/LessonPage'));
const FinLessonPage = lazy(() => import('./pages/FinLessonPage'));
const EducationPage = lazy(() => import('./pages/EducationPage'));

// Tools pages
const CurrencyConverterPage = lazy(() => import('./pages/CurrencyConverterPage'));
const DividendCalendarPage = lazy(() => import('./pages/DividendCalendarPage'));
const StockScreenerPage = lazy(() => import('./pages/StockScreenerPage'));
const GlossaryPage = lazy(() => import('./pages/GlossaryPage'));

// Detail pages
const StockDetailPage = lazy(() => import('./pages/StockDetailPage'));
const ArticleDetailPage = lazy(() => import('./pages/ArticleDetailPage'));

// User pages
const LoginPage = lazy(() => import('./pages/LoginPage'));
const AuthCallback = lazy(() => import('./pages/AuthCallback'));
const WatchlistPage = lazy(() => import('./pages/WatchlistPage'));
const PortfolioPage = lazy(() => import('./pages/PortfolioPage'));
const NotificationSettingsPage = lazy(() => import('./pages/NotificationSettingsPage'));

// Other pages
const CurrenciesPage = lazy(() => import('./pages/CurrenciesPage'));
const AIAdvisorPage = lazy(() => import('./pages/AIAdvisorPage'));
const RiskAssessmentPage = lazy(() => import('./pages/RiskAssessmentPage'));
const LearnTradingPage = lazy(() => import('./pages/LearnTradingPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboardPro'));

// Legal pages (rarely visited)
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const CookiePolicyPage = lazy(() => import('./pages/CookiePolicyPage'));
const DisclaimerPage = lazy(() => import('./pages/DisclaimerPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const FAQPage = lazy(() => import('./pages/FAQPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const AdminPage = lazy(() => import('./pages/AdminPage'));
const QuizPage = lazy(() => import('./pages/QuizPage'));
const FiscalCalculatorPage = lazy(() => import('./pages/FiscalCalculatorPage'));
const PricingPage = lazy(() => import('./pages/PricingPage'));
const PortfolioBVBPage = lazy(() => import('./pages/PortfolioBVBPage'));
const TryProPage = lazy(() => import('./pages/TryProPage'));
const PaymentSuccessPage = lazy(() => import('./pages/PaymentSuccessPage'));

// Lazy load heavy components
const TickerBar = lazy(() => import('./components/TickerBar'));
const SearchBar = lazy(() => import('./components/SearchBar'));
const NewsletterSignup = lazy(() => import('./components/NewsletterSignup'));
const InstallPWA = lazy(() => import('./components/InstallPWA'));
const InteractiveTour = lazy(() => import('./components/InteractiveTour'));

// ============================================
// LOADING FALLBACK - Minimal & Fast
// ============================================
const PageLoader = () => (
  <div className="min-h-[60vh] flex items-center justify-center">
    <div className="text-center space-y-4">
      <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
      <p className="text-muted-foreground text-sm">Se încarcă...</p>
    </div>
  </div>
);

const TickerLoader = () => (
  <div className="h-10 bg-slate-100 dark:bg-slate-800 animate-pulse" />
);

const SearchLoader = () => (
  <Skeleton className="h-9 w-48" />
);

// ============================================
// USER MENU COMPONENT
// ============================================
function UserMenu() {
  const { user, logout, login } = useAuth();
  const navigate = useNavigate();

  if (!user) {
    return (
      <Button onClick={login} variant="default" size="sm">
        <User className="w-4 h-4 mr-2" />
        Conectare
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="flex items-center gap-2">
          {user.picture ? (
            <img src={user.picture} alt="" className="w-8 h-8 rounded-full" loading="lazy" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <span className="text-blue-600 font-bold text-sm">{user.name?.[0]}</span>
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
          <Star className="w-4 h-4 mr-2" />
          Watchlist
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => navigate('/portfolio')}>
          <Briefcase className="w-4 h-4 mr-2" />
          Portofoliu
        </DropdownMenuItem>
        {user.is_admin && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => navigate('/admin')}>
              <Shield className="w-4 h-4 mr-2" />
              Admin Dashboard
            </DropdownMenuItem>
          </>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout} className="text-red-600">
          <LogOut className="w-4 h-4 mr-2" />
          Deconectare
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// ============================================
// WATCHLIST BUTTON COMPONENT
// ============================================
function WatchlistButton({ user, isActive }) {
  if (!user) return null;
  return (
    <Link 
      to="/watchlist" 
      className="relative p-2 rounded-md hover:bg-accent transition-colors"
      title="Watchlist"
    >
      <Star className={`w-5 h-5 ${isActive ? 'text-yellow-500 fill-yellow-500' : 'text-muted-foreground'}`} />
    </Link>
  );
}

// ============================================
// NAVIGATION COMPONENT - Simplified
// ============================================
function Navigation({ darkMode, toggleDarkMode }) {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();
  
  // Main navigation items - ACELEAȘI pentru desktop și mobile
  const navItems = [
    { path: '/', label: 'Acasă', icon: '🏠' },
    { path: '/stocks', label: 'Acțiuni BVB', icon: '📈' },
    { path: '/global', label: 'Piețe Globale', icon: '🌍' },
    { path: '/calculator-fiscal', label: 'Calculator Fiscal', icon: '🧮' },
    { path: '/news', label: 'Știri', icon: '📰' },
  ];

  // Grouped menu items
  const academiaItems = [
    { path: '/trading-school', label: 'Învață Trading', icon: '🎓' },
    { path: '/financial-education', label: 'Educație Financiară', icon: '📚' },
  ];

  const instrumenteItems = [
    { path: '/calendar', label: 'Dividende', icon: '🎯' },
    { path: '/screener', label: 'Screener', icon: '🔍' },
    { path: '/converter', label: 'Convertor', icon: '💱' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4 flex h-14 items-center">
        <Link to="/" className="flex items-center space-x-2 mr-4">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <span className="font-bold text-xl hidden sm:inline">FinRomania</span>
          <BetaBadge />
        </Link>
        
        {/* Search Bar - Lazy */}
        <div className="hidden md:flex items-center gap-2 mr-4">
          <Suspense fallback={<SearchLoader />}>
            <SearchBar />
          </Suspense>
          <NotificationBell />
          <UserMenu />
        </div>
        
        <nav className="hidden lg:flex items-center space-x-1 flex-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location.pathname === item.path 
                  ? 'bg-primary text-primary-foreground' 
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="flex items-center space-x-2 ml-auto">
          <WatchlistButton user={user} isActive={location.pathname === '/watchlist'} />
          
          <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          
          {/* UserMenu doar pe mobile - pe desktop e lângă search */}
          <div className="md:hidden">
            <UserMenu />
          </div>
          
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild className="lg:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-72 overflow-y-auto">
              <div className="flex flex-col space-y-3 mt-8">
                <div className="mb-4">
                  <Suspense fallback={<SearchLoader />}>
                    <SearchBar />
                  </Suspense>
                </div>
                
                {/* Main Navigation (4 items) */}
                <div className="space-y-1">
                  {navItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-3 rounded-md text-sm font-medium transition-colors ${
                        location.pathname === item.path 
                          ? 'bg-primary text-primary-foreground' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      <span className="text-lg">{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </div>

                {/* Academia Group */}
                <div className="pt-3 border-t">
                  <p className="px-4 text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                    <span>🎓</span> ACADEMIA
                  </p>
                  {academiaItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-2 rounded-md text-sm transition-colors ${
                        location.pathname === item.path 
                          ? 'bg-primary text-primary-foreground' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </div>

                {/* Instrumente Group */}
                <div className="pt-3 border-t">
                  <p className="px-4 text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                    <span>🔧</span> INSTRUMENTE
                  </p>
                  {instrumenteItems.map((item) => (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-2 rounded-md text-sm transition-colors ${
                        location.pathname === item.path 
                          ? 'bg-primary text-primary-foreground' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      <span>{item.icon}</span>
                      <span>{item.label}</span>
                    </Link>
                  ))}
                </div>
                
                {/* User Menu */}
                {user && (
                  <div className="pt-3 border-t">
                    <p className="px-4 text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
                      <span>👤</span> CONT
                    </p>
                    <Link
                      to="/watchlist"
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-2 rounded-md text-sm transition-colors ${
                        location.pathname === '/watchlist' 
                          ? 'bg-primary text-primary-foreground' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      <span>⭐</span>
                      <span>Watchlist</span>
                    </Link>
                    <Link
                      to="/portfolio-bvb"
                      onClick={() => setMobileOpen(false)}
                      className={`flex items-center space-x-3 px-4 py-2 rounded-md text-sm transition-colors ${
                        location.pathname === '/portfolio-bvb' 
                          ? 'bg-primary text-primary-foreground' 
                          : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                      }`}
                    >
                      <span>💼</span>
                      <span>Portofoliu BVB</span>
                    </Link>
                  </div>
                )}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

// ============================================
// APP ROUTER - With Suspense
// ============================================
function AppRouter() {
  const location = useLocation();
  
  // CRITICAL: Check URL fragment for session_id synchronously
  if (location.hash?.includes('session_id=')) {
    return (
      <Suspense fallback={<PageLoader />}>
        <AuthCallback />
      </Suspense>
    );
  }
  
  return (
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
        <Route path="/admin" element={<AdminPage />} />
        <Route path="/education" element={<EducationPage />} />
        <Route path="/education/success" element={<EducationPage />} />
        <Route path="/education/lesson/:lessonId" element={<LessonPage />} />
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
        <Route path="/screener" element={<StockScreenerPage />} />
        <Route path="/notifications" element={<NotificationSettingsPage />} />
        <Route path="/global" element={<GlobalMarketsPage />} />
        <Route path="/quiz/:level" element={<QuizPage />} />
        <Route path="/calculator-fiscal" element={<FiscalCalculatorPage />} />
        <Route path="/pricing" element={<PricingPage />} />
        <Route path="/portfolio-bvb" element={<PortfolioBVBPage />} />
        <Route path="/incearca-pro" element={<TryProPage />} />
        <Route path="/payment/success" element={<PaymentSuccessPage />} />
      </Routes>
    </Suspense>
  );
}

// ============================================
// FOOTER - Simplified
// ============================================
function Footer() {
  return (
    <footer className="border-t py-8 mt-8 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div>
            <h4 className="font-semibold mb-3">FinRomania</h4>
            <p className="text-sm text-muted-foreground">
              Platformă de educație și date financiare pentru România
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Navigare</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/" className="text-muted-foreground hover:text-foreground">Acasă</Link></li>
              <li><Link to="/stocks" className="text-muted-foreground hover:text-foreground">Acțiuni BVB</Link></li>
              <li><Link to="/trading-school" className="text-muted-foreground hover:text-foreground">Trading School</Link></li>
              <li><Link to="/financial-education" className="text-muted-foreground hover:text-foreground">Educație Financiară</Link></li>
              <li><Link to="/glossary" className="text-muted-foreground hover:text-foreground">Glosar</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/about" className="text-muted-foreground hover:text-foreground">Despre Noi</Link></li>
              <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground">Confidențialitate</Link></li>
              <li><Link to="/terms" className="text-muted-foreground hover:text-foreground">Termeni</Link></li>
              <li><Link to="/disclaimer" className="text-muted-foreground hover:text-foreground">Disclaimer</Link></li>
              <li><Link to="/faq" className="text-muted-foreground hover:text-foreground">FAQ</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Newsletter</h4>
            <p className="text-sm text-muted-foreground mb-3">
              Primește seara mesajul tău personal cu noutățile pieței
            </p>
            <Suspense fallback={<Skeleton className="h-10 w-full" />}>
              <NewsletterSignup variant="inline" />
            </Suspense>
          </div>
        </div>
        <div className="border-t pt-6 text-center">
          <p className="text-sm text-muted-foreground">
            © 2025 FinRomania - Toate drepturile rezervate
          </p>
        </div>
      </div>
    </footer>
  );
}

// ============================================
// MAIN APP COMPONENT
// ============================================
function App() {
  // Initialize dark mode from localStorage synchronously
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode');
      return saved ? JSON.parse(saved) : false;
    }
    return false;
  });

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
          <Navigation darkMode={darkMode} toggleDarkMode={() => setDarkMode(!darkMode)} />
          <Suspense fallback={<TickerLoader />}>
            <TickerBar />
          </Suspense>
          <main className="max-w-7xl mx-auto px-4 py-6">
            <AppRouter />
          </main>
          <Footer />
          {/* PWA Install Prompt */}
          <Suspense fallback={null}>
            <InstallPWA />
          </Suspense>
          {/* Interactive Tour for new visitors */}
          <Suspense fallback={null}>
            <InteractiveTour />
          </Suspense>
          {/* Feedback Button - BETA */}
          <FeedbackButton />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
