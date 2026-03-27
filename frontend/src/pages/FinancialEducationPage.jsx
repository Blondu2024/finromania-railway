import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Trophy, Lock, CheckCircle, Clock, ChevronRight, Star, TrendingUp, Award, DollarSign } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Link, useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FinancialEducationPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const lessonsRes = await fetch(`${API_URL}/api/financial-education/lessons`);
      if (lessonsRes.ok) {
        const data = await lessonsRes.json();
        setLessons(data.lessons || []);
      }

      if (user) {
        const progressRes = await fetch(`${API_URL}/api/financial-education/progress`, {
        });
        if (progressRes.ok) {
          const progressData = await progressRes.json();
          setProgress(progressData);
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (diff) => {
    switch(diff) {
      case 'beginner': return 'bg-green-100 text-green-700 border-green-200';
      case 'intermediate': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'advanced': return 'bg-red-100 text-red-700 border-red-200';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const isLessonCompleted = (lessonId) => {
    return progress?.completed_lessons?.includes(lessonId) || false;
  };

  const canAccessLesson = (lessonOrder) => {
    if (!user) return lessonOrder === 1; // Only first lesson for non-logged
    if (lessonOrder === 1) return true;
    
    // Check if previous lesson is completed
    const prevLesson = lessons.find(l => l.order === lessonOrder - 1);
    return prevLesson ? isLessonCompleted(prevLesson.id) : false;
  };

  const totalLessons = lessons.length;
  const completedCount = progress?.completed_lessons?.length || 0;
  const progressPercent = totalLessons > 0 ? (completedCount / totalLessons) * 100 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center space-y-6">
            <div className="inline-block p-4 bg-white/20 rounded-full backdrop-blur-sm">
              <DollarSign className="w-16 h-16" />
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold">
              Educație Financiară
            </h1>
            <p className="text-xl sm:text-2xl text-green-100 max-w-2xl mx-auto">
              Gestionează-ți banii inteligent - de la bugete la investiții
            </p>
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <Badge className="bg-white/20 text-white border-white/40 px-4 py-2 text-sm">
                <CheckCircle className="w-4 h-4 mr-2" />
                {totalLessons} Lecții Practice
              </Badge>
              <Badge className="bg-white/20 text-white border-white/40 px-4 py-2 text-sm">
                <Trophy className="w-4 h-4 mr-2" />
                De la ZERO la Expert
              </Badge>
              <Badge className="bg-white/20 text-white border-white/40 px-4 py-2 text-sm">
                <Star className="w-4 h-4 mr-2" />
                100% Gratuit
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Progress Section */}
        {user && progress && (
          <Card className="mb-8 border-2 border-blue-200 shadow-lg">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold">Progresul Tău</h3>
                  <p className="text-muted-foreground">Continuă să înveți!</p>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-bold text-blue-600">{completedCount}/{totalLessons}</div>
                  <div className="text-sm text-muted-foreground">Lecții complete</div>
                </div>
              </div>
              <Progress value={progressPercent} className="h-3" />
              <p className="text-sm text-muted-foreground mt-2">{progressPercent.toFixed(0)}% complet</p>
            </CardContent>
          </Card>
        )}

        {/* Lessons Grid */}
        <div className="space-y-8">
          {/* Module 1 */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-1 w-12 bg-gradient-to-r from-green-500 to-green-600 rounded" />
              <h2 className="text-2xl font-bold">Modul 1: Fundamentele</h2>
              <Badge variant="secondary">Beginner</Badge>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {lessons.filter(l => l.module === 1).map((lesson) => {
                const completed = isLessonCompleted(lesson.id);
                const canAccess = canAccessLesson(lesson.order);
                const locked = !canAccess;

                return (
                  <Card
                    key={lesson.id}
                    className={`group cursor-pointer transition-all duration-300 hover:shadow-xl ${
                      completed ? 'border-2 border-green-500 bg-green-50' :
                      locked ? 'opacity-60 cursor-not-allowed' :
                      'hover:scale-105 border-2 border-transparent hover:border-blue-400'
                    }`}
                    onClick={() => !locked && navigate(`/financial-education/${lesson.id}`)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-5xl">{lesson.emoji}</div>
                        {completed && (
                          <div className="bg-green-500 text-white rounded-full p-2">
                            <CheckCircle className="w-5 h-5" />
                          </div>
                        )}
                        {locked && (
                          <div className="bg-gray-400 text-white rounded-full p-2">
                            <Lock className="w-5 h-5" />
                          </div>
                        )}
                      </div>
                      
                      <h3 className="font-bold text-lg mb-2">{lesson.title}</h3>
                      <p className="text-sm text-muted-foreground mb-4">{lesson.subtitle}</p>
                      
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {lesson.duration}
                        </div>
                        <Badge className={getDifficultyColor(lesson.difficulty)} variant="outline">
                          {lesson.difficulty}
                        </Badge>
                      </div>
                      
                      <Button 
                        className="w-full" 
                        variant={completed ? 'outline' : 'default'}
                        disabled={locked}
                      >
                        {completed ? '✓ Revizuiește' : locked ? '🔒 Locked' : 'Începe Lecția →'}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Module 2 */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-1 w-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded" />
              <h2 className="text-2xl font-bold">Modul 2: Instrumente Financiare</h2>
              <Badge variant="secondary">Intermediate</Badge>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {lessons.filter(l => l.module === 2).map((lesson) => {
                const completed = isLessonCompleted(lesson.id);
                const canAccess = canAccessLesson(lesson.order);
                const locked = !canAccess;

                return (
                  <Card
                    key={lesson.id}
                    className={`group cursor-pointer transition-all duration-300 hover:shadow-xl ${
                      completed ? 'border-2 border-green-500 bg-green-50' :
                      locked ? 'opacity-60 cursor-not-allowed' :
                      'hover:scale-105 border-2 border-transparent hover:border-orange-400'
                    }`}
                    onClick={() => !locked && navigate(`/financial-education/${lesson.id}`)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-5xl">{lesson.emoji}</div>
                        {completed && (
                          <div className="bg-green-500 text-white rounded-full p-2">
                            <CheckCircle className="w-5 h-5" />
                          </div>
                        )}
                        {locked && (
                          <div className="bg-gray-400 text-white rounded-full p-2">
                            <Lock className="w-5 h-5" />
                          </div>
                        )}
                      </div>
                      
                      <h3 className="font-bold text-lg mb-2">{lesson.title}</h3>
                      <p className="text-sm text-muted-foreground mb-4">{lesson.subtitle}</p>
                      
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {lesson.duration}
                        </div>
                        <Badge className={getDifficultyColor(lesson.difficulty)} variant="outline">
                          {lesson.difficulty}
                        </Badge>
                      </div>
                      
                      <Button 
                        className="w-full" 
                        variant={completed ? 'outline' : 'default'}
                        disabled={locked}
                      >
                        {completed ? '✓ Revizuiește' : locked ? '🔒 Locked' : 'Începe Lecția →'}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Module 3 */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="h-1 w-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded" />
              <h2 className="text-2xl font-bold">Modul 3: Introducere în Investiții</h2>
              <Badge variant="secondary">Advanced</Badge>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {lessons.filter(l => l.module === 3).map((lesson) => {
                const completed = isLessonCompleted(lesson.id);
                const canAccess = canAccessLesson(lesson.order);
                const locked = !canAccess;

                return (
                  <Card
                    key={lesson.id}
                    className={`group cursor-pointer transition-all duration-300 hover:shadow-xl ${
                      completed ? 'border-2 border-green-500 bg-green-50' :
                      locked ? 'opacity-60 cursor-not-allowed' :
                      'hover:scale-105 border-2 border-transparent hover:border-blue-400'
                    }`}
                    onClick={() => !locked && navigate(`/financial-education/${lesson.id}`)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="text-5xl">{lesson.emoji}</div>
                        {completed && (
                          <div className="bg-green-500 text-white rounded-full p-2">
                            <CheckCircle className="w-5 h-5" />
                          </div>
                        )}
                        {locked && (
                          <div className="bg-gray-400 text-white rounded-full p-2">
                            <Lock className="w-5 h-5" />
                          </div>
                        )}
                      </div>
                      
                      <h3 className="font-bold text-lg mb-2">{lesson.title}</h3>
                      <p className="text-sm text-muted-foreground mb-4">{lesson.subtitle}</p>
                      
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-4">
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {lesson.duration}
                        </div>
                        <Badge className={getDifficultyColor(lesson.difficulty)} variant="outline">
                          {lesson.difficulty}
                        </Badge>
                      </div>
                      
                      <Button 
                        className="w-full" 
                        variant={completed ? 'outline' : 'default'}
                        disabled={locked}
                      >
                        {completed ? '✓ Revizuiește' : locked ? '🔒 Locked' : 'Începe Lecția →'}
                      </Button>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>
        </div>

        {/* Call to Action */}
        {!user && (
          <Card className="mt-12 bg-gradient-to-r from-blue-700 to-blue-500 text-white border-0">
            <CardContent className="p-8 text-center">
              <Trophy className="w-12 h-12 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">Gata să Începi?</h3>
              <p className="text-blue-100 mb-6">Conectează-te pentru a-ți salva progresul și a obține certificat!</p>
              <Link to="/login">
                <Button size="lg" variant="secondary">
                  Conectare Gratuită
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}