import React, { useState, useEffect } from 'react';
import { AlertTriangle, TrendingUp, TrendingDown, Info, HelpCircle, DollarSign } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Slider } from './ui/slider';
import { Alert, AlertDescription } from './ui/alert';
import { Badge } from './ui/badge';
import { Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function TradeModal({ open, onClose, onSuccess, portfolio }) {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [quantity, setQuantity] = useState(10);
  const [leverage, setLeverage] = useState(1);
  const [stopLoss, setStopLoss] = useState('');
  const [takeProfit, setTakeProfit] = useState('');
  const [positionType, setPositionType] = useState('long');
  const [loading, setLoading] = useState(false);
  const [showLeverageWarning, setShowLeverageWarning] = useState(false);
  const [showNoStopLossWarning, setShowNoStopLossWarning] = useState(false);

  useEffect(() => {
    if (open) {
      fetchStocks();
    }
  }, [open]);

  const fetchStocks = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stocks/bvb`);
      if (res.ok) {
        const data = await res.json();
        setStocks(data);
        if (data.length > 0) {
          setSelectedStock(data[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching stocks:', error);
    }
  };

  const maxLeverage = portfolio?.max_leverage || 2;
  const currentPrice = selectedStock?.price || 0;
  const positionValue = quantity * currentPrice;
  const marginRequired = positionValue / leverage;
  const canAfford = marginRequired <= (portfolio?.cash || 0);

  const handleSubmit = async () => {
    // Educational checks
    if (leverage > 1.5 && !showLeverageWarning) {
      setShowLeverageWarning(true);
      return;
    }

    if (!stopLoss && !showNoStopLossWarning) {
      setShowNoStopLossWarning(true);
      return;
    }

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/portfolio/trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          symbol: selectedStock.symbol,
          market_type: 'bvb',
          position_type: positionType,
          order_type: 'market',
          quantity: parseInt(quantity),
          leverage: leverage,
          stop_loss: stopLoss ? parseFloat(stopLoss) : null,
          take_profit: takeProfit ? parseFloat(takeProfit) : null
        })
      });

      const result = await res.json();

      if (res.ok) {
        alert(`✅ Tranzacție executată!\nMargin folosit: ${result.margin_used.toFixed(2)} RON\nCash rămas: ${result.remaining_cash.toFixed(2)} RON`);
        
        if (result.new_achievements && result.new_achievements.length > 0) {
          alert(`🏆 Realizare nouă: ${result.new_achievements.join(', ')}`);
        }
        
        onSuccess();
        resetForm();
        onClose();
      } else {
        alert(`❌ Eroare: ${result.detail}`);
      }
    } catch (error) {
      console.error('Error executing trade:', error);
      alert('Eroare la executarea tranzacției');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setQuantity(10);
    setLeverage(1);
    setStopLoss('');
    setTakeProfit('');
    setShowLeverageWarning(false);
    setShowNoStopLossWarning(false);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  // Leverage Warning Modal
  if (showLeverageWarning) {
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-orange-600">
              <AlertTriangle className="w-5 h-5" />
              Atenție: Risc Ridicat!
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Alert className="bg-orange-50 border-orange-200">
              <AlertDescription className="text-orange-800">
                <strong>Leverage {leverage}x înseamnă:</strong>
                <ul className="mt-2 space-y-1 list-disc list-inside">
                  <li>Controlezi {leverage}x mai mulți bani</li>
                  <li>Profiturile sunt amplificate cu {leverage}x</li>
                  <li>⚠️ Pierderile sunt amplificate cu {leverage}x</li>
                </ul>
              </AlertDescription>
            </Alert>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Exemplu:</h4>
              <p className="text-sm">• Investești: {marginRequired.toFixed(2)} RON</p>
              <p className="text-sm">• Controlezi: {positionValue.toFixed(2)} RON</p>
              <p className="text-sm text-red-600 font-medium">• Dacă scade {(100/leverage).toFixed(0)}% → Pierzi tot capitalul!</p>
            </div>

            <div className="space-y-2">
              <p className="text-sm font-medium">❓ Știi cum funcționează leverage-ul?</p>
              <div className="flex gap-2">
                <Link to="/advisor" onClick={handleClose}>
                  <Button variant="outline" size="sm">
                    <HelpCircle className="w-4 h-4 mr-2" />
                    Învață despre Leverage
                  </Button>
                </Link>
              </div>
            </div>

            <Alert>
              <Info className="w-4 h-4" />
              <AlertDescription>
                💡 Recomandare: Începe cu leverage 1x (fără levier) până înveți.
              </AlertDescription>
            </Alert>
          </div>
          <DialogFooter className="flex gap-2">
            <Button variant="outline" onClick={() => setShowLeverageWarning(false)}>
              Înapoi
            </Button>
            <Button onClick={handleSubmit} disabled={loading}>
              Am Înțeles, Continuă
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // No Stop Loss Warning
  if (showNoStopLossWarning) {
    return (
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-yellow-600">
              <AlertTriangle className="w-5 h-5" />
              Tranzacție fără protecție!
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Alert className="bg-yellow-50 border-yellow-200">
              <AlertDescription className="text-yellow-800">
                <strong>Nu ai setat Stop Loss!</strong>
                <p className="mt-2">Riscul: Poți pierde mai mult decât planifici.</p>
              </AlertDescription>
            </Alert>

            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">💡 Ce este Stop Loss?</h4>
              <p className="text-sm">Stop Loss închide automat poziția când prețul scade la un nivel setat de tine, limitând pierderile.</p>
              <p className="text-sm mt-2"><strong>Exemplu:</strong> Cumperi la {currentPrice} RON, setezi SL la {(currentPrice * 0.95).toFixed(2)} RON (-5%). Dacă scade, poziția se închide automat.</p>
            </div>

            <div className="space-y-2">
              <Label>Sugestie Stop Loss (recomandat):</Label>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setStopLoss((currentPrice * 0.95).toFixed(2));
                    setShowNoStopLossWarning(false);
                  }}
                >
                  -5% ({(currentPrice * 0.95).toFixed(2)} RON)
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setStopLoss((currentPrice * 0.90).toFixed(2));
                    setShowNoStopLossWarning(false);
                  }}
                >
                  -10% ({(currentPrice * 0.90).toFixed(2)} RON)
                </Button>
              </div>
            </div>
          </div>
          <DialogFooter className="flex gap-2">
            <Button variant="outline" onClick={() => setShowNoStopLossWarning(false)}>
              Adaugă Stop Loss
            </Button>
            <Button variant="destructive" onClick={handleSubmit} disabled={loading}>
              Continuă fără SL (risc)
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  }

  // Main Trade Modal
  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl">Tranzacție Nouă</DialogTitle>
          <DialogDescription>
            Capital disponibil: <strong>{portfolio?.cash.toLocaleString('ro-RO')} RON</strong>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Stock Selection */}
          <div className="space-y-2">
            <Label>Acțiune BVB</Label>
            <Select 
              value={selectedStock?.symbol} 
              onValueChange={(val) => setSelectedStock(stocks.find(s => s.symbol === val))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {stocks.map((stock) => (
                  <SelectItem key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} - {stock.name} ({stock.price} RON)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedStock && (
              <p className="text-sm text-muted-foreground">
                Preț curent: <strong>{selectedStock.price} RON</strong> • 
                Variație: <span className={selectedStock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}>
                  {selectedStock.change_percent >= 0 ? '+' : ''}{selectedStock.change_percent}%
                </span>
              </p>
            )}
          </div>

          {/* Position Type */}
          <div className="space-y-2">
            <Label>Tip Poziție</Label>
            <div className="flex gap-2">
              <Button
                variant={positionType === 'long' ? 'default' : 'outline'}
                onClick={() => setPositionType('long')}
                className="flex-1"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                LONG (Cumpără)
              </Button>
              <Button
                variant={positionType === 'short' ? 'default' : 'outline'}
                onClick={() => setPositionType('short')}
                className="flex-1"
                disabled={portfolio?.experience_level === 'beginner'}
              >
                <TrendingDown className="w-4 h-4 mr-2" />
                SHORT (Vinde în lipsă)
              </Button>
            </div>
            {portfolio?.experience_level === 'beginner' && (
              <p className="text-xs text-muted-foreground">SHORT disponibil de la nivel Intermediar</p>
            )}
          </div>

          {/* Quantity */}
          <div className="space-y-2">
            <Label>Cantitate</Label>
            <Input 
              type="number" 
              value={quantity} 
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              min="1"
            />
          </div>

          {/* Leverage Slider */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Leverage (Efect de levier)</Label>
              <Badge variant={leverage > 1.5 ? 'destructive' : 'secondary'}>
                {leverage}x
              </Badge>
            </div>
            <Slider
              value={[leverage]}
              onValueChange={(val) => setLeverage(val[0])}
              min={1}
              max={maxLeverage}
              step={0.5}
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>1x (Fără levier)</span>
              <span>Max: {maxLeverage}x</span>
            </div>
            {leverage > 1 && (
              <Alert className="bg-orange-50 border-orange-200">
                <AlertTriangle className="w-4 h-4 text-orange-600" />
                <AlertDescription className="text-orange-800 text-sm">
                  Cu {leverage}x leverage, profitul ȘI pierderea se multiplică cu {leverage}!
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Stop Loss & Take Profit */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Stop Loss (RON) - Recomandat</Label>
              <Input 
                type="number" 
                value={stopLoss} 
                onChange={(e) => setStopLoss(e.target.value)}
                placeholder={`ex: ${(currentPrice * 0.95).toFixed(2)}`}
                step="0.01"
              />
            </div>
            <div className="space-y-2">
              <Label>Take Profit (RON) - Opțional</Label>
              <Input 
                type="number" 
                value={takeProfit} 
                onChange={(e) => setTakeProfit(e.target.value)}
                placeholder={`ex: ${(currentPrice * 1.10).toFixed(2)}`}
                step="0.01"
              />
            </div>
          </div>

          {/* Preview */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
            <h4 className="font-semibold text-blue-900">Preview Tranzacție:</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Valoare poziție:</div>
              <div className="font-medium text-right">{positionValue.toFixed(2)} RON</div>
              
              <div>Margin necesar:</div>
              <div className="font-medium text-right">{marginRequired.toFixed(2)} RON</div>
              
              <div>Cash după:</div>
              <div className={`font-medium text-right ${canAfford ? 'text-green-600' : 'text-red-600'}`}>
                {canAfford ? (portfolio.cash - marginRequired).toFixed(2) : 'Insuficient'} RON
              </div>
            </div>
          </div>

          {!canAfford && (
            <Alert variant="destructive">
              <AlertTriangle className="w-4 h-4" />
              <AlertDescription>
                Cash insuficient! Reduce cantitatea sau leverage-ul.
              </AlertDescription>
            </Alert>
          )}
        </div>

        <DialogFooter className="flex gap-2">
          <Button variant="outline" onClick={handleClose}>
            Anulează
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={!canAfford || loading || !selectedStock}
          >
            <DollarSign className="w-4 h-4 mr-2" />
            {loading ? 'Procesare...' : 'Execută Tranzacția'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
