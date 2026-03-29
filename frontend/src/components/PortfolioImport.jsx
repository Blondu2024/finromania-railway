import React, { useState } from 'react';
import { Upload, FileText, Calculator, AlertTriangle, CheckCircle, Loader2, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { useAuth } from '../context/AuthContext';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const BROKER_EXAMPLES = [
  { name: 'XTB', hint: 'Account History → Export CSV' },
  { name: 'Trading 212', hint: 'History → Export → CSV' },
  { name: 'Interactive Brokers', hint: 'Reports → Activity Statement → CSV' },
  { name: 'Revolut', hint: 'Stocks → Statement → Download' },
  { name: 'eToro', hint: 'Portfolio → Account Statement → Excel' },
  { name: 'Tradeville', hint: 'Portofoliu → Istoric → Export' },
];

export default function PortfolioImport() {
  const { token } = useAuth();
  const [csvText, setCsvText] = useState('');
  const [year, setYear] = useState(2025);
  const [hasSalary, setHasSalary] = useState(true);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => setCsvText(ev.target.result);
    reader.readAsText(file);
  };

  const analyze = async () => {
    if (!csvText.trim() || csvText.trim().length < 20) {
      setError('Lipește sau uploadează un raport de tranzacții');
      return;
    }
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await fetch(`${API_URL}/api/portfolio-import/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          csv_text: csvText,
          year,
          has_salary: hasSalary
        })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Eroare la analiză');
      }
      const data = await res.json();
      setReport(data.report);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatRON = (v) => v?.toLocaleString('ro-RO', { maximumFractionDigits: 0 }) + ' RON';

  return (
    <div className="space-y-6">
      {/* Input Section */}
      {!report && (
        <>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Import Portofoliu
              </CardTitle>
              <CardDescription>
                Uploadează sau lipește raportul CSV de la broker. AI-ul parsează automat orice format.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* File upload */}
              <div>
                <Label>Upload fișier CSV/TXT</Label>
                <input
                  type="file"
                  accept=".csv,.txt,.xlsx"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-muted-foreground mt-1
                    file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0
                    file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100 cursor-pointer"
                />
              </div>

              {/* Or paste */}
              <div>
                <Label>Sau lipește textul aici</Label>
                <textarea
                  value={csvText}
                  onChange={(e) => setCsvText(e.target.value)}
                  placeholder={"Date,Symbol,Type,Quantity,Price,P/L\n2025-01-15,AAPL,BUY,10,185.50,\n2025-03-20,AAPL,SELL,10,195.30,98.00"}
                  rows={8}
                  className="w-full mt-1 p-3 border rounded-lg text-sm font-mono bg-muted/30 resize-y"
                />
              </div>

              {/* Options */}
              <div className="flex flex-wrap items-center gap-6">
                <div>
                  <Label>An fiscal</Label>
                  <select
                    value={year}
                    onChange={(e) => setYear(parseInt(e.target.value))}
                    className="block mt-1 border rounded-lg px-3 py-2 text-sm"
                  >
                    <option value={2025}>2025</option>
                    <option value={2024}>2024</option>
                    <option value={2026}>2026</option>
                  </select>
                </div>
                <div className="flex items-center gap-2 pt-5">
                  <Switch checked={hasSalary} onCheckedChange={setHasSalary} />
                  <Label>Am salariu (CASS plătit)</Label>
                </div>
              </div>

              {/* Broker hints */}
              <div className="p-3 bg-muted/30 rounded-lg">
                <p className="text-xs font-medium text-muted-foreground mb-2">Cum exportezi de la broker:</p>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {BROKER_EXAMPLES.map(b => (
                    <div key={b.name} className="text-xs">
                      <span className="font-semibold">{b.name}:</span> {b.hint}
                    </div>
                  ))}
                </div>
              </div>

              <Button
                onClick={analyze}
                disabled={loading || !csvText.trim()}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    AI analizează tranzacțiile...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Calculator className="w-4 h-4" />
                    Analizează și Calculează Taxe
                  </span>
                )}
              </Button>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-950/30 border border-red-200 rounded-lg text-sm text-red-700 dark:text-red-400">
                  <AlertTriangle className="w-4 h-4 inline mr-2" />
                  {error}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Results */}
      {report && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card className="bg-blue-50 dark:bg-blue-950/30">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-muted-foreground">Câștiguri Nete</p>
                <p className={`text-xl font-bold ${report.net_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatRON(report.net_gain)}
                </p>
              </CardContent>
            </Card>
            <Card className="bg-purple-50 dark:bg-purple-950/30">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-muted-foreground">Dividende</p>
                <p className="text-xl font-bold text-purple-600">{formatRON(report.total_dividend_income)}</p>
              </CardContent>
            </Card>
            <Card className="bg-red-50 dark:bg-red-950/30">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-muted-foreground">Total Taxe</p>
                <p className="text-xl font-bold text-red-600">{formatRON(report.total_tax)}</p>
              </CardContent>
            </Card>
            <Card className="bg-green-50 dark:bg-green-950/30">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-muted-foreground">Rată Efectivă</p>
                <p className="text-xl font-bold text-green-600">{report.effective_rate}%</p>
              </CardContent>
            </Card>
          </div>

          {/* Tax Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Detalii Fiscale - {report.year}
              </CardTitle>
              <CardDescription>
                Broker: {report.broker} | Piață: {report.market === 'bvb' ? 'BVB' : 'Internațională'} | {report.total_transactions} vânzări, {report.total_dividends} dividende
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                  <span className="text-sm">Câștiguri brute</span>
                  <span className="font-semibold text-green-600">+{formatRON(report.total_gains)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                  <span className="text-sm">Pierderi</span>
                  <span className="font-semibold text-red-600">-{formatRON(report.total_losses)}</span>
                </div>
                <div className="flex justify-between items-center p-3 border-t pt-3">
                  <span className="text-sm font-medium">Impozit câștiguri capital</span>
                  <span className="font-semibold">{formatRON(report.capital_gains_tax)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                  <span className="text-sm font-medium">Impozit dividende</span>
                  <span className="font-semibold">{formatRON(report.dividend_tax)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-muted/30 rounded-lg">
                  <span className="text-sm font-medium">CASS (contribuție sănătate)</span>
                  <span className="font-semibold">{formatRON(report.cass_amount)}</span>
                </div>
                <div className="flex justify-between items-center p-4 bg-red-50 dark:bg-red-950/30 rounded-lg border border-red-200">
                  <span className="font-bold">TOTAL DE PLATĂ</span>
                  <span className="text-2xl font-bold text-red-600">{formatRON(report.total_tax)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* AI Summary */}
          {report.ai_summary && (
            <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200">
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <FileText className="w-4 h-4" />
                  Explicație AI
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-line">{report.ai_summary}</p>
              </CardContent>
            </Card>
          )}

          {/* Recommendations */}
          {report.recommendations?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  Recomandări
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {report.recommendations.map((r, i) => (
                    <li key={i} className="text-sm flex items-start gap-2">
                      <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 shrink-0" />
                      {r}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Transaction Details */}
          {report.tax_breakdown?.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Tranzacții Detaliate ({report.tax_breakdown.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left">
                        <th className="p-2">Data</th>
                        <th className="p-2">Simbol</th>
                        <th className="p-2">Tip</th>
                        <th className="p-2 text-right">P/L</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.tax_breakdown.map((tx, i) => (
                        <tr key={i} className="border-b hover:bg-muted/30">
                          <td className="p-2 text-muted-foreground">{tx.date}</td>
                          <td className="p-2 font-medium">{tx.symbol}</td>
                          <td className="p-2">
                            <Badge variant="outline" className="text-xs">
                              {tx.type === 'sell' ? 'Vânzare' : tx.type === 'dividend' ? 'Dividend' : tx.type}
                            </Badge>
                          </td>
                          <td className={`p-2 text-right font-medium ${
                            (tx.profit_loss || tx.amount || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {tx.type === 'dividend'
                              ? `+${formatRON(tx.amount)}`
                              : `${(tx.profit_loss || 0) >= 0 ? '+' : ''}${formatRON(tx.profit_loss || 0)}`}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Disclaimer */}
          <div className="p-4 bg-muted/30 rounded-lg text-xs text-muted-foreground flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
            {report.disclaimer}
          </div>

          {/* New Analysis */}
          <Button variant="outline" onClick={() => { setReport(null); setCsvText(''); }} className="w-full">
            Analiză Nouă
          </Button>
        </>
      )}
    </div>
  );
}
