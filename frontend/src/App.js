import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, BarChart3, DollarSign, Menu, Moon, Sun, User, LogOut, Star, Briefcase, Shield, BookOpen, Bot, ClipboardCheck, Calendar, Filter, Bell } from 'lucide-react';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Sheet, SheetContent, SheetTrigger } from './components/ui/sheet';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from './components/ui/dropdown-menu';
import { AuthProvider, useAuth } from './context/AuthContext';
import HomePage from './pages/HomePage';
import StocksPage from './pages/StocksPage';
import NewsPage from './pages/NewsPage';
import CurrenciesPage from './pages/CurrenciesPage';
import StockDetailPage from './pages/StockDetailPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import DisclaimerPage from './pages/DisclaimerPage';
import ContactPage from './pages/ContactPage';
import LoginPage from './pages/LoginPage';
import AuthCallback from './pages/AuthCallback';
import WatchlistPage from './pages/WatchlistPage';
import PortfolioPage from './pages/PortfolioPage';
import AdminDashboard from './pages/AdminDashboard';
import EducationPage from './pages/EducationPage';
import LessonPage from './pages/LessonPage';
import RiskAssessmentPage from './pages/RiskAssessmentPage';
import AIAdvisorPage from './pages/AIAdvisorPage';
import CurrencyConverterPage from './pages/CurrencyConverterPage';
import GlossaryPage from './pages/GlossaryPage';
import LearnTradingPage from './pages/LearnTradingPage';
import TradingSchoolPage from './pages/TradingSchoolPage';
import FinancialEducationPage from './pages/FinancialEducationPage';
import FinLessonPage from './pages/FinLessonPage';
import FAQPage from './pages/FAQPage';
import AboutPage from './pages/AboutPage';
import DividendCalendarPage from './pages/DividendCalendarPage';
import StockScreenerPage from './pages/StockScreenerPage';
import NotificationSettingsPage from './pages/NotificationSettingsPage';
import TickerBar from './components/TickerBar';
import SearchBar from './components/SearchBar';
import NewsletterSignup from './components/NewsletterSignup';
import './App.css';

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
            <img src={user.picture} alt="" className="w-8 h-8 rounded-full" />
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

