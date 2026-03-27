import React from 'react';
import { Shield, Zap, Globe, Lock, CheckCircle } from 'lucide-react';

export default function TrustBadges() {
  const badges = [
    {
      icon: Shield,
      text: "Date Securizate",
      subtext: "SSL & Encryption"
    },
    {
      icon: Zap,
      text: "Date Financiare Premium",
      subtext: "$99.99 All-In-One Plan"
    },
    {
      icon: Globe,
      text: "Made in Romania",
      subtext: "🇷🇴 Pentru români"
    },
    {
      icon: CheckCircle,
      text: "Legislație 2024-2025",
      subtext: "Actualizat constant"
    },
    {
      icon: Lock,
      text: "GDPR Compliant",
      subtext: "Datele tale protejate"
    }
  ];

  return (
    <div className="bg-gray-100 dark:bg-zinc-900 rounded-xl p-6">
      <div className="flex flex-wrap justify-center items-center gap-6">
        {badges.map((badge, idx) => (
          <div key={idx} className="flex items-center gap-2 text-center">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <badge.icon className="w-5 h-5 text-blue-600" />
            </div>
            <div className="text-left">
              <p className="text-sm font-semibold">{badge.text}</p>
              <p className="text-xs text-muted-foreground">{badge.subtext}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
