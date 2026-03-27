import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, TrendingDown, Trash2, PieChart, Target, Award, Lock, AlertCircle, BarChart3, DollarSign, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Format RON
const formatRON = (value) => {
  return new Intl.NumberFormat('ro-RO', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value) + ' RON';
};

// Level Badge
const LevelBadge = ({ level }) => {
  const config = {
    beginner: { label: 'Începător', color: 'bg-green-500', icon: '🟢' },
    intermediate: { label: 'Mediu', color: 'bg-blue-500', icon: '🟡' },
    advanced: { label: 'Expert', color: 'bg-blue-500', icon: '🔴' }
  };
  
  const c = config[level] || config.beginner;
  
  return (
    <Badge className={`${c.color} text-white`}>
      {c.icon} Nivel {c.label}
    </Badge>
  );
};

export default function PortfolioBVBPage() {
  const { user, token } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loadingAI, setLoadingAI] = useState(false);
  
  // Add position form
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newPosition, setNewPosition] = useState({
    symbol: '',
    shares: '',
    purchase_price: ''
  });

  useEffect(() => {
    if (user && token) {
      fetchPortfolio();
      fetchConfig();
    }
  }, [user, token]);

  const fetchPortfolio = async () => {
    try {
      const response = await fetch(`${API_URL}/api/portfolio-bvb/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPortfolio(data);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/api/portfolio-bvb/config`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
      }
    } catch (error) {
      console.error('Error fetching config:', error);
    }
  };

  const handleAddPosition = async () => {
    try {
      const response = await fetch(`${API_URL}/api/portfolio-bvb/position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          symbol: newPosition.symbol.toUpperCase(),
          shares: parseFloat(newPosition.shares),
          purchase_price: parseFloat(newPosition.purchase_price)
        })
      });

      if (response.ok) {
        setShowAddDialog(false);
        setNewPosition({ symbol: '', shares: '', purchase_price: '' });
        fetchPortfolio();
      } else {
        const error = await response.json();
        alert(error.detail?.message || 'Eroare la adăugarea poziției');
      }
    } catch (error) {
      console.error('Error adding position:', error);
      alert('Eroare la adăugarea poziției');
    }
  };

  const handleRemovePosition = async (symbol) => {
    if (!confirm(`Sigur vrei să ștergi poziția ${symbol}?`)) return;
    
    try {
      const response = await fetch(`${API_URL}/api/portfolio-bvb/position/${symbol}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        fetchPortfolio();
      }
    } catch (error) {
      console.error('Error removing position:', error);
    }
  };

  const handleGetAIAnalysis = async () => {
    setLoadingAI(true);
    try {
      const response = await fetch(`${API_URL}/api/portfolio-bvb/ai-analysis`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setAiAnalysis(data);
      } else {
        const error = await response.json();
        alert(error.detail?.message || 'Funcție disponibilă de la nivelul Mediu');
      }
    } catch (error) {
      console.error('Error getting AI analysis:', error);
    } finally {
      setLoadingAI(false);
    }
  };

  const exportPortfolioCSV = () => {
    const positions = portfolio?.positions || [];
    if (positions.length === 0) return;
    
    const headers = ['Simbol', 'Acțiuni', 'Preț Achiziție (RON)', 'Preț Curent (RON)', 'Valoare Totală (RON)', 'Profit/Pierdere (RON)', 'Profit/Pierdere (%)'];
    const rows = positions.map(p => [
      p.symbol,
      p.shares,
      p.avg_purchase_price?.toFixed(2) ?? '',
      p.current_price?.toFixed(2) ?? '',
      p.total_value?.toFixed(2) ?? '',
      p.profit_loss?.toFixed(2) ?? '',
      p.profit_loss_percent?.toFixed(2) ?? ''
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `portofoliu_bvb_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Card>
          <CardContent className="p-8 text-center">
            <Lock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">Autentificare necesară</h2>
            <p className="text-gray-500 mb-4">Conectează-te pentru a accesa portofoliul tău BVB.</p>
            <Button onClick={() => window.location.href = '/login'}>Conectează-te</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-gray-200 rounded"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const summary = portfolio?.summary || {};
  const positions = portfolio?.positions || [];
  const level = summary.level || 'beginner';
  const levelInfo = portfolio?.level_info || {};

  return (
    <>
      <SEO 
        title="Portofoliu BVB cu 3 Straturi | FinRomania"
        description="Urmărește portofoliul tău BVB cu indicatori adaptați nivelului tău de experiență."
      />
      
      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Portofoliu BVB</h1>
            <p className="text-muted-foreground">Sistemul "3 Straturi" - adaptat pentru nivelul tău</p>
          </div>
          <LevelBadge level={level} />
        </div>

        {/* Level Features */}
        <Card className="bg-gradient-to-r from-blue-500/10 to-blue-500/10 border-blue-500/30">
          <CardContent className="p-4">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <Target className="w-5 h-5" />
              Ce îți oferă nivelul {levelInfo.name}:
            </h3>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
              {levelInfo.features?.map((feature, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className="text-blue-500">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Valoare Totală</p>
              <p className="text-2xl font-bold">{formatRON(summary.total_value || 0)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Investit</p>
              <p className="text-2xl font-bold">{formatRON(summary.total_invested || 0)}</p>
            </CardContent>
          </Card>
          <Card className={summary.total_profit_loss >= 0 ? 'bg-green-500/10' : 'bg-red-500/10'}>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Profit/Pierdere</p>
              <p className={`text-2xl font-bold ${summary.total_profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.total_profit_loss >= 0 ? '+' : ''}{formatRON(summary.total_profit_loss || 0)}
                <span className="text-sm ml-2">({summary.total_profit_loss_percent?.toFixed(2)}%)</span>
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Poziții</p>
              <p className="text-2xl font-bold">{summary.positions_count || 0}</p>
            </CardContent>
          </Card>
        </div>

        {/* Diversification Score (Mediu+) */}
        {level !== 'beginner' && summary.diversification_score !== null && (
          <Card>
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <h3 className="font-semibold flex items-center gap-2">
                  <PieChart className="w-5 h-5" />
                  Scor Diversificare
                </h3>
                <p className="text-sm text-muted-foreground">Măsoară echilibrul portofoliului tău</p>
              </div>
              <div className="text-right">
                <p className="text-3xl font-bold">{summary.diversification_score}/100</p>
                <Badge className={summary.diversification_score >= 70 ? 'bg-green-500' : summary.diversification_score >= 40 ? 'bg-yellow-500' : 'bg-red-500'}>
                  {summary.diversification_score >= 70 ? 'Bună' : summary.diversification_score >= 40 ? 'Medie' : 'Slabă'}
                </Badge>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Dividend Income (Expert only) */}
        {level === 'advanced' && summary.dividend_income_annual !== null && (
          <Card className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/30">
            <CardContent className="p-4 flex items-center justify-between">
              <div>
                <h3 className="font-semibold flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-green-600" />
                  Venit din Dividende (estimat anual)
                </h3>
                <p className="text-sm text-muted-foreground">Bazat pe dividend yield actual</p>
              </div>
              <p className="text-2xl font-bold text-green-600">{formatRON(summary.dividend_income_annual || 0)}</p>
            </CardContent>
          </Card>
        )}

        {/* Positions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle>Poziții Active</CardTitle>
              <div className="flex gap-2">
                {positions.length > 0 && (
                  <Button variant="outline" size="sm" onClick={exportPortfolioCSV} data-testid="export-portfolio-csv">
                    <Download className="w-4 h-4 mr-2" />
                    Export CSV
                  </Button>
                )}
                <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
                <DialogTrigger asChild>
                  <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Adaugă Poziție
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Adaugă Poziție Nouă</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 pt-4">
                    <div>
                      <Label>Simbol (ex: TLV, SNP)</Label>
                      <Input 
                        value={newPosition.symbol}
                        onChange={(e) => setNewPosition({...newPosition, symbol: e.target.value})}
                        placeholder="TLV"
                      />
                    </div>
                    <div>
                      <Label>Număr Acțiuni</Label>
                      <Input 
                        type="number"
                        value={newPosition.shares}
                        onChange={(e) => setNewPosition({...newPosition, shares: e.target.value})}
                        placeholder="100"
                      />
                    </div>
                    <div>
                      <Label>Preț Achiziție (RON)</Label>
                      <Input 
                        type="number"
                        step="0.01"
                        value={newPosition.purchase_price}
                        onChange={(e) => setNewPosition({...newPosition, purchase_price: e.target.value})}
                        placeholder="2.50"
                      />
                    </div>
                    <Button onClick={handleAddPosition} className="w-full">
                      Adaugă
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>
            </div>
          </CardHeader>
          <CardContent>
            {positions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <PieChart className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Nu ai încă poziții în portofoliu.</p>
                <p className="text-sm">Adaugă prima ta acțiune BVB!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {positions.map((pos) => {
                  const isProfit = pos.profit_loss >= 0;
                  return (
                    <Card key={pos.symbol} className="bg-slate-50 dark:bg-slate-900">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-xl font-bold">{pos.symbol}</h3>
                            <p className="text-sm text-muted-foreground">
                              {pos.shares} acțiuni @ {pos.avg_purchase_price.toFixed(2)} RON
                            </p>
                          </div>
                          <Button 
                            variant="ghost" 
                            size="sm"
                            onClick={() => handleRemovePosition(pos.symbol)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          <div>
                            <p className="text-xs text-muted-foreground">Preț Curent</p>
                            <p className="font-bold">{pos.current_price.toFixed(2)} RON</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Valoare Totală</p>
                            <p className="font-bold">{formatRON(pos.total_value)}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground">Profit/Pierdere</p>
                            <p className={`font-bold ${isProfit ? 'text-green-600' : 'text-red-600'}`}>
                              {isProfit ? <TrendingUp className="w-4 h-4 inline mr-1" /> : <TrendingDown className="w-4 h-4 inline mr-1" />}
                              {isProfit ? '+' : ''}{formatRON(pos.profit_loss)}
                              <span className="text-sm ml-1">({pos.profit_loss_percent.toFixed(2)}%)</span>
                            </p>
                          </div>
                          {pos.dividend_yield && (
                            <div>
                              <p className="text-xs text-muted-foreground">Dividend Yield</p>
                              <p className="font-bold text-green-600">{pos.dividend_yield.toFixed(2)}%</p>
                            </div>
                          )}
                        </div>

                        {/* Technical Indicators (Mediu+) */}
                        {level !== 'beginner' && pos.technical_indicators && (
                          <div className="mt-4 pt-4 border-t">
                            <p className="text-xs font-semibold mb-2">📈 Indicatori Tehnici:</p>
                            <div className="grid grid-cols-3 gap-2 text-sm">
                              {pos.technical_indicators.rsi && (
                                <div>
                                  <p className="text-xs text-muted-foreground">RSI(14)</p>
                                  <p className="font-medium">{pos.technical_indicators.rsi.toFixed(1)}</p>
                                </div>
                              )}
                              {pos.technical_indicators.sma_50 && (
                                <div>
                                  <p className="text-xs text-muted-foreground">SMA 50</p>
                                  <p className="font-medium">{pos.technical_indicators.sma_50.toFixed(2)}</p>
                                </div>
                              )}
                              {pos.technical_indicators.sma_200 && (
                                <div>
                                  <p className="text-xs text-muted-foreground">SMA 200</p>
                                  <p className="font-medium">{pos.technical_indicators.sma_200.toFixed(2)}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Fundamentals (Expert only) */}
                        {level === 'advanced' && pos.fundamentals && (
                          <div className="mt-4 pt-4 border-t">
                            <p className="text-xs font-semibold mb-2">📋 Date Fundamentale:</p>
                            <div className="grid grid-cols-3 gap-2 text-sm">
                              {pos.fundamentals.pe_ratio && (
                                <div>
                                  <p className="text-xs text-muted-foreground">P/E</p>
                                  <p className="font-medium">{pos.fundamentals.pe_ratio.toFixed(2)}</p>
                                </div>
                              )}
                              {pos.fundamentals.pb_ratio && (
                                <div>
                                  <p className="text-xs text-muted-foreground">P/B</p>
                                  <p className="font-medium">{pos.fundamentals.pb_ratio.toFixed(2)}</p>
                                </div>
                              )}
                              {pos.fundamentals.roe && (
                                <div>
                                  <p className="text-xs text-muted-foreground">ROE</p>
                                  <p className="font-medium">{pos.fundamentals.roe.toFixed(2)}%</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Analysis (Mediu+) */}
        {level !== 'beginner' && positions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Analiză AI Diversificare
              </CardTitle>
              <CardDescription>
                AI analizează portofoliul tău și oferă sugestii de diversificare
              </CardDescription>
            </CardHeader>
            <CardContent>
              {aiAnalysis ? (
                <div className="space-y-4">
                  <div className="prose dark:prose-invert max-w-none">
                    <p className="whitespace-pre-wrap">{aiAnalysis.analysis}</p>
                  </div>
                  {aiAnalysis.diversification_score !== undefined && (
                    <p className="text-sm text-muted-foreground">
                      Scor diversificare: <strong>{aiAnalysis.diversification_score}/100</strong>
                    </p>
                  )}
                </div>
              ) : (
                <Button onClick={handleGetAIAnalysis} disabled={loadingAI}>
                  {loadingAI ? (
                    <span className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Se analizează...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <BarChart3 className="w-4 h-4" />
                      Solicită Analiză AI
                    </span>
                  )}
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
