import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, BarChart3, DollarSign, Menu, Moon, Sun } from 'lucide-react';
import { Button } from './components/ui/button';
import { Badge } from './components/ui/badge';
import { Sheet, SheetContent, SheetTrigger } from './components/ui/sheet';
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
import TickerBar from './components/TickerBar';
import './App.css';

function Navigation({ darkMode, toggleDarkMode }) {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const navItems = [
    { path: '/', label: 'Acasă', icon: <BarChart3 className="w-4 h-4" /> },
    { path: '/stocks', label: 'Acțiuni BVB', icon: <TrendingUp className="w-4 h-4" /> },
    { path: '/news', label: 'Știri', icon: <Newspaper className="w-4 h-4" /> },
    { path: '/currencies', label: 'Valute', icon: <DollarSign className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="max-w-7xl mx-auto px-4 flex h-14 items-center">
        <Link to="/" className="flex items-center space-x-2 mr-6">
          <BarChart3 className="h-6 w-6 text-blue-600" />
          <span className="font-bold text-xl hidden sm:inline">FinRomania</span>
        </Link>
        
        <nav className="hidden md:flex items-center space-x-4 flex-1">
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
          <Button variant="ghost" size="icon" onClick={toggleDarkMode}>
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>
          
          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild className="md:hidden">
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <div className="flex flex-col space-y-4 mt-8">
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
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
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
    <Router>
      <div className={`min-h-screen bg-background ${darkMode ? 'dark' : ''}`}>
        <Navigation darkMode={darkMode} toggleDarkMode={() => setDarkMode(!darkMode)} />
        <TickerBar />
        <main className="max-w-7xl mx-auto px-4 py-6">
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
          </Routes>
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
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Legal</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link to="/privacy" className="text-muted-foreground hover:text-foreground">Politica de Confidențialitate</Link></li>
                  <li><Link to="/terms" className="text-muted-foreground hover:text-foreground">Termeni și Condiții</Link></li>
                  <li><Link to="/cookies" className="text-muted-foreground hover:text-foreground">Politica de Cookie-uri</Link></li>
                  <li><Link to="/disclaimer" className="text-muted-foreground hover:text-foreground">Disclaimer</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Contact</h4>
                <ul className="space-y-2 text-sm">
                  <li><Link to="/contact" className="text-muted-foreground hover:text-foreground">Contactează-ne</Link></li>
                  <li><span className="text-muted-foreground">contact@finromania.ro</span></li>
                </ul>
              </div>
            </div>
            <div className="border-t pt-6 flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-sm text-muted-foreground">
                © 2025 FinRomania - Toate drepturile rezervate
              </p>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">Date BVB: MOCK</Badge>
                <Badge variant="secondary" className="text-xs">MVP v2.0</Badge>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
