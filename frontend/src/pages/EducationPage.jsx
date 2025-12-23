import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { BookOpen, CheckCircle, Lock, Play, FileText, Award, Loader2, ShoppingCart, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function EducationPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [packageInfo, setPackageInfo] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [hasAccess, setHasAccess] = useState(false);
  const [loading, setLoading] = useState(true);
  const [purchasing, setPurchasing] = useState(false);
  const [checkingPayment, setCheckingPayment] = useState(false);

  useEffect(() => {
    fetchData();
    
    // Check for payment success
    const sessionId = searchParams.get('session_id');
    if (sessionId) {
      checkPaymentStatus(sessionId);
    }
  }, [searchParams]);

  const fetchData = async () => {
    try {
      const [pkgRes, lessonsRes] = await Promise.all([
        fetch(`${API_URL}/api/education/package`),
        fetch(`${API_URL}/api/education/lessons`, { credentials: 'include' })
      ]);
      
      if (pkgRes.ok) setPackageInfo(await pkgRes.json());
      if (lessonsRes.ok) {
        const data = await lessonsRes.json();
        setLessons(data.lessons || []);
        setHasAccess(data.has_access);
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
      // Poll for payment status
      for (let i = 0; i < 5; i++) {
        const res = await fetch(`${API_URL}/api/education/checkout/status/${sessionId}`, {
          credentials: 'include'
        });
        
        if (res.ok) {
          const data = await res.json();
          if (data.access_granted) {
            setHasAccess(true);
            // Remove session_id from URL
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

  const handlePurchase = async () => {
    if (!user) {
      login();
      return;
    }
    
    setPurchasing(true);
    try {
      const res = await fetch(`${API_URL}/api/education/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ origin_url: window.location.origin })
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
      setPurchasing(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-64" />
        <Skeleton className="h-48" />
        <div className="grid md:grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-32" />)}
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
          Învață bazele investițiilor de la zero. Pachet complet pentru începători.
        </p>
      </div>

      {/* Success Message */}
      {hasAccess && (
        <Card className="bg-green-50 dark:bg-green-900/20 border-green-200">
          <CardContent className="p-4 flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-green-600" />
            <div>
              <p className="font-semibold text-green-800 dark:text-green-200">
                Ai acces complet la toate lecțiile!
              </p>
              <p className="text-sm text-green-700 dark:text-green-300">
                Mulțumim pentru achiziție. Începe să înveți acum.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Package Info - Show if no access */}
      {!hasAccess && packageInfo && (
        <Card className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white overflow-hidden">
          <CardContent className="p-8">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <Badge className="bg-yellow-400 text-yellow-900 mb-4">Pachet Complet</Badge>
                <h2 className="text-3xl font-bold mb-4">{packageInfo.name}</h2>
                <ul className="space-y-3">
                  {packageInfo.includes?.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="text-center">
                <div className="mb-4">
                  <span className="text-6xl font-bold">{packageInfo.price}</span>
                  <span className="text-2xl ml-1">RON</span>
                </div>
                <p className="text-blue-100 mb-6">Plată unică - Acces permanent</p>
                <Button 
                  size="lg" 
                  variant="secondary" 
                  className="w-full max-w-xs text-lg"
                  onClick={handlePurchase}
                  disabled={purchasing}
                >
                  {purchasing ? (
                    <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Se procesează...</>
                  ) : (
                    <><ShoppingCart className="w-5 h-5 mr-2" /> Cumpără Acum</>
                  )}
                </Button>
                {!user && (
                  <p className="text-sm text-blue-200 mt-3">
                    Trebuie să fii autentificat pentru a cumpăra
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
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
                      : 'bg-blue-100 text-blue-600'
                  }`}>
                    {lesson.is_locked ? <Lock className="w-5 h-5" /> : idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{lesson.title}</h3>
                      {lesson.is_free && (
                        <Badge variant="secondary" className="text-xs">GRATUIT</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{lesson.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      \u23f1 {lesson.duration}
                    </p>
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

      {/* E-Book Section */}
      {hasAccess && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-green-600" />
              E-Book: Ghidul Începătorului
            </CardTitle>
            <CardDescription>
              Descarcă ghidul complet în format PDF
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button disabled>
              <FileText className="w-4 h-4 mr-2" />
              Descărcare PDF (în curând)
            </Button>
          </CardContent>
        </Card>
      )}

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
              <h4 className="font-semibold mb-2">\ud83c\udfaf Conținut Practic</h4>
              <p className="text-sm text-muted-foreground">
                Nu teorie abstractă, ci exemple reale și strategii pe care le poți aplica imediat.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">\ud83c\uddf7\ud83c\uddf4 Adaptat României</h4>
              <p className="text-sm text-muted-foreground">
                Conținut specific pentru investitorii români, cu exemple de pe BVB.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-2">\ud83d\ude80 Fără Cunostințe Prealabile</h4>
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
