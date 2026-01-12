import React from 'react';
import { Users, Calculator, TrendingUp, Award, Star } from 'lucide-react';
import { Card, CardContent } from './ui/card';

const STATS = [
  {
    icon: Users,
    value: "500+",
    label: "Investitori Activi",
    color: "text-blue-500"
  },
  {
    icon: Calculator,
    value: "2.000+",
    label: "Calculări Fiscale",
    color: "text-amber-500"
  },
  {
    icon: TrendingUp,
    value: "150k+",
    label: "RON Economisiți (total)",
    color: "text-green-500"
  },
  {
    icon: Award,
    value: "4.8/5",
    label: "Rating Utilizatori",
    color: "text-purple-500"
  }
];

const TESTIMONIALS = [
  {
    name: "Andrei M.",
    role: "Investitor BVB",
    text: "Calculatorul fiscal mi-a arătat că economisesc 8.000 RON/an ca PF față de SRL. Incredible!",
    rating: 5
  },
  {
    name: "Elena T.",
    role: "Trader Activ",
    text: "Indicatorii tehnici și AI-ul m-au ajutat să îmi optimizez portofoliul. Scor diversificare: 85/100!",
    rating: 5
  },
  {
    name: "Mihai D.",
    role: "Începător",
    text: "Am început cu planul gratuit și am trecut la PRO în 2 săptămâni. Merită fiecare leu!",
    rating: 5
  }
];

export default function SocialProof() {
  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map((stat, idx) => (
          <Card key={idx} className="bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-800 hover:shadow-lg transition-all">
            <CardContent className="p-6 text-center">
              <stat.icon className={`w-8 h-8 ${stat.color} mx-auto mb-2`} />
              <p className="text-3xl font-bold mb-1">{stat.value}</p>
              <p className="text-sm text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Testimonials */}
      <div>
        <h3 className="text-2xl font-bold text-center mb-6">Ce Spun Utilizatorii</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TESTIMONIALS.map((testimonial, idx) => (
            <Card key={idx} className="bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/10 dark:to-slate-800">
              <CardContent className="p-6">
                <div className="flex gap-1 mb-3">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-500 text-amber-500" />
                  ))}
                </div>
                <p className="text-sm italic mb-4 text-muted-foreground">"{testimonial.text}"</p>
                <div>
                  <p className="font-semibold">{testimonial.name}</p>
                  <p className="text-xs text-muted-foreground">{testimonial.role}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
