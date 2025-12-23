import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, CheckCircle, BookOpen, Clock, Loader2 } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function LessonPage() {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [allLessons, setAllLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchLesson();
    fetchAllLessons();
  }, [lessonId]);

  const fetchLesson = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/education/lessons/${lessonId}`, {
        credentials: 'include'
      });
      
      if (res.ok) {
        setLesson(await res.json());
        setError(null);
      } else if (res.status === 403) {
        setError('locked');
      } else {
        setError('not_found');
      }
    } catch (err) {
      setError('error');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllLessons = async () => {
    try {
      const res = await fetch(`${API_URL}/api/education/lessons`, {
        credentials: 'include'
      });
      if (res.ok) {
        const data = await res.json();
        setAllLessons(data.lessons || []);
      }
    } catch (err) {
      console.error('Error fetching lessons:', err);
    }
  };

  const currentIndex = allLessons.findIndex(l => l.id === lessonId);
  const prevLesson = currentIndex > 0 ? allLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < allLessons.length - 1 ? allLessons[currentIndex + 1] : null;

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (error === 'locked') {
    return (
      <div className="max-w-2xl mx-auto text-center py-12">
        <div className="p-4 bg-yellow-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <BookOpen className="w-8 h-8 text-yellow-600" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Lec\u021bie Premium</h2>
        <p className="text-muted-foreground mb-6">
          Aceast\u0103 lec\u021bie face parte din pachetul educa\u021bional premium.
        </p>
        <div className="space-x-4">
          <Link to="/education">
            <Button><ArrowLeft className="w-4 h-4 mr-2" /> \u00cenapoi la Curs</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Lec\u021bia nu a fost g\u0103sit\u0103</p>
        <Link to="/education">
          <Button className="mt-4"><ArrowLeft className="w-4 h-4 mr-2" /> \u00cenapoi</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Navigation */}
      <Link to="/education">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> \u00cenapoi la Curs
        </Button>
      </Link>

      {/* Lesson Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="secondary">Lec\u021bia {lesson.order}</Badge>
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="w-3 h-3" /> {lesson.duration}
          </Badge>
          {lesson.is_free && (
            <Badge className="bg-green-100 text-green-700">GRATUIT</Badge>
          )}
        </div>
        <h1 className="text-3xl font-bold">{lesson.title}</h1>
        <p className="text-muted-foreground mt-2">{lesson.description}</p>
      </div>

      {/* Lesson Content */}
      <Card>
        <CardContent className="p-8 prose prose-lg dark:prose-invert max-w-none">
          <ReactMarkdown
            components={{
              h2: ({children}) => <h2 className="text-2xl font-bold mt-8 mb-4 text-foreground">{children}</h2>,
              h3: ({children}) => <h3 className="text-xl font-semibold mt-6 mb-3 text-foreground">{children}</h3>,
              p: ({children}) => <p className="mb-4 leading-relaxed text-foreground">{children}</p>,
              ul: ({children}) => <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>,
              ol: ({children}) => <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>,
              li: ({children}) => <li className="text-foreground">{children}</li>,
              strong: ({children}) => <strong className="font-bold text-foreground">{children}</strong>,
              blockquote: ({children}) => (
                <blockquote className="border-l-4 border-blue-500 pl-4 italic my-4 text-muted-foreground">
                  {children}
                </blockquote>
              ),
              table: ({children}) => (
                <div className="overflow-x-auto my-4">
                  <table className="min-w-full border border-border">{children}</table>
                </div>
              ),
              th: ({children}) => <th className="border border-border px-4 py-2 bg-muted font-semibold">{children}</th>,
              td: ({children}) => <td className="border border-border px-4 py-2">{children}</td>,
            }}
          >
            {lesson.content}
          </ReactMarkdown>
        </CardContent>
      </Card>

      {/* Navigation Footer */}
      <div className="flex justify-between items-center pt-6 border-t">
        {prevLesson && !prevLesson.is_locked ? (
          <Button variant="outline" onClick={() => navigate(`/education/lesson/${prevLesson.id}`)}>
            <ArrowLeft className="w-4 h-4 mr-2" /> {prevLesson.title}
          </Button>
        ) : (
          <div />
        )}
        
        {nextLesson ? (
          nextLesson.is_locked ? (
            <Link to="/education">
              <Button>
                Deblocheaz\u0103 Restul Cursului <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          ) : (
            <Button onClick={() => navigate(`/education/lesson/${nextLesson.id}`)}>
              {nextLesson.title} <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          )
        ) : (
          <Link to="/education">
            <Button variant="secondary">
              <CheckCircle className="w-4 h-4 mr-2" /> Curs Finalizat!
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
}
