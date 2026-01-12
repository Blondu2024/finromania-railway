import React, { useState, useEffect, memo } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, RefreshCw, GraduationCap, BarChart3, Globe, BookOpen, Calculator, Search, PieChart, Target, Award, Zap, Crown, Activity, Briefcase } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import NewsletterSignup from '../components/NewsletterSignup';
import VerticalScroller from '../components/VerticalScroller';
import SEO from '../components/SEO';
import FearGreedIndex from '../components/FearGreedIndex';
import { useAuth } from '../context/AuthContext';
import FeatureCard from '../components/FeatureCard';
import QuickCalculator from '../components/QuickCalculator';
import TrustBadges from '../components/TrustBadges';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Memoized Stock Card - no animations for performance
const StockCard = memo(function StockCard({ stock, type = 'bvb' }) {
  const isPositive = stock.change_percent >= 0;
  const linkPath = type === 'global' 
    ? `/stocks/global/${encodeURIComponent(stock.symbol)}`
    : `/stocks/bvb/${stock.symbol}`;
  
  return (
    <Link to={linkPath}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <CardContent className="p-4">
          <div className="flex justify-between items-start mb-2">
            <div>
              <p className="font-bold text-lg">{stock.symbol || stock.name}</p>
              <p className="text-sm text-muted-foreground truncate max-w-[120px]">{stock.name}</p>
            </div>
          </div>
          <div className="flex justify-between items-end">
            <p className="text-2xl font-bold">
              {stock.price?.toLocaleString('ro-RO', { maximumFractionDigits: 2 })}
              <span className="text-sm font-normal text-muted-foreground ml-1">{stock.currency || ''}</span>
            </p>
            <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? <TrendingUp className="w-4 h-4 mr-1" /> : <TrendingDown className="w-4 h-4 mr-1" />}
              <span className="font-medium">{isPositive ? '+' : ''}{stock.change_percent?.toFixed(2)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
});

// Memoized News Card
const NewsCard = memo(function NewsCard({ article }) {
  return (
    <Link to={`/news/${article.id}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <CardContent className="p-4">
          <div className="flex gap-4">
            {article.image_url && (
              <img 
                src={article.image_url} 
                alt="" 
                className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                loading="lazy"
                onError={(e) => e.target.style.display = 'none'}
              />
            )}
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold line-clamp-2 mb-1">{article.title}</h3>
              <p className="text-sm text-muted-foreground line-clamp-2">{article.description}</p>
              <div className="flex items-center mt-2 text-xs text-muted-foreground">
                <span>{article.source?.name}</span>
                <span className="mx-2">•</span>
                <span>{new Date(article.published_at).toLocaleDateString('ro-RO')}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
});

// ============================================
// HERO SECTION - Clear Value Props
// ============================================
const HeroSection = memo(function HeroSection({ user }) {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-6 md:p-10">
      {/* Background decorations */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl -mr-32 -mt-32" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/20 rounded-full blur-3xl -ml-24 -mb-24" />
      
      <div className="relative z-10">
        {/* Main Message */}
        <div className="text-center mb-8">
          <Badge className="bg-green-500/20 text-green-300 border-green-500/50 mb-4">
            <Zap className="w-3 h-3 mr-1" />
            Date LIVE · Delay 1s pentru Global Markets
          </Badge>
          <h1 className="text-3xl md:text-5xl font-bold mb-4 leading-tight">
            Investește <span className="text-blue-400">Inteligent</span> pe BVB și Global
          </h1>
          <p className="text-lg md:text-xl text-blue-200 max-w-2xl mx-auto mb-2">
            Portofoliu · Calculator Fiscal · Date Live · AI Advisor
          </p>
          <p className="text-base text-blue-300/80 max-w-xl mx-auto">
            Platforma românească completă pentru investitori moderni.
          </p>
        </div>

        {/* 4 Pillars - ORDINEA CORECTĂ pentru prima impresie PRO */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {/* 1. BVB - PRIMUL (arată că e platformă serioasă) */}
          <Link to="/stocks" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">📈 Bursa BVB</h3>
              <p className="text-sm text-blue-200">50+ acțiuni, date live, delay 15min</p>
              <Badge className="mt-2 bg-green-500/20 text-green-300 text-xs">LIVE DATA</Badge>
            </div>
          </Link>

          {/* 2. GLOBAL - AL DOILEA (arată feature PRO) */}
          <Link to="/global" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Globe className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🌍 Piețe Globale</h3>
              <p className="text-sm text-blue-200">US, EU, Asia - delay doar 1 secundă!</p>
              <Badge className="mt-2 bg-purple-500/20 text-purple-300 text-xs animate-pulse">1s DELAY</Badge>
            </div>
          </Link>

          {/* 3. CALCULATOR - AL TREILEA (valoare reală) */}
          <Link to="/calculator-fiscal" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105 ring-2 ring-amber-400/50">
              <div className="w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Calculator className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🧮 Calculator Fiscal</h3>
              <p className="text-sm text-blue-200">Economisește până la 50k+ RON/an</p>
              <Badge className="mt-2 bg-amber-500/20 text-amber-300 text-xs">PRO</Badge>
            </div>
          </Link>

          {/* 4. EDUCAȚIE - LA FINAL (pentru cei care vor să învețe) */}
          <Link to="/trading-school" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🎓 Educație</h3>
              <p className="text-sm text-blue-200">Cursuri gratuite pentru toți</p>
              <Badge className="mt-2 bg-blue-500/20 text-blue-300 text-xs">GRATUIT</Badge>
            </div>
          </Link>
        </div>

        {/* CTA Buttons - Focus pe VALUE */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/stocks">
            <Button size="lg" className="bg-green-600 hover:bg-green-700 w-full sm:w-auto">
              <TrendingUp className="w-5 h-5 mr-2" />
              Vezi Bursa BVB
            </Button>
          </Link>
          <Link to="/calculator-fiscal">
            <Button size="lg" className="bg-amber-600 hover:bg-amber-700 w-full sm:w-auto">
              <Calculator className="w-5 h-5 mr-2" />
              Calculator Fiscal PRO
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
});

export default function HomePage() {
  const { user } = useAuth();
  const [bvbStocks, setBvbStocks] = useState([]);
  const [globalIndices, setGlobalIndices] = useState([]);
  const [news, setNews] = useState([]);
  const [currencies, setCurrencies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      const [bvbRes, globalRes, newsRes, currRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb`),
        fetch(`${API_URL}/api/stocks/global`),
        fetch(`${API_URL}/api/news?limit=12`),
        fetch(`${API_URL}/api/currencies`)
      ]);
      
      const [bvb, global, newsData, curr] = await Promise.all([
        bvbRes.json(),
        globalRes.json(),
        newsRes.json(),
        currRes.json()
      ]);
      
      setBvbStocks(bvb);
      setGlobalIndices(global);
      setNews(newsData);
      setCurrencies(curr);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-64 w-full" />
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO 
        title="FinRomania - Investește Inteligent pe BVB și Global"
        description="Portofoliu BVB cu 3 Straturi, Calculator Fiscal PRO, Date LIVE Global (1s delay), AI Advisor."
        keywords="calculator fiscal, portofoliu bvb, date live bvb, global markets, investitii romania"
      />
      
      <div className="space-y-10">
        {/* Hero Section */}
        <HeroSection user={user} />

        {/* Fear & Greed Index - Prominent Position */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <FearGreedIndex />
          </div>
          <div className="lg:col-span-2">
            <Card className="h-full bg-gradient-to-br from-slate-50 to-white dark:from-slate-900 dark:to-slate-800 border-slate-200 dark:border-slate-700">
              <CardContent className="p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  Cum să interpretezi Fear & Greed?
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-red-500/10 rounded-lg border border-red-500/20">
                    <p className="font-semibold text-red-600 dark:text-red-400">0-25: Frică Extremă</p>
                    <p className="text-sm text-muted-foreground mt-1">Investitorii sunt panicați. Poate fi moment de cumpărare pentru cei cu strategie pe termen lung.</p>
                  </div>
                  <div className="p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
                    <p className="font-semibold text-orange-600 dark:text-orange-400">25-45: Frică</p>
                    <p className="text-sm text-muted-foreground mt-1">Pesimism general. Oportunități selective pentru investitori educați.</p>
                  </div>
                  <div className="p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                    <p className="font-semibold text-yellow-600 dark:text-yellow-400">45-55: Neutru</p>
                    <p className="text-sm text-muted-foreground mt-1">Piață echilibrată. Continuă analiza individuală a fiecărei acțiuni.</p>
                  </div>
                  <div className="p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                    <p className="font-semibold text-green-600 dark:text-green-400">55-100: Lăcomie</p>
                    <p className="text-sm text-muted-foreground mt-1">Optimism crescut. Atenție la supraevaluare și protejează profiturile.</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-4 italic">
                  ⚠️ Indicatorul Fear & Greed nu este o recomandare de investiții. Folosește-l ca un instrument de analiză alături de cercetarea ta.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Main Features Grid - TOATE Vizibile (8 Carduri) */}
        <section>
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-2">Explorează Platforma Completă</h2>
            <p className="text-muted-foreground">BVB · Global · Dividende · Știri · Screener · Convertor · Portofoliu · AI</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Row 1: Piețe și Date */}
            <FeatureCard 
              to="/stocks"
              icon={TrendingUp}
              title="Bursa București"
              description="50+ acțiuni BVB live (delay 15min)"
              badge={{ text: "LIVE", color: "bg-green-500" }}
              gradient="from-green-500 to-emerald-500"
              stats={[
                { value: "50+", label: "Acțiuni" },
                { value: "BET", label: "Index" }
              ]}
            />

            <FeatureCard 
              to="/global"
              icon={Globe}
              title="Piețe Globale"
              description="US, EU, Asia - Delay 1 secundă!"
              badge={{ text: "1s Delay", color: "bg-purple-500" }}
              gradient="from-purple-500 to-pink-500"
              stats={[
                { value: "LIVE", label: "Real-time" },
                { value: "1s", label: "Delay" }
              ]}
            />

            <FeatureCard 
              to="/calendar"
              icon={Target}
              title="Calendar Dividende"
              description="Plăți dividende BVB upcoming"
              badge={{ text: "Calendar", color: "bg-blue-500" }}
              gradient="from-blue-500 to-cyan-500"
              stats={[
                { value: "BVB", label: "Companii" },
                { value: "Live", label: "Updates" }
              ]}
            />

            <FeatureCard 
              to="/news"
              icon={Newspaper}
              title="Știri Financiare"
              description="Știri BVB și piețe internaționale"
              badge={{ text: "Daily", color: "bg-red-500" }}
              gradient="from-red-500 to-pink-500"
              stats={[
                { value: "Fresh", label: "Updates" },
                { value: "RO", label: "Limbă" }
              ]}
            />

            {/* Row 2: Tools și Instrumente */}
            <FeatureCard 
              to="/screener"
              icon={Search}
              title="Stock Screener"
              description="Filtrează acțiuni BVB după criterii"
              gradient="from-cyan-500 to-blue-500"
              stats={[
                { value: "50+", label: "Acțiuni" },
                { value: "Filtre", label: "Multiple" }
              ]}
            />

            <FeatureCard 
              to="/converter"
              icon={ArrowRight}
              title="Convertor Valutar"
              description="RON ⇄ USD, EUR, GBP live"
              gradient="from-orange-500 to-red-500"
              stats={[
                { value: "BNR", label: "Oficial" },
                { value: "Live", label: "Cursuri" }
              ]}
            />

            <FeatureCard 
              to="/portfolio-bvb"
              icon={Briefcase}
              title="Portofoliu BVB"
              description="Sistem 3 Straturi cu AI"
              badge={user ? { text: "Activ", color: "bg-green-500" } : { text: "Login", color: "bg-gray-500" }}
              gradient="from-blue-500 to-indigo-500"
              stats={[
                { value: "3", label: "Nivele" },
                { value: "AI", label: "Analiză" }
              ]}
            />

            <FeatureCard 
              to="/advisor"
              icon={Activity}
              title="AI Advisor"
              description="5 gratis/zi, nelimitat cu PRO"
              badge={{ text: "AI", color: "bg-purple-500" }}
              gradient="from-purple-500 to-fuchsia-500"
              stats={[
                { value: "5", label: "FREE/zi" },
                { value: "∞", label: "PRO" }
              ]}
            />
          </div>
        </section>

        {/* Quick Calculator + CTA Încearcă PRO */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <QuickCalculator user={user} />
          
          {/* CTA Încearcă PRO */}
          <Link to="/incearca-pro">
            <Card className="h-full bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 text-white hover:shadow-2xl transition-all cursor-pointer">
              <CardContent className="p-8 flex flex-col items-center justify-center h-full text-center">
                <Crown className="w-16 h-16 mb-4" />
                <h3 className="text-2xl font-bold mb-2">Vezi Toate Diferențele</h3>
                <p className="text-white/90 mb-4">
                  Comparație completă FREE vs PRO
                </p>
                <Badge className="bg-white/20 text-white text-lg px-4 py-2">
                  Tabel Detaliat →
                </Badge>
              </CardContent>
            </Card>
          </Link>
        </div>

        {/* BVB Stocks - Vertical Auto-Scroll */}
        <section>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                Bursa de Valori București
              </h2>
              <p className="text-muted-foreground mt-1">Acțiuni românești - scroll automat ⬇️</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleRefresh} disabled={refreshing} size="sm">
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Actualizează
              </Button>
              <Link to="/stocks">
                <Button variant="ghost" size="sm">
                  Vezi toate <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
          </div>
          <VerticalScroller speed={40}>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {bvbStocks.map(stock => (
                <StockCard key={stock.symbol} stock={stock} type="bvb" />
              ))}
            </div>
          </VerticalScroller>
        </section>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-4 gap-6">
          {/* News - Left side */}
          <div className="lg:col-span-3 space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-2xl sm:text-3xl font-bold flex items-center gap-2">
                  <Newspaper className="w-6 h-6 text-purple-600" />
                  Ultimele Știri Financiare
                </h2>
                <p className="text-muted-foreground mt-1">Actualizate automat din surse românești</p>
              </div>
              <Link to="/news">
                <Button variant="ghost" size="sm">
                  Vezi toate <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            
            <div className="space-y-4">
              {news.slice(0, 12).map(article => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          </div>

          {/* Sidebar - Right */}
          <div className="space-y-6">
            {/* Global Indices - Vertical Scroll */}
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Indici Globali</CardTitle>
                <p className="text-xs text-muted-foreground">Scroll automat ⬇️</p>
              </CardHeader>
              <CardContent>
                <VerticalScroller speed={30}>
                  {globalIndices.map(index => {
                    const isPositive = index.change_percent >= 0;
                    return (
                      <div key={index.symbol} className="flex justify-between items-center p-3 bg-muted/30 rounded-lg hover:bg-muted/60 transition-colors">
                        <div>
                          <p className="font-medium text-sm">{index.name || index.symbol}</p>
                          <p className="text-xs text-muted-foreground">{index.symbol}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-sm">{index.price?.toLocaleString('ro-RO')}</p>
                          <p className={`text-xs font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositive ? '+' : ''}{index.change_percent?.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </VerticalScroller>
              </CardContent>
            </Card>

            {/* Currencies Widget - Vertical Scroll */}
            {currencies?.rates && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Curs Valutar BNR</CardTitle>
                  <p className="text-xs text-muted-foreground">Top 10 valute</p>
                </CardHeader>
                <CardContent>
                  <div style={{ maxHeight: '250px', overflow: 'hidden' }}>
                    <VerticalScroller speed={15}>
                      <div className="space-y-1.5">
                        {Object.entries(currencies.rates).slice(0, 10).map(([code, data]) => (
                          <div key={code} className="flex justify-between items-center p-2 bg-muted/30 rounded hover:bg-muted/60 transition-colors">
                            <span className="font-semibold text-sm">{code}</span>
                            <p className="font-bold text-sm">{data.rate?.toFixed(4)} <span className="text-xs text-muted-foreground">RON</span></p>
                          </div>
                        ))}
                      </div>
                    </VerticalScroller>
                  </div>
                  <Link to="/converter" className="block mt-3">
                    <Button variant="outline" size="sm" className="w-full text-xs">
                      Vezi Toate Valutele →
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}

            {/* Newsletter */}
            <NewsletterSignup variant="sidebar" />

            {/* Trading School CTA - Professional Tone */}
            <Card className="bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900 text-white border-0">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-3 bg-white/10 rounded-full">
                  <GraduationCap className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold">
                  Școala de Trading
                </h3>
                <p className="text-sm text-slate-300">
                  17 lecții structurate cu quiz-uri de verificare
                </p>
                <p className="text-xs text-slate-400">
                  Gratuit. În română. La ritmul tău.
                </p>
                <Link to="/trading-school/lesson_1">
                  <Button className="w-full bg-blue-600 hover:bg-blue-700 font-medium">
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Începe Lecția 1
                  </Button>
                </Link>
                <Link to="/trading-school">
                  <Button variant="ghost" className="w-full text-slate-300 hover:text-white hover:bg-white/10">
                    Vezi Programa →
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Top Movers Section - WITH VERTICAL SCROLL! */}
        <section className="mt-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-2">
            📊 Mișcările Zilei pe BVB
          </h2>
          <p className="text-center text-muted-foreground mb-6">
            Cele mai semnificative variații de preț — actualizate în timp real
          </p>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Top Gainers - Vertical Scroll */}
            <Card className="border-2 border-green-300">
              <CardHeader className="bg-green-50">
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <TrendingUp className="w-5 h-5" />
                  Top Gainers (Creșteri)
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div style={{ maxHeight: '400px', overflow: 'hidden' }}>
                  <VerticalScroller speed={20}>
                    <div className="space-y-2">
                      {bvbStocks
                        .filter(s => s.change_percent > 0)
                        .sort((a, b) => b.change_percent - a.change_percent)
                        .map((stock, idx) => (
                          <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                            <div className="flex items-center justify-between p-3 bg-green-50 hover:bg-green-100 rounded-lg transition-colors cursor-pointer">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                                  {idx + 1}
                                </div>
                                <div>
                                  <p className="font-bold">{stock.symbol}</p>
                                  <p className="text-xs text-muted-foreground">{stock.name}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="font-bold text-sm">{stock.price?.toFixed(2)} RON</p>
                                <p className="text-sm font-bold text-green-600">
                                  +{stock.change_percent?.toFixed(2)}%
                                </p>
                              </div>
                            </div>
                          </Link>
                        ))}
                    </div>
                  </VerticalScroller>
                </div>
              </CardContent>
            </Card>

            {/* Top Losers - Vertical Scroll */}
            <Card className="border-2 border-red-300">
              <CardHeader className="bg-red-50">
                <CardTitle className="flex items-center gap-2 text-red-700">
                  <TrendingDown className="w-5 h-5" />
                  Top Losers (Scăderi)
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4">
                <div style={{ maxHeight: '400px', overflow: 'hidden' }}>
                  <VerticalScroller speed={20}>
                    <div className="space-y-2">
                      {bvbStocks
                        .filter(s => s.change_percent < 0)
                        .sort((a, b) => a.change_percent - b.change_percent)
                        .map((stock, idx) => (
                          <Link key={stock.symbol} to={`/stocks/bvb/${stock.symbol}`}>
                            <div className="flex items-center justify-between p-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors cursor-pointer">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 bg-red-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                                  {idx + 1}
                                </div>
                                <div>
                                  <p className="font-bold">{stock.symbol}</p>
                                  <p className="text-xs text-muted-foreground">{stock.name}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="font-bold text-sm">{stock.price?.toFixed(2)} RON</p>
                                <p className="text-sm font-bold text-red-600">
                                  {stock.change_percent?.toFixed(2)}%
                                </p>
                              </div>
                            </div>
                          </Link>
                        ))}
                    </div>
                  </VerticalScroller>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Educational Benefits - PROFESSIONAL TONE */}
        <section className="mt-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-2">
            🎓 Educație Structurată
          </h2>
          <p className="text-center text-muted-foreground mb-6 max-w-xl mx-auto">
            Fără promisiuni, fără hype. Doar cunoștințe concrete pentru decizii informate.
          </p>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <Card className="border-2 border-blue-200 hover:border-blue-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-blue-100 rounded-full">
                  <BookOpen className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold">Școala de Trading</h3>
                <p className="text-muted-foreground">
                  De la bazele pieței de capital la indicatori tehnici și strategii avansate
                </p>
                <Link to="/trading-school">
                  <Button className="w-full">
                    Accesează <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-200 hover:border-green-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-green-100 rounded-full">
                  <Target className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-bold">💰 Finanțe Personale</h3>
                <p className="text-muted-foreground">
                  Bugete, economii, pensii — fundația oricărei decizii financiare solide
                </p>
                <Link to="/financial-education">
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    Accesează <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="border-2 border-purple-200 hover:border-purple-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-purple-100 rounded-full">
                  <Award className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold">Verificare Cunoștințe</h3>
                <p className="text-muted-foreground">
                  Quiz-uri la finalul fiecărei lecții pentru a-ți consolida înțelegerea
                </p>
                <Link to="/trading-school">
                  <Button className="w-full" variant="outline">
                    Testează-te <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Final CTA - Professional & Clear */}
        <section className="mt-12">
          <Card className="bg-gradient-to-br from-slate-800 to-slate-900 text-white border-0 max-w-4xl mx-auto">
            <CardContent className="p-8 text-center space-y-4">
              <h2 className="text-2xl md:text-3xl font-bold">
                Claritate într-un domeniu haotic.
              </h2>
              <p className="text-base text-slate-300 max-w-2xl mx-auto">
                FinRomania nu îți promite îmbogățire rapidă. Îți oferă instrumentele și cunoștințele 
                necesare pentru a lua decizii informate — fie că ești la început sau ai experiență.
              </p>
              <div className="flex gap-4 justify-center flex-wrap pt-2">
                <Link to="/financial-education/fin_lesson_1">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                    <Target className="w-5 h-5 mr-2" />
                    Începe cu Bazele
                  </Button>
                </Link>
                <Link to="/stocks">
                  <Button size="lg" variant="outline" className="border-slate-500 text-white hover:bg-slate-700">
                    Explorează Piața →
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </>
  );
}
