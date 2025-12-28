import React, { useState, useEffect, memo } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, RefreshCw, GraduationCap, BarChart3, Globe, BookOpen, Calculator, Search, PieChart, Target, Award } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import NewsletterSignup from '../components/NewsletterSignup';
import VerticalScroller from '../components/VerticalScroller';
import SEO from '../components/SEO';

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
// HERO SECTION - What is FinRomania?
// ============================================
const HeroSection = memo(function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white p-6 md:p-10">
      {/* Background decorations */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/20 rounded-full blur-3xl -mr-32 -mt-32" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/20 rounded-full blur-3xl -ml-24 -mb-24" />
      
      <div className="relative z-10">
        {/* Main Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-5xl font-bold mb-3">
            🇷🇴 Bine ai venit pe <span className="text-blue-400">FinRomania</span>
          </h1>
          <p className="text-lg md:text-xl text-blue-200 max-w-2xl mx-auto">
            Prima platformă din România care combină <strong>educația financiară gratuită</strong> cu <strong>date live de pe bursă</strong>
          </p>
        </div>

        {/* 4 Pillars Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {/* Pillar 1: Education */}
          <Link to="/trading-school" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <GraduationCap className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🎓 Educație</h3>
              <p className="text-sm text-blue-200">32 lecții gratuite de trading și finanțe</p>
              <Badge className="mt-2 bg-green-500/20 text-green-300">100% GRATUIT</Badge>
            </div>
          </Link>

          {/* Pillar 2: BVB Data */}
          <Link to="/stocks" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">📈 Date BVB</h3>
              <p className="text-sm text-blue-200">Prețuri live de pe Bursa București</p>
              <Badge className="mt-2 bg-blue-500/20 text-blue-300">LIVE</Badge>
            </div>
          </Link>

          {/* Pillar 3: Global Markets */}
          <Link to="/global" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Globe className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🌍 Piețe Globale</h3>
              <p className="text-sm text-blue-200">S&P 500, Bitcoin, Aur, Forex</p>
              <Badge className="mt-2 bg-purple-500/20 text-purple-300">24/7</Badge>
            </div>
          </Link>

          {/* Pillar 4: Tools */}
          <Link to="/screener" className="group">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center hover:bg-white/20 transition-all hover:scale-105">
              <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Search className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg mb-1">🔧 Instrumente</h3>
              <p className="text-sm text-blue-200">Screener, Calendar, Convertor</p>
              <Badge className="mt-2 bg-orange-500/20 text-orange-300">PRO</Badge>
            </div>
          </Link>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/trading-school">
            <Button size="lg" className="bg-green-600 hover:bg-green-700 w-full sm:w-auto">
              <BookOpen className="w-5 h-5 mr-2" />
              Începe să Înveți Gratuit
            </Button>
          </Link>
          <Link to="/stocks">
            <Button size="lg" variant="outline" className="border-white/30 text-white hover:bg-white/10 w-full sm:w-auto">
              <TrendingUp className="w-5 h-5 mr-2" />
              Vezi Bursa BVB
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
});

export default function HomePage() {
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
        title="FinRomania - Educație Financiară Gratuită + Date Live BVB"
        description="Prima platformă din România cu educație financiară gratuită și date live de pe bursă. 32 lecții de trading, prețuri BVB în timp real, screener acțiuni, calendar dividende. 100% gratuit!"
        keywords="educatie financiara gratuita, cursuri trading romania, bursa bucuresti live, bvb actiuni, investitii romania, analiza tehnica, trading pentru incepatori, actiuni romanesti"
      />
      
      <div className="space-y-10">
        {/* NEW: Hero Section with 4 Pillars */}
        <HeroSection />

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

            {/* Trading School CTA - REPLACED WITH HERO */}
            <Card className="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 text-white border-0">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-3 bg-white/20 rounded-full backdrop-blur-sm">
                  <GraduationCap className="w-8 h-8" />
                </div>
                <h3 className="text-2xl font-bold">
                  Gata Să Înveți Trading?
                </h3>
                <p className="text-sm text-blue-100">
                  17 lecții interactive + quiz-uri
                </p>
                <p className="text-xs text-blue-50">
                  100% GRATUIT în română
                </p>
                <Link to="/trading-school/lesson_1">
                  <Button className="w-full bg-white text-blue-600 hover:bg-blue-50 font-semibold">
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Începe Lecția 1
                  </Button>
                </Link>
                <Link to="/trading-school">
                  <Button variant="outline" className="w-full border-white text-white hover:bg-white/10">
                    Vezi Programul →
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Top Movers Section - WITH VERTICAL SCROLL! */}
        <section className="mt-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6">
            📊 Mișcările Pieței Astăzi
          </h2>
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

        {/* Educational Benefits - MOVED HERE */}
        <section className="mt-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-center mb-6">
            🎓 Învață Să Investești Inteligent
          </h2>
          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <Card className="border-2 border-blue-200 hover:border-blue-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-blue-100 rounded-full">
                  <BookOpen className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-xl font-bold">Școala de Trading</h3>
                <p className="text-muted-foreground">
                  17 lecții: acțiuni, leverage, indicatori tehnici, strategii
                </p>
                <Link to="/trading-school">
                  <Button className="w-full">
                    Vezi Lecțiile <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="border-2 border-green-200 hover:border-green-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-green-100 rounded-full">
                  <Target className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-xl font-bold">💰 Educație Financiară</h3>
                <p className="text-muted-foreground">
                  15 lecții: bugete, economii, pensii, investiții de bază
                </p>
                <Link to="/financial-education">
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    Începe Gratuit <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="border-2 border-purple-200 hover:border-purple-400 transition-colors">
              <CardContent className="p-6 text-center space-y-3">
                <div className="inline-block p-4 bg-purple-100 rounded-full">
                  <Award className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-xl font-bold">Quiz-uri Interactive</h3>
                <p className="text-muted-foreground">
                  Verifică-ți cunoștințele și primește feedback instant
                </p>
                <Link to="/trading-school">
                  <Button className="w-full" variant="outline">
                    Încearcă un Quiz <ArrowRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Final CTA - Compact */}
        <section className="mt-12">
          <Card className="bg-gradient-to-br from-green-600 to-blue-600 text-white border-0 max-w-4xl mx-auto">
            <CardContent className="p-8 text-center space-y-4">
              <div className="inline-block p-3 bg-white/20 rounded-full">
                <GraduationCap className="w-10 h-10" />
              </div>
              <h2 className="text-3xl font-bold">
                Nu Știi De Unde Să Începi? Hai Să Te Ajutăm!
              </h2>
              <p className="text-lg text-green-100 max-w-2xl mx-auto">
                De la bazele finanțelor personale până la strategii avansate de trading — totul gratuit, în română, pentru tine!
              </p>
              <div className="flex gap-4 justify-center flex-wrap">
                <Link to="/financial-education/fin_lesson_1">
                  <Button size="lg" className="bg-white text-green-600 hover:bg-green-50">
                    <Target className="w-5 h-5 mr-2" />
                    Începe cu Bazele
                  </Button>
                </Link>
                <Link to="/trading-school">
                  <Button size="lg" variant="outline" className="border-2 border-white text-white hover:bg-white/10">
                    Școala de Trading →
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </motion.section>
      </div>
    </>
  );
}
