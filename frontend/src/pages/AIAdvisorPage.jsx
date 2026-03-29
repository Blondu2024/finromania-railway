import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bot, Send, Lightbulb, TrendingUp, MessageCircle, Loader2, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AIAdvisorPage() {
  const { user, login } = useAuth();
  const [tipOfDay, setTipOfDay] = useState(null);
  const [portfolioAdvice, setPortfolioAdvice] = useState(null);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState({ tip: true, advice: false, ask: false });

  useEffect(() => {
    fetchTipOfDay();
    if (user) fetchPortfolioAdvice();
  }, [user]);

  const fetchTipOfDay = async () => {
    try {
      const res = await fetch(`${API_URL}/api/advisor/tip-of-the-day`);
      if (res.ok) setTipOfDay(await res.json());
    } catch (error) {
      console.error('Error fetching tip:', error);
    } finally {
      setLoading(prev => ({ ...prev, tip: false }));
    }
  };

  const fetchPortfolioAdvice = async () => {
    setLoading(prev => ({ ...prev, advice: true }));
    try {
      const res = await fetch(`${API_URL}/api/advisor/portfolio-advice`, {
      });
      if (res.ok) setPortfolioAdvice(await res.json());
    } catch (error) {
      console.error('Error fetching advice:', error);
    } finally {
      setLoading(prev => ({ ...prev, advice: false }));
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    if (!user) {
      login();
      return;
    }

    setLoading(prev => ({ ...prev, ask: true }));
    setAnswer(null);
    
    try {
      const res = await fetch(`${API_URL}/api/advisor/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      
      if (res.ok) {
        setAnswer(await res.json());
      }
    } catch (error) {
      console.error('Error asking:', error);
    } finally {
      setLoading(prev => ({ ...prev, ask: false }));
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="flex justify-center mb-4">
          <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <Bot className="w-10 h-10 text-blue-600" />
          </div>
        </div>
        <h1 className="text-4xl font-bold mb-4">Consilier AI</h1>
        <p className="text-lg text-muted-foreground">
          Primește sfaturi și educație financiară personalizată
        </p>
      </div>

      {/* Tip of the Day */}
      {tipOfDay && (
        <Card className="bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-200">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="p-2 bg-yellow-100 dark:bg-yellow-800 rounded-full">
                <Lightbulb className="w-6 h-6 text-yellow-600" />
              </div>
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-semibold">Sfatul Zilei</h3>
                  <Badge variant="outline">{tipOfDay.category}</Badge>
                </div>
                <p className="text-muted-foreground">{tipOfDay.tip}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Portfolio Advice */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-600" />
              Sfaturi pentru Portofoliu
            </CardTitle>
            <CardDescription>
              Recomandări bazate pe profilul tău de risc
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!user ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground mb-4">Conectează-te pentru sfaturi personalizate</p>
                <Button onClick={login}>Conectare</Button>
              </div>
            ) : loading.advice ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            ) : portfolioAdvice?.needs_assessment ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground mb-4">{portfolioAdvice.advice}</p>
                <Link to="/risk-assessment">
                  <Button>Completează Chestionarul</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge className={
                    portfolioAdvice?.profile === 'conservative' ? 'bg-blue-500 text-white' :
                    portfolioAdvice?.profile === 'moderate' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                  }>
                    Profil: {portfolioAdvice?.profile === 'conservative' ? 'Conservator' :
                             portfolioAdvice?.profile === 'moderate' ? 'Moderat' : 'Agresiv'}
                  </Badge>
                  <Badge variant="outline">{portfolioAdvice?.holdings_count || 0} dețineri</Badge>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="whitespace-pre-wrap">{portfolioAdvice?.advice}</p>
                </div>
                <Button variant="outline" className="w-full" onClick={fetchPortfolioAdvice}>
                  <Sparkles className="w-4 h-4 mr-2" /> Regenerează Sfatul
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Ask Question */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-blue-600" />
              Întreabă Consilierul
            </CardTitle>
            <CardDescription>
              Pune orice întrebare despre investiții
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-2">
              <Input
                placeholder="Ex: Ce este DCA?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              />
              <Button onClick={handleAsk} disabled={loading.ask || !question.trim()}>
                {loading.ask ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </Button>
            </div>
            
            {answer && (
              <div className="p-4 bg-muted/50 rounded-lg">
                <p className="font-medium mb-2">Întrebare: {answer.question}</p>
                <p className="whitespace-pre-wrap text-muted-foreground">{answer.answer}</p>
                <p className="text-xs text-muted-foreground mt-3 italic">{answer.disclaimer}</p>
              </div>
            )}

            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground mb-3">Întrebări populare:</p>
              <div className="flex flex-wrap gap-2">
                {['Ce este un ETF?', 'Cum funcționează bursa?', 'Ce înseamnă diversificare?'].map((q) => (
                  <Button
                    key={q}
                    variant="outline"
                    size="sm"
                    onClick={() => { setQuestion(q); }}
                  >
                    {q}
                  </Button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="grid md:grid-cols-3 gap-4">
        <Link to="/risk-assessment">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full w-fit mx-auto mb-3">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold">Evaluare Risc</h3>
              <p className="text-sm text-muted-foreground">Descoperă-ți profilul de investitor</p>
            </CardContent>
          </Card>
        </Link>
        
        <Link to="/trading-school">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-green-100 dark:bg-green-900 rounded-full w-fit mx-auto mb-3">
                <Lightbulb className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold">Trading School</h3>
              <p className="text-sm text-muted-foreground">17 lecții gratuite - Învață de la zero</p>
            </CardContent>
          </Card>
        </Link>
        
        <Link to="/portfolio">
          <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
            <CardContent className="p-6 text-center">
              <div className="p-3 bg-blue-100 dark:bg-blue-900 rounded-full w-fit mx-auto mb-3">
                <Bot className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold">Portofoliu Virtual</h3>
              <p className="text-sm text-muted-foreground">Practică fără risc</p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Disclaimer */}
      <Card className="bg-muted/30">
        <CardContent className="p-4">
          <p className="text-sm text-muted-foreground text-center">
            \u26a0\ufe0f <strong>Disclaimer:</strong> Informațiile oferite sunt doar în scop educațional și nu constituie sfat de investiții. 
            Consultați un specialist financiar autorizat înainte de a lua decizii de investiții.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
