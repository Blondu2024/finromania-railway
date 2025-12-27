import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Star, Plus, Trash2, Bell, BellOff, TrendingUp, TrendingDown,
  AlertTriangle, Settings, Eye, Edit2, X, Save, RefreshCw,
  Globe, Newspaper, GraduationCap, Loader2
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { Switch } from '../components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Notification Settings Dialog
const NotificationSettingsDialog = ({ token }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState({
    market_open_close: false,
    market_big_moves: false,
    daily_summary: false,
    watchlist_price_alerts: true,
    watchlist_big_moves: true,
    dividend_announcements: false,
    important_news: false,
    watchlist_news: false,
    lesson_reminders: false
  });

  useEffect(() => {
    if (isOpen && token) {
      fetchPreferences();
    }
  }, [isOpen, token]);

  const fetchPreferences = async () => {
    try {
      const res = await fetch(`${API_URL}/api/watchlist/notifications/preferences`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setPreferences(prev => ({ ...prev, ...data }));
      }
    } catch (err) {
      console.error('Error fetching preferences:', err);
    }
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/api/watchlist/notifications/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(preferences)
      });
      setIsOpen(false);
    } catch (err) {
      console.error('Error saving preferences:', err);
    } finally {
      setSaving(false);
    }
  };

  const Toggle = ({ label, description, checked, onChange, icon: Icon }) => (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div className="flex items-center gap-3">
        {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
        <div>
          <p className="font-medium text-sm">{label}</p>
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </div>
      <Switch checked={checked} onCheckedChange={onChange} />
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Bell className="w-4 h-4 mr-2" />
          Setări Notificări
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-md max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-blue-500" />
            Ce notificări vrei să primești?
          </DialogTitle>
          <DialogDescription>
            Alege ce alerte și actualizări vrei să primești
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Piață */}
          <div>
            <h4 className="font-semibold text-sm text-blue-600 mb-2 flex items-center gap-2">
              <Globe className="w-4 h-4" /> Piață
            </h4>
            <div className="bg-muted/30 rounded-lg px-3">
              <Toggle
                label="Deschidere/Închidere Bursă"
                description="La 10:00 și 18:00"
                checked={preferences.market_open_close}
                onChange={(v) => setPreferences(p => ({ ...p, market_open_close: v }))}
              />
              <Toggle
                label="Variații Mari (>2%)"
                description="Când indicele BET variază mult"
                checked={preferences.market_big_moves}
                onChange={(v) => setPreferences(p => ({ ...p, market_big_moves: v }))}
              />
              <Toggle
                label="Rezumat Zilnic"
                description="Seara la 18:30"
                checked={preferences.daily_summary}
                onChange={(v) => setPreferences(p => ({ ...p, daily_summary: v }))}
              />
            </div>
          </div>

          {/* Watchlist */}
          <div>
            <h4 className="font-semibold text-sm text-yellow-600 mb-2 flex items-center gap-2">
              <Star className="w-4 h-4" /> Watchlist
            </h4>
            <div className="bg-muted/30 rounded-lg px-3">
              <Toggle
                label="Alerte de Preț"
                description="Când prețul atinge valorile setate"
                checked={preferences.watchlist_price_alerts}
                onChange={(v) => setPreferences(p => ({ ...p, watchlist_price_alerts: v }))}
              />
              <Toggle
                label="Variații Mari (>5%)"
                description="Acțiunile tale variază mult"
                checked={preferences.watchlist_big_moves}
                onChange={(v) => setPreferences(p => ({ ...p, watchlist_big_moves: v }))}
              />
              <Toggle
                label="Anunțuri Dividende"
                description="Companiile anunță dividende"
                checked={preferences.dividend_announcements}
                onChange={(v) => setPreferences(p => ({ ...p, dividend_announcements: v }))}
              />
            </div>
          </div>

          {/* Știri */}
          <div>
            <h4 className="font-semibold text-sm text-purple-600 mb-2 flex items-center gap-2">
              <Newspaper className="w-4 h-4" /> Știri
            </h4>
            <div className="bg-muted/30 rounded-lg px-3">
              <Toggle
                label="Știri Importante"
                description="Breaking news financiar"
                checked={preferences.important_news}
                onChange={(v) => setPreferences(p => ({ ...p, important_news: v }))}
              />
              <Toggle
                label="Știri Watchlist"
                description="Despre companiile tale"
                checked={preferences.watchlist_news}
                onChange={(v) => setPreferences(p => ({ ...p, watchlist_news: v }))}
              />
            </div>
          </div>

          {/* Educație */}
          <div>
            <h4 className="font-semibold text-sm text-green-600 mb-2 flex items-center gap-2">
              <GraduationCap className="w-4 h-4" /> Educație
            </h4>
            <div className="bg-muted/30 rounded-lg px-3">
              <Toggle
                label="Reminder Lecții"
                description="Continuă cursurile începute"
                checked={preferences.lesson_reminders}
                onChange={(v) => setPreferences(p => ({ ...p, lesson_reminders: v }))}
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={savePreferences} disabled={saving}>
            {saving ? (
              <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Se salvează...</>
            ) : (
              <><Save className="w-4 h-4 mr-2" /> Salvează</>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Add Stock Dialog
const AddStockDialog = ({ onAdd, existingSymbols }) => {
  const [symbol, setSymbol] = useState('');
  const [alertAbove, setAlertAbove] = useState('');
  const [alertBelow, setAlertBelow] = useState('');
  const [notes, setNotes] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    if (!symbol.trim()) return;
    
    setLoading(true);
    await onAdd({
      symbol: symbol.toUpperCase(),
      alert_above: alertAbove ? parseFloat(alertAbove) : null,
      alert_below: alertBelow ? parseFloat(alertBelow) : null,
      notes: notes || null
    });
    setLoading(false);
    setSymbol('');
    setAlertAbove('');
    setAlertBelow('');
    setNotes('');
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Adaugă Acțiune
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Adaugă în Watchlist</DialogTitle>
          <DialogDescription>
            Adaugă o acțiune BVB și setează alerte de preț opționale
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div>
            <label className="text-sm font-medium">Simbol *</label>
            <Input
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="Ex: TLV, SNP, BRD"
              className="mt-1"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-green-600">🔔 Alertă peste (RON)</label>
              <Input
                type="number"
                value={alertAbove}
                onChange={(e) => setAlertAbove(e.target.value)}
                placeholder="Ex: 30.00"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-red-600">🔔 Alertă sub (RON)</label>
              <Input
                type="number"
                value={alertBelow}
                onChange={(e) => setAlertBelow(e.target.value)}
                placeholder="Ex: 25.00"
                className="mt-1"
              />
            </div>
          </div>
          
          <div>
            <label className="text-sm font-medium">Note (opțional)</label>
            <Input
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Cumpărat la 27.50"
              className="mt-1"
            />
          </div>
        </div>
        
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Anulează
          </Button>
          <Button onClick={handleAdd} disabled={!symbol.trim() || loading}>
            {loading ? 'Se adaugă...' : 'Adaugă'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

// Watchlist Item Component
const WatchlistItem = ({ item, onRemove, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [alertAbove, setAlertAbove] = useState(item.alert_above || '');
  const [alertBelow, setAlertBelow] = useState(item.alert_below || '');
  const [notes, setNotes] = useState(item.notes || '');

  const handleSave = async () => {
    await onUpdate(item.symbol, {
      symbol: item.symbol,
      alert_above: alertAbove ? parseFloat(alertAbove) : null,
      alert_below: alertBelow ? parseFloat(alertBelow) : null,
      notes: notes || null
    });
    setIsEditing(false);
  };

  const isPositive = (item.change_percent || 0) >= 0;
  const hasTriggeredAlert = item.alert_triggered_above || item.alert_triggered_below;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
    >
      <Card className={`overflow-hidden ${hasTriggeredAlert ? 'ring-2 ring-yellow-500 animate-pulse' : ''}`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            {/* Stock Info */}
            <div className="flex items-center gap-4">
              <Link to={`/stocks/bvb/${item.symbol}`}>
                <div className="text-center hover:text-blue-600 transition-colors">
                  <p className="font-bold text-lg">{item.symbol}</p>
                  <p className="text-xs text-muted-foreground truncate max-w-[100px]">
                    {item.name}
                  </p>
                </div>
              </Link>
              
              <div className="text-center">
                <p className="text-xl font-bold">{item.price?.toFixed(2)} RON</p>
                <div className={`flex items-center justify-center gap-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {isPositive ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  <span className="font-medium">
                    {isPositive ? '+' : ''}{item.change_percent?.toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Alerts */}
            <div className="flex items-center gap-4">
              {isEditing ? (
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={alertAbove}
                    onChange={(e) => setAlertAbove(e.target.value)}
                    placeholder="Peste"
                    className="w-20 h-8 text-sm"
                  />
                  <Input
                    type="number"
                    value={alertBelow}
                    onChange={(e) => setAlertBelow(e.target.value)}
                    placeholder="Sub"
                    className="w-20 h-8 text-sm"
                  />
                  <Button size="sm" onClick={handleSave}>
                    <Save className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setIsEditing(false)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              ) : (
                <>
                  {(item.alert_above || item.alert_below) && (
                    <div className="flex flex-col gap-1 text-sm">
                      {item.alert_above && (
                        <Badge variant={item.alert_triggered_above ? "default" : "outline"} className="gap-1">
                          <Bell className="w-3 h-3" />
                          ≥ {item.alert_above} RON
                          {item.alert_triggered_above && <AlertTriangle className="w-3 h-3 text-yellow-500" />}
                        </Badge>
                      )}
                      {item.alert_below && (
                        <Badge variant={item.alert_triggered_below ? "destructive" : "outline"} className="gap-1">
                          <Bell className="w-3 h-3" />
                          ≤ {item.alert_below} RON
                          {item.alert_triggered_below && <AlertTriangle className="w-3 h-3 text-yellow-500" />}
                        </Badge>
                      )}
                    </div>
                  )}
                  
                  <div className="flex items-center gap-1">
                    <Button size="sm" variant="ghost" onClick={() => setIsEditing(true)}>
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button size="sm" variant="ghost" className="text-red-500" onClick={() => onRemove(item.symbol)}>
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </>
              )}
            </div>
          </div>
          
          {/* Notes */}
          {item.notes && !isEditing && (
            <p className="mt-2 text-sm text-muted-foreground italic">
              📝 {item.notes}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

// Main Page Component
export default function WatchlistPage() {
  const { user, token } = useAuth();
  const [watchlist, setWatchlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchWatchlist = useCallback(async () => {
    if (!token) return;
    
    try {
      const res = await fetch(`${API_URL}/api/watchlist`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setWatchlist(data.items || []);
      }
    } catch (err) {
      console.error('Error fetching watchlist:', err);
      setError('Nu am putut încărca watchlist-ul');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    fetchWatchlist();
    const interval = setInterval(fetchWatchlist, 30000);
    return () => clearInterval(interval);
  }, [fetchWatchlist]);

  const handleAdd = async (item) => {
    try {
      const res = await fetch(`${API_URL}/api/watchlist/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(item)
      });
      
      if (res.ok) {
        await fetchWatchlist();
      } else {
        const data = await res.json();
        alert(data.detail || 'Eroare la adăugare');
      }
    } catch (err) {
      console.error('Error adding to watchlist:', err);
    }
  };

  const handleRemove = async (symbol) => {
    if (!window.confirm(`Ștergi ${symbol} din watchlist?`)) return;
    
    try {
      const res = await fetch(`${API_URL}/api/watchlist/remove/${symbol}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (res.ok) {
        setWatchlist(prev => prev.filter(item => item.symbol !== symbol));
      }
    } catch (err) {
      console.error('Error removing from watchlist:', err);
    }
  };

  const handleUpdate = async (symbol, updates) => {
    try {
      const res = await fetch(`${API_URL}/api/watchlist/update/${symbol}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updates)
      });
      
      if (res.ok) {
        await fetchWatchlist();
      }
    } catch (err) {
      console.error('Error updating watchlist item:', err);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchWatchlist();
  };

  // Not logged in
  if (!user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-8 text-center">
            <Star className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Watchlist Personal</h2>
            <p className="text-muted-foreground mb-6">
              Creează-ți un cont gratuit pentru a urmări acțiunile preferate și a seta alerte de preț.
            </p>
            <div className="flex gap-3 justify-center">
              <Link to="/login">
                <Button>Conectare</Button>
              </Link>
              <Link to="/register">
                <Button variant="outline">Înregistrare</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <>
      <SEO 
        title="Watchlist Personal | FinRomania"
        description="Urmărește acțiunile BVB preferate și setează alerte de preț personalizate."
      />

      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-2">
              <Star className="w-8 h-8 text-yellow-500" />
              Watchlist Personal
            </h1>
            <p className="text-muted-foreground">
              {watchlist.length} acțiuni urmărite • Actualizare la 30 secunde
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleRefresh} disabled={refreshing}>
              <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Actualizează
            </Button>
            <NotificationSettingsDialog token={token} />
            <AddStockDialog 
              onAdd={handleAdd} 
              existingSymbols={watchlist.map(w => w.symbol)} 
            />
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-24" />)}
          </div>
        )}

        {/* Empty State */}
        {!loading && watchlist.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Eye className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-bold mb-2">Watchlist-ul tău este gol</h3>
              <p className="text-muted-foreground mb-6">
                Adaugă acțiuni pentru a le urmări și a primi alerte când prețul atinge valorile setate.
              </p>
              <AddStockDialog 
                onAdd={handleAdd} 
                existingSymbols={[]} 
              />
              
              {/* Explicație cum funcționează */}
              <div className="mt-8 pt-8 border-t text-left max-w-lg mx-auto">
                <h4 className="font-bold text-lg mb-4">📖 Cum funcționează Watchlist-ul?</h4>
                <div className="space-y-3 text-sm text-muted-foreground">
                  <div className="flex items-start gap-3">
                    <span className="text-xl">1️⃣</span>
                    <p><strong>Adaugă acțiuni</strong> - Caută simbolul (ex: TLV, SNP) și adaugă în listă</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-xl">2️⃣</span>
                    <p><strong>Setează alerte</strong> - Primești notificare când prețul depășește/scade sub o valoare</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-xl">3️⃣</span>
                    <p><strong>Urmărește live</strong> - Vezi prețurile actualizate la fiecare 30 secunde</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-xl">4️⃣</span>
                    <p><strong>Adaugă note</strong> - Notează prețul la care ai cumpărat sau alte detalii</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Watchlist Items */}
        <AnimatePresence>
          <div className="space-y-3">
            {watchlist.map(item => (
              <WatchlistItem
                key={item.symbol}
                item={item}
                onRemove={handleRemove}
                onUpdate={handleUpdate}
              />
            ))}
          </div>
        </AnimatePresence>

        {/* Triggered Alerts Summary */}
        {watchlist.some(w => w.alert_triggered_above || w.alert_triggered_below) && (
          <Card className="border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-yellow-700 dark:text-yellow-400">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-bold">Alerte Declanșate!</span>
              </div>
              <ul className="mt-2 space-y-1 text-sm">
                {watchlist.filter(w => w.alert_triggered_above).map(w => (
                  <li key={`${w.symbol}-above`}>
                    🔔 {w.symbol} a depășit {w.alert_above} RON (acum: {w.price?.toFixed(2)} RON)
                  </li>
                ))}
                {watchlist.filter(w => w.alert_triggered_below).map(w => (
                  <li key={`${w.symbol}-below`}>
                    🔔 {w.symbol} a scăzut sub {w.alert_below} RON (acum: {w.price?.toFixed(2)} RON)
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Quick Add Popular */}
        {watchlist.length < 5 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sugestii Populare</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {['TLV', 'SNP', 'BRD', 'DIGI', 'SNN', 'TGN', 'M', 'SFG'].filter(
                  s => !watchlist.find(w => w.symbol === s)
                ).map(symbol => (
                  <Button
                    key={symbol}
                    variant="outline"
                    size="sm"
                    onClick={() => handleAdd({ symbol })}
                  >
                    <Plus className="w-3 h-3 mr-1" />
                    {symbol}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </>
  );
}
