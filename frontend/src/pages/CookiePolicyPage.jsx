import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, Cookie } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

export default function CookiePolicyPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="w-4 h-4 mr-2" /> Înapoi
        </Button>
      </Link>

      <div className="flex items-center gap-3">
        <Cookie className="w-8 h-8 text-blue-600" />
        <h1 className="text-3xl font-bold">Politica de Cookie-uri</h1>
      </div>
      
      <p className="text-muted-foreground">Ultima actualizare: 23 Decembrie 2025</p>

      <Card>
        <CardContent className="prose dark:prose-invert max-w-none p-6 space-y-6">
          <section>
            <h2 className="text-xl font-semibold">1. Ce sunt cookie-urile?</h2>
            <p>
              Cookie-urile sunt fișiere mici de text stocate pe dispozitivul dumneavoastră atunci 
              când vizitați un site web. Acestea permit site-ului să vă recunoască și să rețină 
              anumite informații despre preferințele dumneavoastră.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">2. Tipuri de cookie-uri utilizate</h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tip</TableHead>
                  <TableHead>Scop</TableHead>
                  <TableHead>Durată</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Esențiale</TableCell>
                  <TableCell>Funcționarea de bază a site-ului</TableCell>
                  <TableCell>Sesiune</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Preferințe</TableCell>
                  <TableCell>Salvarea modului întunecat/luminos</TableCell>
                  <TableCell>1 an</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Analiză</TableCell>
                  <TableCell>Înțelegerea modului de utilizare a site-ului</TableCell>
                  <TableCell>2 ani</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </section>

          <section>
            <h2 className="text-xl font-semibold">3. Cookie-uri utilizate</h2>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>darkMode:</strong> Salvează preferința pentru tema întunecată (localStorage)</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">4. Cum să gestionați cookie-urile</h2>
            <p>
              Puteți controla și șterge cookie-urile prin setările browser-ului dumneavoastră. 
              Rețineți că dezactivarea cookie-urilor poate afecta funcționalitatea site-ului.
            </p>
            <p>Ghiduri pentru browsere populare:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Chrome</a></li>
              <li><a href="https://support.mozilla.org/ro/kb/cookie-urile" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Mozilla Firefox</a></li>
              <li><a href="https://support.apple.com/ro-ro/guide/safari/sfri11471/mac" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Safari</a></li>
              <li><a href="https://support.microsoft.com/ro-ro/microsoft-edge/ștergerea-cookie-urilor" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Microsoft Edge</a></li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold">5. Consimțământul</h2>
            <p>
              Prin continuarea navigării pe site-ul nostru, vă exprimați consimțământul pentru 
              utilizarea cookie-urilor în conformitate cu această politică.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">6. Actualizări</h2>
            <p>
              Această Politică de Cookie-uri poate fi actualizată periodic. Vă recomandăm să 
              verificați această pagină regulat pentru a fi la curent cu modificările.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold">7. Contact</h2>
            <p>
              Pentru întrebări despre cookie-uri: <strong>contact@finromania.ro</strong>
            </p>
          </section>
        </CardContent>
      </Card>
    </div>
  );
}
