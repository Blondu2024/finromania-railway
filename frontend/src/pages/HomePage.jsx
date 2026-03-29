import React, { useState, useEffect, memo, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, TrendingDown, Newspaper, ArrowRight, GraduationCap, Globe, Search, Activity, Zap, Crown, Gift } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import SEO from '../components/SEO';
import { useAuth } from '../context/AuthContext';
import FearGreedIndex from '../components/FearGreedIndex';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Compact News Card
const NewsCard = memo(function NewsCard({ article, isInternational }) {
  return (
    <Link to={`/news/${article.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardContent className="p-3">
          <div className="flex gap-3 items-start">
            {article.image_url && (
              <img
                src={article.image_url}
                alt=""
                className="w-16 h-16 object-cover rounded flex-shrink-0"
                loading="lazy"
                onError={(e) => e.target.style.display = 'none'}
              />
            )}
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm line-clamp-2 leading-tight">{article.title}</h3>
              <div className="flex items-center mt-1.5 text-xs text-muted-foreground">
                <span className="truncate">{article.source?.name}</span>
                {isInternational && <Badge variant="outline" className="ml-1.5 text-[10px] py-0 px-1">EN</Badge>}
                <span className="mx-1.5">&middot;</span>
                <span className="flex-shrink-0">{new Date(article.published_at).toLocaleDateString(isInternational ? 'en-US' : 'ro-RO')}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
});

// Mover row (static, no auto-scroll)
const MoverRow = memo(function MoverRow({ stock, rank, isGainer }) {
  return (
    <Link to={`/stocks/bvb/${stock.symbol}`}>
      <div className={`flex items-center justify-between p-2.5 rounded-lg transition-colors cursor-pointer ${
        isGainer ? 'bg-green-50 hover:bg-green-100 dark:bg-green-950/30 dark:hover:bg-green-950/50' : 'bg-red-50 hover:bg-red-100 dark:bg-red-950/30 dark:hover:bg-red-950/50'
      }`}>
        <div className="flex items-center gap-2.5">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold ${isGainer ? 'bg-green-600' : 'bg-red-600'}`}>
            {rank}
          </div>
          <div>
            <p className="font-bold text-sm">{stock.symbol}</p>
            <p className="text-xs text-muted-foreground truncate max-w-[100px]">{stock.name}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="font-bold text-sm">{stock.price?.toFixed(2)} RON</p>
          <p className={`text-xs font-bold ${isGainer ? 'text-green-600' : 'text-red-600'}`}>
            {isGainer ? '+' : ''}{stock.change_percent?.toFixed(2)}%
          </p>
        </div>
      </div>
    </Link>
  );
});

