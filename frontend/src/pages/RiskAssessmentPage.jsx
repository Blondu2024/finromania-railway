import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ClipboardCheck, ArrowRight, ArrowLeft, CheckCircle, Shield, TrendingUp, Zap, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function RiskAssessmentPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [existingProfile, setExistingProfile] = useState(null);

  useEffect(() => {
    fetchQuestions();
    if (user) fetchExistingProfile();
  }, [user]);

  const fetchQuestions = async () => {
    try {
      const res = await fetch(`${API_URL}/api/risk-assessment/questions`);
      if (res.ok) {
        const data = await res.json();
        setQuestions(data.questions || []);
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchExistingProfile = async () => {
    try {
      const res = await fetch(`${API_URL}/api/risk-assessment/my-profile`, {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        if (data.has_profile) {
          setExistingProfile(data);
        }
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }));
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    if (!user) {
      login();
      return;
    }

    setSubmitting(true);
    try {
      const formattedAnswers = Object.entries(answers).map(([question_id, answer_value]) => ({
        question_id,
        answer_value
      }));

      const res = await fetch(`${API_URL}/api/risk-assessment/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ answers: formattedAnswers })
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const ProfileIcon = ({ profileKey }) => {
    switch (profileKey) {
      case 'conservative': return <Shield className="w-12 h-12" />;
      case 'moderate': return <TrendingUp className="w-12 h-12" />;
      case 'aggressive': return <Zap className="w-12 h-12" />;
      default: return <ClipboardCheck className="w-12 h-12" />;
    }
  };

  // Show existing profile
  if (existingProfile && !result) {
    const profile = existingProfile.profile;
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">Profilul Tău de Risc</h1>
          <p className="text-muted-foreground">Evaluat pe {new Date(existingProfile.assessed_at).toLocaleDateString('ro-RO')}</p>
        </div>

        <Card className="overflow-hidden">
          <div className="p-8 text-center" style={{ backgroundColor: `${profile.color}20` }}>
            <div className="inline-flex p-4 rounded-full mb-4" style={{ backgroundColor: profile.color, color: 'white' }}>
              <ProfileIcon profileKey={profile.key} />
            </div>
            <h2 className="text-3xl font-bold" style={{ color: profile.color }}>{profile.name}</h2>
            <p className="text-muted-foreground mt-2 max-w-md mx-auto">{profile.description}</p>
            <p className="mt-4 text-sm">Scor: {existingProfile.score}/{existingProfile.max_score}</p>
          </div>
          
          <CardContent className="p-6">
            <h3 className="font-semibold mb-3">Alocare Recomandată:</h3>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{profile.allocation.stocks}%</p>
                <p className="text-sm text-muted-foreground">Acțiuni</p>
              </div>
              <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{profile.allocation.bonds}%</p>
                <p className="text-sm text-muted-foreground">Obligațiuni</p>
              </div>
              <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-2xl font-bold text-yellow-600">{profile.allocation.cash}%</p>
                <p className="text-sm text-muted-foreground">Cash</p>
              </div>
            </div>

            <div className="space-y-4">
              <Button className="w-full" onClick={() => navigate('/portfolio')}>
                Mergi la Portofoliu
              </Button>
              <Button variant="outline" className="w-full" onClick={() => setExistingProfile(null)}>
                Refă Evaluarea
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show result
  if (result) {
    const profile = result.profile;
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center">
          <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold">Evaluare Completă!</h1>
        </div>

        <Card className="overflow-hidden">
          <div className="p-8 text-center" style={{ backgroundColor: `${profile.color}20` }}>
            <div className="inline-flex p-4 rounded-full mb-4" style={{ backgroundColor: profile.color, color: 'white' }}>
              <ProfileIcon profileKey={profile.key} />
            </div>
            <h2 className="text-3xl font-bold" style={{ color: profile.color }}>Ești {profile.name}</h2>
            <p className="text-muted-foreground mt-2 max-w-md mx-auto">{profile.description}</p>
            <p className="mt-4 text-sm">Scor: {result.score}/{result.max_score}</p>
          </div>
          
          <CardContent className="p-6">
            <h3 className="font-semibold mb-3">Alocare Recomandată:</h3>
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{profile.allocation.stocks}%</p>
                <p className="text-sm text-muted-foreground">Acțiuni</p>
              </div>
              <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{profile.allocation.bonds}%</p>
                <p className="text-sm text-muted-foreground">Obligațiuni</p>
              </div>
              <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                <p className="text-2xl font-bold text-yellow-600">{profile.allocation.cash}%</p>
                <p className="text-sm text-muted-foreground">Cash</p>
              </div>
            </div>

            <h3 className="font-semibold mb-3">Recomandări:</h3>
            <ul className="space-y-2 mb-6">
              {profile.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>

            <div className="space-y-3">
              <Button className="w-full" onClick={() => navigate('/portfolio')}>
                Creează-ți Portofoliul
              </Button>
              <Button variant="outline" className="w-full" onClick={() => navigate('/education')}>
                Continuă să Înveți
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show questionnaire
  if (loading || questions.length === 0) {
    return <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin" /></div>;
  }

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;
  const canSubmit = Object.keys(answers).length === questions.length;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <ClipboardCheck className="w-12 h-12 text-blue-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold">Evaluează-ți Profilul de Risc</h1>
        <p className="text-muted-foreground mt-2">
          Răspunde la {questions.length} întrebări pentru a descoperi ce tip de investitor ești
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-muted-foreground">
              Întrebarea {currentQuestion + 1} din {questions.length}
            </span>
            <span className="text-sm font-medium">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </CardHeader>
        <CardContent className="space-y-6">
          <h2 className="text-xl font-semibold">{currentQ.question}</h2>
          
          <RadioGroup
            value={answers[currentQ.id] || ''}
            onValueChange={(value) => handleAnswer(currentQ.id, value)}
          >
            {currentQ.options.map((option) => (
              <div key={option.value} className="flex items-center space-x-3 p-3 rounded-lg border hover:bg-muted/50 cursor-pointer">
                <RadioGroupItem value={option.value} id={option.value} />
                <Label htmlFor={option.value} className="flex-1 cursor-pointer">
                  {option.label}
                </Label>
              </div>
            ))}
          </RadioGroup>

          <div className="flex justify-between pt-4">
            <Button 
              variant="outline" 
              onClick={handlePrev}
              disabled={currentQuestion === 0}
            >
              <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
            </Button>
            
            {currentQuestion === questions.length - 1 ? (
              <Button 
                onClick={handleSubmit}
                disabled={!canSubmit || submitting}
              >
                {submitting ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Se procesează...</>
                ) : (
                  <>Finalizează <CheckCircle className="w-4 h-4 ml-2" /></>
                )}
              </Button>
            ) : (
              <Button 
                onClick={handleNext}
                disabled={!answers[currentQ.id]}
              >
                Următoarea <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {!user && (
        <p className="text-center text-sm text-muted-foreground">
          Vei fi rugat să te autentifici pentru a salva rezultatul.
        </p>
      )}
    </div>
  );
}
