import React from 'react';
import { Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export default function PortfolioNewsSection({ news }) {
  const articles = news?.news || [];
  if (articles.length === 0) return null;

  return (
    <Card className="mt-4" data-testid="portfolio-news-section">
      <CardHeader className="py-3 px-4 border-b">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-500" />
          Știri Relevante — Portofoliul Tău
          <span className="text-xs font-normal text-muted-foreground">
            · filtrate după simbolurile deținute
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y">
          {articles.map((art, i) => (
            <a
              key={art.id || i}
              href={art.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex gap-3 p-3 hover:bg-muted/30 transition-colors"
              data-testid={`portfolio-news-${i}`}
            >
              {art.image_url && (
                <img
                  src={art.image_url}
                  alt=""
                  className="w-16 h-16 object-cover rounded flex-shrink-0"
                  loading="lazy"
                  onError={e => (e.target.style.display = 'none')}
                />
              )}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {(art.related_symbols || []).map(sym => (
                    <span
                      key={sym}
                      className="text-[10px] font-bold px-1.5 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 rounded"
                    >
                      {sym}
                    </span>
                  ))}
                </div>
                <p className="font-medium text-sm line-clamp-2 leading-snug">
                  {art.title_ro || art.title}
                </p>
                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                  <span>{art.source?.name}</span>
                  <span>·</span>
                  <span>{new Date(art.published_at).toLocaleDateString('ro-RO')}</span>
                </div>
              </div>
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