export default function HomePage() {
  const { user } = useAuth();
  const [bvbStocks, setBvbStocks] = useState([]);
  const [news, setNews] = useState([]);
  const [intlNews, setIntlNews] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const [bvbRes, newsRes, intlNewsRes] = await Promise.all([
        fetch(`${API_URL}/api/stocks/bvb`),
        fetch(`${API_URL}/api/news/romania?limit=6`),
        fetch(`${API_URL}/api/news/international?limit=6`),
      ]);

      const [bvb, newsData, intlNewsData] = await Promise.all([
        bvbRes.json(),
        newsRes.json(),
        intlNewsRes.json(),
      ]);

      setBvbStocks(bvb);
      setNews(Array.isArray(newsData) ? newsData : []);
      setIntlNews(Array.isArray(intlNewsData) ? intlNewsData : []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Top movers (static, top 5)
  const gainers = bvbStocks
    .filter(s => s.change_percent > 0)
    .sort((a, b) => b.change_percent - a.change_percent)
    .slice(0, 5);

  const losers = bvbStocks
    .filter(s => s.change_percent < 0)
    .sort((a, b) => a.change_percent - b.change_percent)
    .slice(0, 5);

  if (loading) {
    return (
      <div className="space-y-8">
        <Skeleton className="h-64 w-full rounded-2xl" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32" />)}
        </div>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="FinRomania - Investește Inteligent pe BVB și Global"
        description="Platforma românească de educație financiară cu date reale BVB, AI Advisor, Stock Screener și Trading School."
        keywords="bvb, bursa bucuresti, actiuni romania, investitii, screener, dividende"
      />

      <div className="space-y-10">

        {/* ====== SECTION 1: HERO ====== */}
        <section className="relative overflow-hidden rounded-2xl bg-black text-white p-6 md:p-10">
          <div className="relative z-10">
            <div className="text-center mb-8">
              <Badge className="bg-green-500/20 text-green-300 border-green-500/50 mb-4">
                <Zap className="w-3 h-3 mr-1" />
                Date Live BVB &middot; 55+ Acțiuni &middot; AI Powered
              </Badge>
              <h1 className="text-3xl md:text-5xl font-bold mb-4 leading-tight">
                Înțelege Piața <span className="text-blue-400">Înainte</span> să Investești
              </h1>
              <p className="text-lg md:text-xl text-gray-300 max-w-2xl mx-auto mb-2">
                Educație &middot; Analiză &middot; Date Live &middot; Instrumente Profesionale
              </p>
              <p className="text-base text-gray-400 max-w-xl mx-auto">
                Platforma românească de educație financiară cu date reale BVB și Global.
              </p>
            </div>

            {/* PRO Gratuit - Early Adopter Offer (only for non-PRO users) */}
            {(!user || (!user.is_early_adopter && user.subscription_level !== 'pro')) && (
              <div className="bg-green-600/20 border border-green-500/40 rounded-xl p-4 max-w-lg mx-auto mb-6 text-center">
                <p className="flex items-center justify-center gap-2 font-bold text-green-300 text-lg">
                  <Gift className="w-5 h-5" />
                  PRO GRATUIT până pe 5 Iunie!
                </p>
                <p className="text-sm text-green-200/80 mt-1">
                  Înregistrează-te acum — acces complet la AI Advisor, Analiză Tehnică, Calculator Fiscal și toate funcțiile PRO. Fără card bancar.
                </p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {!user ? (
                <Link to="/login">
                  <Button size="lg" className="bg-green-600 hover:bg-green-700 w-full sm:w-auto">
                    <Gift className="w-5 h-5 mr-2" />
                    Începe GRATUIT cu PRO
                  </Button>
                </Link>
              ) : (
                <Link to="/stocks">
                  <Button size="lg" className="bg-green-600 hover:bg-green-700 w-full sm:w-auto">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Vezi Bursa BVB
                  </Button>
                </Link>
              )}
              <Link to="/trading-school">
                <Button size="lg" variant="outline" className="border-gray-500 text-white hover:bg-white/10 w-full sm:w-auto">
                  <GraduationCap className="w-5 h-5 mr-2" />
                  Școala de Trading
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* ====== SECTION 2: MARKET SNAPSHOT ====== */}
        <section>
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-600" />
            Piața Azi
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Fear & Greed - compact */}
            <FearGreedIndex />

            {/* Top Gainers */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-green-600" />
                  Top Creșteri BVB
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {gainers.length > 0 ? gainers.map((stock, idx) => (
                  <MoverRow key={stock.symbol} stock={stock} rank={idx + 1} isGainer />
                )) : (
                  <p className="text-sm text-muted-foreground py-4 text-center">Nicio creștere azi</p>
                )}
                <Link to="/stocks" className="block pt-2">
                  <Button variant="ghost" size="sm" className="w-full text-xs">
                    Vezi toate acțiunile <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Top Losers */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingDown className="w-4 h-4 text-red-600" />
                  Top Scăderi BVB
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-1.5">
                {losers.length > 0 ? losers.map((stock, idx) => (
                  <MoverRow key={stock.symbol} stock={stock} rank={idx + 1} isGainer={false} />
                )) : (
                  <p className="text-sm text-muted-foreground py-4 text-center">Nicio scădere azi</p>
                )}
                <Link to="/stocks" className="block pt-2">
                  <Button variant="ghost" size="sm" className="w-full text-xs">
                    Vezi toate acțiunile <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* ====== SECTION 3: 4 FEATURE CARDS ====== */}
        <section>
          <div className="text-center mb-8">
            <h2 className="text-2xl md:text-3xl font-bold mb-2">Ce Poți Face pe FinRomania</h2>
            <p className="text-muted-foreground">Instrumente profesionale pentru investitorul român</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* BVB Live */}
            <Link to="/stocks">
              <Card className="h-full hover:shadow-lg transition-all border-2 hover:border-green-400 cursor-pointer group">
                <CardContent className="p-5 text-center space-y-3">
                  <div className="inline-flex p-3 rounded-xl bg-green-100 dark:bg-green-900/30 group-hover:scale-110 transition-transform">
                    <TrendingUp className="w-7 h-7 text-green-600" />
                  </div>
                  <h3 className="font-bold text-lg">Bursa BVB</h3>
                  <p className="text-sm text-muted-foreground">55+ acțiuni cu date live, grafice, dividende și analiză tehnică</p>
                  <Badge className="bg-green-500 text-white">LIVE</Badge>
                </CardContent>
              </Card>
            </Link>

            {/* Stock Screener */}
            <Link to="/screener">
              <Card className="h-full hover:shadow-lg transition-all border-2 hover:border-blue-400 cursor-pointer group">
                <CardContent className="p-5 text-center space-y-3">
                  <div className="inline-flex p-3 rounded-xl bg-blue-100 dark:bg-blue-900/30 group-hover:scale-110 transition-transform">
                    <Search className="w-7 h-7 text-blue-600" />
                  </div>
                  <h3 className="font-bold text-lg">Stock Screener</h3>
                  <p className="text-sm text-muted-foreground">Filtrează acțiuni BVB după P/E, dividende, RSI, volum și mai mult</p>
                  <Badge variant="outline">Filtre Multiple</Badge>
                </CardContent>
              </Card>
            </Link>

            {/* AI Advisor */}
            <Link to="/advisor">
              <Card className="h-full hover:shadow-lg transition-all border-2 hover:border-purple-400 cursor-pointer group">
                <CardContent className="p-5 text-center space-y-3">
                  <div className="inline-flex p-3 rounded-xl bg-purple-100 dark:bg-purple-900/30 group-hover:scale-110 transition-transform">
                    <Activity className="w-7 h-7 text-purple-600" />
                  </div>
                  <h3 className="font-bold text-lg">AI Advisor</h3>
                  <p className="text-sm text-muted-foreground">Întreabă orice despre investiții, fiscalitate sau piața BVB</p>
                  <Badge className="bg-purple-500 text-white">AI</Badge>
                </CardContent>
              </Card>
            </Link>

            {/* Piețe Globale */}
            <Link to="/global">
              <Card className="h-full hover:shadow-lg transition-all border-2 hover:border-cyan-400 cursor-pointer group">
                <CardContent className="p-5 text-center space-y-3">
                  <div className="inline-flex p-3 rounded-xl bg-cyan-100 dark:bg-cyan-900/30 group-hover:scale-110 transition-transform">
                    <Globe className="w-7 h-7 text-cyan-600" />
                  </div>
                  <h3 className="font-bold text-lg">Piețe Globale</h3>
                  <p className="text-sm text-muted-foreground">S&P 500, NASDAQ, DAX, FTSE și alți indici cu delay 1 secundă</p>
                  <Badge className="bg-cyan-500 text-white">1s Delay</Badge>
                </CardContent>
              </Card>
            </Link>
          </div>

          {/* Quick links to other features */}
          <div className="flex flex-wrap justify-center gap-3 mt-6">
            <Link to="/calendar"><Badge variant="outline" className="cursor-pointer hover:bg-muted py-1.5 px-3">Calendar Dividende</Badge></Link>
            <Link to="/converter"><Badge variant="outline" className="cursor-pointer hover:bg-muted py-1.5 px-3">Convertor Valutar</Badge></Link>
            <Link to="/portfolio-bvb"><Badge variant="outline" className="cursor-pointer hover:bg-muted py-1.5 px-3">Portofoliu BVB</Badge></Link>
            <Link to="/calculator-fiscal"><Badge variant="outline" className="cursor-pointer hover:bg-muted py-1.5 px-3">Calculator Fiscal</Badge></Link>
            <Link to="/financial-education"><Badge variant="outline" className="cursor-pointer hover:bg-muted py-1.5 px-3">Educație Financiară</Badge></Link>
          </div>
        </section>

        {/* ====== SECTION 4: NEWS ====== */}
        <section>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Newspaper className="w-6 h-6 text-blue-600" />
              Știri Financiare
            </h2>
            <Link to="/news">
              <Button variant="ghost" size="sm">
                Vezi toate <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {/* Romanian News */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 pb-2 border-b">
                <span className="text-lg">&#x1F1F7;&#x1F1F4;</span>
                <h3 className="font-semibold text-sm">BVB & România</h3>
                <Badge variant="secondary" className="text-xs">{news.length}</Badge>
              </div>
              {news.slice(0, 6).map(article => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>

            {/* International News */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 pb-2 border-b">
                <span className="text-lg">&#x1F30D;</span>
                <h3 className="font-semibold text-sm">Internațional</h3>
                <Badge variant="secondary" className="text-xs">{intlNews.length}</Badge>
              </div>
              {intlNews.slice(0, 6).map(article => (
                <NewsCard key={article.id} article={article} isInternational />
              ))}
            </div>
          </div>
        </section>

        {/* ====== SECTION 5: EDUCATION + PRO CTA ====== */}
        <section>
          <div className="grid md:grid-cols-2 gap-6">
            {/* Trading School CTA */}
            <Link to="/trading-school">
              <Card className="h-full bg-gradient-to-br from-zinc-700 via-zinc-800 to-zinc-900 text-white border-0 hover:shadow-2xl transition-all cursor-pointer">
                <CardContent className="p-8 flex flex-col justify-center h-full">
                  <div className="inline-block p-3 bg-white/10 rounded-full w-fit mb-4">
                    <GraduationCap className="w-8 h-8" />
                  </div>
                  <h3 className="text-2xl font-bold mb-2">Școala de Trading</h3>
                  <p className="text-slate-300 mb-2">
                    17 lecții structurate de la bazele pieței de capital la strategii avansate, cu quiz-uri de verificare.
                  </p>
                  <p className="text-sm text-slate-400">
                    Gratuit &middot; În română &middot; La ritmul tău
                  </p>
                </CardContent>
              </Card>
            </Link>

            {/* PRO CTA or additional feature */}
            {(!user?.subscription_level || user?.subscription_level === 'free') ? (
              <Link to="/incearca-pro">
                <Card className="h-full bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 text-white hover:shadow-2xl transition-all cursor-pointer border-0">
                  <CardContent className="p-8 flex flex-col items-center justify-center h-full text-center">
                    <Crown className="w-14 h-14 mb-4" />
                    <h3 className="text-2xl font-bold mb-2">FinRomania PRO</h3>
                    <p className="text-white/90 mb-4">
                      AI Advisor nelimitat, Analiză Tehnică AI, Calculator Fiscal avansat, Screener PRO și mai mult.
                    </p>
                    <Badge className="bg-white/20 text-white text-base px-4 py-2">
                      Vezi Diferențele FREE vs PRO
                    </Badge>
                  </CardContent>
                </Card>
              </Link>
            ) : (
              <Link to="/financial-education">
                <Card className="h-full bg-gradient-to-br from-green-600 to-emerald-700 text-white border-0 hover:shadow-2xl transition-all cursor-pointer">
                  <CardContent className="p-8 flex flex-col justify-center h-full">
                    <div className="inline-block p-3 bg-white/10 rounded-full w-fit mb-4">
                      <TrendingUp className="w-8 h-8" />
                    </div>
                    <h3 className="text-2xl font-bold mb-2">Educație Financiară</h3>
                    <p className="text-white/90">
                      Bugete, economii, pensii, investiții — fundația oricărei decizii financiare solide.
                    </p>
                  </CardContent>
                </Card>
              </Link>
            )}
          </div>
        </section>

        {/* ====== SECTION 6: FINAL CTA ====== */}
        <section>
          <Card className="bg-gradient-to-br from-zinc-800 to-zinc-900 text-white border-0 max-w-4xl mx-auto">
            <CardContent className="p-8 text-center space-y-4">
              <h2 className="text-2xl md:text-3xl font-bold">
                Claritate într-un domeniu haotic.
              </h2>
              <p className="text-base text-slate-300 max-w-2xl mx-auto">
                FinRomania nu îți promite îmbogățire rapidă. Îți oferă instrumentele și cunoștințele
                necesare pentru a lua decizii informate — fie că ești la început sau ai experiență.
              </p>
              <div className="flex gap-4 justify-center flex-wrap pt-2">
                <Link to="/trading-school/lesson_1">
                  <Button size="lg" className="bg-blue-600 hover:bg-blue-700">
                    Începe cu Bazele
                  </Button>
                </Link>
                <Link to="/stocks">
                  <Button size="lg" variant="outline" className="border-slate-500 text-white hover:bg-zinc-700">
                    Explorează Piața <ArrowRight className="w-4 h-4 ml-2" />
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