function Navigation({ darkMode, toggleDarkMode }) {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user } = useAuth();
  
  const navItems = [
    { path: '/', label: 'Acasă', icon: <BarChart3 className="w-4 h-4" /> },
    { path: '/trading-school', label: '🎓 Învață Trading', icon: <BookOpen className="w-4 h-4" /> },
    { path: '/financial-education', label: '💰 Educație Financiară', icon: <DollarSign className="w-4 h-4" /> },
    { path: '/stocks', label: 'Acțiuni BVB', icon: <TrendingUp className="w-4 h-4" /> },
    { path: '/screener', label: '🔍 Screener', icon: <Filter className="w-4 h-4" /> },
    { path: '/calendar', label: '📅 Dividende', icon: <Calendar className="w-4 h-4" /> },
    { path: '/news', label: 'Știri', icon: <Newspaper className="w-4 h-4" /> },
    { path: '/converter', label: 'Convertor', icon: <DollarSign className="w-4 h-4" /> },
  ];

  const userNavItems = user ? [
    // Watchlist va fi afișat separat lângă user menu
  ] : [];

  // Watchlist button pentru useri logați
  const WatchlistButton = () => {
    if (!user) return null;
    return (
      <Link 
        to="/watchlist" 
        className="relative p-2 rounded-md hover:bg-accent transition-colors"
        title="Watchlist - Acțiunile tale preferate"
      >
        <Star className={`w-5 h-5 ${location.pathname === '/watchlist' ? 'text-yellow-500 fill-yellow-500' : 'text-muted-foreground'}`} />
      </Link>
    );
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4 flex h-14 items-center">
        <Link to="/" className="flex items-center space-x-2 mr-4">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <span className="font-bold text-xl hidden sm:inline">FinRomania</span>
        </Link>
        
        {/* Search Bar - lângă logo */}
        <div className="hidden md:block mr-4">
          <SearchBar />
        </div>
        
        <nav className="hidden lg:flex items-center space-x-1 flex-1">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === item.path ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent'}`}
            >
              {item.icon}
              <span>{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="flex items-center space-x-2 ml-auto">
          <WatchlistButton />
          
          <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          
          <UserMenu />
          
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild className="lg:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-72">
              <div className="flex flex-col space-y-4 mt-8">
                <div className="mb-4">
                  <SearchBar />
                </div>
                {navItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === item.path ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent'}`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </Link>
                ))}
                {user && (
                  <Link
                    to="/watchlist"
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${location.pathname === '/watchlist' ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-accent'}`}
                  >
                    <Star className="w-4 h-4" />
                    <span>⭐ Watchlist</span>
                  </Link>
                )}
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

function AppRouter() {
  const location = useLocation();
  
  // CRITICAL: Check URL fragment for session_id synchronously during render
  // This prevents race conditions with ProtectedRoute checks
  if (location.hash?.includes('session_id=')) {
    return <AuthCallback />;
  }
  
  return (
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
    </Routes>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('darkMode');
    if (saved) {
      setDarkMode(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  return (
    <AuthProvider>
      <Router>
        <div className={`min-h-screen bg-background ${darkMode ? 'dark' : ''}`}>
          <Navigation darkMode={darkMode} toggleDarkMode={() => setDarkMode(!darkMode)} />
          <TickerBar />
          <main className="max-w-7xl mx-auto px-4 py-6">
            <AppRouter />
          </main>
          <footer className="border-t py-8 mt-8 bg-muted/30">
            <div className="max-w-7xl mx-auto px-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
                <div>
                  <h4 className="font-semibold mb-3">FinRomania</h4>
                  <p className="text-sm text-muted-foreground">
                    Platformă de știri și date financiare pentru România
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Navigare</h4>
                  <ul className="space-y-2 text-sm">
                    <li><Link to="/" className="text-muted-foreground hover:text-foreground">Acasă</Link></li>
                    <li><Link to="/stocks" className="text-muted-foreground hover:text-foreground">Acțiuni BVB</Link></li>
                    <li><Link to="/news" className="text-muted-foreground hover:text-foreground">Știri</Link></li>
                    <li><Link to="/currencies" className="text-muted-foreground hover:text-foreground">Valute</Link></li>
                    <li><Link to="/trading-school" className="text-muted-foreground hover:text-foreground">Trading School</Link></li>
                    <li><Link to="/financial-education" className="text-muted-foreground hover:text-foreground">💰 Educație Financiară</Link></li>
                    <li><Link to="/glossary" className="text-muted-foreground hover:text-foreground">Glosar</Link></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Legal</h4>
                  <ul className="space-y-2 text-sm">
                    <li><Link to="/about" className="text-muted-foreground hover:text-foreground">Despre Noi</Link></li>
                    <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground">Politica de Confidențialitate</Link></li>
                    <li><Link to="/terms" className="text-muted-foreground hover:text-foreground">Termeni și Condiții</Link></li>
                    <li><Link to="/cookies" className="text-muted-foreground hover:text-foreground">Politica de Cookie-uri</Link></li>
                    <li><Link to="/disclaimer" className="text-muted-foreground hover:text-foreground">Disclaimer</Link></li>
                    <li><Link to="/faq" className="text-muted-foreground hover:text-foreground">Întrebări Frecvente</Link></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-3">Newsletter</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    Primește ultimele știri financiare
                  </p>
                  <NewsletterSignup variant="inline" />
                </div>
              </div>
              <div className="border-t pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
                <p className="text-sm text-muted-foreground">
                  © 2025 FinRomania - Toate drepturile rezervate
                </p>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
