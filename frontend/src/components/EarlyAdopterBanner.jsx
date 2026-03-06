import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Gift, Users, Clock, Zap, Crown, Check, ArrowRight, Loader2 } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function EarlyAdopterBanner({ variant = 'full' }) {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [claiming, setClaiming] = useState(false);
  const [claimResult, setClaimResult] = useState(null);

  useEffect(() => {
    fetchStatus();
  }, [user]);

  const fetchStatus = async () => {
    try {
      // Use public endpoint if not logged in
      const endpoint = user 
        ? `${API_URL}/api/early-adopter/status`
        : `${API_URL}/api/early-adopter/public-status`;
      
      const headers = user && token 
        ? { 'Authorization': `Bearer ${token}` }
        : {};
      
      const res = await fetch(endpoint, { headers });
      const data = await res.json();
      setStatus(data);
    } catch (error) {
      console.error('Error fetching early adopter status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClaim = async () => {
    if (!user) {
      // Redirect to login
      navigate('/login');
      return;
    }

    setClaiming(true);
    try {
      const res = await fetch(`${API_URL}/api/early-adopter/claim`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await res.json();
      setClaimResult(data);
      
      if (data.success) {
        // Refresh status
        fetchStatus();
        // Reload page to update user context
        setTimeout(() => window.location.reload(), 2000);
      }
    } catch (error) {
      console.error('Error claiming early adopter slot:', error);
      setClaimResult({ success: false, message: 'A apărut o eroare. Încearcă din nou.' });
    } finally {
      setClaiming(false);
    }
  };

  if (loading) {
    return (
      <Card className="animate-pulse">
        <CardContent className="p-6 h-32" />
      </Card>
    );
  }

  if (!status || !status.is_active) {
    // Program closed
    return null;
  }

  // If user is already early adopter, show thank you message
  if (status.is_user_early_adopter) {
    return (
      <Card className="bg-gradient-to-r from-green-600 to-emerald-600 text-white border-0 overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/20 rounded-full">
              <Crown className="w-8 h-8" />
            </div>
            <div className="flex-1">
              <h3 className="text-xl font-bold flex items-center gap-2">
                🎉 Ești Early Adopter!
              </h3>
              <p className="text-green-100">
                PRO gratuit până la {new Date(status.user_expires_at).toLocaleDateString('ro-RO')}
              </p>
            </div>
            <Badge className="bg-white/20 text-white text-lg px-4 py-2">
              <Check className="w-4 h-4 mr-2" />
              PRO Activ
            </Badge>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Show claim result
  if (claimResult) {
    return (
      <Card className={`border-0 overflow-hidden ${claimResult.success ? 'bg-gradient-to-r from-green-600 to-emerald-600' : 'bg-gradient-to-r from-red-600 to-orange-600'} text-white`}>
        <CardContent className="p-6 text-center">
          {claimResult.success ? (
            <>
              <Crown className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">{claimResult.message}</h3>
              <p className="text-white/90 mb-2">
                Ai PRO gratuit pentru {claimResult.duration}
              </p>
              <p className="text-sm text-white/70">
                Mai sunt {claimResult.slots_remaining} locuri disponibile
              </p>
            </>
          ) : (
            <>
              <h3 className="text-xl font-bold mb-2">{claimResult.message}</h3>
              {claimResult.alternative && (
                <p className="text-white/90">{claimResult.alternative}</p>
              )}
            </>
          )}
        </CardContent>
      </Card>
    );
  }

  const progressPercent = (status.slots_taken / status.total_slots) * 100;

  // Compact variant for sidebar/small spaces
  if (variant === 'compact') {
    return (
      <Card className="bg-gradient-to-br from-amber-500 via-orange-500 to-red-500 text-white border-0">
        <CardContent className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <Gift className="w-6 h-6" />
            <span className="font-bold">Early Adopter PRO</span>
          </div>
          <div className="mb-3">
            <div className="flex justify-between text-sm mb-1">
              <span>Locuri ocupate</span>
              <span className="font-bold">{status.slots_taken}/{status.total_slots}</span>
            </div>
            <Progress value={progressPercent} className="h-2 bg-white/20" />
          </div>
          <p className="text-xs text-white/80 mb-3">{status.urgency_message}</p>
          <Button 
            onClick={handleClaim}
            disabled={claiming}
            className="w-full bg-white text-orange-600 hover:bg-orange-50"
            size="sm"
          >
            {claiming ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Zap className="w-4 h-4 mr-2" />}
            {user ? 'Revendică Locul' : 'Înregistrează-te'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Full variant
  return (
    <Card className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 text-white border-0 overflow-hidden relative">
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -translate-y-32 translate-x-32" />
      <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full translate-y-24 -translate-x-24" />
      
      <CardContent className="p-6 md:p-8 relative z-10">
        <div className="grid md:grid-cols-2 gap-6 items-center">
          {/* Left side - Info */}
          <div>
            <Badge className="bg-white/20 text-white mb-4">
              <Gift className="w-3 h-3 mr-1" />
              OFERTĂ LIMITATĂ
            </Badge>
            
            <h2 className="text-2xl md:text-3xl font-bold mb-3">
              🎁 Primii 100 de Useri = PRO GRATUIT!
            </h2>
            
            <p className="text-white/90 mb-4">
              Înregistrează-te acum și primești <strong>3 luni de PRO gratuit</strong> - 
              acces complet la toate funcțiile premium!
            </p>
            
            <div className="flex flex-wrap gap-2 mb-4">
              {status.benefits?.slice(0, 3).map((benefit, idx) => (
                <Badge key={idx} variant="outline" className="border-white/30 text-white">
                  <Check className="w-3 h-3 mr-1" />
                  {benefit}
                </Badge>
              ))}
            </div>
            
            <p className="text-sm text-white/70 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              PRO gratuit pentru 90 de zile
            </p>
          </div>
          
          {/* Right side - Counter & CTA */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6">
            <div className="text-center mb-4">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Users className="w-5 h-5" />
                <span className="text-lg font-medium">Locuri disponibile</span>
              </div>
              
              <div className="text-5xl md:text-6xl font-bold mb-2">
                {status.slots_remaining}
                <span className="text-2xl text-white/70">/{status.total_slots}</span>
              </div>
              
              <Progress value={progressPercent} className="h-3 bg-white/20 mb-2" />
              
              <p className="text-sm font-medium">{status.urgency_message}</p>
            </div>
            
            <Button 
              onClick={handleClaim}
              disabled={claiming}
              size="lg"
              className="w-full bg-white text-orange-600 hover:bg-orange-50 font-bold text-lg py-6"
            >
              {claiming ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Se procesează...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  {user ? 'Revendică Locul GRATUIT' : 'Înregistrează-te GRATUIT'}
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
            
            {!user && (
              <p className="text-xs text-white/70 text-center mt-2">
                Trebuie să te înregistrezi pentru a revendica locul
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
