import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

export default function FeatureCard({ 
  to, 
  icon: Icon, 
  title, 
  description, 
  badge, 
  gradient = "from-blue-500 to-purple-500",
  stats = [],
  highlight = false
}) {
  return (
    <Link to={to}>
      <Card className={`group hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] cursor-pointer overflow-hidden h-full ${highlight ? 'ring-2 ring-amber-500' : ''}`}>
        <div className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-5 group-hover:opacity-10 transition-opacity`} />
        
        <CardContent className="p-6 relative">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className={`p-3 rounded-xl bg-gradient-to-br ${gradient} bg-opacity-10`}>
              <Icon className="w-8 h-8 text-white" style={{ filter: 'drop-shadow(0 0 8px rgba(255,255,255,0.5))' }} />
            </div>
            {badge && (
              <Badge className={`${badge.color || 'bg-blue-500'} text-white`}>
                {badge.text}
              </Badge>
            )}
          </div>

          {/* Content */}
          <h3 className="text-2xl font-bold mb-2 group-hover:text-blue-600 transition-colors">
            {title}
          </h3>
          <p className="text-muted-foreground mb-4">
            {description}
          </p>

          {/* Stats */}
          {stats.length > 0 && (
            <div className="grid grid-cols-2 gap-2 mb-4">
              {stats.map((stat, idx) => (
                <div key={idx} className="bg-slate-100 dark:bg-slate-800 rounded-lg p-2 text-center">
                  <p className="text-lg font-bold">{stat.value}</p>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* CTA */}
          <Button 
            variant="ghost" 
            className="w-full group-hover:bg-blue-500 group-hover:text-white transition-all"
          >
            Deschide
            <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
          </Button>
        </CardContent>
      </Card>
    </Link>
  );
}
