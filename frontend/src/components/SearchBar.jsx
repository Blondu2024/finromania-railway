import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Search, X, TrendingUp, Newspaper, Loader2 } from 'lucide-react';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function SearchBar() {
  const { t } = useTranslation();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const debounceTimer = setTimeout(() => {
      if (query.length >= 2) {
        search();
      } else {
        setResults(null);
      }
    }, 300);
    return () => clearTimeout(debounceTimer);
  }, [query]);

  const search = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        setIsOpen(true);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (path) => {
    setIsOpen(false);
    setQuery('');
    navigate(path);
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder={t('search.placeholder')}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results && setIsOpen(true)}
          className="pl-10 pr-10 w-64"
        />
        {loading && (
          <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
        )}
        {query && !loading && (
          <button
            onClick={() => { setQuery(''); setResults(null); }}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {isOpen && results && (results.stocks?.length > 0 || results.news?.length > 0) && (
        <div className="absolute top-full mt-2 w-96 bg-background border rounded-lg shadow-lg z-50 max-h-96 overflow-auto">
          {results.stocks?.length > 0 && (
            <div className="p-2">
              <p className="text-xs text-muted-foreground px-2 py-1 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" /> {t('search.stocks')}
              </p>
              {results.stocks.map((stock, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(`/stocks/${stock.stock_type}/${encodeURIComponent(stock.symbol)}`)}
                  className="w-full text-left px-3 py-2 hover:bg-muted rounded-md flex items-center justify-between"
                >
                  <div>
                    <span className="font-medium">{stock.symbol}</span>
                    <span className="text-sm text-muted-foreground ml-2">{stock.name}</span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {stock.stock_type === 'bvb' ? 'BVB' : 'Global'}
                  </Badge>
                </button>
              ))}
            </div>
          )}
          
          {results.news?.length > 0 && (
            <div className="p-2 border-t">
              <p className="text-xs text-muted-foreground px-2 py-1 flex items-center gap-1">
                <Newspaper className="w-3 h-3" /> {t('search.news')}
              </p>
              {results.news.slice(0, 5).map((article, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelect(`/news/${article.id}`)}
                  className="w-full text-left px-3 py-2 hover:bg-muted rounded-md"
                >
                  <p className="text-sm line-clamp-1">{article.title}</p>
                  <p className="text-xs text-muted-foreground">{article.source?.name}</p>
                </button>
              ))}
            </div>
          )}
          
          {results.total === 0 && (
            <p className="p-4 text-center text-muted-foreground">{t('search.noResults', { query })}</p>
          )}
        </div>
      )}
    </div>
  );
}
