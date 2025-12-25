import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, RefreshCw, GraduationCap, Target, Award, BookOpen, BarChart3, Zap } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import NewsletterSignup from '../components/NewsletterSignup';
import VerticalScroller from '../components/VerticalScroller';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function StockCard({ stock, type = 'bvb' }) {
  const isPositive = stock.change_percent >= 0;
  const linkPath = type === 'global' 
    ? `/stocks/global/${encodeURIComponent(stock.symbol)}`
    : `/stocks/bvb/${stock.symbol}`;
  
  return (
    <Link to={linkPath}>
      <motion.div
        whileHover={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="hover:shadow-lg transition-all cursor-pointer h-full">
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
      </motion.div>
    </Link>
  );
}

function NewsCard({ article }) {
  return (
    <Link to={`/news/${article.id}`}>
      <motion.div
        whileHover={{ scale: 1.01 }}
        transition={{ duration: 0.2 }}
      >
        <Card className="hover:shadow-lg transition-all cursor-pointer h-full">
          <CardContent className="p-4">
            <div className="flex gap-4">
              {article.image_url && (
                <img 
                  src={article.image_url} 
                  alt="" 
                  className="w-20 h-20 object-cover rounded-md flex-shrink-0"
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
      </motion.div>
    </Link>
  );
}

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
        fetch(`${API_URL}/api/news?limit=6`),
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
        title="FinRomania - Învață Trading Gratuit de la Zero"
        description="Prima platformă educațională de trading din România. 17 lecții interactive gratuite, date live BVB, AI Advisor, quiz-uri și portofoliu demo. Învață trading în română, 100% gratuit!"
        keywords="invatare trading romania, cursuri trading gratuite, bursa bucuresti, bvb, actiuni romanesti, analiza tehnica, investitii romania, educational trading, trading pentru incepatori"
      />
      
      <div className="space-y-12">
        {/* Hero Section - REWRITE COMPLET */}
        <motion.section 
          className="relative overflow-hidden"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="bg-gradient-to-br from-blue-600 via-purple-600 to-blue-800 text-white rounded-2xl p-8 md:p-12 lg:p-16">
            <div className="max-w-4xl mx-auto text-center space-y-6">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-block p-4 bg-white/20 rounded-full backdrop-blur-sm"
              >
                <GraduationCap className="w-12 h-12" />
              </motion.div>
              
              <motion.h1 
                className="text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Învață Trading de la ZERO
              </motion.h1>
              
              <motion.p 
                className="text-xl sm:text-2xl text-blue-100 max-w-3xl mx-auto"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                Înțelege Piața, Termenii, Graficele și Strategiile
              </motion.p>
              
              <motion.p 
                className="text-lg text-blue-50 max-w-2xl mx-auto"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                Curs complet cu <strong>17 lecții interactive</strong>, quiz-uri la fiecare capitol, 
                și portofoliu demo — totul în română, <strong>100% GRATUIT!</strong>
              </motion.p>
              
              <motion.div 
                className="flex gap-4 justify-center flex-wrap pt-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                <Link to="/trading-school/lesson_1">
                  <Button size="lg" className="bg-white text-blue-600 hover:bg-blue-50 text-lg px-8 py-6 h-auto">
                    <GraduationCap className="w-5 h-5 mr-2" />
                    Începe Lecția 1 GRATUIT
                  </Button>
                </Link>
                <Link to="/trading-school">
                  <Button size="lg" variant="outline" className="border-2 border-white text-white hover:bg-white/10 text-lg px-8 py-6 h-auto">
                    <BookOpen className="w-5 h-5 mr-2" />
                    Vezi Programul Complet
                  </Button>
                </Link>
              </motion.div>
              
              <motion.div 
                className="flex items-center justify-center gap-6 pt-6 flex-wrap text-sm text-blue-100"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  <span>17 Lecții Complete</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  <span>Quiz Interactive</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  <span>Date Reale BVB</span>
                </div>
              </motion.div>
            </div>
          </div>
        </motion.section>

        {/* Benefits Section - 3 Coloane */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="grid md:grid-cols-3 gap-6"
        >
          <Card className="border-2 border-blue-200 hover:border-blue-400 transition-colors">
            <CardContent className="p-6 text-center space-y-3">
              <div className="inline-block p-4 bg-blue-100 rounded-full">
                <BookOpen className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold">17 Lecții Interactive</h3>
              <p className="text-muted-foreground">
                Învață concepte de la bază până la avansat: acțiuni, leverage, indicatori tehnici, strategii de trading
              </p>
              <Link to="/trading-school">
                <Button variant="link" className="text-blue-600">
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
              <h3 className="text-xl font-bold">Quiz cu Feedback</h3>
              <p className="text-muted-foreground">
                Verifică-ți cunoștințele după fiecare lecție și primește explicații detaliate pentru fiecare răspuns
              </p>
              <Link to="/trading-school">
                <Button variant="link" className="text-green-600">
                  Încearcă un Quiz <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card className="border-2 border-purple-200 hover:border-purple-400 transition-colors">
            <CardContent className="p-6 text-center space-y-3">
              <div className="inline-block p-4 bg-purple-100 rounded-full">
                <BarChart3 className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold">Date Reale BVB</h3>
              <p className="text-muted-foreground">
                Prețuri live de pe Bursa de Valori București, actualizate automat - vezi piața reală, nu simulări
              </p>
              <Link to="/stocks">
                <Button variant="link" className="text-purple-600">
                  Explorează BVB <ArrowRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.section>

        {/* BVB Stocks */}
        <section>
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-blue-600" />
                Bursa de Valori București
              </h2>
              <p className="text-muted-foreground mt-1">Acțiuni românești - date live</p>
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
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            {bvbStocks.slice(0, 5).map(stock => (
              <StockCard key={stock.symbol} stock={stock} type="bvb" />
            ))}
          </motion.div>
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
            
            <motion.div 
              className="space-y-4"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {news.slice(0, 6).map(article => (
                <NewsCard key={article.id} article={article} />
              ))}
            </motion.div>
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

            {/* Currencies Widget */}
            {currencies?.rates && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">Curs Valutar BNR</CardTitle>
                  <p className="text-xs text-muted-foreground">Data: {currencies.date}</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {['EUR', 'USD', 'GBP', 'CHF'].map(code => currencies.rates[code] && (
                      <div key={code} className="text-center p-3 bg-muted/50 rounded-lg">
                        <p className="text-lg font-bold">{currencies.rates[code].rate?.toFixed(4)}</p>
                        <p className="text-xs text-muted-foreground">{code}/RON</p>
                      </div>
                    ))}
                  </div>
                  <Link to="/converter" className="block mt-3">
                    <Button variant="outline" size="sm" className="w-full">
                      Convertor Valutar <ArrowRight className="w-4 h-4 ml-1" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            )}

            {/* Newsletter */}
            <NewsletterSignup variant="sidebar" />

            {/* Trading School CTA */}
            <Card className="bg-gradient-to-br from-green-50 to-blue-50 border-2 border-green-300">
              <CardContent className="p-6 text-center space-y-4">
                <div className="inline-block p-3 bg-green-600 text-white rounded-full">
                  <GraduationCap className="w-8 h-8" />
                </div>
                <h3 className="text-xl font-bold">Învață Trading Gratuit</h3>
                <p className="text-sm text-muted-foreground">
                  17 lecții interactive, quiz-uri, și ghidare pas-cu-pas
                </p>
                <Link to="/trading-school">
                  <Button className="w-full bg-green-600 hover:bg-green-700">
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Începe Acum
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
