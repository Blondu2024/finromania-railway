import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ArrowLeft, CheckCircle, AlertCircle, Lightbulb, Trophy, ChevronRight } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import ReactMarkdown from 'react-markdown';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function LessonPage() {
  const { t } = useTranslation();
  const { lessonId } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [showQuiz, setShowQuiz] = useState(false);
  const [quizAnswers, setQuizAnswers] = useState([]);
  const [quizResult, setQuizResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLesson();
  }, [lessonId]);

  const fetchLesson = async () => {
    try {
      const res = await fetch(`${API_URL}/api/trading-school/lessons/${lessonId}`);
      if (res.ok) {
        const data = await res.json();
        setLesson(data);
        setQuizAnswers(new Array(data.quiz?.length || 0).fill(null));
      }
    } catch (error) {
      console.error('Error fetching lesson:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuizSubmit = async () => {
    if (!user) {
      alert(t('education.loginToSaveProgress'));
      return;
    }

    if (quizAnswers.includes(null)) {
      alert(t('education.answerAllQuestions'));
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/trading-school/quiz/submit`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          lesson_id: lessonId,
          answers: quizAnswers
        })
      });

      if (res.ok) {
        const result = await res.json();
        setQuizResult(result);
      } else {
        let errorMsg = t('education.quizSubmitError');
        try {
          const error = await res.json();
          errorMsg = error.detail || errorMsg;
        } catch {}
        if (res.status === 401) {
          errorMsg = t('education.sessionExpired');
        }
        alert(errorMsg);
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert(t('education.connectionError'));
    }
  };

  const handleRetry = () => {
    setQuizResult(null);
    setQuizAnswers(new Array(lesson.quiz?.length || 0).fill(null));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">{t('education.loadingLesson')}</p>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
        <h2 className="text-xl font-semibold">{t('education.lessonNotFound')}</h2>
        <Link to="/trading-school">
          <Button className="mt-4">{t('education.backToSchool')}</Button>
        </Link>
      </div>
    );
  }

  // Quiz Results Screen
  if (quizResult) {
    const passed = quizResult.passed;
    
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <Card className={`border-2 ${
          passed ? 'border-green-500 bg-green-50' : 'border-orange-500 bg-orange-50'
        }`}>
          <CardContent className="p-8 text-center">
            <div className={`inline-block p-4 rounded-full mb-4 ${
              passed ? 'bg-green-200' : 'bg-orange-200'
            }`}>
              {passed ? (
                <Trophy className="w-16 h-16 text-green-600" />
              ) : (
                <AlertCircle className="w-16 h-16 text-orange-600" />
              )}
            </div>
            
            <h2 className="text-3xl font-bold mb-2">
              {passed ? `🎉 ${t('education.congratulations')}` : `💪 ${t('education.almostThere')}`}
            </h2>
            <p className="text-xl mb-6">
              {t('education.scoreLabel')}: <span className="font-bold">{quizResult.score.toFixed(0)}%</span> ({quizResult.correct}/{quizResult.total} {t('education.correctLabel')})
            </p>
            
            {/* Results Detail */}
            <div className="text-left space-y-4 mb-8">
              {quizResult.results.map((result, idx) => (
                <Card key={idx} className={result.correct ? 'border-green-300' : 'border-red-300'}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-2 mb-2">
                      {result.correct ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                      ) : (
                        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className="font-medium">{result.question}</p>
                        <p className="text-sm text-muted-foreground mt-1">{t('education.answerLabel')}: {result.your_answer}</p>
                      </div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded mt-2">
                      <div className="flex items-start gap-2">
                        <Lightbulb className="w-4 h-4 text-blue-600 mt-0.5" />
                        <p className="text-sm text-blue-900">{result.explanation}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <div className="flex gap-3 justify-center">
              {!passed && (
                <Button onClick={handleRetry} size="lg">
                  🔄 {t('education.tryAgainBtn')}
                </Button>
              )}
              <Link to="/trading-school">
                <Button variant="outline" size="lg">
                  {passed ? `${t('education.continueNextLesson')} →` : t('education.backToSchool')}
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Quiz Screen
  if (showQuiz) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12">
        <Link to="/trading-school">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="w-4 h-4 mr-2" /> {t('education.backBtn')}
          </Button>
        </Link>

        <Card className="border-2 border-blue-500">
          <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-500 text-white">
            <CardTitle className="text-2xl">📝 Quiz: {lesson.title}</CardTitle>
          </CardHeader>
          <CardContent className="p-6 space-y-6">
            {lesson.quiz.map((q, qIdx) => (
              <Card key={qIdx}>
                <CardContent className="p-4">
                  <p className="font-semibold mb-4">{t('education.questionLabel')} {qIdx + 1}: {q.question}</p>
                  <div className="space-y-2">
                    {q.options.map((option, oIdx) => (
                      <div
                        key={oIdx}
                        className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                          quizAnswers[qIdx] === oIdx
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                        }`}
                        onClick={() => {
                          const newAnswers = [...quizAnswers];
                          newAnswers[qIdx] = oIdx;
                          setQuizAnswers(newAnswers);
                        }}
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            quizAnswers[qIdx] === oIdx
                              ? 'border-blue-500 bg-blue-500'
                              : 'border-gray-300'
                          }`}>
                            {quizAnswers[qIdx] === oIdx && (
                              <div className="w-2 h-2 bg-white rounded-full" />
                            )}
                          </div>
                          <span>{option}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setShowQuiz(false)} className="flex-1">
                {t('education.reviewLessonBtn')}
              </Button>
              <Button
                onClick={handleQuizSubmit}
                disabled={quizAnswers.includes(null)}
                className="flex-1"
                size="lg"
              >
                {t('education.submitAnswers')} →
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Lesson Content Screen
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <SEO title={lesson ? `${lesson.title} | Trading School | FinRomania` : 'Trading School | FinRomania'} description={lesson?.subtitle || 'Free trading lessons for Romanian investors'} />
      <Link to="/trading-school">
        <Button variant="ghost" className="mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('education.backToSchool')}
        </Button>
      </Link>

      <Card className="border-2 border-blue-200 shadow-xl">
        <CardHeader className="bg-gradient-to-r from-blue-700 to-blue-500 text-white p-8">
          <div className="flex items-center gap-4">
            <div className="text-6xl">{lesson.emoji}</div>
            <div className="flex-1">
              <CardTitle className="text-3xl mb-2">{lesson.title}</CardTitle>
              <p className="text-blue-100">{lesson.subtitle}</p>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-8">
          {/* Lesson Content */}
          <div className="prose prose-lg max-w-none mb-8">
            <ReactMarkdown>{lesson.content}</ReactMarkdown>
          </div>

          {/* Next Step */}
          <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-blue-300">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="bg-blue-600 text-white rounded-full p-3">
                  <CheckCircle className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-lg">{t('education.readyToTest')}</h4>
                  <p className="text-muted-foreground">{t('education.answerQuestions', { count: lesson.quiz?.length || 0 })}</p>
                </div>
                <Button size="lg" onClick={() => setShowQuiz(true)}>
                  {t('education.startQuiz')} →
                </Button>
              </div>
            </CardContent>
          </Card>
        </CardContent>
      </Card>
    </div>
  );
}