import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Briefcase, TrendingUp, TrendingDown, Plus, History, PieChart } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function PortfolioPage() {
  const { user } = useAuth();
  const [holdings, setHoldings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newTxn, setNewTxn] = useState({ symbol: '', type: 'bvb', action: 'buy', quantity: '', price: '' });

  useEffect(() => {
    if (user) fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [holdingsRes, summaryRes, txnRes] = await Promise.all([
        fetch(`${API_URL}/api/portfolio/holdings`, { credentials: 'include' }),
        fetch(`${API_URL}/api/portfolio/summary`, { credentials: 'include' }),
        fetch(`${API_URL}/api/portfolio/transactions?limit=10`, { credentials: 'include' })
      ]);
      
      if (holdingsRes.ok) setHoldings(await holdingsRes.json());
      if (summaryRes.ok) setSummary(await summaryRes.json());
      if (txnRes.ok) setTransactions(await txnRes.json());
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const addTransaction = async () => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio/transaction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ...newTxn,
          quantity: parseInt(newTxn.quantity),
          price: parseFloat(newTxn.price)
        })
      });
      
      if (res.ok) {
        setShowAddDialog(false);
        setNewTxn({ symbol: '', type: 'bvb', action: 'buy', quantity: '', price: '' });
        fetchData();
      }
    } catch (error) {
      console.error('Error adding transaction:', error);
    }
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Conectează-te pentru Portofoliu</h2>
        <p className="text-muted-foreground mb-4">Trebuie să fii conectat pentru a gestiona portofoliul virtual.</p>
        <Link to="/login"><Button>Conectează-te</Button></Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-64" />
        <div className="grid md:grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Briefcase className="w-8 h-8 text-green-600" />
            Portofoliu Virtual
          </h1>
          <p className="text-muted-foreground">Simulează investiții fără risc</p>
        </div>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button><Plus className="w-4 h-4 mr-2" /> Adaugă Tranzacție</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Adaugă Tranzacție</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <Input 
                placeholder="Simbol (ex: TLV, AAPL)" 
                value={newTxn.symbol}
                onChange={(e) => setNewTxn({...newTxn, symbol: e.target.value.toUpperCase()})}
              />
              <Select value={newTxn.type} onValueChange={(v) => setNewTxn({...newTxn, type: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="bvb">BVB</SelectItem>
                  <SelectItem value="global">Global</SelectItem>
                </SelectContent>
              </Select>
              <Select value={newTxn.action} onValueChange={(v) => setNewTxn({...newTxn, action: v})}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="buy">Cumpără</SelectItem>
                  <SelectItem value="sell">Vinde</SelectItem>
                </SelectContent>
              </Select>
              <Input 
                type="number" 
                placeholder="Cantitate" 
                value={newTxn.quantity}
                onChange={(e) => setNewTxn({...newTxn, quantity: e.target.value})}
              />
              <Input 
                type="number" 
                step="0.01"
                placeholder="Preț per acțiune" 
                value={newTxn.price}
                onChange={(e) => setNewTxn({...newTxn, price: e.target.value})}
              />
              <Button onClick={addTransaction} className="w-full">Adaugă</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Total Investit</p>
              <p className="text-2xl font-bold">{summary.total_invested?.toLocaleString('ro-RO')} RON</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Valoare Curentă</p>
              <p className="text-2xl font-bold">{summary.total_current?.toLocaleString('ro-RO')} RON</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Profit/Pierdere</p>
              <p className={`text-2xl font-bold ${summary.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.profit_loss >= 0 ? '+' : ''}{summary.profit_loss?.toLocaleString('ro-RO')} RON
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-sm text-muted-foreground">Randament</p>
              <p className={`text-2xl font-bold flex items-center ${summary.profit_loss_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {summary.profit_loss_percent >= 0 ? <TrendingUp className="w-5 h-5 mr-1" /> : <TrendingDown className="w-5 h-5 mr-1" />}
                {summary.profit_loss_percent >= 0 ? '+' : ''}{summary.profit_loss_percent?.toFixed(2)}%
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Holdings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="w-5 h-5" /> Dețineri ({holdings.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {holdings.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              Nu ai nicio deținere. Adaugă prima tranzacție!
            </p>
          ) : (
            <div className="space-y-3">
              {holdings.map((h, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div>
                    <p className="font-bold">{h.symbol}</p>
                    <p className="text-sm text-muted-foreground">{h.quantity} acțiuni @ {h.avg_price?.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{h.current_value?.toLocaleString('ro-RO')} RON</p>
                    <p className={`text-sm ${h.profit_loss >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {h.profit_loss >= 0 ? '+' : ''}{h.profit_loss?.toFixed(2)} ({h.profit_loss_percent?.toFixed(2)}%)
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Transactions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="w-5 h-5" /> Ultimele Tranzacții
          </CardTitle>
        </CardHeader>
        <CardContent>
          {transactions.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">Nicio tranzacție</p>
          ) : (
            <div className="space-y-2">
              {transactions.map((txn, idx) => (
                <div key={idx} className="flex items-center justify-between p-2 border-b last:border-0">
                  <div className="flex items-center gap-3">
                    <Badge variant={txn.action === 'buy' ? 'default' : 'secondary'}>
                      {txn.action === 'buy' ? 'CUMPĂRARE' : 'VÂNZARE'}
                    </Badge>
                    <span className="font-medium">{txn.symbol}</span>
                    <span className="text-sm text-muted-foreground">{txn.quantity} x {txn.price}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{txn.total?.toFixed(2)} RON</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(txn.created_at).toLocaleDateString('ro-RO')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
