import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, XCircle, Clock, Trophy, Lock, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const getLevelInfo = (t) => ({
  intermediate: {
    name: t('education.levelIntermediate'),
    description: t('education.descIntermediate'),
    color: 'blue',
    unlocks: [
      t('education.unlockTechIndicators'),
      t('education.unlockAllBVB'),
      t('education.unlockAdvancedAI'),
      t('education.unlockDiversifiedPortfolio')
    ]
  },
  advanced: {
    name: t('education.levelAdvanced'),
    description: t('education.descAdvanced'),
    color: 'blue',
    unlocks: [
      t('education.unlockFundamentalAnalysis'),
      t('education.unlockAICharts'),
      t('education.unlockTaxCalc'),
      t('education.unlockAllMarkets')
    ]
  }
});

export default function QuizPage() {
  const { t } = useTranslation();
  const { level } = useParams();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  
  const [quizData, setQuizData] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(15 * 60); // 15 minutes

  useEffect(() => {
    if (!user || !token) {
      navigate('/login');
      return;
    }
    fetchQuiz();
  }, [user, token, level]);

  useEffect(() => {
    if (!submitted && quizData && timeLeft > 0) {
      const timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [submitted, quizData, timeLeft]);

  const fetchQuiz = async () => {
    try {
      const response = await fetch(`${API_URL}/api/quiz/${level}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      
      if (data.skip_quiz) {
        // PRO user - redirect
        navigate('/profile?tab=subscription');
        return;
      }
      
      if (data.already_unlocked) {
        navigate('/profile?tab=experience');
        return;
      }
      
      setQuizData(data);
    } catch (error) {
      console.error('Error fetching quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (questionId, answerIndex) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answerIndex
    }));
  };

  const handleSubmit = async () => {
    if (submitting) return;
    setSubmitting(true);

    try {
      const response = await fetch(`${API_URL}/api/quiz/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          level: level,
          answers: answers
        })
      });

      const data = await response.json();
      setResults(data);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <Card>
          <CardContent className="p-8 text-center">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-500" />
            <p>{t('education.loadingQuiz')}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <Card>
          <CardContent className="p-8 text-center">
            <Lock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">{t('education.authRequired')}</h2>
            <p className="text-gray-500 mb-4">{t('education.loginForQuiz')}</p>
            <Button onClick={() => navigate('/login')}>{t('education.loginButton')}</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const levelInfo = getLevelInfo(t)[level];
  
  if (!levelInfo) {
    return (
      <div className="max-w-4xl mx-auto p-4">
        <Card>
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">{t('education.invalidLevel')}</h2>
            <Button onClick={() => navigate('/')}>{t('education.backHome')}</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Results screen
  if (submitted && results) {
    return (
      <div className="max-w-4xl mx-auto p-4 space-y-6">
        <Card className={results.passed ? 'border-green-500 bg-green-500/5' : 'border-red-500 bg-red-500/5'}>
          <CardContent className="p-8 text-center">
            {results.passed ? (
              <>
                <Trophy className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-green-600 mb-2">{t('education.congratulations')} 🎉</h2>
                <p className="text-lg mb-4">{results.message}</p>
                <Badge className="bg-green-500 text-white text-lg px-4 py-2">
                  {results.score}/{results.total} {t('education.correctAnswers')}
                </Badge>
              </>
            ) : (
              <>
                <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-red-600 mb-2">{t('education.tryAgain')}</h2>
                <p className="text-lg mb-4">{results.message}</p>
                <Badge variant="destructive" className="text-lg px-4 py-2">
                  {results.score}/{results.total} {t('education.correctAnswers')}
                </Badge>
              </>
            )}
          </CardContent>
        </Card>

        {/* Unlocked features */}
        {results.passed && results.next_steps?.features_unlocked?.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                {t('education.featuresUnlocked')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {results.next_steps.features_unlocked.map((feature, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-green-500" />
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Detailed results */}
        <Card>
          <CardHeader>
            <CardTitle>{t('education.yourAnswers')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {results.results?.map((r, idx) => (
              <div 
                key={idx} 
                className={`p-4 rounded-lg border ${r.is_correct ? 'bg-green-500/10 border-green-500/30' : 'bg-red-500/10 border-red-500/30'}`}
              >
                <div className="flex items-start gap-2">
                  {r.is_correct ? (
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500 mt-0.5" />
                  )}
                  <div>
                    <p className="font-medium">{r.question}</p>
                    {!r.is_correct && (
                      <p className="text-sm text-gray-500 mt-1">
                        <span className="text-red-500">{t('education.yourAnswer')}</span> vs <span className="text-green-500">{t('education.correctAnswer')}</span>
                      </p>
                    )}
                    <p className="text-sm text-blue-600 mt-2 italic">{r.explanation}</p>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Action buttons */}
        <div className="flex gap-4 justify-center">
          {!results.passed && (
            <Button onClick={() => window.location.reload()}>
              <RefreshCw className="w-4 h-4 mr-2" />
              {t('education.retryQuiz')}
            </Button>
          )}
          <Button variant="outline" onClick={() => navigate('/')}>
            {t('education.backHome')}
          </Button>
        </div>
      </div>
    );
  }

  // Quiz screen
  const question = quizData?.questions?.[currentQuestion];
  const progress = ((currentQuestion + 1) / (quizData?.total_questions || 1)) * 100;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <SEO title="Quiz | Trading School | FinRomania" description="Test your trading knowledge with interactive quizzes after each lesson." />
      {/* Header */}
      <Card className="bg-gradient-to-r from-blue-700 to-blue-500 text-white">
        <CardContent className="p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">{t('education.quizLevel', { level: levelInfo.name })}</h1>
              <p className="text-blue-100">{quizData?.instructions}</p>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-mono font-bold ${timeLeft < 60 ? 'text-red-300 animate-pulse' : ''}`}>
                <Clock className="w-5 h-5 inline mr-1" />
                {formatTime(timeLeft)}
              </div>
              <p className="text-sm text-blue-200">{t('education.timeRemaining')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>{t('education.questionOf', { current: currentQuestion + 1, total: quizData?.total_questions })}</span>
          <span>{t('education.answersGiven', { count: answeredCount })}</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Question */}
      {question && (
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold mb-6">{question.question}</h2>
            
            <div className="space-y-3">
              {question.options.map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => handleAnswer(question.id, idx)}
                  className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                    answers[question.id] === idx
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <span className="font-medium mr-2">{String.fromCharCode(65 + idx)}.</span>
                  {option}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
          disabled={currentQuestion === 0}
        >
          {t('education.previous')}
        </Button>
        
        <div className="flex gap-2">
          {/* Question dots */}
          {quizData?.questions?.map((q, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentQuestion(idx)}
              className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                idx === currentQuestion
                  ? 'bg-blue-500 text-white'
                  : answers[q.id] !== undefined
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 dark:bg-gray-700'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>
        
        {currentQuestion < (quizData?.total_questions || 0) - 1 ? (
          <Button
            onClick={() => setCurrentQuestion(prev => prev + 1)}
          >
            {t('education.nextQuestion')}
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={submitting || answeredCount < quizData?.total_questions}
            className="bg-green-600 hover:bg-green-700"
          >
            {submitting ? (
              <RefreshCw className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <CheckCircle className="w-4 h-4 mr-2" />
            )}
            {t('education.finishQuiz')}
          </Button>
        )}
      </div>

      {/* Warning if not all answered */}
      {answeredCount < (quizData?.total_questions || 0) && (
        <p className="text-center text-amber-500 text-sm">
          <AlertCircle className="w-4 h-4 inline mr-1" />
          {t('education.unansweredWarning', { count: (quizData?.total_questions || 0) - answeredCount })}
        </p>
      )}
    </div>
  );
}
