import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Upload, CheckCircle, AlertCircle, X, FileText, Loader2,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '../ui/dialog';
import { toast } from 'sonner';
import { API_URL, fmt } from './shared';

const BROKER_INFO = {
  xtb: {
    name: 'XTB',
    color: 'bg-blue-100 text-blue-700',
    instructions: 'XTB: Rapoarte → Poziții Deschise → Export CSV',
    symbol_note: 'Simbolurile TLVRO → TLV (sufixul RO e eliminat automat)',
  },
  tradeville: {
    name: 'Tradeville',
    color: 'bg-green-100 text-green-700',
    instructions: 'Tradeville: Portofoliu → Export Excel/CSV',
    symbol_note: 'Simbolurile TLV, SNP etc. sunt importate direct',
  },
  generic: {
    name: 'Generic',
    color: 'bg-gray-100 text-gray-700',
    instructions: 'Format: Symbol/Simbol, Quantity/Cantitate, Price/Pret (coloane CSV)',
    symbol_note: 'Asigură-te că simbolurile sunt în format BVB (ex: TLV, SNP)',
  },
};

export default function CSVImportDialog({ open, onClose, token, onImportComplete }) {
  const { t } = useTranslation();
  const [step, setStep] = useState('upload'); // upload | preview | importing | done
  const [detectedBroker, setDetectedBroker] = useState(null);
  const [parsedPositions, setParsedPositions] = useState([]);
  const [errors, setErrors] = useState([]);
  const [importing, setImporting] = useState(false);
  const [importResults, setImportResults] = useState(null);
  const fileRef = useRef(null);

  const reset = () => {
    setStep('upload');
    setDetectedBroker(null);
    setParsedPositions([]);
    setErrors([]);
    setImporting(false);
    setImportResults(null);
    if (fileRef.current) fileRef.current.value = '';
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleFile = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
      toast.error(t('csv.selectFile'));
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/api/portfolio-bvb/parse-csv`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || t('csv.parseError'));
        return;
      }

      setDetectedBroker(data.broker);
      setParsedPositions(data.positions || []);
      setErrors(data.errors || []);
      setStep('preview');
    } catch (e) {
      toast.error(t('csv.readError'));
    }
  };

  const handleImport = async () => {
    if (parsedPositions.length === 0) return;
    setImporting(true);
    setStep('importing');

    try {
      const res = await fetch(`${API_URL}/api/portfolio-bvb/import-positions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ positions: parsedPositions }),
      });
      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || t('csv.importError'));
        setStep('preview');
        return;
      }

      setImportResults(data);
      setStep('done');
      toast.success(t('csv.importSuccess', { count: data.imported }));
    } catch (e) {
      toast.error(t('csv.importError'));
      setStep('preview');
    } finally {
      setImporting(false);
    }
  };

  const brokerInfo = detectedBroker ? BROKER_INFO[detectedBroker] : null;

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5 text-blue-600" />
            {t('csv.importTitle')}
          </DialogTitle>
        </DialogHeader>

        {/* STEP 1: Upload */}
        {step === 'upload' && (
          <div className="space-y-5 py-2">
            {/* Supported brokers */}
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(BROKER_INFO).map(([key, info]) => (
                <div key={key} className="text-center p-3 rounded-lg border bg-muted/20">
                  <Badge className={`${info.color} mb-2`}>{info.name}</Badge>
                  <p className="text-xs text-muted-foreground">{info.instructions}</p>
                </div>
              ))}
            </div>

            {/* Drop zone */}
            <div
              className="border-2 border-dashed border-border rounded-xl p-10 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-colors"
              onClick={() => fileRef.current?.click()}
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); }}
              data-testid="csv-drop-zone"
            >
              <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
              <p className="font-medium mb-1">{t('csv.dragOrClick')}</p>
              <p className="text-sm text-muted-foreground">{t('csv.acceptedFormats')}</p>
              <input
                ref={fileRef}
                type="file"
                accept=".csv,.txt"
                className="hidden"
                onChange={e => handleFile(e.target.files[0])}
                data-testid="csv-file-input"
              />
            </div>

            {/* Generic format hint */}
            <div className="bg-muted/40 rounded-lg p-3 text-xs text-muted-foreground">
              <p className="font-medium text-foreground mb-1">{t('csv.genericFormat')}:</p>
              <code className="block bg-background border rounded p-2 font-mono text-xs mt-1">
                Symbol,Quantity,Price<br />
                TLV,100,24.50<br />
                SNP,500,0.58
              </code>
            </div>
          </div>
        )}

        {/* STEP 2: Preview */}
        {step === 'preview' && (
          <div className="space-y-4 py-2">
            {brokerInfo && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-muted-foreground">{t('csv.detectedFormat')}:</span>
                <Badge className={brokerInfo.color}>{brokerInfo.name}</Badge>
                <span className="text-xs text-muted-foreground">· {brokerInfo.symbol_note}</span>
              </div>
            )}

            {errors.length > 0 && (
              <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-3">
                <p className="text-sm font-medium text-amber-700 dark:text-amber-400 mb-1">
                  {t('csv.rowsIgnored', { count: errors.length })}:
                </p>
                {errors.slice(0, 3).map((e, i) => (
                  <p key={i} className="text-xs text-amber-600 dark:text-amber-500">{e}</p>
                ))}
                {errors.length > 3 && (
                  <p className="text-xs text-amber-500">...{t('csv.andMore', { count: errors.length - 3 })}</p>
                )}
              </div>
            )}

            {parsedPositions.length === 0 ? (
              <div className="text-center py-8">
                <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
                <p className="font-medium">{t('csv.noValidPositions')}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {t('csv.checkFormat')}
                </p>
                <Button variant="outline" onClick={reset} className="mt-4">{t('csv.tryAnotherFile')}</Button>
              </div>
            ) : (
              <>
                <p className="text-sm font-medium">{t('csv.positionsDetected', { count: parsedPositions.length })}:</p>
                <div className="overflow-x-auto border rounded-lg">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left px-3 py-2 font-medium">{t('csv.symbol')}</th>
                        <th className="text-right px-3 py-2 font-medium">{t('csv.quantity')}</th>
                        <th className="text-right px-3 py-2 font-medium">{t('csv.entryPrice')}</th>
                        <th className="text-right px-3 py-2 font-medium">{t('csv.estValue')}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      {parsedPositions.map((pos, i) => (
                        <tr key={i} className="hover:bg-muted/20">
                          <td className="px-3 py-2 font-bold font-mono">{pos.symbol}</td>
                          <td className="px-3 py-2 text-right font-mono">{fmt(pos.shares, 0)}</td>
                          <td className="px-3 py-2 text-right font-mono">{fmt(pos.purchase_price)} RON</td>
                          <td className="px-3 py-2 text-right font-mono text-muted-foreground">
                            {fmt(pos.shares * pos.purchase_price)} RON
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-muted-foreground">
                  * {t('csv.existingNote')}
                </p>
              </>
            )}
          </div>
        )}

        {/* STEP 3: Importing */}
        {step === 'importing' && (
          <div className="py-12 text-center">
            <Loader2 className="w-12 h-12 text-blue-500 mx-auto mb-4 animate-spin" />
            <p className="font-medium">{t('csv.importing')}</p>
            <p className="text-sm text-muted-foreground mt-1">
              {t('csv.processing', { count: parsedPositions.length })}
            </p>
          </div>
        )}

        {/* STEP 4: Done */}
        {step === 'done' && importResults && (
          <div className="py-8 text-center space-y-4">
            <CheckCircle className="w-14 h-14 text-emerald-500 mx-auto" />
            <div>
              <p className="text-xl font-bold">{t('csv.importComplete')}</p>
              <p className="text-muted-foreground mt-1">
                {importResults.imported} {t('csv.imported')} ·{' '}
                {importResults.updated} {t('csv.updated')} ·{' '}
                {importResults.skipped} {t('csv.skipped')}
              </p>
            </div>
            <Button
              onClick={() => { onImportComplete(); handleClose(); }}
              className="bg-blue-600 hover:bg-blue-700 text-white"
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              {t('csv.openPortfolio')}
            </Button>
          </div>
        )}

        <DialogFooter className="gap-2">
          {step === 'upload' && (
            <Button variant="outline" onClick={handleClose}>{t('common.cancel')}</Button>
          )}
          {step === 'preview' && parsedPositions.length > 0 && (
            <>
              <Button variant="outline" onClick={reset}>
                <X className="w-4 h-4 mr-1" /> {t('csv.anotherFile')}
              </Button>
              <Button
                onClick={handleImport}
                className="bg-blue-600 hover:bg-blue-700 text-white"
                data-testid="csv-import-confirm-btn"
              >
                <Upload className="w-4 h-4 mr-2" />
                {t('csv.importCount', { count: parsedPositions.length })}
              </Button>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
