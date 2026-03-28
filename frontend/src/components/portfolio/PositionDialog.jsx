import React, { useState, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../ui/dialog';

export default function PositionDialog({ open, onClose, onSave, editData, loading }) {
  const [form, setForm] = useState({
    symbol: '', shares: '', purchase_price: '', purchase_date: '', notes: ''
  });
  const [err, setErr] = useState('');

  useEffect(() => {
    if (editData) {
      setForm({
        symbol: editData.symbol || '',
        shares: String(editData.shares || ''),
        purchase_price: String(editData.purchase_price || ''),
        purchase_date: editData.purchase_date || '',
        notes: editData.notes || '',
      });
    } else {
      setForm({ symbol: '', shares: '', purchase_price: '', purchase_date: '', notes: '' });
    }
    setErr('');
  }, [editData, open]);

  const handleSave = () => {
    if (!form.symbol.trim()) return setErr('Introdu simbolul acțiunii (ex: TLV)');
    if (!form.shares || isNaN(Number(form.shares)) || Number(form.shares) <= 0)
      return setErr('Cantitate invalidă');
    if (!form.purchase_price || isNaN(Number(form.purchase_price)) || Number(form.purchase_price) <= 0)
      return setErr('Preț de intrare invalid');
    setErr('');
    onSave({
      symbol: form.symbol.trim().toUpperCase(),
      shares: Number(form.shares),
      purchase_price: Number(form.purchase_price),
      purchase_date: form.purchase_date || undefined,
      notes: form.notes || undefined,
    });
  };

  const isEdit = !!editData;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{isEdit ? `Editează ${editData?.symbol}` : 'Adaugă Poziție Nouă'}</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          {!isEdit && (
            <div>
              <Label>Simbol BVB <span className="text-red-500">*</span></Label>
              <Input
                placeholder="ex: TLV, SNP, BRD, H2O"
                value={form.symbol}
                onChange={e => setForm(p => ({ ...p, symbol: e.target.value.toUpperCase() }))}
                data-testid="portfolio-symbol-input"
                className="font-mono uppercase"
              />
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Cantitate (nr. acțiuni) <span className="text-red-500">*</span></Label>
              <Input
                type="number"
                min="1"
                step="1"
                placeholder="ex: 500"
                value={form.shares}
                onChange={e => setForm(p => ({ ...p, shares: e.target.value }))}
                data-testid="portfolio-shares-input"
                className="font-mono"
              />
            </div>
            <div>
              <Label>Preț mediu intrare (RON) <span className="text-red-500">*</span></Label>
              <Input
                type="number"
                min="0.01"
                step="0.01"
                placeholder="ex: 22.50"
                value={form.purchase_price}
                onChange={e => setForm(p => ({ ...p, purchase_price: e.target.value }))}
                data-testid="portfolio-price-input"
                className="font-mono"
              />
            </div>
          </div>
          <div>
            <Label>Dată intrare</Label>
            <Input
              type="date"
              value={form.purchase_date}
              onChange={e => setForm(p => ({ ...p, purchase_date: e.target.value }))}
              max={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div>
            <Label>Note (opțional)</Label>
            <Textarea
              placeholder="ex: Cumpărat la anunț dividende..."
              value={form.notes}
              onChange={e => setForm(p => ({ ...p, notes: e.target.value }))}
              rows={2}
            />
          </div>
          {err && (
            <div className="flex items-center gap-2 text-red-500 text-sm">
              <AlertCircle className="w-4 h-4" />
              {err}
            </div>
          )}
        </div>
        <DialogFooter className="gap-2">
          <Button variant="outline" onClick={onClose}>Anulează</Button>
          <Button
            onClick={handleSave}
            disabled={loading}
            data-testid="portfolio-save-btn"
            className="bg-blue-600 hover:bg-blue-700 text-white"
          >
            {loading ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : null}
            {isEdit ? 'Salvează' : 'Adaugă'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
