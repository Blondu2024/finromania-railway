import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Clock, Building2, Loader2 } from 'lucide-react';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Skeleton } from '../components/ui/skeleton';
import SocialShare from '../components/SocialShare';
import NewsStockAnalysis from '../components/NewsStockAnalysis';
import SEO from '../components/SEO';

// Rename import to use smart analysis
const SmartNewsAnalysis = NewsStockAnalysis;

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ArticleDetailPage() {
  const { t } = useTranslation();
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
        <div className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          <span className="text-sm">Se încarcă articolul complet...</span>
        </div>
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

  // Format content with paragraphs
  const formatContent = (content) => {
    if (!content) return null;
    
    return content.split('\n\n').map((paragraph, idx) => {
      // Check if it's a heading (bold text)
      if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
        return (
          <h2 key={idx} className="text-xl font-semibold mt-6 mb-3">
            {paragraph.replace(/\*\*/g, '')}
          </h2>
        );
      }
      // Check if it's a blockquote
      if (paragraph.startsWith('>')) {
        return (
          <blockquote key={idx} className="border-l-4 border-blue-500 pl-4 italic text-muted-foreground my-4">
            {paragraph.substring(1).trim()}
          </blockquote>
        );
      }
      // Check if it's a list item
      if (paragraph.startsWith('•')) {
        return (
          <li key={idx} className="ml-4">
            {paragraph.substring(1).trim()}
          </li>
        );
      }
      // Regular paragraph
      return (
        <p key={idx} className="mb-4 leading-relaxed">
          {paragraph}
        </p>
      );
    });
  };

  const hasFullContent = article.content && article.content.length > 200;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <SEO title={article ? `${article.title} | FinRomania` : 'Financial News | FinRomania'} description={article?.description || article?.summary || 'Latest financial news from Romania and international markets'} />
      {/* Back Button */}
      <Link to="/news">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi la Știri
        </Button>
      </Link>

      {/* Article Header */}
      <article className="space-y-6">
        <header>
          <div className="flex flex-wrap items-center gap-2 mb-4">
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
            {hasFullContent && (
              <Badge variant="default" className="bg-green-600">
                ✓ Articol Complet
              </Badge>
            )}
          </div>
          
          <h1 className="text-3xl font-bold leading-tight">{article.title}</h1>
          
          {article.description && !hasFullContent && (
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
              className="w-full h-auto object-cover max-h-96"
              onError={(e) => e.target.style.display = 'none'}
            />
          </div>
        )}

        {/* Article Content */}
        <div className="prose prose-lg dark:prose-invert max-w-none">
          {hasFullContent ? (
            <div className="text-base">
              {formatContent(article.content)}
            </div>
          ) : article.description ? (
            <div>
              <p className="text-base leading-relaxed mb-6">{article.description}</p>
              <Card className="bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200">
                <CardContent className="p-4">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    ℹ️ Conținutul complet nu a putut fi extras automat. 
                    Pentru a citi articolul integral, vizitează sursa originală.
                  </p>
                </CardContent>
              </Card>
            </div>
          ) : (
            <p className="text-muted-foreground italic">
              Conținutul nu este disponibil. Vizitează sursa originală.
            </p>
          )}
        </div>

        {/* Source Link - always visible but not prominent */}
        <Card className="bg-muted/30 border-dashed">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-muted-foreground">Sursă originală</p>
                <p className="text-sm font-medium">{article.source?.name}</p>
              </div>
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
              >
                <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                  <ExternalLink className="w-3 h-3 mr-1" />
                  <span className="text-xs">Vizitează sursa</span>
                </Button>
              </a>
            </div>
          </CardContent>
        </Card>

        {/* Author */}
        {article.author && article.author !== article.source?.name && (
          <p className="text-sm text-muted-foreground">
            Autor: {article.author}
          </p>
        )}

        {/* Social Share */}
        <div className="border-t pt-4 mt-4">
          <SocialShare title={article.title} url={window.location.href} />
        </div>

        {/* Smart AI Analysis for the news */}
        <SmartNewsAnalysis article={article} />

        {/* Financial Education CTA */}
        <Card className="bg-gradient-to-r from-green-600 to-emerald-600 text-white border-0 mt-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-4">
              <div className="text-center md:text-left">
                <h3 className="text-lg font-bold mb-1">💰 Vrei Să Înțelegi Mai Bine Știrile Financiare?</h3>
                <p className="text-green-100 text-sm">Învață bazele finanțelor personale și investițiilor în 15 lecții gratuite</p>
              </div>
              <Link to="/financial-education">
                <Button className="bg-white text-green-600 hover:bg-green-50 whitespace-nowrap">
                  Începe Educația Financiară →
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </article>
    </div>
  );
}
