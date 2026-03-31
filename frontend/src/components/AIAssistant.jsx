import React, { useState } from 'react';
import { Bot, MessageCircle, Award, BookOpen, X, Send } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Link } from 'react-router-dom';

export default function AIAssistant({ messages = [], achievements = [], onAskQuestion }) {
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(true);
  const [question, setQuestion] = useState('');

  const handleAsk = () => {
    if (question.trim()) {
      onAskQuestion && onAskQuestion(question);
      setQuestion('');
    }
  };

  if (!isExpanded) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          size="lg"
          className="rounded-full h-16 w-16 shadow-lg"
          onClick={() => setIsExpanded(true)}
        >
          <Bot className="w-8 h-8" />
        </Button>
      </div>
    );
  }

  return (
    <Card className="fixed bottom-4 right-4 w-80 max-h-[600px] shadow-2xl z-50 flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="w-5 h-5 text-blue-600" />
            {t('assistant.title')}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4 flex-1 overflow-y-auto">
        {/* Messages */}
        <div className="space-y-3">
          {messages.length > 0 ? (
            messages.map((msg, idx) => (
              <div key={idx} className="bg-blue-50 p-3 rounded-lg">
                <div className="flex items-start gap-2">
                  <MessageCircle className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
                  <p className="text-sm text-blue-900">{msg}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="flex items-start gap-2">
                <Bot className="w-4 h-4 text-blue-600 mt-1 flex-shrink-0" />
                <p className="text-sm text-blue-900">
                  {t('assistant.welcomeMessage')}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Quick Tips */}
        <div>
          <h4 className="text-xs font-semibold text-muted-foreground mb-2">{t('assistant.quickTips')}</h4>
          <div className="space-y-2 text-xs">
            <div className="bg-gray-50 p-2 rounded">
              {t('assistant.tip1')}
            </div>
            <div className="bg-gray-50 p-2 rounded">
              {t('assistant.tip2')}
            </div>
            <div className="bg-gray-50 p-2 rounded">
              {t('assistant.tip3')}
            </div>
          </div>
        </div>

        {/* Achievements */}
        {achievements.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
              <Award className="w-3 h-3" />
              {t('assistant.achievements')}
            </h4>
            <div className="flex flex-wrap gap-1">
              {achievements.map((ach, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  🏆 {ach}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Ask Question */}
        <div>
          <div className="flex gap-2">
            <Input
              placeholder={t('assistant.askPlaceholder')}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
              className="text-sm"
            />
            <Button size="sm" onClick={handleAsk}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Links */}
        <div className="flex gap-2 pt-2 border-t">
          <Link to="/glossary" className="flex-1">
            <Button variant="outline" size="sm" className="w-full text-xs">
              <BookOpen className="w-3 h-3 mr-1" />
              {t('assistant.glossary')}
            </Button>
          </Link>
          <Link to="/advisor" className="flex-1">
            <Button variant="outline" size="sm" className="w-full text-xs">
              <Bot className="w-3 h-3 mr-1" />
              {t('assistant.aiChat')}
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}