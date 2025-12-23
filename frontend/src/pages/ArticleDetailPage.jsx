import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Clock, Building2 } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ArticleDetailPage() {
  const { articleId } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchArticle = async () => {
      try {
        setLoading(true);
        
        const res = await fetch(`${API_URL}/api/news/${articleId}`);
        if (!res.ok) throw new Error('Article not found');
        
        const data = await res.json();
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [articleId]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-12 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Articolul nu a fost găsit</p>
        <Link to="/news">
          <Button className="mt-4"><ArrowLeft className="w-4 h-4 mr-2" /> Înapoi la Știri</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back Button */}
      <Link to="/news">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi la Știri
        </Button>
      </Link>

      {/* Article Header */}
      <article className="space-y-6">
        <header>
          <div className="flex items-center gap-2 mb-4">
            <Badge variant="secondary">
              <Building2 className="w-3 h-3 mr-1" />
              {article.source?.name}
            </Badge>
            <Badge variant="outline">
              <Clock className="w-3 h-3 mr-1" />
              {new Date(article.published_at).toLocaleDateString('ro-RO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </Badge>
            {article.is_romanian_source && (
              <Badge variant="default" className="bg-blue-600">
                🇷🇴 Sursă Română
              </Badge>
            )}
          </div>
          
          <h1 className="text-3xl font-bold leading-tight">{article.title}</h1>
          
          {article.description && (
            <p className="text-lg text-muted-foreground mt-4 leading-relaxed">
              {article.description}
            </p>
          )}
        </header>

        {/* Featured Image */}
        {article.image_url && (
          <div className="rounded-lg overflow-hidden">
            <img 
              src={article.image_url} 
              alt={article.title}
              className="w-full h-auto object-cover"
              onError={(e) => e.target.style.display = 'none'}
            />
          </div>
        )}

        {/* Article Content */}
        <div className="prose prose-lg dark:prose-invert max-w-none">
          {article.content ? (
            <div className="text-base leading-relaxed whitespace-pre-wrap">
              {article.content}
            </div>
          ) : (
            <p className="text-muted-foreground italic">
              Pentru a citi articolul complet, vizitează sursa originală.
            </p>
          )}
        </div>

        {/* Source Link */}
        <Card className="bg-muted/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Sursă originală</p>
                <p className="font-medium">{article.source?.name}</p>
              </div>
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
              >
                <Button variant="outline" size="sm">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Citește la sursă
                </Button>
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Author */}
        {article.author && (
          <p className="text-sm text-muted-foreground">
            Autor: {article.author}
          </p>
        )}
      </article>
    </div>
  );
}
