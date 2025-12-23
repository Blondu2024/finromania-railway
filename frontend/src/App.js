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
          </Routes>
        </main>
        <footer className="border-t py-6 mt-8">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted-foreground">
            <p>© 2025 FinRomania - Platformă de știri financiare pentru România</p>
            <p className="mt-1">Date BVB: <Badge variant="outline" className="text-xs">MOCK</Badge> (MVP)</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
