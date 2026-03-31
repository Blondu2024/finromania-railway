import React from 'react';
import { useTranslation } from 'react-i18next';
import { TrendingUp, TrendingDown, Info } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

export default function IndexCard({ index, onSelect, isSelected }) {
  const { t } = useTranslation();
  const getBadgeColor = (volatility) => {
    switch(volatility) {
      case 'high': return 'destructive';
      case 'medium': return 'secondary';
      case 'low': return 'outline';
      default: return 'secondary';
    }
  };

  const getRiskColor = (risk) => {
    switch(risk) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-orange-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <Card 
      className={`cursor-pointer transition-all hover:shadow-lg hover:scale-105 ${
        isSelected ? 'border-2 border-blue-500 shadow-lg' : 'border'
      }`}
      onClick={() => onSelect(index)}
    >
      <CardContent className="p-6">
        <div className="flex flex-col items-center text-center space-y-3">
          {/* Emoji Mare */}
          <div className="text-6xl mb-2">{index.emoji}</div>
          
          {/* Nume */}
          <h3 className="text-xl font-bold">{index.name}</h3>
          
          {/* Categorie */}
          <Badge variant="outline" className="text-xs">
            {index.category_ro}
          </Badge>
          
          {/* Descriere */}
          <p className="text-sm text-muted-foreground">
            {index.description_ro}
          </p>
          
          {/* Volatilitate */}
          <div className="flex items-center gap-2">
            {index.volatility === 'high' ? (
              <TrendingUp className="w-4 h-4 text-orange-600" />
            ) : (
              <TrendingDown className="w-4 h-4 text-green-600" />
            )}
            <Badge variant={getBadgeColor(index.volatility)}>
              {index.volatility_ro}
            </Badge>
          </div>
          
          {/* Risc */}
          <div className={`text-xs font-medium ${getRiskColor(index.risk_level)}`}>
            Risc: {index.risk_level === 'low' ? 'Scăzut' : index.risk_level === 'medium' ? 'Mediu' : 'Ridicat'}
          </div>
          
          {/* Learning Tip */}
          {index.good_for_learning && (
            <div className="bg-blue-50 p-3 rounded-lg mt-2">
              <div className="flex items-start gap-2">
                <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-blue-800">{index.learning_tip}</p>
              </div>
            </div>
          )}
          
          {/* Button */}
          <Button 
            className="w-full mt-4"
            size="lg"
            variant={isSelected ? 'default' : 'outline'}
          >
            {isSelected ? t('common.selected') : t('common.select')}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}