import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BookOpen, CheckCircle, Lock, Play, FileText, Award, Loader2, ShoppingCart, Sparkles, Crown, Star } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function EducationPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [packages, setPackages] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [hasStarter, setHasStarter] = useState(false);
  const [hasPremium, setHasPremium] = useState(false);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(null);
  const [checkingPayment, setCheckingPayment] = useState(false);

  useEffect(() => {
    fetchData();
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [searchParams]);

  const fetchData = async () => {
    try {
      const [pkgRes, lessonsRes] = await Promise.all([
        fetch(`${API_URL}/api/education/packages`),
      ]);
      
      if (pkgRes.ok) {
        const data = await pkgRes.json();
        setPackages(data.packages || []);
      }
      if (lessonsRes.ok) {
        const data = await lessonsRes.json();
        setLessons(data.lessons || []);
        setHasStarter(data.has_starter);
        setHasPremium(data.has_premium);
      }
    } catch (error) {
      console.error('Error fetching education data:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkPaymentStatus = async (sessionId) => {
    setCheckingPayment(true);
    try {
      for (let i = 0; i < 5; i++) {
        const res = await fetch(`${API_URL}/api/education/checkout/status/${sessionId}`, {
        });
        
        if (res.ok) {
          const data = await res.json();
          if (data.access_granted) {
            window.history.replaceState({}, '', '/education');
            fetchData();
            break;
          }
        }
        await new Promise(r => setTimeout(r, 2000));
      }
    } catch (error) {
      console.error('Payment check error:', error);
    } finally {
      setCheckingPayment(false);
    }
  };

  const handlePurchase = async (packageId) => {
    if (!user) {
      login();
      return;
    }
    
    setPurchasing(packageId);
    try {
      const res = await fetch(`${API_URL}/api/education/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          origin_url: window.location.origin,
          package_id: packageId 
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        window.location.href = data.url;
      } else {
        const error = await res.json();
        alert(error.detail || 'Eroare la procesarea plății');
      }
    } catch (error) {
      console.error('Purchase error:', error);
      alert('Eroare la conectarea cu serviciul de plăți');
    } finally {
      setPurchasing(null);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64 mx-auto" />
        <div className="grid md:grid-cols-2 gap-4">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
        </div>
      </div>
    );
  }

  if (checkingPayment) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
          <h2 className="text-xl font-semibold">Se verifică plata...</h2>
          <p className="text-muted-foreground">Te rugăm să aștepți</p>
        </div>
      </div>
    );
  }

  const starterPkg = packages.find(p => p.id === 'edu_starter_pack');
  const premiumPkg = packages.find(p => p.id === 'edu_premium_pack');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <BookOpen className="w-10 h-10 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mb-4">Academie Investiții</h1>
        <p className="text-lg text-muted-foreground">
          Învață bazele investițiilor de la zero. Cursuri complete pentru începători.
        </p>
      </div>

      {/* Success Messages */}
      {(hasStarter || hasPremium) && (
        <Card className="bg-green-50 dark:bg-green-900/20 border-green-200">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-semibold text-green-800 dark:text-green-200">
                {hasPremium ? 'Ai acces Premium complet!' : 'Ai acces la pachetul Starter!'}
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">
                {hasPremium ? 'Toate cele 12 lecții sunt deblocate.' : '6 lecții de bază sunt deblocate.'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Packages */}
      {!hasPremium && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Starter Package */}
          {starterPkg && !hasStarter && (
            <Card className="bg-gradient-to-br from-blue-500 to-blue-700 text-white overflow-hidden relative">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
              <CardContent className="p-6 relative">
                <Badge className="bg-white/20 text-white mb-3">Pachet Starter</Badge>
                <h2 className="text-2xl font-bold mb-4">{starterPkg.name}</h2>
                <ul className="space-y-2 mb-6">
                  {starterPkg.features?.map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <div className="flex items-end justify-between">
                  <div>
                    <span className="text-4xl font-bold">{starterPkg.price}</span>
                    <span className="text-xl ml-1">RON</span>
                    <p className="text-blue-100 text-sm">Plată unică</p>
                  </div>
                  <Button 
                    variant="secondary" 
                    onClick={() => handlePurchase('starter')}
                    disabled={purchasing === 'starter'}
                  >
                    {purchasing === 'starter' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <ShoppingCart className="w-4 h-4 mr-2" />
                        Cumpără
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Premium Package */}
          {premiumPkg && (
            <Card className="bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800 text-white overflow-hidden relative">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16" />
              <div className="absolute top-4 right-4">
                <Crown className="w-8 h-8 text-yellow-300" />
              </div>
              <CardContent className="p-6 relative">
                <Badge className="bg-yellow-400 text-yellow-900 mb-3">
                  <Star className="w-3 h-3 mr-1" /> Recomandat
                </Badge>
                <h2 className="text-2xl font-bold mb-4">{premiumPkg.name}</h2>
                <ul className="space-y-2 mb-6">
                  {premiumPkg.features?.map((f, i) => (
                    <li key={i} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 flex-shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <div className="flex items-end justify-between">
                  <div>
                    <span className="text-4xl font-bold">{premiumPkg.price}</span>
                    <span className="text-xl ml-1">RON</span>
                    <p className="text-purple-200 text-sm">Acces complet permanent</p>
                  </div>
                  <Button 
                    className="bg-yellow-400 text-yellow-900 hover:bg-yellow-300"
                    onClick={() => handlePurchase('premium')}
                    disabled={purchasing === 'premium'}
                  >
                    {purchasing === 'premium' ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>
                        <Crown className="w-4 h-4 mr-2" />
                        Cumpără Premium
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {!user && (
        <p className="text-center text-sm text-muted-foreground">
          Trebuie să fii autentificat pentru a cumpăra. <button onClick={login} className="text-blue-600 underline">Conectează-te</button>
        </p>
      )}

      {/* Lessons */}
      <div>
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Play className="w-6 h-6 text-blue-600" />
          Conținut Curs ({lessons.length} lecții)
        </h2>
        
        <div className="grid gap-4">
          {lessons.map((lesson, idx) => (
            <Card 
              key={lesson.id} 
              className={`transition-all ${lesson.is_locked ? 'opacity-75' : 'hover:shadow-md cursor-pointer'}`}
              onClick={() => !lesson.is_locked && navigate(`/education/lesson/${lesson.id}`)}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold ${
                    lesson.is_locked 
                      ? 'bg-gray-100 text-gray-400' 
                      : lesson.tier === 'premium' 
                        ? 'bg-purple-100 text-purple-600'
                        : 'bg-blue-100 text-blue-600'
                  }`}>
                    {lesson.is_locked ? <Lock className="w-5 h-5" /> : idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-semibold">{lesson.title}</h3>
                      {lesson.is_free && (
                        <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">GRATUIT</Badge>
                      )}
                      {lesson.tier === 'premium' && !lesson.is_free && (
                        <Badge className="text-xs bg-purple-100 text-purple-700">
                          <Crown className="w-3 h-3 mr-1" /> Premium
                        </Badge>
                      )}
                      {lesson.has_quiz && (
                        <Badge variant="outline" className="text-xs">Quiz</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{lesson.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">⏱ {lesson.duration}</p>
                  </div>
                  {lesson.is_locked ? (
                    <Lock className="w-5 h-5 text-muted-foreground" />
                  ) : (
                    <Play className="w-5 h-5 text-blue-600" />
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Glossary Link */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-green-600" />
            Glosar de Termeni
          </CardTitle>
          <CardDescription>
            100+ termeni financiari explicați simplu
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button variant="outline" onClick={() => navigate('/education/glossary')}>
            Vezi Glosarul
          </Button>
        </CardContent>
      </Card>

      {/* Why Learn */}
      <Card className="bg-muted/30">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-yellow-500" />
            De ce să înveți cu noi?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-semibold mb-2">🎯 Conținut Practic</h4>
              <p className="text-sm text-muted-foreground">
                Exemple reale și strategii aplicabile imediat.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">🇷🇴 Adaptat României</h4>
              <p className="text-sm text-muted-foreground">
                Conținut specific pentru investitorii români, cu exemple de pe BVB.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">🚀 Fără Cunoștințe Prealabile</h4>
              <p className="text-sm text-muted-foreground">
                Poți începe de la zero. Explicăm totul pas cu pas.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
