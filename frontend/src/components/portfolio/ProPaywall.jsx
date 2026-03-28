import React from 'react';
import { Link } from 'react-router-dom';
import { Crown } from 'lucide-react';
import { Button } from '../ui/button';

export default function ProPaywall() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6">
      <div className="w-20 h-20 rounded-full bg-amber-500/10 flex items-center justify-center">
        <Crown className="w-10 h-10 text-amber-500" />
      </div>
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Portofoliu PRO</h2>
        <p className="text-muted-foreground max-w-md">
          Urmărire poziții BVB cu date live, P&L în timp real, RSI per acțiune, AI Advisor și dividende estimate.
        </p>
      </div>
      <Link to="/pricing">
        <Button size="lg" className="bg-amber-500 hover:bg-amber-600 text-white">
          <Crown className="w-4 h-4 mr-2" />
          Upgrade la PRO
        </Button>
      </Link>
    </div>
  );
}
