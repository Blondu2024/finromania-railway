import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Search, BookOpen } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Skeleton } from '../components/ui/skeleton';
import { Badge } from '../components/ui/badge';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function GlossaryPage() {
  const { t } = useTranslation();
  const [terms, setTerms] = useState({});
  const [filteredTerms, setFilteredTerms] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchGlossary();
  }, []);

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = {};
      Object.entries(terms).forEach(([term, definition]) => {
        if (
          term.toLowerCase().includes(searchQuery.toLowerCase()) ||
          definition.toLowerCase().includes(searchQuery.toLowerCase())
        ) {
          filtered[term] = definition;
        }
      });
      setFilteredTerms(filtered);
    } else {
      setFilteredTerms(terms);
    }
  }, [searchQuery, terms]);

  const fetchGlossary = async () => {
    try {
      const res = await fetch(`${API_URL}/api/education/glossary`);
      if (res.ok) {
        const data = await res.json();
        setTerms(data.terms || {});
        setFilteredTerms(data.terms || {});
        setTotal(data.total || 0);
      }
    } catch (error) {
      console.error('Error fetching glossary:', error);
    } finally {
      setLoading(false);
    }
  };

  // Group terms alphabetically
  const groupedTerms = {};
  Object.entries(filteredTerms)
    .sort(([a], [b]) => a.localeCompare(b))
    .forEach(([term, definition]) => {
      const firstLetter = term[0].toUpperCase();
      if (!groupedTerms[firstLetter]) {
        groupedTerms[firstLetter] = [];
      }
      groupedTerms[firstLetter].push({ term, definition });
    });

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-12" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <BookOpen className="w-8 h-8 text-blue-600" />
          <h1 className="text-4xl font-bold">{t('education.glossaryTitle')}</h1>
        </div>
        <p className="text-muted-foreground">
          {t('education.glossaryDesc')}
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
        <Input
          type="text"
          placeholder="Caută termeni... (ex: acțiune, dividend, ETF)"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Results Count */}
      {searchQuery && (
        <div className="flex items-center gap-2">
          <Badge variant="secondary">
            {Object.keys(filteredTerms).length} rezultate
          </Badge>
          {Object.keys(filteredTerms).length === 0 && (
            <p className="text-sm text-muted-foreground">
              Nu am găsit termeni care să corespundă căutării tale.
            </p>
          )}
        </div>
      )}

      {/* Glossary Terms - Grouped by Letter */}
      {Object.keys(groupedTerms).length > 0 ? (
        <div className="space-y-8">
          {Object.entries(groupedTerms).map(([letter, termsList]) => (
            <div key={letter}>
              <div className="flex items-center gap-4 mb-4">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-2xl font-bold text-blue-600">{letter}</span>
                </div>
                <div className="flex-1 h-px bg-border" />
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                {termsList.map(({ term, definition }) => (
                  <Card key={term} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">{term}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">{definition}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        !loading && (
          <Card>
            <CardContent className="text-center py-12">
              <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nu s-au găsit termeni.</p>
            </CardContent>
          </Card>
        )
      )}

      {/* Info Footer */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <BookOpen className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-semibold text-blue-900 mb-2">
                💡 Ghid de utilizare
              </h3>
              <p className="text-sm text-blue-800">
                Acest glosar conține termeni esențiali din lumea investițiilor și finanțelor.
                Folosește bara de căutare pentru a găsi rapid definiții sau navighează alfabetic.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
